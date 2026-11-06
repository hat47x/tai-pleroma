"""Scale check: save a synthetic projection with many cards.

This is a synthetic fixture, not the pilot projection. It is labeled synthetic
in the receipt and does not count as real-execution evidence of the pilot.
"""

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
    parser.add_argument("--cards", type=int, default=300)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    tmp = tempfile.mkdtemp(prefix="sui-large-")
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{Path(tmp) / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "large-test-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from fastapi.testclient import TestClient

    from sui_sensemaking_api.db import engine
    from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload
    from sui_sensemaking_api.main import app
    from sui_sensemaking_api.models import Base

    Base.metadata.create_all(engine)
    artifact = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    document = artifact["document"]
    original = list(document["cards"])
    for index in range(len(original) + 1, args.cards + 1):
        original.append(
            {
                "id": f"gen-card-{index}",
                "text": f"synthetic card {index}",
                "x": float(index % 20),
                "y": float(index // 20),
            }
        )
    document["cards"] = original
    projected = from_artifact(artifact)
    payload = to_documentv1_payload(
        projected,
        transform={"panX": 0.0, "panY": 0.0, "zoom": 1.0},
        created_at="2026-11-03T00:00:00Z",
        updated_at="2026-11-03T00:00:00Z",
    )
    headers = {"X-API-Key": "large-test-key"}
    with TestClient(app) as client:
        created = client.put(f"/docs/{projected.id}", json=payload, headers=headers)
        fetched = client.get(f"/docs/{projected.id}", headers=headers)
        doc_id = "large-doc"
        payload["id"] = doc_id
        large = client.put(f"/docs/{doc_id}", json=payload, headers=headers)
        large_read = client.get(f"/docs/{doc_id}", headers=headers)

    saved = large_read.json() if large_read.status_code == 200 else {}
    receipt = {
        "schema": "tai.reference.tei-sui-large-doc/v0",
        "synthetic": True,
        "evidenceKind": "synthetic-test",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/large_save.py --sui-repo {args.sui_repo} --artifact {args.artifact} --cards {args.cards}",
        "result": "PASS",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": {
            "requestedCards": args.cards,
            "putStatus": large.status_code,
            "readStatus": large_read.status_code,
            "savedCards": len(saved.get("cards", [])),
            "payloadBytes": len(json.dumps(payload).encode("utf-8")),
            "syntheticCardsAdded": args.cards - len(json.loads(Path(args.artifact).read_text(encoding='utf-8'))["document"]["cards"]),
        },
        "scope": "The cards beyond the pilot projection are synthetic and labeled. This checks the save path at a larger card count; it is not pilot evidence and does not prove production limits.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(receipt["observed"]))


if __name__ == "__main__":
    main()
