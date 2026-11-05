"""Check SUI's admin plane: unauthenticated refusal and an authorized audit read."""

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

    workdir = Path(tempfile.mkdtemp(prefix="sui-admin-", dir=os.environ.get("GOTMPDIR") or None))
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
    anonymous = business = admin = None
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                httpx.get(f"{base}/openapi.json", timeout=2)
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        anonymous = httpx.get(f"{base}/admin/provision/audit", timeout=30)
        business = httpx.get(
            f"{base}/admin/provision/audit", headers={"X-Api-Key": "business-key"}, timeout=30
        )
        admin = httpx.get(
            f"{base}/admin/provision/audit", headers={"X-Admin-Api-Key": "admin-key"}, timeout=30
        )
    finally:
        server.should_exit = True
        thread.join(timeout=20)

    body = admin.json() if admin is not None and admin.status_code == 200 else {}
    checks = {
        "anonymousStatus": anonymous.status_code if anonymous else None,
        "businessKeyStatus": business.status_code if business else None,
        "adminStatus": admin.status_code if admin else None,
        "adminBodyShape": isinstance(body.get("events"), list),
    }
    passed = (
        checks["anonymousStatus"] in (401, 403)
        and checks["businessKeyStatus"] in (401, 403)
        and checks["adminStatus"] == 200
        and checks["adminBodyShape"]
    )
    receipt = {
        "schema": "tai.reference.sui-admin-plane/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with SUI in local-dev profile and an admin key",
        "command": "python integrations/pilot-sui-document/assembler/admin_plane_check.py --sui-repo <SUI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/SUI-TEI-admin-2026-11-03.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Checks that the admin audit read refuses anonymous and business-key callers and accepts the admin key. It does not provision users or exercise identity-provider stage B.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
