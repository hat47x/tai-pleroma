"""Fire two conditional PUTs at once against SUI on PostgreSQL."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import threading
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
    import psycopg

    pg = pgserver.get_server(tempfile.mkdtemp(prefix="sui-pgrace-"))
    uri = pg.get_uri()
    os.environ["SUI_DATABASE_URL"] = uri
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "race-key"
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    import httpx
    import uvicorn
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

    port = 8101
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"
    headers = {"X-API-Key": "race-key"}
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                httpx.get(f"{base_url}/openapi.json", timeout=2)
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        created = httpx.put(f"{base_url}/docs/{projected.id}", json=payload, headers=headers, timeout=60)
        etag = created.headers.get("ETag")
        variants = []
        for title in ("Race A", "Race B"):
            body = json.loads(json.dumps(payload))
            body["title"] = title
            variants.append(body)
        results = [None, None]
        barrier = threading.Barrier(2)

        def send(index):
            barrier.wait()
            response = httpx.put(
                f"{base_url}/docs/{projected.id}",
                json=variants[index],
                headers={**headers, "If-Match": etag},
                timeout=60,
            )
            results[index] = response.status_code

        workers = [threading.Thread(target=send, args=(index,)) for index in range(2)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()
    finally:
        server.should_exit = True
        thread.join(timeout=15)

    with psycopg.connect(uri) as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) from documents")
            document_rows = cur.fetchone()[0]
            cur.execute("select count(*) from canvas_revision_heads")
            head_rows = cur.fetchone()[0]

    winners = [status for status in results if status == 200]
    conflicts = [status for status in results if status == 409]
    receipt = {
        "schema": "tai.reference.sui-postgres-concurrency/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, uvicorn, and an embedded PostgreSQL 16.2",
        "command": f"python integrations/pilot-sui-document/assembler/postgres_concurrency_check.py --sui-repo {args.sui_repo} --artifact {args.artifact}",
        "result": "PASS" if len(winners) == 1 and len(conflicts) == 1 else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": {
            "createStatus": created.status_code,
            "statuses": results,
            "winners": len(winners),
            "conflicts": len(conflicts),
            "documentRows": document_rows,
            "headRows": head_rows,
            "database": "embedded PostgreSQL 16.2",
        },
        "scope": "Two conditional PUTs race with the same ETag against a real PostgreSQL. It shows one winner and one conflict for this run; it does not prove fairness, throughput, or behaviour under sustained contention.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pg.cleanup()
    print(json.dumps(receipt["observed"]))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
