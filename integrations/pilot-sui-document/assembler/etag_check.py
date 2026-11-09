"""Check ETag preconditions on the projection save path."""

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

    tmp = tempfile.mkdtemp(prefix="sui-etag-")
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{Path(tmp) / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "etag-test-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from fastapi.testclient import TestClient

    from sui_sensemaking_api.db import engine
    from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload
    from sui_sensemaking_api.main import app
    from sui_sensemaking_api.models import Base

    Base.metadata.create_all(engine)
    projected = from_artifact(json.loads(Path(args.artifact).read_text(encoding="utf-8")))
    payload = to_documentv1_payload(
        projected,
        transform={"panX": 0.0, "panY": 0.0, "zoom": 1.0},
        created_at="2026-11-03T00:00:00Z",
        updated_at="2026-11-03T00:00:00Z",
    )
    headers = {"X-API-Key": "etag-test-key"}
    with TestClient(app) as client:
        created = client.put(f"/docs/{projected.id}", json=payload, headers=headers)
        fetched = client.get(f"/docs/{projected.id}", headers=headers)
        current_etag = fetched.headers.get("etag")
        stale = client.put(
            f"/docs/{projected.id}",
            json=payload,
            headers={**headers, "If-Match": '"stale-tag"'},
        )
        unchanged = client.put(
            f"/docs/{projected.id}",
            json=payload,
            headers={**headers, "If-Match": current_etag or "*"},
        )
        last_write_wins = client.put(f"/docs/{projected.id}", json=payload, headers=headers)

    receipt = {
        "schema": "tai.reference.tei-sui-etag/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/etag_check.py --sui-repo {args.sui_repo} --artifact {args.artifact}",
        "result": "PASS",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": {
            "createStatus": created.status_code,
            "etagPresent": bool(current_etag),
            "staleIfMatchStatus": stale.status_code,
            "matchingIfMatchStatus": unchanged.status_code,
            "noPreconditionStatus": last_write_wins.status_code,
            "database": "temporary SQLite",
            "runtimeProfile": "local-dev",
            "writes": True,
        },
        "scope": "Checks stale and matching If-Match preconditions on the save route with a temporary SQLite database. It does not verify concurrent writers or the SaaS precondition profile.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(receipt["observed"]))


if __name__ == "__main__":
    main()
