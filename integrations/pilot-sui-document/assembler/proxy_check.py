"""Serve SUI behind a local TLS-terminating reverse proxy and save a document."""

import argparse
import datetime
import hashlib
import http.client
import ipaddress
import json
import os
import socket
import ssl
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_cert(directory):
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=1))
        .add_extension(
            x509.SubjectAlternativeName(
                [x509.DNSName("localhost"), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]
            ),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )
    cert_path = directory / "cert.pem"
    key_path = directory / "key.pem"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    return cert_path, key_path


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class ProxyHandler(BaseHTTPRequestHandler):
    backend = None

    def _forward(self, method):
        length = int(self.headers.get("content-length", "0"))
        body = self.rfile.read(length) if length else None
        conn = http.client.HTTPConnection(self.backend, timeout=60)
        headers = {
            key: value
            for key, value in self.headers.items()
            if key.lower() not in {"host", "connection", "content-length"}
        }
        headers["X-Forwarded-Proto"] = "https"
        headers["X-Forwarded-For"] = self.client_address[0]
        headers["X-Forwarded-Host"] = self.headers.get("host", "localhost")
        conn.request(method, self.path, body=body, headers=headers)
        response = conn.getresponse()
        payload = response.read()
        self.send_response(response.status)
        for key, value in response.getheaders():
            if key.lower() in {"transfer-encoding", "connection", "content-length", "date", "server"}:
                continue
            self.send_header(key, value)
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        if payload:
            self.wfile.write(payload)
        conn.close()

    def do_GET(self):
        self._forward("GET")

    def do_PUT(self):
        self._forward("PUT")

    def do_POST(self):
        self._forward("POST")

    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="sui-proxy-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite+pysqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "proxy-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    import httpx
    import uvicorn
    from sqlalchemy import text

    from sui_sensemaking_api.db import engine
    from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload
    from sui_sensemaking_api.main import app
    from sui_sensemaking_api.models import Base

    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                "insert into tenants (id, display_name, lifecycle_state, created_at, updated_at) "
                "values ('local-default', 'Local', 'active', '2026-11-03T00:00:00Z', '2026-11-03T00:00:00Z') "
                "on conflict (id) do nothing"
            )
        )
    projected = from_artifact(json.loads(Path(args.artifact).read_text(encoding="utf-8")))
    payload = to_documentv1_payload(
        projected,
        transform={"panX": 0.0, "panY": 0.0, "zoom": 1.0},
        created_at="2026-11-03T00:00:00Z",
        updated_at="2026-11-03T00:00:00Z",
    )

    backend_port = free_port()
    uvicorn_server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=backend_port, log_level="error", proxy_headers=True)
    )
    thread = threading.Thread(target=uvicorn_server.run, daemon=True)
    thread.start()

    proxy_port = free_port()
    ProxyHandler.backend = f"127.0.0.1:{backend_port}"
    proxy = ThreadingHTTPServer(("127.0.0.1", proxy_port), ProxyHandler)
    cert_path, key_path = make_cert(workdir)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))
    proxy.socket = context.wrap_socket(proxy.socket, server_side=True)
    proxy_thread = threading.Thread(target=proxy.serve_forever, daemon=True)
    proxy_thread.start()

    base = f"https://127.0.0.1:{proxy_port}"
    verify = str(cert_path)
    ready = False
    created = fetched = anonymous = None
    try:
        deadline = time.time() + 90
        while time.time() < deadline:
            try:
                httpx.get(f"{base}/openapi.json", verify=verify, timeout=3)
                ready = True
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        if not ready:
            raise RuntimeError("proxy did not become ready")
        headers = {"X-API-Key": "proxy-key"}
        created = httpx.put(f"{base}/docs/{projected.id}", json=payload, headers=headers, verify=verify, timeout=60)
        fetched = httpx.get(f"{base}/docs/{projected.id}", headers=headers, verify=verify, timeout=60)
        anonymous = httpx.put(f"{base}/docs/{projected.id}", json=payload, verify=verify, timeout=60)
    finally:
        uvicorn_server.should_exit = True
        proxy.shutdown()
        thread.join(timeout=20)

    checks = {
        "proxyReady": ready,
        "createStatus": created.status_code if created else None,
        "fetchStatus": fetched.status_code if fetched else None,
        "roundTrip": bool(fetched) and fetched.json().get("id") == projected.id,
        "anonymousStatus": anonymous.status_code if anonymous else None,
    }
    passed = (
        checks["proxyReady"]
        and checks["createStatus"] in (200, 201)
        and checks["fetchStatus"] == 200
        and checks["roundTrip"]
        and checks["anonymousStatus"] in (401, 403)
    )
    receipt = {
        "schema": "tai.reference.sui-proxy-check/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with a local TLS-terminating proxy in front of SUI on loopback",
        "command": "python integrations/pilot-sui-document/assembler/proxy_check.py --sui-repo <SUI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/SUI-TEI-proxy-2026-11-03.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Runs SUI behind a small local TLS-terminating proxy that adds X-Forwarded-* headers, then saves and reads one document. It is not a production reverse proxy and does not exercise HSTS or real certificates.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
