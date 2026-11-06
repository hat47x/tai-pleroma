"""Record where SUI wires the agent credential hash key, and what local-dev does without it."""

import argparse
import ast
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def wiring_scope(main_py):
    """Report the runtime-profile conditions that guard the module-level state wiring."""
    tree = ast.parse(main_py.read_text(encoding="utf-8"))
    found = []
    for node in tree.body:
        if not isinstance(node, ast.If):
            continue
        test = ast.unparse(node.test)
        names = {
            target.attr
            for child in ast.walk(node)
            if isinstance(child, ast.Assign)
            for target in child.targets
            if isinstance(target, ast.Attribute)
        }
        if "agent_credential_hash_key" in names or "agent_oauth_audience" in names:
            found.append({"condition": test, "wiredState": sorted(names)})
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    main_py = Path(args.sui_repo) / "03_Implement/backend/src/sui_sensemaking_api/main.py"
    scopes = wiring_scope(main_py)
    guards = [scope["condition"] for scope in scopes]

    workdir = Path(tempfile.mkdtemp(prefix="sui-agentwiring-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "wiring-key"
    os.environ["SUI_AGENT_CREDENTIAL_HASH_KEY"] = "0" * 64
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
    with TestClient(app) as client:
        created = client.put(
            f"/docs/{projected.id}", json=payload, headers={"X-API-Key": "wiring-key"}
        )
        offered = client.get(
            f"/docs/{projected.id}",
            headers={AGENT_CREDENTIAL_HEADER: "suiag_offeredtoken", "X-API-Key": "wiring-key"},
        )

    state_key_present = getattr(app.state, "agent_credential_hash_key", None) is not None
    detail = offered.json().get("detail") if offered.status_code >= 400 else None
    code = detail.get("code") if isinstance(detail, dict) else None
    checks = {
        "wiringGuards": guards,
        "wiredState": sorted({name for scope in scopes for name in scope["wiredState"]}),
        "wiringConditionalOnSaas": any("saas-multitenant" in guard for guard in guards),
        "localDevStateKeyPresent": state_key_present,
        "createStatus": created.status_code,
        "agentRequestStatus": offered.status_code,
        "agentRequestCode": code,
    }
    passed = (
        checks["wiringConditionalOnSaas"] is True
        and checks["localDevStateKeyPresent"] is False
        and checks["createStatus"] == 200
        and checks["agentRequestStatus"] == 503
        and checks["agentRequestCode"] == "agent_credential_unavailable"
    )
    receipt = {
        "schema": "tai.reference.sui-agent-key-wiring/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/agent_key_wiring_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-agent-key-wiring-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Reads main.py's module-level assignments with AST to find the guarding runtime-profile condition, then boots local-dev with SUI_AGENT_CREDENTIAL_HASH_KEY set and confirms the agent path answers 503. It does not boot saas-multitenant.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
