"""Run the TAI-side verification steps in one command and record the result."""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_step(name, args, timeout=900):
    started = time.time()
    completed = subprocess.run(
        [sys.executable, *args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        cwd=ROOT,
    )
    return {
        "returncode": completed.returncode,
        "seconds": round(time.time() - started, 2),
        "stdoutTail": completed.stdout.strip().splitlines()[-3:],
        "stderrTail": completed.stderr.strip().splitlines()[-3:],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--out", default="evaluations/records/TEI-suite-2026-11-03.json")
    args = parser.parse_args()

    steps = {
        "checker": run_step("checker", ["tools/check-synthetic-receipts/check.py", "--root", str(ROOT)]),
        "artifacts": run_step("artifacts", ["integrations/tools/validate_artifacts.py"]),
        "scenario": run_step("scenario", ["integrations/tools/check_scenario_artifacts.py"]),
        "pipeline": run_step(
            "pipeline",
            [
                "integrations/pilot-sui-document/assembler/run_pilot.py",
                "--tei-repo",
                args.tei_repo,
                "--sui-repo",
                args.sui_repo,
                "--workspace",
                str(ROOT / "integrations/pilot-sui-document"),
                "--out",
                "evaluations/records/TEI-suite-pipeline-2026-11-03.json",
            ],
        ),
        "compose": run_step(
            "compose",
            ["integrations/tools/compose_scn_003.py", "--sui-repo", args.sui_repo],
        ),
        "tls": run_step(
            "tls",
            [
                "integrations/pilot-sui-document/assembler/tls_check.py",
                "--sui-repo",
                args.sui_repo,
                "--out",
                "evaluations/records/SUI-TEI-tls-2026-11-03.json",
            ],
        ),
        "postgres": run_step(
            "postgres",
            [
                "integrations/pilot-sui-document/assembler/postgres_save.py",
                "--sui-repo",
                args.sui_repo,
                "--artifact",
                "evaluations/artifacts/scn-003-document.json",
                "--out",
                "evaluations/records/SUI-TEI-postgres-2026-11-03.json",
            ],
        ),
        "postgres_migrate": run_step(
            "postgres_migrate",
            [
                "integrations/pilot-sui-document/assembler/postgres_migrate_save.py",
                "--sui-repo",
                args.sui_repo,
                "--artifact",
                "evaluations/artifacts/scn-003-document.json",
                "--out",
                "evaluations/records/SUI-TEI-postgres-migrate-2026-11-03.json",
            ],
        ),
    }
    passed = all(step["returncode"] == 0 for step in steps.values())
    receipt = {
        "schema": "tai.reference.tei-suite/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go on PATH, Python 3.12, and the SUI consumer",
        "command": "python integrations/tools/run_suite.py --tei-repo <TEI> --sui-repo <SUI>",
        "result": "PASS" if passed else "FAIL",
        "steps": steps,
        "scope": "Runs the checker, artifact schema checks, SCN-003 link check, and the SUI pipeline (without save). It does not run Postgres, deployment, or external effects.",
    }
    out = ROOT / args.out
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": receipt["result"], "steps": {k: v["returncode"] for k, v in steps.items()}}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
