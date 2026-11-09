"""Provision one user through SUI's admin plane and check the response and audit trail."""

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

    workdir = Path(tempfile.mkdtemp(prefix="sui-provision-", dir=os.environ.get("GOTMPDIR") or None))
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
    payload = {
        "provider": "local",
        "externalUid": "tei-user-1",
        "displayName": "TEI User",
        "roles": ["reader"],
    }
    admin = {"X-Admin-Api-Key": "admin-key"}
    created = repeat = anonymous = audit = None
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                httpx.get(f"{base}/openapi.json", timeout=2)
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        created = httpx.post(f"{base}/admin/provision/users", json=payload, headers=admin, timeout=30)
        repeat = httpx.post(f"{base}/admin/provision/users", json=payload, headers=admin, timeout=30)
        anonymous = httpx.post(f"{base}/admin/provision/users", json=payload, timeout=30)
        audit = httpx.get(f"{base}/admin/provision/audit", headers=admin, timeout=30)
    finally:
        server.should_exit = True
        thread.join(timeout=20)

    first = created.json() if created is not None and created.status_code == 201 else {}
    second = repeat.json() if repeat is not None and repeat.status_code in (200, 201) else {}
    audit_body = audit.json() if audit is not None and audit.status_code == 200 else {}
    checks = {
        "createStatus": created.status_code if created else None,
        "provisioned": first.get("provisioned") is True,
        "refs": str(first.get("reviewerRef", "")).startswith("user:")
        and str(first.get("ownerRef", "")).startswith("user:"),
        "repeatSameUser": bool(second) and second.get("userId") == first.get("userId"),
        "anonymousStatus": anonymous.status_code if anonymous else None,
        "auditEvents": len(audit_body.get("events", [])),
    }
    passed = (
        checks["createStatus"] == 201
        and checks["provisioned"]
        and checks["refs"]
        and checks["repeatSameUser"]
        and checks["anonymousStatus"] in (401, 403)
        and checks["auditEvents"] >= 1
    )
    receipt = {
        "schema": "tai.reference.sui-provision/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with SUI in local-dev profile and an admin key",
        "command": "python integrations/pilot-sui-document/assembler/provision_user_check.py --sui-repo <SUI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/SUI-TEI-provision-2026-11-03.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Provisions one synthetic user through the admin API, repeats the call, refuses anonymous callers and reads the admin audit trail. It does not connect an identity provider.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
