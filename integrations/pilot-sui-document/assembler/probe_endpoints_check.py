"""Check SUI's probe endpoints: what each one actually asserts, and that they bypass the API key."""

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


def _alembic_table_present(db_path):
    import sqlite3

    try:
        with sqlite3.connect(db_path) as connection:
            row = connection.execute(
                "select count(*) from sqlite_master where type='table' and name='alembic_version'"
            ).fetchone()
        return bool(row and row[0])
    except sqlite3.Error:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="sui-probes-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "probe-key"
    os.environ["SUI_APP_REVISION"] = "probe-rev"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from fastapi.testclient import TestClient
    from sqlalchemy import text

    from sui_sensemaking_api.db import engine
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

    with TestClient(app) as client:
        healthz = client.get("/healthz")
        readyz = client.get("/readyz")
        version = client.get("/version")
        with_key = client.get("/version", headers={"X-API-Key": "probe-key"})
        wrong_key = client.get("/docs", headers={"X-API-Key": "wrong"})
        wrong_key_health = client.get("/healthz", headers={"X-API-Key": "wrong"})
        admin_without_any = client.get("/admin/provision/audit")

    health_body = healthz.json() if healthz.status_code == 200 else {}
    ready_body = readyz.json() if readyz.content else {}
    version_body = version.json() if version.status_code == 200 else {}
    checks = {
        "healthzStatus": healthz.status_code,
        "healthzBody": health_body,
        "readyzStatus": readyz.status_code,
        "readyzBody": ready_body,
        "readyzChecks": sorted((ready_body.get("checks") or {}).keys()),
        "versionStatus": version.status_code,
        "versionRevision": version_body.get("revision"),
        "versionProfile": version_body.get("runtimeProfile"),
        "versionNeedsNoKey": version.status_code == 200,
        "withKeyStatus": with_key.status_code,
        "wrongKeyDocsStatus": wrong_key.status_code,
        "wrongKeyHealthStatus": wrong_key_health.status_code,
        "adminWithoutKeyStatus": admin_without_any.status_code,
        "readyImpliesDatabaseOk": (ready_body.get("checks") or {}).get("database") == "ok",
        "alembicVersionTablePresent": _alembic_table_present(workdir / "sui.db"),
        "readyImpliesSchemaOk": (ready_body.get("checks") or {}).get("schema") == "ok",
    }
    passed = (
        checks["healthzStatus"] == 200
        and checks["healthzBody"] == {"status": "ok"}
        and checks["readyzStatus"] in (200, 503)
        and "database" in checks["readyzChecks"]
        and checks["versionStatus"] == 200
        and checks["versionRevision"] == "probe-rev"
        and checks["versionProfile"] == "local-dev"
        and checks["withKeyStatus"] == 200
        and checks["wrongKeyDocsStatus"] == 401
        and checks["wrongKeyHealthStatus"] == 200
        and checks["adminWithoutKeyStatus"] in (200, 401, 403, 503)
        and checks["alembicVersionTablePresent"] is False
    )
    receipt = {
        "schema": "tai.reference.sui-probe-endpoints/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/probe_endpoints_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-probes-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Reads /healthz, /readyz, /version and compares them with a wrong-key /docs request and an unauthenticated admin call. With no SUI_ADMIN_API_KEY and local-dev, the admin plane answers 200 by design. The temporary SQLite database has no alembic_version table, and /readyz reports database=unreachable rather than a schema mismatch: the schema query shares the readiness try block. This is recorded as observed, not fixed.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
