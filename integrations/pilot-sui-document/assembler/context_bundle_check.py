"""Check SUI's context bundle construction."""

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

    workdir = Path(tempfile.mkdtemp(prefix="sui-bundle-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite+pysqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "bundle-key"
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
    headers = {"X-API-Key": "bundle-key"}
    query = {
        "queryId": "q-1",
        "goal": "summarize current state",
        "scope": "document",
        "depth": 2,
        "constraints": {},
        "reviewFilter": "reviewedOnly",
        "safeModePolicy": "strict",
        "outputMode": "summary",
        "previewConfirmed": True,
    }
    body = {"query": query, "stubDatasetId": "A2-minimal-v1"}
    first = second = no_preview = None
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                httpx.get(f"{base}/openapi.json", timeout=2)
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        first = httpx.post(f"{base}/context/bundle", json=body, headers=headers, timeout=60)
        second = httpx.post(f"{base}/context/bundle", json=body, headers=headers, timeout=60)
        no_preview = httpx.post(
            f"{base}/context/bundle",
            json={"query": {**query, "previewConfirmed": False}, "stubDatasetId": "A2-minimal-v1"},
            headers=headers,
            timeout=60,
        )
    finally:
        server.should_exit = True
        thread.join(timeout=20)

    first_body = first.json() if first is not None and first.status_code == 200 else {}
    second_body = second.json() if second is not None and second.status_code == 200 else {}
    checks = {
        "firstStatus": first.status_code if first else None,
        "bundleHash": first_body.get("bundleHash"),
        "deterministic": bool(first_body.get("bundleHash")) and first_body.get("bundleHash") == second_body.get("bundleHash"),
        "hasQueryHash": isinstance(first_body.get("queryCanonicalHash"), str),
        "noPreviewStatus": no_preview.status_code if no_preview else None,
        "noPreviewCode": (no_preview.json().get("detail") or {}).get("code") if no_preview is not None else None,
    }
    passed = (
        checks["firstStatus"] == 200
        and isinstance(checks["bundleHash"], str)
        and checks["deterministic"]
        and checks["hasQueryHash"]
        and checks["noPreviewStatus"] == 422
        and checks["noPreviewCode"] == "preview_required"
    )
    receipt = {
        "schema": "tai.reference.sui-context-bundle/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with SUI in local-dev profile",
        "command": "python integrations/pilot-sui-document/assembler/context_bundle_check.py --sui-repo <SUI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/SUI-TEI-context-bundle-2026-11-03.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Builds SUI's context bundle twice from the same query with the A2-minimal-v1 stub dataset, checks the hash is stable, and checks that a query without preview confirmation is refused. The stub dataset is synthetic.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
