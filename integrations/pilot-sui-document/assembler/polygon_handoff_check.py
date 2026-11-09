"""Check SUI's polygon handoff contract verification route."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

INPUT_HASH = "1" * 64
OUTPUT_HASH = "2" * 64
DEFAULT_ORDER = [
    "padding_compliance",
    "self_intersection_avoidance",
    "minimum_area_delta",
    "minimum_vertex_count",
]


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="sui-polygon-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "polygon-key"
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
    headers = {"X-API-Key": "polygon-key"}
    doc_id = projected.id
    base = {"input": {"gateApprovalRef": "gate-1", "a2VerifyRef": "a2-1", "inputHash": INPUT_HASH}}

    def body(expected, order=None):
        contract = {"outputPolygonHash": OUTPUT_HASH, "paddingViolationCount": expected}
        if order is not None:
            contract["tieBreakOrder"] = order
        return {**base, "expectedOutput": contract}

    with TestClient(app) as client:
        created = client.put(f"/docs/{doc_id}", json=payload, headers=headers)
        ok = client.post(f"/docs/{doc_id}/polygon-handoff/verify-contract", json=body(0), headers=headers)
        padded = client.post(f"/docs/{doc_id}/polygon-handoff/verify-contract", json=body(2), headers=headers)
        reordered = client.post(
            f"/docs/{doc_id}/polygon-handoff/verify-contract",
            json=body(0, list(reversed(DEFAULT_ORDER))),
            headers=headers,
        )
        explicit = client.post(
            f"/docs/{doc_id}/polygon-handoff/verify-contract", json=body(0, DEFAULT_ORDER), headers=headers
        )
        missing_doc = client.post(
            "/docs/doc-absent/polygon-handoff/verify-contract", json=body(0), headers=headers
        )
        bad_hash = client.post(
            f"/docs/{doc_id}/polygon-handoff/verify-contract",
            json={"input": {**base["input"], "inputHash": "nothex"}, "expectedOutput": body(0)["expectedOutput"]},
            headers=headers,
        )

    def payload_of(response):
        return response.json() if response.status_code == 200 else {}

    checks = {
        "createStatus": created.status_code,
        "okStatus": ok.status_code,
        "okDecision": payload_of(ok).get("status"),
        "okRollback": payload_of(ok).get("rollbackRequired"),
        "okVerificationKeyLength": len(payload_of(ok).get("verificationKey") or ""),
        "paddingStatus": padded.status_code,
        "paddingDecision": payload_of(padded).get("status"),
        "paddingReasons": payload_of(padded).get("failureReasons"),
        "reorderedStatus": reordered.status_code,
        "reorderedReasons": payload_of(reordered).get("failureReasons"),
        "explicitOrderStatus": explicit.status_code,
        "explicitOrderDecision": payload_of(explicit).get("status"),
        "missingDocStatus": missing_doc.status_code,
        "badHashStatus": bad_hash.status_code,
    }
    passed = (
        checks["createStatus"] == 200
        and checks["okStatus"] == 200
        and checks["okDecision"] == "ok"
        and checks["okRollback"] is False
        and checks["okVerificationKeyLength"] == 64
        and checks["paddingStatus"] == 200
        and checks["paddingDecision"] == "rollback_required"
        and checks["paddingReasons"] == ["paddingViolationCount>0"]
        and checks["reorderedStatus"] == 200
        and checks["reorderedReasons"] == ["tieBreakOrderChanged=true"]
        and checks["explicitOrderStatus"] == 200
        and checks["explicitOrderDecision"] == "ok"
        and checks["missingDocStatus"] == 404
        and checks["badHashStatus"] == 422
    )
    receipt = {
        "schema": "tai.reference.sui-polygon-handoff-verify/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/polygon_handoff_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-polygon-handoff-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Verifies the polygon handoff contract with a clean case, a padding violation, a reordered tie-break, an explicit matching order, a missing document, and a malformed hash. It recomputes the verification key but does not run a real polygon pipeline.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
