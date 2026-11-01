#!/usr/bin/env python3
"""Measure one TEI text-projection workflow: generate a candidate, select it
against fixtures, and record machine-observable cost.

This measures the tool steps only. It does not measure human effort, meaning
correctness, or productivity. The receipt states that boundary.
"""

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import time


def digest(path: str) -> str:
    with open(path, "rb") as handle:
        return "sha256:" + hashlib.sha256(handle.read()).hexdigest()


def run(command, cwd):
    started = time.monotonic()
    result = subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return {
        "command": " ".join(command),
        "elapsedMillis": round((time.monotonic() - started) * 1000),
        "exitCode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--fixtures", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--human-interventions", type=int, default=0)
    args = parser.parse_args()

    tei_repo = os.path.abspath(args.tei_repo)
    contract = os.path.abspath(args.contract)
    fixtures = os.path.abspath(args.fixtures)
    workspace = os.path.abspath(args.workspace)

    with tempfile.TemporaryDirectory(prefix="tei-measure-") as tmp:
        candidate_dir = os.path.join(tmp, "text-template")
        build = run(
            [
                "go", "run", "./tools/reference-generator-selection/cmd/tei-generator-build",
                "-contract", contract, "-strategy", "text-template", "-out", candidate_dir,
            ],
            cwd=tei_repo,
        )
        steps = [{"name": "generate", **{k: build[k] for k in ("command", "elapsedMillis", "exitCode")}}]
        if build["exitCode"] != 0:
            receipt = {
                "schema": "tai.reference.tei-workflow-measurement/v0",
                "passed": False,
                "steps": steps,
                "stderr": build["stderr"],
                "humanInterventions": args.human_interventions,
                "scope": "Tool-step measurement only; not a productivity or autonomy proof.",
            }
            with open(args.out, "w", encoding="utf-8") as handle:
                json.dump(receipt, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            return 1

        selected = run(
            [
                "go", "run", "./tools/reference-generator-selection/cmd/tei-generator-select",
                "-workspace", workspace, "-contract", contract,
                "-fixtures", fixtures, "-candidates", tmp,
            ],
            cwd=tei_repo,
        )
        steps.append({"name": "select", **{k: selected[k] for k in ("command", "elapsedMillis", "exitCode")}})

    select_stdout = selected.get("stdout") or ""
    try:
        result = json.loads(select_stdout)
    except json.JSONDecodeError:
        result = {}

    tei_commit = run(["git", "rev-parse", "HEAD"], cwd=tei_repo)["stdout"].strip()
    passed = bool(result.get("passed")) and selected["exitCode"] == 0
    receipt = {
        "schema": "tai.reference.tei-workflow-measurement/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "teiCommit": tei_commit,
        "host": f"{platform.system()} {platform.release()} with Go on PATH",
        "command": f"{steps[0]['command']} && {steps[1]['command']}",
        "result": "PASS" if passed else "FAIL",
        "workspace": os.path.relpath(workspace),
        "steps": steps,
        "attempts": {"generate": 1, "select": 1},
        "passed": passed,
        "qualified": result.get("qualified", []),
        "cases": sum(len(candidate.get("results", [])) for candidate in result.get("candidates", [])),
        "digests": {"contract": digest(contract), "fixtures": digest(fixtures)},
        "humanInterventions": args.human_interventions,
        "autonomousSteps": len(steps),
        "scope": "Tool-step measurement only. It records elapsed time, attempts, and human interventions supplied by the caller; it does not measure human effort, meaning correctness, productivity, or autonomy.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
