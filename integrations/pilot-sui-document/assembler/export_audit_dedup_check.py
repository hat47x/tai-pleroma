"""Check SUI's export-audit dedup: a repeated exportId is suppressed, distinct ones are kept."""

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
        EVENTS.append(body)
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


def export_kinds(events):
    found = []
    for event in events:
        metadata = event.get("metadata") or {}
        if metadata.get("route", "").endswith("/export-audit"):
            found.append(metadata.get("exportKind"))
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="sui-exportdedup-", dir=os.environ.get("GOTMPDIR") or None))
    sink = ThreadingHTTPServer(("127.0.0.1", 0), Sink)
    threading.Thread(target=sink.serve_forever, daemon=True).start()

    os.environ["SUI_DATABASE_URL"] = f"sqlite+pysqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "export-dedup-key"
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
    headers = {"X-API-Key": "export-dedup-key"}
    created = None
    first_export = repeat_export = third_export = no_id_export = None
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                httpx.get(f"{base}/openapi.json", timeout=2)
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        created = httpx.put(f"{base}/docs/{projected.id}", json=payload, headers=headers, timeout=60)
        first_export = httpx.post(
            f"{base}/docs/{projected.id}/export-audit",
            json={"safeMode": False, "exportKind": "bundle", "exportId": "export-alpha"},
            headers=headers,
            timeout=30,
        )
        repeat_export = httpx.post(
            f"{base}/docs/{projected.id}/export-audit",
            json={"safeMode": False, "exportKind": "bundle", "exportId": "export-alpha"},
            headers=headers,
            timeout=30,
        )
        third_export = httpx.post(
            f"{base}/docs/{projected.id}/export-audit",
            json={"safeMode": False, "exportKind": "bundle", "exportId": "export-beta"},
            headers=headers,
            timeout=30,
        )
        no_id_export = httpx.post(
            f"{base}/docs/{projected.id}/export-audit",
            json={"safeMode": False, "exportKind": "markdown"},
            headers=headers,
            timeout=30,
        )
        deadline = time.time() + 15
        while time.time() < deadline and len(export_kinds(EVENTS)) < 3:
            time.sleep(0.5)
    finally:
        server.should_exit = True
        thread.join(timeout=20)
        sink.shutdown()

    ids = export_kinds(EVENTS)
    checks = {
        "createStatus": created.status_code if created else None,
        "firstExportStatus": first_export.status_code if first_export else None,
        "repeatExportStatus": repeat_export.status_code if repeat_export else None,
        "thirdExportStatus": third_export.status_code if third_export else None,
        "noIdExportStatus": no_id_export.status_code if no_id_export else None,
        "deliveredExportKinds": ids,
        "eventCounts": {kind: ids.count(kind) for kind in set(ids)},
        "deliveredCount": len(ids),
        "repeatSuppressed": ids.count("bundle") == 2,
        "distinctKept": ids.count("bundle") == 2,
        "noIdDelivered": ids.count("markdown") == 1,
    }
    passed = (
        checks["createStatus"] == 200
        and checks["firstExportStatus"] == 200
        and checks["repeatExportStatus"] == 200
        and checks["thirdExportStatus"] == 200
        and checks["noIdExportStatus"] == 200
        and checks["repeatSuppressed"]
        and checks["noIdDelivered"]
    )
    receipt = {
        "schema": "tai.reference.sui-export-audit-dedup/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with SUI exporting audit events over HTTP to a local sink",
        "command": f"python integrations/pilot-sui-document/assembler/export_audit_dedup_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-export-dedup-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Records the same exportId twice, then a different exportId, then one export without an exportId, and checks what reached the sink. It does not test the dedup window boundary or a restart.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
