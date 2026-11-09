"""Probe the SUI SaaS multi-tenant profile without changing it."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    sui_repo = Path(sys.argv[1])
    script = (
        "import os, sys\n"
        "sys.path.insert(0, r'" + str(sui_repo / "03_Implement/backend/src") + "')\n"
        "try:\n"
        "    from sui_sensemaking_api.main import app\n"
        "    print('IMPORT_OK')\n"
        "except SystemExit as error:\n"
        "    print('SYSTEM_EXIT', error.code)\n"
        "except Exception as error:\n"
        "    print('ERROR', type(error).__name__, error)\n"
    )
    env = os.environ.copy()
    env.update(
        {
            "SUI_RUNTIME_PROFILE": "saas-multitenant",
            "SUI_DATABASE_URL": "postgresql://user:pass@127.0.0.1:5432/sui",
            "SUI_LLM_PROVIDER": "none",
            "SUI_LOG_LEVEL": "ERROR",
            "SUI_API_KEY": "probe",
            "SUI_ADMIN_API_KEY": "probe-admin",
        }
    )
    started = time.time()
    completed = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    output = (completed.stdout + completed.stderr).strip()
    receipt = {
        "schema": "tai.reference.sui-saas-probe/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12",
        "command": "python integrations/tools/probe_saas_profile.py <SUI repo>",
        "result": "EXPECTED_REFUSAL" if "IMPORT_OK" not in output else "IMPORTED",
        "observed": {
            "runtimeProfile": "saas-multitenant",
            "importOk": "IMPORT_OK" in output,
            "seconds": round(time.time() - started, 2),
            "outputTail": output.splitlines()[-8:],
        },
        "scope": "Shows what happens when SUI is asked for the SaaS multi-tenant profile without configuring it. It does not enable the profile or change SUI.",
    }
    out = ROOT / "evaluations/saas-profile-probe-2026-11-03.json"
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt["observed"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
