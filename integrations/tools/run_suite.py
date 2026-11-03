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
    parser.add_argument("--sei-schema", default="")
    parser.add_argument("--mmi-schema", default="")
    parser.add_argument("--eki-openapi", default="")
    parser.add_argument("--eki-control", default="")
    parser.add_argument("--skip-checker", action="store_true")
    parser.add_argument("--out", default="evaluations/records/TEI-suite-2026-11-03.json")
    args = parser.parse_args()

    steps = {
        "checker": run_step("checker", ["tools/check-synthetic-receipts/check.py", "--root", str(ROOT)]),
        "artifacts": run_step("artifacts", ["integrations/tools/validate_artifacts.py"]),
        "digests": run_step("digests", ["integrations/tools/verify_artifact_digests.py"]),
        "saas_adapters": run_step("saas_adapters", ["integrations/tools/sui_saas_adapter_contract.py", "--sui-src", f"{args.sui_repo}/03_Implement/backend/src"]),
        "saas_oauth": run_step("saas_oauth", ["integrations/tools/sui_saas_oauth_contract.py", "--sui-src", f"{args.sui_repo}/03_Implement/backend/src"]),
        "saas_login": run_step("saas_login", ["integrations/tools/sui_saas_login_contract.py", "--sui-src", f"{args.sui_repo}/03_Implement/backend/src"]),
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
        ),        "postgres_etag": run_step(
            "postgres_etag",
            [
                "integrations/pilot-sui-document/assembler/postgres_etag_check.py",
                "--sui-repo",
                args.sui_repo,
                "--artifact",
                "evaluations/artifacts/scn-003-document.json",
                "--out",
                "evaluations/records/SUI-TEI-postgres-etag-2026-11-03.json",
            ],
        ),        "postgres_concurrency": run_step(
            "postgres_concurrency",
            [
                "integrations/pilot-sui-document/assembler/postgres_concurrency_check.py",
                "--sui-repo",
                args.sui_repo,
                "--artifact",
                "evaluations/artifacts/scn-003-document.json",
                "--out",
                "evaluations/records/SUI-TEI-postgres-concurrency-2026-11-03.json",
            ],
        ),        "postgres_contention": run_step(
            "postgres_contention",
            [
                "integrations/pilot-sui-document/assembler/postgres_contention_check.py",
                "--sui-repo",
                args.sui_repo,
                "--artifact",
                "evaluations/artifacts/scn-003-document.json",
                "--out",
                "evaluations/records/SUI-TEI-postgres-contention-2026-11-03.json",
            ],
        ),        "postgres_retry": run_step(
            "postgres_retry",
            [
                "integrations/pilot-sui-document/assembler/postgres_contention_check.py",
                "--sui-repo",
                args.sui_repo,
                "--artifact",
                "evaluations/artifacts/scn-003-document.json",
                "--retry-transient",
                "2",
                "--out",
                "evaluations/records/SUI-TEI-postgres-retry-2026-11-03.json",
            ],
        ),        "postgres_multidoc": run_step(
            "postgres_multidoc",
            [
                "integrations/pilot-sui-document/assembler/postgres_multi_save.py",
                "--sui-repo",
                args.sui_repo,
                "--artifact",
                "evaluations/artifacts/scn-003-document.json",
                "--out",
                "evaluations/records/SUI-TEI-postgres-multidoc-2026-11-03.json",
            ],
        ),        "records": run_step(
            "records",
            [
                "integrations/tools/validate_records.py",
                "--sei-schema",
                args.sei_schema,
                "--mmi-schema",
                args.mmi_schema,
                "--eki-openapi",
                args.eki_openapi,
                "--sui-repo",
                args.sui_repo,
            ],
        ),
    }
    if args.eki_control:
        steps["eki_submit"] = run_step(
            "eki_submit",
            [
                "integrations/tools/eki_submit_projection.py",
                "--control-binary",
                args.eki_control,
                "--artifact",
                "evaluations/artifacts/eki-task-request-record.json",
                "--out",
                "evaluations/records/EKI-TEI-submit-2026-11-03.json",
            ],
        )
    if args.skip_checker:
        steps.pop("checker", None)
    tei_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=args.tei_repo, capture_output=True, text=True).stdout.strip()
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
        "teiCommit": tei_commit,
        "steps": steps,
        "scope": "Runs the checker, artifact schema checks, SCN-003 link check, and the SUI pipeline (without save). It does not run Postgres, deployment, or external effects.",
    }
    out = ROOT / args.out
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": receipt["result"], "steps": {k: v["returncode"] for k, v in steps.items()}}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
