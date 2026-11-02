"""Save a projection artifact into SUI through its HTTP API on a temporary SQLite DB."""

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
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()

    db_dir = tempfile.mkdtemp(prefix="sui-save-")
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{Path(db_dir) / 'sui.db'}"
    os.environ.setdefault("SUI_RUNTIME_PROFILE", "local-dev")
    os.environ.setdefault("SUI_LLM_PROVIDER", "none")
    os.environ.setdefault("SUI_LOG_LEVEL", "ERROR")
    if args.api_key:
        os.environ["SUI_API_KEY"] = args.api_key
    else:
        os.environ.pop("SUI_API_KEY", None)
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from fastapi.testclient import TestClient

    from sui_sensemaking_api.db import engine
    from sui_sensemaking_api.documentv1_merge import (
        merge_preserving_existing,
        validate_existing_document,
    )
    from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload
    from sui_sensemaking_api.main import app
    from sui_sensemaking_api.models import Base

    Base.metadata.create_all(engine)
    artifact = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    projected = from_artifact(artifact)
    payload = to_documentv1_payload(
        projected,
        transform={"panX": 0.0, "panY": 0.0, "zoom": 1.0},
        created_at="2026-11-03T00:00:00Z",
        updated_at="2026-11-03T00:00:00Z",
    )

    headers = {"X-API-Key": args.api_key} if args.api_key else {}
    with TestClient(app) as client:
        unauthorized = (
            client.put(f"/docs/{projected.id}", json=payload) if args.api_key else None
        )
        created = client.put(f"/docs/{projected.id}", json=payload, headers=headers)
        fetched = client.get(f"/docs/{projected.id}", headers=headers)
        existing = fetched.json() if fetched.status_code == 200 else None
        if existing is not None:
            validate_existing_document(existing)
            update_payload = merge_preserving_existing(
                projected,
                transform={"panX": 0.0, "panY": 0.0, "zoom": 1.0},
                created_at="2026-11-03T00:00:00Z",
                updated_at="2026-11-03T00:00:00Z",
                existing=existing,
            )
        else:
            update_payload = payload
        updated = client.put(f"/docs/{projected.id}", json=update_payload, headers=headers)
        final = client.get(f"/docs/{projected.id}", headers=headers)

    saved = final.json() if final.status_code == 200 else {}
    projected_cards = {card["id"]: card for card in payload["cards"]}
    saved_cards = {card.get("id"): card for card in saved.get("cards", [])}
    projected_islands = {island["id"]: island for island in payload["islands"]}
    saved_islands = {island.get("id"): island for island in saved.get("islands", [])}
    projected_edges = {edge["id"]: edge for edge in payload["edges"]}
    saved_edges = {edge.get("id"): edge for edge in saved.get("edges", [])}
    checks = {
        "cardIds": set(projected_cards) == set(saved_cards),
        "cardText": all(
            saved_cards[cid].get("text") == card.get("text")
            for cid, card in projected_cards.items()
            if cid in saved_cards
        ),
        "cardPosition": all(
            (saved_cards[cid].get("x"), saved_cards[cid].get("y")) == (card.get("x"), card.get("y"))
            for cid, card in projected_cards.items()
            if cid in saved_cards
        ),
        "islandIds": set(projected_islands) == set(saved_islands),
        "islandCardIds": all(
            saved_islands[iid].get("cardIds") == island.get("cardIds")
            for iid, island in projected_islands.items()
            if iid in saved_islands
        ),
        "edgeIds": set(projected_edges) == set(saved_edges),
    }

    receipt = {
        "schema": "tai.reference.tei-sui-save/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/save_to_sui.py --sui-repo {args.sui_repo} --artifact {args.artifact}",
        "result": "PASS",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": {
            "createStatus": created.status_code,
            "createReadStatus": fetched.status_code,
            "updateStatus": updated.status_code,
            "finalReadStatus": final.status_code,
            "documentId": projected.id,
            "cards": len(payload["cards"]),
            "writes": True,
            "database": "temporary SQLite",
            "runtimeProfile": "local-dev",
            "apiKey": "configured" if args.api_key else "unset",
            "unauthorizedStatus": unauthorized.status_code if unauthorized is not None else None,
            "roundTrip": all(checks.values()),
            "roundTripChecks": checks,
        },
        "scope": "The SUI app runs in-process with a temporary SQLite database, no API key, and the local-dev profile. It exercises create, read, and update over HTTP. It does not verify a production database, authentication, or deployment.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(receipt["observed"]))


if __name__ == "__main__":
    main()
