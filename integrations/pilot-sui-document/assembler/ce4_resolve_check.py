"""Check SUI's CE4 bundle resolve endpoints."""

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

    workdir = Path(tempfile.mkdtemp(prefix="sui-ce4-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite+pysqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "ce4-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
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
    headers = {"X-API-Key": "ce4-key"}
    request = {
        "query": "summarize current state",
        "dryRun": True,
        "sourceBundleHash": "sha256:" + "a" * 64,
        "safeMode": True,
    }
    dry = apply = bad_hash = unknown = None
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                httpx.get(f"{base}/openapi.json", timeout=2)
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        dry = httpx.post(f"{base}/context/bundles:resolve", json=request, headers=headers, timeout=30)
        apply = httpx.post(f"{base}/context/bundles:resolve", json={**request, "dryRun": False}, headers=headers, timeout=30)
        bad_hash = httpx.post(f"{base}/context/bundles:resolve", json={**request, "sourceBundleHash": "not-a-hash"}, headers=headers, timeout=30)
        unknown = httpx.post(f"{base}/context/bundles:resolve", json={**request, "unknownKey": 1}, headers=headers, timeout=30)
    finally:
        server.should_exit = True
        thread.join(timeout=20)

    dry_body = dry.json() if dry is not None and dry.status_code == 200 else {}
    checks = {
        "dryStatus": dry.status_code if dry else None,
        "dryBodyKeys": sorted(dry_body.keys()) if dry_body else [],
        "hasBundleHash": bool(dry_body.get("bundleHash")),
        "hasEquivalenceKey": bool(dry_body.get("equivalenceKey")),
        "applyStatus": apply.status_code if apply else None,
        "applyStatusOk": bool(apply is not None and apply.status_code == 200),
        "badHashStatus": bad_hash.status_code if bad_hash else None,
        "unknownKeyStatus": unknown.status_code if unknown else None,
    }
    passed = (
        checks["dryStatus"] == 200
        and bool(checks["dryBodyKeys"])
        and checks["hasBundleHash"]
        and checks["hasEquivalenceKey"]
        and checks["applyStatus"] == 200
        and checks["badHashStatus"] in (400, 422)
        and checks["unknownKeyStatus"] == 400
    )
    receipt = {
        "schema": "tai.reference.sui-ce4-resolve/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with SUI in local-dev profile",
        "command": "python integrations/pilot-sui-document/assembler/ce4_resolve_check.py --sui-repo <SUI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/SUI-TEI-ce4-2026-11-03.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Calls SUI's CE4 bundle resolve endpoint in dry-run and apply modes, with a malformed source hash and with an unknown key. It does not connect a real context provider.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
