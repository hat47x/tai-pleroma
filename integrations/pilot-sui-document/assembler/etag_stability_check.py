"""Check SUI's document ETag stability and conditional GET behaviour."""

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

    workdir = Path(tempfile.mkdtemp(prefix="sui-etagstable-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "etag-stable-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from fastapi.testclient import TestClient
    from sqlalchemy import text

    from sui_sensemaking_api.db import engine
    from sui_sensemaking_api.main import app
    from sui_sensemaking_api.models import Base
    from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload

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
    headers = {"X-API-Key": "etag-stable-key"}
    with TestClient(app) as client:
        created = client.put(f"/docs/{projected.id}", json=payload, headers=headers)
        first = client.get(f"/docs/{projected.id}", headers=headers)
        second = client.get(f"/docs/{projected.id}", headers=headers)
        conditional = client.get(
            f"/docs/{projected.id}", headers={**headers, "If-None-Match": first.headers.get("etag") or '"none"'}
        )
        edited = dict(payload)
        edited["cards"] = [dict(card, text="edited") for card in payload.get("cards", [])]
        saved = client.put(f"/docs/{projected.id}", json=edited, headers={**headers, "If-Match": first.headers.get("etag") or "*"})
        after = client.get(f"/docs/{projected.id}", headers=headers)

    first_etag = first.headers.get("etag")
    second_etag = second.headers.get("etag")
    after_etag = after.headers.get("etag")
    checks = {
        "createStatus": created.status_code,
        "firstEtagPresent": bool(first_etag),
        "etagStableAcrossReads": bool(first_etag) and first_etag == second_etag,
        "conditionalGetStatus": conditional.status_code,
        "conditionalGetBodyMatches": conditional.content == first.content if conditional.status_code == 200 else False,
        "saveStatus": saved.status_code,
        "etagChangedAfterSave": bool(first_etag) and bool(after_etag) and first_etag != after_etag,
    }
    passed = (
        checks["createStatus"] == 200
        and checks["firstEtagPresent"]
        and checks["etagStableAcrossReads"]
        and checks["conditionalGetBodyMatches"]
        and checks["saveStatus"] == 200
        and checks["etagChangedAfterSave"]
    )
    receipt = {
        "schema": "tai.reference.sui-document-etag-stability/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/etag_stability_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-etag-stability-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Reads a document twice, repeats a read with If-None-Match, then saves an edit and reads again. Records that a conditional GET is answered with the full body (no 304), so readers re-read every time. It does not test concurrent writers.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
