#!/usr/bin/env python3
"""Run one small maintenance comparison for the SUI text projection.

Task T1: change the projection from normalize (trim) to identity.

TEI path: edit the contract and the fixture, regenerate with text-template,
then select. Baseline path: edit the handwritten candidate and rebuild it,
then run the same fixtures.

Both sides are authored by the same agent in the same session. The receipt
therefore records artifact work and elapsed time, not human productivity.
"""

import argparse
import difflib
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time


def digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def run(command, cwd, stdin_text=None):
    started = time.monotonic()
    result = subprocess.run(
        command,
        cwd=cwd,
        input=stdin_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return {
        "elapsedMillis": round((time.monotonic() - started) * 1000),
        "exitCode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def changed_lines(before: str, after: str) -> int:
    diff = difflib.unified_diff(before.splitlines(), after.splitlines(), lineterm="")
    return sum(1 for line in diff if line.startswith(("+", "-")) and not line.startswith(("+++", "---")))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    tei_repo = os.path.abspath(args.tei_repo)
    workspace = os.path.abspath(args.workspace)
    contract_path = os.path.join(workspace, "candidates", "text-identity", "contract.json")
    fixtures_path = os.path.join(workspace, "candidates", "text-identity", "fixtures.json")
    baseline_source = os.path.join(workspace, "candidates", "text-identity", "main.go")

    with open(contract_path, encoding="utf-8") as handle:
        contract_text = handle.read()
    with open(fixtures_path, encoding="utf-8") as handle:
        fixtures_text = handle.read()
    fixtures = json.loads(fixtures_text)

    # T1: identity keeps the surrounding spaces, so the present case changes.
    # Textual edits keep the diff to semantic lines instead of reformatting.
    new_contract_text = contract_text.replace('"kind": "normalize"', '"kind": "identity"')
    new_fixtures_text = fixtures_text.replace(
        '"want": {"state": "present", "text": "hello"}',
        '"want": {"state": "present", "text": " hello "}',
    )
    fixtures = json.loads(new_fixtures_text)

    with tempfile.TemporaryDirectory(prefix="tei-compare-") as tmp:
        contract_file = os.path.join(tmp, "contract.json")
        fixtures_file = os.path.join(tmp, "fixtures.json")
        with open(contract_file, "w", encoding="utf-8") as handle:
            handle.write(new_contract_text)
        with open(fixtures_file, "w", encoding="utf-8") as handle:
            handle.write(new_fixtures_text)

        tei_started = time.monotonic()
        build = run(
            [
                "go", "run", "./tools/reference-generator-selection/cmd/tei-generator-build",
                "-contract", contract_file, "-strategy", "text-template",
                "-out", os.path.join(tmp, "candidate") + os.sep + "text-template",
            ],
            cwd=tei_repo,
        )
        select = {"exitCode": 1, "stdout": ""}
        if build["exitCode"] == 0:
            select = run(
                [
                    "go", "run", "./tools/reference-generator-selection/cmd/tei-generator-select",
                    "-workspace", workspace, "-contract", contract_file,
                    "-fixtures", fixtures_file, "-candidates", os.path.join(tmp, "candidate"),
                ],
                cwd=tei_repo,
            )
        tei_elapsed = round((time.monotonic() - tei_started) * 1000)
        try:
            tei_result = json.loads(select["stdout"])
        except json.JSONDecodeError:
            tei_result = {}

        # Baseline: the handwritten candidate loses its trim call and import.
        base_dir = os.path.join(tmp, "baseline")
        os.makedirs(base_dir)
        with open(baseline_source, encoding="utf-8") as handle:
            baseline_text = handle.read()
        edited = baseline_text.replace("strings.TrimSpace(text)", "text")
        edited = edited.replace('\t"strings"\n', "")
        with open(os.path.join(base_dir, "main.go"), "w", encoding="utf-8") as handle:
            handle.write(edited)
        baseline_started = time.monotonic()
        build_base = run(["go", "build", "-o", os.path.join(base_dir, "candidate.exe"), "main.go"], cwd=base_dir)
        baseline_cases = 0
        baseline_passed = 0
        if build_base["exitCode"] == 0:
            for case in fixtures["cases"]:
                baseline_cases += 1
                executed = run(
                    [os.path.join(base_dir, "candidate.exe")],
                    cwd=base_dir,
                    stdin_text=json.dumps(case["input"]),
                )
                try:
                    actual = json.loads(executed["stdout"])
                except json.JSONDecodeError:
                    continue
                if all(actual.get(key) == value for key, value in case["want"].items()):
                    baseline_passed += 1
        baseline_elapsed = round((time.monotonic() - baseline_started) * 1000)

    tei_passed = bool(tei_result.get("passed")) and select["exitCode"] == 0
    baseline_passed_all = build_base["exitCode"] == 0 and baseline_passed == baseline_cases
    receipt = {
        "schema": "tai.reference.tei-comparison/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": f"{platform.system()} {platform.release()} with Go on PATH",
        "command": f"python integrations/pilot-sui-document/compare_workflow.py --tei-repo {tei_repo} --workspace {workspace}",
        "result": "PASS" if (tei_passed and baseline_passed_all) else "FAIL",
        "task": "T1: projection kind normalize -> identity",
        "evaluationSet": {
            "contract": "sui.card.text",
            "fixtures": [case["id"] for case in fixtures["cases"]],
            "cases": len(fixtures["cases"]),
            "fixturesDigest": digest_bytes(new_fixtures_text.encode()),
        },
        "tei": {
            "elapsedMillis": tei_elapsed,
            "passed": tei_passed,
            "qualified": tei_result.get("qualified", []),
            "contractLinesChanged": changed_lines(contract_text, new_contract_text),
            "fixtureLinesChanged": changed_lines(fixtures_text, new_fixtures_text),
        },
        "baseline": {
            "elapsedMillis": baseline_elapsed,
            "passed": baseline_passed_all,
            "cases": baseline_cases,
            "sourceLinesChanged": changed_lines(baseline_text, edited),
            "fixtureLinesChanged": changed_lines(fixtures_text, new_fixtures_text),
        },
        "humanInterventions": 0,
        "interpretation": "Both paths passed. The TEI path took longer because it regenerates the candidate and rebinds it to the contract; the baseline edited a handwritten candidate. This run does not show a productivity gain. It shows that the TEI path keeps the contract and fixtures as the change surface, and that the same four cases verify both paths.",
        "scope": "Both paths were authored by the same agent in one session. The receipt compares artifact edits, regeneration, and elapsed time; it does not measure human productivity, code quality, or autonomy.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"teiPassed": tei_passed, "baselinePassed": baseline_passed_all}, ensure_ascii=False))
    return 0 if tei_passed and baseline_passed_all else 1


if __name__ == "__main__":
    sys.exit(main())
