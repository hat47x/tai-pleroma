"""Check SUI's response headers: security defaults, request ids, and agent-specific cache rules."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="sui-headers-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "headers-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from fastapi.testclient import TestClient
    from sqlalchemy import text

    from sui_sensemaking_api.agent_credentials import AGENT_CREDENTIAL_HEADER
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
    headers = {"X-API-Key": "headers-key"}
    with TestClient(app) as client:
        created = client.put(f"/docs/{projected.id}", json=payload, headers=headers)
        read = client.get(f"/docs/{projected.id}", headers=headers)
        unauthorized = client.get("/docs", headers={"X-API-Key": "wrong"})
        with_trace = client.get(
            "/version", headers={"x-trace-id": "caller-supplied-id"}
        )
        unsafe_trace = client.get("/version", headers={"x-trace-id": "bad id with spaces/and/slashes"})
        agent_shaped = client.get(
            f"/docs/{projected.id}",
            headers={AGENT_CREDENTIAL_HEADER: "suiag_offered", **headers},
        )

    def header_block(response):
        return {
            "nosniff": response.headers.get("x-content-type-options"),
            "frameOptions": response.headers.get("x-frame-options"),
            "cacheControl": response.headers.get("cache-control"),
            "vary": response.headers.get("vary"),
            "requestId": response.headers.get("x-request-id"),
        }

    checks = {
        "createStatus": created.status_code,
        "readHeaders": header_block(read),
        "unauthorizedHeaders": header_block(unauthorized),
        "unauthorizedBodyHasRequestId": "requestId" in (unauthorized.json() or {}),
        "traceEchoed": with_trace.headers.get("x-request-id"),
        "unsafeTraceReplaced": unsafe_trace.headers.get("x-request-id"),
        "agentHeaders": header_block(agent_shaped),
        "agentStatus": agent_shaped.status_code,
    }
    passed = (
        checks["createStatus"] == 200
        and checks["readHeaders"]["nosniff"] == "nosniff"
        and checks["readHeaders"]["frameOptions"] == "DENY"
        and checks["unauthorizedHeaders"]["nosniff"] == "nosniff"
        and checks["unauthorizedHeaders"]["frameOptions"] == "DENY"
        and checks["unauthorizedBodyHasRequestId"] is True
        and checks["readHeaders"]["requestId"]
        and checks["traceEchoed"] == "caller-supplied-id"
        and checks["unsafeTraceReplaced"] not in (None, "bad id with spaces/and/slashes")
        and checks["agentHeaders"]["cacheControl"] == "private, no-store"
        and "Sui-Sensemaking-Agent-Credential" in (checks["agentHeaders"]["vary"] or "")
    )
    receipt = {
        "schema": "tai.reference.sui-response-headers/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/response_headers_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-headers-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Reads the security headers on success and 401 responses, checks that an inbound x-trace-id is echoed or replaced when unsafe, and checks the agent-specific cache headers. It does not test a reverse proxy or the browser CSRF guard.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
