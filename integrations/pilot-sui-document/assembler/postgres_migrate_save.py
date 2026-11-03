"""Save a projection artifact into SUI backed by an embedded PostgreSQL."""

import argparse
import hashlib
import json
import os
import sys
import subprocess
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

    data_dir = tempfile.mkdtemp(prefix="sui-pg-")
    server = pgserver.get_server(data_dir)
    uri = server.get_uri()
    os.environ["SUI_DATABASE_URL"] = uri
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "pg-test-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    import httpx
    import uvicorn

    from sui_sensemaking_api.db import engine
    from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload
    from sui_sensemaking_api.main import app
    from sqlalchemy import text
    from sui_sensemaking_api.models import Base

    migration = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=str(Path(args.sui_repo) / "03_Implement/backend"), env=os.environ.copy(), capture_output=True, encoding="utf-8", errors="replace")
    if migration.returncode != 0:
        print(migration.stderr, file=sys.stderr)
        return 1
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

    port = 8100
    uvicorn_server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=uvicorn_server.run, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"
    ready = False
    created = fetched = anonymous = None
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                httpx.get(f"{base_url}/openapi.json", timeout=2)
                ready = True
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        if not ready:
            raise RuntimeError("server did not become ready")
        headers = {"X-API-Key": "pg-test-key"}
        created = httpx.put(f"{base_url}/docs/{projected.id}", json=payload, headers=headers, timeout=60)
        fetched = httpx.get(f"{base_url}/docs/{projected.id}", headers=headers, timeout=60)
        anonymous = httpx.put(f"{base_url}/docs/{projected.id}", json=payload, timeout=60)
    finally:
        uvicorn_server.should_exit = True
        thread.join(timeout=20)

    with psycopg.connect(uri) as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) from documents")
            document_rows = cur.fetchone()[0]
            cur.execute("select count(*) from canvas_revisions")
            card_rows = cur.fetchone()[0]

    saved = fetched.json() if fetched is not None and fetched.status_code == 200 else {}
    round_trip = {card.get("id") for card in saved.get("cards", [])} == {
        card.id for card in projected.cards
    }
    receipt = {
        "schema": "tai.reference.tei-sui-postgres/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, uvicorn, and an embedded PostgreSQL 16.2",
        "command": f"python integrations/pilot-sui-document/assembler/postgres_migrate_save.py --sui-repo {args.sui_repo} --artifact {args.artifact}",
        "result": "PASS" if round_trip else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": {
            "serverReady": ready,
            "createStatus": created.status_code if created is not None else None,
            "createBody": created.text[:300] if created is not None else None,
            "readStatus": fetched.status_code if fetched is not None else None,
            "anonymousStatus": anonymous.status_code if anonymous is not None else None,
            "documentId": projected.id,
            "cards": len(saved.get("cards", [])),
            "roundTrip": round_trip,
            "database": "embedded PostgreSQL 16.2",
            "documentRows": document_rows,
            "revisionRows": card_rows,
            "runtimeProfile": "local-dev",
            "migration": "alembic upgrade head",
        },
        "scope": "SUI runs against a real PostgreSQL process started by pgserver. It does not verify a managed database, the SaaS multi-tenant profile, backups, migrations, or deployment.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    server.cleanup()
    print(json.dumps(receipt["observed"]))
    return 0 if round_trip else 1


if __name__ == "__main__":
    raise SystemExit(main())
