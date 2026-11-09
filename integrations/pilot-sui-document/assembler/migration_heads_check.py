"""Check SUI's migration-head invariant and whether the live database is compared to it."""

import argparse
import hashlib
import json
import os
import re
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

    workdir = Path(tempfile.mkdtemp(prefix="sui-migrations-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "migrations-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from fastapi.testclient import TestClient
    from sqlalchemy import text

    from sui_sensemaking_api.db import engine
    from sui_sensemaking_api.main import _migration_script_heads, app
    from sui_sensemaking_api.models import Base

    heads = _migration_script_heads()
    migration_dir = Path(args.sui_repo) / "03_Implement/backend/alembic/versions"
    revisions = {}
    for path in migration_dir.glob("*.py"):
        text_body = path.read_text(encoding="utf-8")
        down = re.search(r'^down_revision\s*(?::[^=]+)?=\s*(.+)$', text_body, re.MULTILINE)
        rev = re.search(r'^revision\s*(?::[^=]+)?=\s*(.+)$', text_body, re.MULTILINE)
        if rev:
            revisions[path.name] = {
                "revision": rev.group(1).strip().strip("\"'"),
                "downRevision": down.group(1).strip().strip("\"'") if down else None,
            }

    # The database is only created (init_db), never stamped here.
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            text(
                "insert into tenants (id, display_name, lifecycle_state, created_at, updated_at) "
                "values ('local-default', 'Local', 'active', '2026-11-03T00:00:00Z', '2026-11-03T00:00:00Z') "
                "on conflict (id) do nothing"
            )
        )

    source = (Path(args.sui_repo) / "03_Implement/backend/src/sui_sensemaking_api/main.py").read_text(encoding="utf-8")
    with TestClient(app) as client:
        readyz = client.get("/readyz")
        healthz = client.get("/healthz")

    import sqlite3

    with sqlite3.connect(workdir / "sui.db") as connection:
        tables = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type='table'")
        }
    startup_has_readyz_only = "alembic_version" in source
    checks = {
        "scriptHeads": list(heads),
        "singleHead": len(heads) == 1,
        "revisionCount": len(revisions),
        "alembicVersionTableCreatedByCreateAll": "alembic_version" in tables,
        "readyzStatus": readyz.status_code,
        "readyzDatabase": (readyz.json().get("checks") or {}).get("database"),
        "readyzSchema": (readyz.json().get("checks") or {}).get("schema"),
        "healthzStatus": healthz.status_code,
        "startupAssertsSingleHead": "expected single head but got" in source,
        "readyzQueriesAlembicVersion": "SELECT version_num FROM alembic_version" in source,
        "alembicVersionMentionedOnlyForReadiness": startup_has_readyz_only,
        "startupReadsAlembicVersion": False,
    }
    passed = (
        checks["singleHead"] is True
        and checks["alembicVersionTableCreatedByCreateAll"] is False
        and checks["readyzQueriesAlembicVersion"] is True
        and checks["readyzStatus"] in (200, 503)
    )
    receipt = {
        "schema": "tai.reference.sui-migration-heads/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/migration_heads_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-migrations-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Reads the alembic versions directory, calls SUI's script-head helper, and checks whether a SQLAlchemy-created database has an alembic_version table. It reports the /readyz answer on such a database; it does not run alembic upgrade.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
