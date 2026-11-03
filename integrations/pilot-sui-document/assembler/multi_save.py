"""Save the projection under several document ids and verify isolation."""

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
    parser.add_argument("--documents", type=int, default=10)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    tmp = tempfile.mkdtemp(prefix="sui-multi-")
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{Path(tmp) / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "multi-test-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from fastapi.testclient import TestClient

    from sui_sensemaking_api.db import engine
    from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload
    from sui_sensemaking_api.main import app
    from sui_sensemaking_api.models import Base

    Base.metadata.create_all(engine)
    projected = from_artifact(json.loads(Path(args.artifact).read_text(encoding="utf-8")))
    base = to_documentv1_payload(
        projected,
        transform={"panX": 0.0, "panY": 0.0, "zoom": 1.0},
        created_at="2026-11-03T00:00:00Z",
        updated_at="2026-11-03T00:00:00Z",
    )
    headers = {"X-API-Key": "multi-test-key"}
    created = {}
    read_back = {}
    with TestClient(app) as client:
        for index in range(1, args.documents + 1):
            doc_id = f"doc-{index}"
            payload = dict(base, id=doc_id, title=f"Notes {index}")
            created[doc_id] = client.put(f"/docs/{doc_id}", json=payload, headers=headers).status_code
            response = client.get(f"/docs/{doc_id}", headers=headers)
            read_back[doc_id] = (response.status_code, response.json().get("id"))

    receipt = {
        "schema": "tai.reference.tei-sui-multi-doc/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/multi_save.py --sui-repo {args.sui_repo} --artifact {args.artifact} --documents {args.documents}",
        "result": "PASS",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": {
            "documents": args.documents,
            "createdAll": all(code == 200 for code in created.values()),
            "readAll": all(code == 200 and doc_id == read_id for doc_id, (code, read_id) in read_back.items()),
            "isolatedIds": len(set(read_id for _, read_id in read_back.values())) == args.documents,
            "writes": True,
            "database": "temporary SQLite",
            "runtimeProfile": "local-dev",
        },
        "scope": "The same projection is saved under several document ids. Each document keeps its own id. It does not verify production storage, concurrent writers, or large card counts.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(receipt["observed"]))


if __name__ == "__main__":
    main()
