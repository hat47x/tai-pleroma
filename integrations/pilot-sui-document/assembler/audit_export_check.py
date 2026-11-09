"""Enable SUI's HTTP audit export against a local sink and confirm one event arrives."""

import argparse
import hashlib
import json
import os
import socket
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

EVENTS = []


class Sink(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("content-length", "0"))
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            body = {"raw": raw[:200].decode("utf-8", "replace")}
        EVENTS.append(
            {
                "path": self.path,
                "authorization": self.headers.get("authorization"),
                "contentType": self.headers.get("content-type"),
                "body": body,
            }
        )
        self.send_response(204)
        self.send_header("content-length", "0")
        self.end_headers()

    def log_message(self, *args):
        pass


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="sui-audit-", dir=os.environ.get("GOTMPDIR") or None))
    sink = ThreadingHTTPServer(("127.0.0.1", 0), Sink)
    threading.Thread(target=sink.serve_forever, daemon=True).start()

    os.environ["SUI_DATABASE_URL"] = f"sqlite+pysqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "audit-key"
    os.environ["SUI_AUDIT_EXPORT_ENABLED"] = "true"
    os.environ["SUI_AUDIT_TRANSPORT"] = "http"
    os.environ["SUI_AUDIT_HTTP_ENDPOINT"] = f"http://127.0.0.1:{sink.server_address[1]}/events"
    os.environ["SUI_AUDIT_HTTP_API_KEY"] = "sink-key"
    os.environ["SUI_AUDIT_ALLOW_IN_SAFE_MODE"] = "true"
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

    port = free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    created = None
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                httpx.get(f"{base}/openapi.json", timeout=2)
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        created = httpx.put(
            f"{base}/docs/{projected.id}",
            json=payload,
            headers={"X-API-Key": "audit-key"},
            timeout=60,
        )
        viewed = httpx.get(
            f"{base}/docs/{projected.id}", headers={"X-API-Key": "audit-key"}, timeout=60
        )
        deadline = time.time() + 15
        while time.time() < deadline and not EVENTS:
            time.sleep(0.5)
    finally:
        server.should_exit = True
        thread.join(timeout=20)
        sink.shutdown()

    first = EVENTS[0] if EVENTS else {}
    serialized = json.dumps(first, ensure_ascii=False)
    checks = {
        "createStatus": created.status_code if created else None,
        "viewStatus": viewed.status_code if viewed else None,
        "eventCount": len(EVENTS),
        "eventHasDoc": projected.id in serialized,
        "eventHasAction": any(key in serialized for key in ("action", "event", "operation", "type")),
        "authorizationHeader": first.get("authorization") == "Bearer sink-key",
    }
    passed = (
        checks["createStatus"] in (200, 201)
        and checks["eventCount"] >= 1
        and checks["eventHasDoc"]
        and checks["authorizationHeader"]
    )
    receipt = {
        "schema": "tai.reference.sui-audit-export/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with SUI exporting audit events over HTTP to a local sink",
        "command": "python integrations/pilot-sui-document/assembler/audit_export_check.py --sui-repo <SUI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/SUI-TEI-audit-2026-11-03.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "sampleEvent": first,
        "scope": "Enables SUI's HTTP audit export, saves one document, and checks that an event naming the document reached the sink with the configured bearer token. The sink is local and in-process.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
