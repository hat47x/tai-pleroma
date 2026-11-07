"""Check SUI's archive lifecycle gate on document writes."""

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

    workdir = Path(tempfile.mkdtemp(prefix="sui-archive-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "archive-test-key"
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
    headers = {"X-API-Key": "archive-test-key"}
    doc_id = projected.id
    with TestClient(app) as client:
        created = client.put(f"/docs/{doc_id}", json=payload, headers=headers)
        archived = client.post(f"/docs/{doc_id}/archive", headers=headers)
        read_archived = client.get(f"/docs/{doc_id}", headers=headers)
        write_archived = client.put(
            f"/docs/{doc_id}", json=payload, headers={**headers, "If-Match": read_archived.headers.get("etag") or "*"}
        )
        unarchived = client.post(f"/docs/{doc_id}/unarchive", headers=headers)
        write_after = client.put(
            f"/docs/{doc_id}", json=payload, headers={**headers, "If-Match": read_archived.headers.get("etag") or "*"}
        )

    checks = {
        "createStatus": created.status_code,
        "archiveStatus": archived.status_code,
        "readArchivedStatus": read_archived.status_code,
        "writeArchivedStatus": write_archived.status_code,
        "writeArchivedCode": (write_archived.json().get("detail", {}) or {}).get("code")
        if write_archived.status_code >= 400
        else None,
        "unarchiveStatus": unarchived.status_code,
        "writeAfterUnarchiveStatus": write_after.status_code,
    }
    passed = (
        checks["createStatus"] == 200
        and checks["archiveStatus"] == 204
        and checks["readArchivedStatus"] == 200
        and checks["writeArchivedStatus"] == 423
        and checks["writeArchivedCode"] == "document_archived"
        and checks["unarchiveStatus"] == 204
        and checks["writeAfterUnarchiveStatus"] in (200, 409)
    )
    receipt = {
        "schema": "tai.reference.sui-archive-lifecycle-gate/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/archive_lifecycle_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-archive-lifecycle-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Archives a document, reads it, tries to write it, then unarchives and writes again. It does not test the archive gate under concurrent writers or with an agent credential.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
