"""Check SUI's admin audit pagination with a cursor."""

import argparse
import hashlib
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

    workdir = Path(tempfile.mkdtemp(prefix="sui-audit-page-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite+pysqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "business-key"
    os.environ["SUI_ADMIN_API_KEY"] = "admin-key"
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    import httpx
    import uvicorn
    from sqlalchemy import text

    from sui_sensemaking_api.db import engine
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

    port = free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    admin = {"X-Admin-Api-Key": "admin-key"}
    first = second = None
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                httpx.get(f"{base}/openapi.json", timeout=2)
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        for index in range(3):
            httpx.post(
                f"{base}/admin/provision/users",
                json={"provider": "local", "externalUid": f"page-user-{index}", "displayName": f"User {index}"},
                headers=admin,
                timeout=30,
            )
        first = httpx.get(f"{base}/admin/provision/audit", params={"limit": 1}, headers=admin, timeout=30)
        cursor = first.json().get("nextCursor") if first.status_code == 200 else None
        if cursor:
            second = httpx.get(
                f"{base}/admin/provision/audit", params={"limit": 1, "cursor": cursor}, headers=admin, timeout=30
            )
    finally:
        server.should_exit = True
        thread.join(timeout=20)

    page1 = first.json() if first is not None and first.status_code == 200 else {}
    page2 = second.json() if second is not None and second.status_code == 200 else {}
    ids1 = [event.get("eventId") for event in page1.get("events", [])]
    ids2 = [event.get("eventId") for event in page2.get("events", [])]
    checks = {
        "firstStatus": first.status_code if first else None,
        "page1Size": len(ids1),
        "hasCursor": bool(page1.get("nextCursor")),
        "secondStatus": second.status_code if second else None,
        "page2Size": len(ids2),
        "noOverlap": bool(ids1) and bool(ids2) and not set(ids1) & set(ids2),
    }
    passed = (
        checks["firstStatus"] == 200
        and checks["page1Size"] == 1
        and checks["hasCursor"]
        and checks["secondStatus"] == 200
        and checks["page2Size"] == 1
        and checks["noOverlap"]
    )
    receipt = {
        "schema": "tai.reference.sui-admin-audit-pagination/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with SUI in local-dev profile and an admin key",
        "command": "python integrations/pilot-sui-document/assembler/admin_audit_pagination_check.py --sui-repo <SUI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/SUI-TEI-audit-pagination-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Provisions three users, then reads the admin audit trail one event at a time with the returned cursor and checks the pages do not overlap. It does not test cursor expiry or a large trail.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
