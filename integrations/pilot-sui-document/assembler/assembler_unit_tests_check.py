"""Run the pilot assembler's unit tests and record the result as a receipt."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default="integrations/pilot-sui-document")
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[3]
    assembler = (root / args.workspace / "assembler").resolve()
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "test_document_assembler", "-v"],
        cwd=assembler,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONPATH": str(assembler)},
    )
    output = (completed.stderr or completed.stdout).strip().splitlines()
    summary = output[-1] if output else ""
    ran_line = next((line for line in output if line.startswith("Ran ")), "")
    try:
        tests_run = int(ran_line.split()[1])
    except (IndexError, ValueError):
        tests_run = None

    checks = {
        "exit": completed.returncode,
        "testsRun": tests_run,
        "summary": summary,
        "failed": "FAILED" in summary,
    }
    passed = checks["exit"] == 0 and checks["testsRun"] is not None and not checks["failed"]
    receipt = {
        "schema": "tai.reference.tei-assembler-unit-tests/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 running the pilot assembler's unittest cases",
        "command": f"python integrations/pilot-sui-document/assembler/assembler_unit_tests_check.py --artifact {args.artifact} --out evaluations/records/SUI-TEI-assembler-tests-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Runs test_document_assembler with unittest and records the test count and result. It covers identifier uniqueness, endpoint resolution including absent kinds, containment, and affiliation collisions; it does not exercise the HTTP or persistence paths.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
