"""Check SUI's similar-candidate group heuristic on the document read model."""

import argparse
import copy
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

    workdir = Path(tempfile.mkdtemp(prefix="sui-candidates-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "candidates-key"
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

    def card(card_id, text, x, **extra):
        body = {"id": card_id, "text": text, "x": x, "y": 0.0}
        body.update(extra)
        return body

    cards = [
        card("card-a", "Same  Text", 10.0),
        card("card-b", "same text", 20.0),
        card("card-c", "alpha beta", 30.0),
        card("card-d", "beta alpha", 40.0),
        card("card-e", "unrelated phrase", 50.0),
        card("card-f", "", 60.0),
        card("card-g", "same text", 70.0, mergedIntoCardId="card-b"),
        card("card-h", "same text", 80.0, sources=["src-1"]),
        card("card-i", "same text", 90.0, canonicalId="canon-1"),
    ]
    custom_doc = f"{projected.id}-candidates"
    custom = copy.deepcopy(payload)
    custom["id"] = custom_doc
    custom["cards"] = cards
    custom["edges"] = []
    custom["islands"] = []
    for key in ("affiliations", "actions", "shelves"):
        if key in custom:
            custom[key] = []

    headers = {"X-API-Key": "candidates-key"}
    with TestClient(app) as client:
        created = client.put(f"/docs/{custom_doc}", json=custom, headers=headers)
        groups = client.get(f"/docs/{custom_doc}/similar-candidate-groups", headers=headers)
        original = client.put(f"/docs/{projected.id}", json=payload, headers=headers)
        plain = client.get(f"/docs/{projected.id}/similar-candidate-groups", headers=headers)
        missing = client.get("/docs/doc-absent/similar-candidate-groups", headers=headers)

    body = groups.json() if groups.status_code == 200 else {}
    found = {
        (group.get("targetCardId"), tuple(group.get("candidateCardIds") or [])): group
        for group in body.get("groups", [])
    }
    text_group = found.get(("card-a", ("card-b",)))
    token_group = found.get(("card-c", ("card-d",)))
    checks = {
        "createStatus": created.status_code,
        "groupsStatus": groups.status_code,
        "totalGroupCount": body.get("totalGroupCount"),
        "groupCount": len(body.get("groups", [])),
        "textGroupPresent": text_group is not None,
        "textGroupReasons": text_group.get("reasonCodes") if text_group else None,
        "tokenGroupPresent": token_group is not None,
        "tokenGroupReasons": token_group.get("reasonCodes") if token_group else None,
        "mergedCardExcluded": all("card-g" not in group.get("candidateCardIds", []) and group.get("targetCardId") != "card-g" for group in body.get("groups", [])),
        "sourcedCardExcluded": all("card-h" not in group.get("candidateCardIds", []) and group.get("targetCardId") != "card-h" for group in body.get("groups", [])),
        "canonicalCardExcluded": all("card-i" not in group.get("candidateCardIds", []) and group.get("targetCardId") != "card-i" for group in body.get("groups", [])),
        "snapshotVersionLength": len((text_group or {}).get("snapshotVersion") or ""),
        "plainDocStatus": plain.status_code,
        "plainDocTotalGroups": (plain.json() or {}).get("totalGroupCount") if plain.status_code == 200 else None,
        "missingDocStatus": missing.status_code,
    }
    passed = (
        checks["createStatus"] == 200
        and checks["groupsStatus"] == 200
        and checks["textGroupPresent"]
        and checks["textGroupReasons"] == ["normalized_text", "token_signature"]
        and checks["tokenGroupPresent"]
        and checks["tokenGroupReasons"] == ["token_signature"]
        and checks["mergedCardExcluded"]
        and checks["sourcedCardExcluded"]
        and checks["canonicalCardExcluded"]
        and checks["snapshotVersionLength"] == 12
        and checks["plainDocStatus"] == 200
        and checks["missingDocStatus"] == 404
    )
    receipt = {
        "schema": "tai.reference.sui-similar-candidate-groups/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/similar_candidate_groups_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-similar-candidates-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Writes a document with normalised-equal, token-equal, unrelated, empty, merged, sourced, and canonical cards, then reads the candidate groups. It checks eligibility exclusion and reason codes, not a real similarity model. A group can carry both reason codes when the two heuristics agree.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
