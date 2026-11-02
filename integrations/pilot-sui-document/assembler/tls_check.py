"""Serve SUI over TLS on a real local socket and check the handshake."""

import argparse
import datetime
import hashlib
import ipaddress
import json
import os
import socket
import sys
import tempfile
import threading
import time
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
        .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost"), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), critical=False)
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    repo = Path(args.sui_repo)
    tmp = Path(tempfile.mkdtemp(prefix="sui-tls-"))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{tmp / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "tls-test-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(repo / "03_Implement/backend/src"))

    import httpx
    import uvicorn

    from sui_sensemaking_api.db import engine
    from sui_sensemaking_api.main import app
    from sui_sensemaking_api.models import Base

    Base.metadata.create_all(engine)
    cert_path, key_path = make_cert(tmp)
    port = free_port()
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host="127.0.0.1",
            port=port,
            log_level="error",
            ssl_certfile=str(cert_path),
            ssl_keyfile=str(key_path),
        )
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    base_url = f"https://127.0.0.1:{port}"
    ready = False
    authenticated = None
    anonymous = None
    try:
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                authenticated = httpx.get(
                    f"{base_url}/openapi.json",
                    headers={"X-API-Key": "tls-test-key"},
                    verify=False,
                    timeout=3,
                )
                ready = True
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        if ready:
            anonymous = httpx.get(f"{base_url}/openapi.json", verify=False, timeout=5)
    finally:
        server.should_exit = True
        thread.join(timeout=15)

    receipt = {
        "schema": "tai.reference.tei-sui-tls/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, uvicorn, and a self-signed certificate",
        "command": f"python integrations/pilot-sui-document/assembler/tls_check.py --sui-repo {args.sui_repo}",
        "result": "PASS" if ready and authenticated is not None and authenticated.status_code == 200 else "FAIL",
        "observed": {
            "serverReady": ready,
            "url": base_url,
            "certificate": "self-signed for localhost/127.0.0.1",
            "authenticatedStatus": authenticated.status_code if authenticated is not None else None,
            "anonymousStatus": anonymous.status_code if anonymous is not None else None,
            "tls": True,
            "database": "temporary SQLite",
            "runtimeProfile": "local-dev",
        },
        "scope": "SUI runs behind its own TLS listener with a self-signed certificate on a local socket. It does not verify a real CA, a reverse proxy, HSTS, client certificates, or deployment.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt["observed"]))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
