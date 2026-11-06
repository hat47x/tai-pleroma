"""Check SUI's merge decision log append-only semantics."""

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

    workdir = Path(tempfile.mkdtemp(prefix="sui-merge-log-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "merge-log-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from fastapi.testclient import TestClient
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
    headers = {"X-API-Key": "merge-log-key"}
    doc_id = projected.id
    record = {
        "decisionId": "decision-1",
        "groupId": "group-1",
        "action": "accept",
        "selectedCardIds": [payload["cards"][0]["id"]] if payload.get("cards") else [],
        "note": "accepted for the pilot",
        "decidedBy": "local-user",
        "decidedAt": "2026-11-03T00:00:00Z",
        "snapshotVersion": "snap-1",
    }
    with TestClient(app) as client:
        created = client.put(f"/docs/{doc_id}", json=payload, headers=headers)
        appended = client.post(f"/docs/{doc_id}/merge-decision-logs", json={"record": record}, headers=headers)
        duplicate = client.post(f"/docs/{doc_id}/merge-decision-logs", json={"record": record}, headers=headers)
        listed = client.get(f"/docs/{doc_id}/merge-decision-logs/by-group/group-1", headers=headers)
        missing = client.get(
            f"/docs/{doc_id}/merge-decision-logs/by-group/group-absent", headers=headers
        )

    checks = {
        "createStatus": created.status_code,
        "appendStatus": appended.status_code,
        "duplicateStatus": duplicate.status_code,
        "listStatus": listed.status_code,
        "listCount": len(listed.json()) if listed.status_code == 200 else None,
        "listedDecisionId": listed.json()[0].get("decisionId")
        if listed.status_code == 200 and listed.json()
        else None,
        "absentGroupStatus": missing.status_code,
        "absentGroupCount": len(missing.json()) if missing.status_code == 200 else None,
    }
    passed = (
        checks["createStatus"] == 200
        and checks["appendStatus"] == 201
        and checks["duplicateStatus"] == 409
        and checks["listStatus"] == 200
        and checks["listCount"] == 1
        and checks["listedDecisionId"] == "decision-1"
        and checks["absentGroupStatus"] == 200
        and checks["absentGroupCount"] == 0
    )
    receipt = {
        "schema": "tai.reference.sui-merge-decision-log/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/merge_decision_log_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-merge-decision-log-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Appends one merge decision, replays the same decision, lists the group, and lists a group with no decisions. It does not test concurrent appends or authorisation of other tenants.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
