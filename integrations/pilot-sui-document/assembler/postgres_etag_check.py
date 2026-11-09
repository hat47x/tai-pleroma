"""Check SUI's ETag preconditions against an embedded PostgreSQL."""

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

    import pgserver

    pg = pgserver.get_server(tempfile.mkdtemp(prefix="sui-pgetag-"))
    os.environ["SUI_DATABASE_URL"] = pg.get_uri()
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "etag-key"
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
    headers = {"X-API-Key": "etag-key"}
    with TestClient(app) as client:
        created = client.put(f"/docs/{projected.id}", json=payload, headers=headers)
        etag = created.headers.get("ETag")
        stale = client.put(
            f"/docs/{projected.id}",
            json=payload,
            headers={**headers, "If-Match": '"stale"'},
        )
        wrong_payload = json.loads(json.dumps(payload))
        wrong_payload["title"] = "Changed"
        matched = client.put(
            f"/docs/{projected.id}",
            json=wrong_payload,
            headers={**headers, "If-Match": etag},
        )

    receipt = {
        "schema": "tai.reference.sui-postgres-etag/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, TestClient, and an embedded PostgreSQL 16.2",
        "command": f"python integrations/pilot-sui-document/assembler/postgres_etag_check.py --sui-repo {args.sui_repo} --artifact {args.artifact}",
        "result": "PASS" if stale.status_code == 409 and matched.status_code == 200 else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": {
            "createStatus": created.status_code,
            "etagPresent": bool(etag),
            "staleStatus": stale.status_code,
            "matchingStatus": matched.status_code,
            "database": "embedded PostgreSQL 16.2",
            "runtimeProfile": "local-dev",
        },
        "scope": "Checks conditional PUT semantics against a real PostgreSQL. It does not verify concurrent writers, a managed database, or deployment.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pg.cleanup()
    print(json.dumps(receipt["observed"]))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
