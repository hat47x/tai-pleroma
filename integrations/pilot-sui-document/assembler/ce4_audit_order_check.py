"""Check SUI's CE4 audit event ordering rules on the document context-audit route."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="sui-ce4-order-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "ce4-order-key"
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
    headers = {"X-API-Key": "ce4-order-key"}
    doc_id = projected.id

    def event(operation, command, *, source_bundle_hash=None, bundle_hash=HASH_B, key=HASH_A, **extra):
        body = {
            "operation": operation,
            "safeMode": True,
            "equivalenceKey": key,
            "bundleHash": bundle_hash,
            "command": command,
            "channel": "api",
            "dryRun": True,
            "sideEffect": "none",
        }
        if source_bundle_hash is not None:
            body["sourceBundleHash"] = source_bundle_hash
        body.update(extra)
        return body

    with TestClient(app) as client:
        created = client.put(f"/docs/{doc_id}", json=payload, headers=headers)
        apply_first = client.post(
            f"/docs/{doc_id}/context-audit",
            json=event("apply", "apply --dry-run", source_bundle_hash=HASH_C),
            headers=headers,
        )
        query = client.post(
            f"/docs/{doc_id}/context-audit", json=event("query", "context-query"), headers=headers
        )
        bundle = client.post(
            f"/docs/{doc_id}/context-audit", json=event("bundle", "context-bundle"), headers=headers
        )
        proposal = client.post(
            f"/docs/{doc_id}/context-audit",
            json=event("proposal", "proposal-diff", source_bundle_hash=HASH_C),
            headers=headers,
        )
        apply_after = client.post(
            f"/docs/{doc_id}/context-audit",
            json=event("apply", "apply --dry-run", source_bundle_hash=HASH_C),
            headers=headers,
        )
        mismatch = client.post(
            f"/docs/{doc_id}/context-audit",
            json=event(
                "apply", "apply --dry-run", source_bundle_hash=HASH_A, key=HASH_A, bundle_hash=HASH_B
            ),
            headers=headers,
        )
        bad_command = client.post(
            f"/docs/{doc_id}/context-audit",
            json=event("query", "apply --dry-run"),
            headers=headers,
        )

    def code_of(response):
        if response is None or response.status_code < 400:
            return None
        detail = response.json().get("detail")
        return detail.get("code") if isinstance(detail, dict) else detail

    checks = {
        "createStatus": created.status_code,
        "applyBeforeAnyEventStatus": apply_first.status_code,
        "applyBeforeAnyEventCode": code_of(apply_first),
        "applyBeforeAnyEventMissing": (apply_first.json().get("detail") or {}).get("missingEvents")
        if apply_first.status_code == 409
        else None,
        "queryStatus": query.status_code,
        "bundleStatus": bundle.status_code,
        "proposalStatus": proposal.status_code,
        "applyAfterFullSetStatus": apply_after.status_code,
        "sourceBundleMismatchStatus": mismatch.status_code,
        "sourceBundleMismatchCode": code_of(mismatch),
        "operationCommandMismatchStatus": bad_command.status_code,
        "operationCommandMismatchCode": code_of(bad_command),
    }
    passed = (
        checks["createStatus"] == 200
        and checks["applyBeforeAnyEventStatus"] == 409
        and checks["queryStatus"] == 200
        and checks["bundleStatus"] == 200
        and checks["proposalStatus"] == 200
        and checks["applyAfterFullSetStatus"] == 200
        and checks["sourceBundleMismatchStatus"] == 409
        and checks["operationCommandMismatchStatus"] == 422
    )
    receipt = {
        "schema": "tai.reference.sui-ce4-audit-order/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/ce4_audit_order_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-ce4-audit-order-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Records a CE4 apply before any other event, then query/bundle/proposal, then apply again, then a mismatched source bundle and a mismatched command. It does not test the tracker expiry window or a second tenant.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
