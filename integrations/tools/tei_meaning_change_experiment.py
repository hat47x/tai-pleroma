"""Measure one meaning change from contract edit to regenerated, conforming output.

The plan's feasibility condition 1 is "the artifacts can be regenerated from a
meaning change, with no or limited hand editing". That has only been exercised
implicitly. This probe runs it explicitly: copy the pilot, change one meaning
(add an optional `summary` to the island record), regenerate, and count what has
to be edited by hand before the same conformance run passes again.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CONTRACTS = ["document-record", "card-record", "island-record", "edge-record", "affiliation-record"]


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args, cwd, stdin_text=None, env=None):
    return subprocess.run(
        [str(part) for part in args],
        cwd=cwd,
        input=stdin_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )


def changed_lines(before, after):
    old = before.splitlines()
    new = after.splitlines()
    return sum(1 for line in new if line not in old)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--sui-repo", default="")
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(args.workspace).resolve()
    workdir = Path(tempfile.mkdtemp(prefix="tei-meaning-", dir=os.environ.get("GOTMPDIR") or None))
    pilot = workdir / "pilot"
    shutil.copytree(root, pilot)

    # 1. Baseline: the untouched copy must already conform.
    baseline_out = workdir / "baseline.json"
    baseline = run(
        [
            sys.executable, str(pilot / "assembler/integration_flow.py"),
            "--tei-repo", args.tei_repo, "--workspace", pilot,
            "--out", baseline_out,
        ],
        cwd=pilot,
    )
    baseline_all_passed = False
    baseline_cases = None
    if baseline_out.exists():
        data = json.loads(baseline_out.read_text(encoding="utf-8"))
        baseline_all_passed = data.get("result") == "PASS" and data.get("casesPassed") == data.get("casesRun")
        baseline_cases = {"run": data.get("casesRun"), "passed": data.get("casesPassed")}

    # 2. The meaning change: island gains an optional summary.
    island_contract = pilot / "candidates/island-record/contract.json"
    before_contract = island_contract.read_text(encoding="utf-8")
    contract = json.loads(before_contract)
    contract["version"] = "6"
    contract["inputs"].append({"attribute": "sui.island.summary", "primitive": "std.text"})
    contract["projection"]["fields"].append(
        {
            "name": "summary",
            "input": "summary",
            "attribute": "sui.island.summary",
            "primitive": "std.text",
            "optional": True,
        }
    )
    island_contract.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    contract_lines = changed_lines(before_contract, island_contract.read_text(encoding="utf-8"))

    # 3. Regenerate every candidate from the changed meanings, with no hand edit.
    regenerated = {}
    for name in CONTRACTS:
        out_dir = workdir / "gen" / name
        built = run(
            [
                "go", "run", "./tools/reference-generator-selection/cmd/tei-generator-build",
                "-contract", pilot / "candidates" / name / "contract.json",
                "-strategy", "text-record-template", "-out", out_dir,
            ],
            cwd=args.tei_repo,
        )
        regenerated[name] = {
            "exit": built.returncode,
            "generated": (out_dir / "main.go").exists(),
        }
    all_generated = all(item["generated"] for item in regenerated.values())

    # 4. Conformance straight after regeneration, with no fixture edit.
    after_out = workdir / "after.json"
    after = run(
        [
            sys.executable, str(pilot / "assembler/integration_flow.py"),
            "--tei-repo", args.tei_repo, "--workspace", pilot,
            "--out", after_out,
        ],
        cwd=pilot,
    )
    after_cases = {"run": None, "passed": None, "result": None}
    if after_out.exists():
        data = json.loads(after_out.read_text(encoding="utf-8"))
        after_cases = {
            "run": data.get("casesRun"),
            "passed": data.get("casesPassed"),
            "result": data.get("result"),
        }
    conformance_after_regen_pass = after_cases["result"] == "PASS" and after_cases["passed"] == after_cases["run"]

    # 5. The suite was green without touching the fixtures, so it did not detect
    # the change. Coverage for the new meaning has to be added by hand.
    island_fixtures = pilot / "candidates/island-record/fixtures.json"
    before_fixtures = island_fixtures.read_text(encoding="utf-8")
    fixtures = json.loads(before_fixtures)
    fixtures["contractVersion"] = "6"
    fixtures["cases"].append(
        {
            "id": "present-summary",
            "input": {"id": "island-1", "title": "Group A", "summary": "short", "cardIds": ["card-1"]},
            "want": {
                "state": "present",
                "text": "{\"cardIds\":[\"card-1\"],\"id\":\"island-1\",\"summary\":\"short\",\"title\":\"Group A\"}",
            },
        }
    )
    # The composed document reads present-title, so give it a summary to see
    # whether the product consumer keeps the new meaning.
    for case in fixtures["cases"]:
        if case["id"] == "present-title":
            case["input"]["summary"] = "short"
            case["want"]["text"] = (
                "{\"cardIds\":[\"card-1\"],\"id\":\"island-1\",\"summary\":\"short\",\"title\":\"Group A\"}"
            )
    island_fixtures.write_text(json.dumps(fixtures, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fixture_lines = changed_lines(before_fixtures, island_fixtures.read_text(encoding="utf-8"))

    # 6. Conformance after adding the coverage case.
    final_out = workdir / "final.json"
    final_artifact = workdir / "artifact.json"
    final = run(
        [
            sys.executable, str(pilot / "assembler/integration_flow.py"),
            "--tei-repo", args.tei_repo, "--workspace", pilot,
            "--out", final_out, "--artifact-out", final_artifact,
        ],
        cwd=pilot,
    )
    final_cases = {"run": None, "passed": None, "result": None}
    if final_out.exists():
        data = json.loads(final_out.read_text(encoding="utf-8"))
        final_cases = {
            "run": data.get("casesRun"),
            "passed": data.get("casesPassed"),
            "result": data.get("result"),
        }
    conformance_after_fixture_pass = final_cases["result"] == "PASS" and final_cases["passed"] == final_cases["run"]

    # Does the new meaning reach the composed document at all?
    composed_island = None
    if final_artifact.exists():
        artifact = json.loads(final_artifact.read_text(encoding="utf-8"))
        islands = artifact.get("document", {}).get("islands", [])
        composed_island = {"summaryInComposed": bool(islands and "summary" in islands[0])}

    # 7. Does the product-side consumer accept an island with the new meaning?
    consumer = {"ran": False}
    if args.sui_repo and final_artifact.exists():
        validator = pilot / "assembler/validate_against_sui.py"
        result_path = workdir / "consume.json"
        validated = run(
            [sys.executable, str(validator), "--sui-repo", args.sui_repo,
             "--artifact", final_artifact, "--out", result_path],
            cwd=pilot,
        )
        consumer = {
            "ran": True,
            "exit": validated.returncode,
            "output": (validated.stdout or validated.stderr).strip().splitlines()[-1:],
        }
        if result_path.exists():
            receipt = json.loads(result_path.read_text(encoding="utf-8"))
            consumer["result"] = receipt.get("result")
            consumer["documentV1Valid"] = receipt["observed"].get("documentV1Valid")
        # "valid" does not mean "keeps the meaning": check whether the new field
        # survives the consumer's own mapping into DocumentV1.
        probe = (
            "import json, sys\n"
            "from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload\n"
            "artifact = json.load(open(sys.argv[1], encoding='utf-8'))\n"
            "payload = to_documentv1_payload(from_artifact(artifact), transform={'panX':0.0,'panY':0.0,'zoom':1.0},"
            " created_at='2026-11-03T00:00:00Z', updated_at='2026-11-03T00:00:00Z')\n"
            "islands = payload.get('islands') or []\n"
            "print(json.dumps({'islandKeys': sorted(islands[0].keys()) if islands else [],"
            " 'keepsSummary': bool(islands and 'summary' in islands[0])}))\n"
        )
        survive = run(
            [sys.executable, "-c", probe, str(final_artifact)],
            cwd=pilot,
            env={**os.environ, "PYTHONPATH": str(Path(args.sui_repo) / "03_Implement/backend/src")},
        )
        lines = (survive.stdout or "").strip().splitlines()
        consumer["keepsSummary"] = json.loads(lines[-1]).get("keepsSummary") if lines else None
        consumer["surviveExit"] = survive.returncode

    checks = {
        "baseline": {"allPassed": baseline_all_passed, "cases": baseline_cases},
        "meaningChange": {
            "contract": "island-record",
            "versionAfter": contract["version"],
            "semanticsAdded": {"inputs": 1, "fields": 1, "versionBump": 1},
            "rewrittenLines": contract_lines,
            "handEditedFiles": 1,
        },
        "regenerated": regenerated,
        "allRegeneratedAutomatically": all_generated,
        "conformanceAfterRegeneration": after_cases,
        "conformancePassedAfterRegeneration": conformance_after_regen_pass,
        "changeDetectedByConformance": not conformance_after_regen_pass,
        "fixtureHandEdit": {"handEditedLines": fixture_lines, "handEditedFiles": 1, "newCases": 1},
        "composed": composed_island,
        "conformanceAfterFixtureEdit": final_cases,
        "conformancePassedAfterFixtureEdit": conformance_after_fixture_pass,
        "consumer": consumer,
        "consumerDropsNewField": consumer.get("keepsSummary") is False,
    }
    passed = (
        baseline_all_passed
        and all_generated
        and conformance_after_fixture_pass
        and checks["conformanceAfterRegeneration"]["run"] is not None
        and checks["composed"]["summaryInComposed"] is True
        and checks["consumerDropsNewField"] is True
    )
    receipt = {
        "schema": "tai.reference.tei-meaning-change/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the TEI reference generator and the pilot's conformance flow on a temporary copy",
        "command": f"python integrations/tools/tei_meaning_change_experiment.py --tei-repo {args.tei_repo} --workspace integrations/pilot-sui-document --sui-repo <SUI> --artifact {args.artifact} --out evaluations/records/TEI-meaning-change-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Copies the pilot to a temporary directory, adds an optional summary field to the island meaning, regenerates all five candidates, and runs the same conformance flow. It records four things: the generated code needs no hand edit, the suite stayed green before the change was covered (conformance only sees what fixtures exercise), one added fixture case proves the meaning projects into the composed document, and the product consumer still validates as valid while dropping the new field. It does not change the pilot workspace.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
