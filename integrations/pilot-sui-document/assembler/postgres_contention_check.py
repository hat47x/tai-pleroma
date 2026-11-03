"""Repeat conditional-PUT contention against SUI on PostgreSQL."""

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
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--writers", type=int, default=3)
    parser.add_argument("--retry-transient", type=int, default=2)
    args = parser.parse_args()

    import pgserver
    import psycopg

    pg = pgserver.get_server(tempfile.mkdtemp(prefix="sui-pgcont-"))
    uri = pg.get_uri()
    os.environ["SUI_DATABASE_URL"] = uri
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "cont-key"
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

    port = 8102
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"
    headers = {"X-API-Key": "cont-key"}
    rounds = []
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                httpx.get(f"{base_url}/openapi.json", timeout=2)
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        created = httpx.put(f"{base_url}/docs/{projected.id}", json=payload, headers=headers, timeout=60)
        for round_index in range(args.rounds):
            current = httpx.get(f"{base_url}/docs/{projected.id}", headers=headers, timeout=30)
            etag = current.headers.get("ETag")
            statuses = [None] * args.writers
            retries = [0] * args.writers
            barrier = threading.Barrier(args.writers)

            def send(index, current_etag=etag, round_no=round_index):
                barrier.wait()
                attempt = 0
                while True:
                    body = json.loads(json.dumps(payload))
                    body["title"] = f"round-{round_no}-writer-{index}"
                    response = httpx.put(
                        f"{base_url}/docs/{projected.id}",
                        json=body,
                        headers={**headers, "If-Match": current_etag},
                        timeout=60,
                    )
                    if response.status_code == 503 and attempt < args.retry_transient:
                        attempt += 1
                        retries[index] = attempt
                        refreshed = httpx.get(
                            f"{base_url}/docs/{projected.id}", headers=headers, timeout=30
                        )
                        current_etag = refreshed.headers.get("ETag")
                        continue
                    statuses[index] = response.status_code
                    break

            workers = [threading.Thread(target=send, args=(index,)) for index in range(args.writers)]
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join()
            rounds.append({"round": round_index + 1, "statuses": statuses, "retries": retries})
    finally:
        server.should_exit = True
        thread.join(timeout=15)

    with psycopg.connect(uri) as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) from documents")
            document_rows = cur.fetchone()[0]

    settled = all(all(status in (200, 409) for status in item["statuses"]) for item in rounds)
    transient = sum(
        1 for item in rounds for status in item["statuses"] if status not in (200, 409)
    )
    receipt = {
        "schema": "tai.reference.sui-postgres-contention/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, uvicorn, and an embedded PostgreSQL 16.2",
        "command": f"python integrations/pilot-sui-document/assembler/postgres_contention_check.py --sui-repo {args.sui_repo} --artifact {args.artifact}",
        "result": "PASS" if settled else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": {
            "createStatus": created.status_code,
            "rounds": rounds,
            "roundCount": len(rounds),
            "writers": args.writers,
            "transient": transient,
            "retries": sum(sum(item.get("retries", [])) for item in rounds),
            "documentRows": document_rows,
            "database": "embedded PostgreSQL 16.2",
        },
        "scope": "Repeats conditional-PUT contention for a few rounds against a real PostgreSQL. It does not prove throughput, fairness, or long-running stability.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pg.cleanup()
    print(json.dumps({"settled": settled, "rounds": rounds}))
    return 0 if settled else 1


if __name__ == "__main__":
    raise SystemExit(main())
