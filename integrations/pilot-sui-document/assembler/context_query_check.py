"""Check SUI's context query contract endpoints."""

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

    workdir = Path(tempfile.mkdtemp(prefix="sui-context-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite+pysqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "ctx-key"
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
    headers = {"X-API-Key": "ctx-key"}
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
    accepted = preview = unknown = out_of_range = None
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                httpx.get(f"{base}/openapi.json", timeout=2)
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        accepted = httpx.post(f"{base}/context/query", json=query, headers=headers, timeout=30)
        no_preview = dict(query)
        no_preview["previewConfirmed"] = False
        preview = httpx.post(f"{base}/context/query", json=no_preview, headers=headers, timeout=30)
        unknown = httpx.post(f"{base}/context/query", json={**query, "unknownKey": 1}, headers=headers, timeout=30)
        bad = dict(query)
        bad["depth"] = 9
        out_of_range = httpx.post(f"{base}/context/query", json=bad, headers=headers, timeout=30)
    finally:
        server.should_exit = True
        thread.join(timeout=20)

    body = accepted.json() if accepted is not None and accepted.status_code == 200 else {}
    checks = {
        "acceptedStatus": accepted.status_code if accepted else None,
        "accepted": body.get("accepted") is True,
        "hashPresent": isinstance(body.get("queryCanonicalHash"), str) and len(body.get("queryCanonicalHash", "")) > 0,
        "previewStatus": preview.status_code if preview else None,
        "previewCode": (preview.json().get("detail") or {}).get("code") if preview is not None else None,
        "unknownKeyStatus": unknown.status_code if unknown else None,
        "unknownKeyCode": (unknown.json().get("detail") or {}).get("code") if unknown is not None else None,
        "outOfRangeStatus": out_of_range.status_code if out_of_range else None,
    }
    passed = (
        checks["acceptedStatus"] == 200
        and checks["accepted"]
        and checks["hashPresent"]
        and checks["previewStatus"] == 422
        and checks["previewCode"] == "preview_required"
        and checks["unknownKeyStatus"] == 400
        and checks["unknownKeyCode"] == "unknown_contract_key"
        and checks["outOfRangeStatus"] == 400
    )
    receipt = {
        "schema": "tai.reference.sui-context-contract/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with SUI in local-dev profile",
        "command": "python integrations/pilot-sui-document/assembler/context_query_check.py --sui-repo <SUI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/SUI-TEI-context-2026-11-03.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Exercises SUI's /context/query validation: an accepted query, a query without preview confirmation, an unknown key and an out-of-range depth. It does not build a bundle.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
