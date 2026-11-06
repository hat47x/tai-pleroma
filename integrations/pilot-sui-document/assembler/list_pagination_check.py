"""Check SUI's document list keyset pagination via X-Next-Cursor."""

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

    workdir = Path(tempfile.mkdtemp(prefix="sui-listpage-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "list-page-key"
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

    base_payload = to_documentv1_payload(
        from_artifact(json.loads(Path(args.artifact).read_text(encoding="utf-8"))),
        transform={"panX": 0.0, "panY": 0.0, "zoom": 1.0},
        created_at="2026-11-03T00:00:00Z",
        updated_at="2026-11-03T00:00:00Z",
    )
    headers = {"X-API-Key": "list-page-key"}
    doc_ids = [f"doc-page-{index}" for index in range(4)]
    with TestClient(app) as client:
        created = []
        for index, doc_id in enumerate(doc_ids):
            body = dict(base_payload)
            body["id"] = doc_id
            body["title"] = f"Doc {index}"
            created.append(client.put(f"/docs/{doc_id}", json=body, headers=headers))
        first = client.get("/docs", params={"limit": 2}, headers=headers)
        cursor = first.headers.get("X-Next-Cursor")
        second = client.get("/docs", params={"limit": 2, "cursor": cursor}, headers=headers) if cursor else None
        second_cursor = second.headers.get("X-Next-Cursor") if second is not None else None
        third = (
            client.get("/docs", params={"limit": 2, "cursor": second_cursor}, headers=headers)
            if second_cursor
            else None
        )
        too_many = client.get("/docs", params={"limit": 501}, headers=headers)

    page1 = [item.get("id") for item in first.json()] if first.status_code == 200 else []
    page2 = [item.get("id") for item in second.json()] if second is not None and second.status_code == 200 else []
    page3 = [item.get("id") for item in third.json()] if third is not None and third.status_code == 200 else []
    checks = {
        "createStatuses": [response.status_code for response in created],
        "firstStatus": first.status_code,
        "firstPageSize": len(page1),
        "firstHasCursor": bool(cursor),
        "secondStatus": second.status_code if second is not None else None,
        "secondPageSize": len(page2),
        "noOverlap12": not set(page1) & set(page2),
        "allSeenOnce": sorted(page1 + page2 + page3) == sorted(doc_ids),
        "thirdHasCursor": bool(second_cursor),
        "overLimitStatus": too_many.status_code,
        "payloadHasNoText": all(
            "cards" not in item or not item.get("cards")
            for page in (first.json() if first.status_code == 200 else [])
            for item in [page]
        ),
    }
    passed = (
        all(status == 200 for status in checks["createStatuses"])
        and checks["firstStatus"] == 200
        and checks["firstPageSize"] == 2
        and checks["firstHasCursor"]
        and checks["secondStatus"] == 200
        and checks["secondPageSize"] == 2
        and checks["noOverlap12"]
        and checks["allSeenOnce"]
        and checks["overLimitStatus"] == 422
    )
    receipt = {
        "schema": "tai.reference.sui-document-list-pagination/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/list_pagination_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-list-pagination-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Writes four documents, then reads the list with limit=2 and follows X-Next-Cursor to the end, checking for overlap and completeness, plus an over-limit request. It does not test concurrent writes during pagination.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
