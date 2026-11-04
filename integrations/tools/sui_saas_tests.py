"""Run SUI's SaaS auth test subset and record the result."""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

FILES = [
    "tests/test_saas_session_csrf.py",
    "tests/test_trusted_saas_runtime.py",
    "tests/test_saas_document_read_pdp_outage.py",
    "tests/test_tenant_session_precondition.py",
]


def main():
    if len(sys.argv) < 3:
        print("usage: script --sui-repo <path>")
        return 2
    repo = Path(sys.argv[2])
    backend = repo / "03_Implement" / "backend"
    env = {key: value for key, value in os.environ.items() if not key.startswith("SUI_")}
    env["PYTHONPATH"] = str(backend / "src")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *FILES, "-q"],
        cwd=backend,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = result.stdout + result.stderr
    passed_match = re.search(r"(\d+) passed", output)
    failed_match = re.search(r"(\d+) failed", output)
    passed = int(passed_match.group(1)) if passed_match else 0
    failed = int(failed_match.group(1)) if failed_match else 0
    ok = result.returncode == 0 and failed == 0 and passed > 0
    receipt = {
        "schema": "tai.reference.sui-saas-tests/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 and the SUI checkout on PYTHONPATH",
        "command": "python integrations/tools/sui_saas_tests.py --sui-repo <SUI>",
        "result": "PASS" if ok else "FAIL",
        "suiCommit": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
        ).stdout.strip(),
        "observed": {"files": FILES, "passed": passed, "failed": failed, "returncode": result.returncode},
        "scope": "Runs four SUI test files covering SaaS CSRF, runtime policy, PDP outage and tenant session preconditions. It does not exercise a live deployment.",
    }
    Path("evaluations/records/SUI-saas-tests-2026-11-03.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt["observed"]))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
