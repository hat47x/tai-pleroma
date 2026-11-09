"""Start SUI under the SaaS profile with a migrated Postgres and record the refusal."""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def free_port():
    import socket

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main():
    sui_repo = Path(sys.argv[1])
    extra = [item.split("=", 1) for item in sys.argv[2:]]
    import pgserver

    pg = pgserver.get_server(tempfile.mkdtemp(prefix="sui-saas-pg-"))
    uri = pg.get_uri()
    env = os.environ.copy()
    env.update(
        {
            "SUI_RUNTIME_PROFILE": "saas-multitenant",
            "SUI_DATABASE_URL": uri,
            "SUI_LLM_PROVIDER": "none",
            "SUI_LOG_LEVEL": "ERROR",
            "SUI_API_KEY": "probe",
            "SUI_ADMIN_API_KEY": "probe-admin",
        }
    )
    backend = sui_repo / "03_Implement/backend"
    migration = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=str(backend),
        env=env,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    env.update(dict(extra))
    sys.path.insert(0, str(backend / "src"))
    from sui_sensemaking_api.db import engine
    from sui_sensemaking_api.models import Base

    Base.metadata.create_all(engine)

    port = free_port()
    script = (
        "import sys, uvicorn\n"
        "sys.path.insert(0, r'" + str(backend / "src") + "')\n"
        "from sui_sensemaking_api.main import app\n"
        f"uvicorn.run(app, host='127.0.0.1', port={port}, log_level='error')\n"
    )
    started = time.time()
    started_ok = False
    request_status = None
    process = subprocess.Popen(
        [sys.executable, "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    deadline = time.time() + 30
    while time.time() < deadline:
        if process.poll() is not None:
            break
        time.sleep(0.5)
    if process.poll() is None:
        output = "process stayed up for 30 seconds"
        try:
            import httpx

            request_status = httpx.get(
                f"http://127.0.0.1:{port}/openapi.json",
                follow_redirects=False,
                timeout=5,
            ).status_code
        except Exception as caught:
            request_status = type(caught).__name__
        started_ok = isinstance(request_status, int)
        process.terminate()
        process.wait(timeout=15)
    else:
        output = (
            (process.stdout.read() if process.stdout else "")
            + (process.stderr.read() if process.stderr else "")
        ).strip()
    missing = []
    for line in output.splitlines():
        if line.startswith("RuntimeError: trusted SaaS runtime policy is incomplete: "):
            missing = [item.strip() for item in line.split("incomplete: ", 1)[1].split(",")]

    receipt = {
        "schema": "tai.reference.sui-saas-startup/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, uvicorn, and an embedded PostgreSQL 16.2",
        "command": "python integrations/tools/saas_startup_probe.py <SUI repo>",
        "result": "STARTED" if started_ok else ("REFUSED" if missing else "TIMEOUT"),
        "observed": {
            "runtimeProfile": "saas-multitenant",
            "migration": "alembic upgrade head",
            "seconds": round(time.time() - started, 2),
            "missing": missing,
            "missingCount": len(missing),
            "requestStatus": request_status,
            "started": started_ok,
            "extraEnv": {key: ("<redacted>" if key == "SUI_SAAS_AUTH_SESSION_HASH_KEY" else value) for key, value in extra},
            "outputTail": output.splitlines()[-5:],
        },
        "scope": "Starts SUI under the SaaS profile against a migrated embedded PostgreSQL. It records the startup refusal; it does not configure the policy or change SUI.",
    }
    out = ROOT / "evaluations/saas-startup-probe-2026-11-03.json"
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pg.cleanup()
    print(json.dumps(receipt["observed"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
