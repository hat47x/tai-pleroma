"""Save several projection documents into SUI on PostgreSQL and read them back."""

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
    parser.add_argument("--documents", type=int, default=10)
    args = parser.parse_args()

    import pgserver
    import psycopg

    pg = pgserver.get_server(tempfile.mkdtemp(prefix="sui-pgmulti-"))
    uri = pg.get_uri()
    os.environ["SUI_DATABASE_URL"] = uri
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "multi-key"
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
    base = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    headers = {"X-API-Key": "multi-key"}
    created = []
    read = []
    with TestClient(app) as client:
        for index in range(args.documents):
            document = copy.deepcopy(base)
            document["document"]["document"]["id"] = f"doc-{index + 1}"
            document["document"]["document"]["title"] = f"Document {index + 1}"
            projected = from_artifact(document)
            payload = to_documentv1_payload(
                projected,
                transform={"panX": 0.0, "panY": 0.0, "zoom": 1.0},
                created_at="2026-11-03T00:00:00Z",
                updated_at="2026-11-03T00:00:00Z",
            )
            response = client.put(f"/docs/{projected.id}", json=payload, headers=headers)
            created.append(response.status_code)
            fetched = client.get(f"/docs/{projected.id}", headers=headers)
            read.append(
                {
                    "id": projected.id,
                    "status": fetched.status_code,
                    "title": fetched.json().get("title") if fetched.status_code == 200 else None,
                }
            )

    with psycopg.connect(uri) as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) from documents")
            document_rows = cur.fetchone()[0]

    all_created = all(status == 200 for status in created)
    all_read = all(item["status"] == 200 for item in read)
    titles_match = all(item["title"] == f"Document {index + 1}" for index, item in enumerate(read))
    receipt = {
        "schema": "tai.reference.sui-postgres-multidoc/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, TestClient, and an embedded PostgreSQL 16.2",
        "command": f"python integrations/pilot-sui-document/assembler/postgres_multi_save.py --sui-repo {args.sui_repo} --artifact {args.artifact}",
        "result": "PASS" if all_created and all_read and titles_match and document_rows == args.documents else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": {
            "documents": args.documents,
            "createStatuses": created,
            "reads": read,
            "documentRows": document_rows,
            "titlesMatch": titles_match,
            "database": "embedded PostgreSQL 16.2",
        },
        "scope": "Saves several documents with distinct ids into a real PostgreSQL and reads them back. It does not verify tenancy isolation, access control, or deployment.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pg.cleanup()
    print(json.dumps({"created": all_created, "read": all_read, "rows": document_rows, "titlesMatch": titles_match}))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
