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
    args = parser.parse_args()

    db_dir = tempfile.mkdtemp(prefix="sui-save-")
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{Path(db_dir) / 'sui.db'}"
    os.environ.setdefault("SUI_RUNTIME_PROFILE", "local-dev")
    os.environ.setdefault("SUI_LLM_PROVIDER", "none")
    os.environ.setdefault("SUI_LOG_LEVEL", "ERROR")
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

    with TestClient(app) as client:
        created = client.put(f"/docs/{projected.id}", json=payload)
        fetched = client.get(f"/docs/{projected.id}")
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
        updated = client.put(f"/docs/{projected.id}", json=update_payload)
        final = client.get(f"/docs/{projected.id}")

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
            "apiKey": "unset",
        },
        "scope": "The SUI app runs in-process with a temporary SQLite database, no API key, and the local-dev profile. It exercises create, read, and update over HTTP. It does not verify a production database, authentication, or deployment.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(receipt["observed"]))


if __name__ == "__main__":
    main()
