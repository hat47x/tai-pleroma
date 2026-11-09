"""Check SUI's model registry admin endpoints."""

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

    workdir = Path(tempfile.mkdtemp(prefix="sui-registry-", dir=os.environ.get("GOTMPDIR") or None))
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
    listing = created = anonymous = unsupported = None
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                httpx.get(f"{base}/openapi.json", timeout=2)
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        listing = httpx.get(f"{base}/admin/provision/models", headers=admin, timeout=30)
        created = httpx.post(
            f"{base}/admin/provision/models/providers",
            json={"id": "prov-1", "providerKind": "local", "displayName": "Local provider"},
            headers=admin,
            timeout=30,
        )
        anonymous = httpx.get(f"{base}/admin/provision/models", timeout=30)
        unsupported = httpx.post(
            f"{base}/admin/provision/models/providers",
            json={"id": "prov-2", "providerKind": "not-supported", "displayName": "Bad provider"},
            headers=admin,
            timeout=30,
        )
    finally:
        server.should_exit = True
        thread.join(timeout=20)

    listed = listing.json() if listing is not None and listing.status_code == 200 else {}
    checks = {
        "listStatus": listing.status_code if listing else None,
        "listShape": isinstance(listed.get("providers"), list) and isinstance(listed.get("models"), list),
        "createStatus": created.status_code if created else None,
        "anonymousStatus": anonymous.status_code if anonymous else None,
        "unsupportedStatus": unsupported.status_code if unsupported else None,
    }
    passed = (
        checks["listStatus"] == 200
        and checks["listShape"]
        and checks["createStatus"] == 201
        and checks["anonymousStatus"] in (401, 403)
        and checks["unsupportedStatus"] in (400, 422)
    )
    receipt = {
        "schema": "tai.reference.sui-model-registry/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with SUI in local-dev profile and an admin key",
        "command": "python integrations/pilot-sui-document/assembler/model_registry_check.py --sui-repo <SUI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/SUI-TEI-registry-2026-11-03.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Reads the model registry, registers one provider, refuses an anonymous read and an unsupported provider kind. It does not call a model.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
