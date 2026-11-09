"""Third meaning change: make an existing optional field required.

The first two changes added a field. This one changes the requiredness of a field
that already exists, so the set of fields stays the same. That makes it the case
where the product's hand-written mapping needs no follow-up, and it tests whether
the conformance suite sees the change without new coverage.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tei_meaning_change_experiment import changed_lines, digest, run  # noqa: E402

CONTRACTS = ["document-record", "card-record", "island-record", "edge-record", "affiliation-record"]


def flow(pilot, tei_repo, out, artifact_out=None):
    args = [
        sys.executable, str(pilot / "assembler/integration_flow.py"),
        "--tei-repo", tei_repo, "--workspace", pilot, "--out", out,
    ]
    if artifact_out:
        args += ["--artifact-out", artifact_out]
    completed = run(args, cwd=pilot)
    if not Path(out).exists():
        return {"result": None, "casesRun": None, "casesPassed": None,
                "tail": (completed.stderr or "").strip().splitlines()[-1:]}
    data = json.loads(Path(out).read_text(encoding="utf-8"))
    return {"result": data.get("result"), "casesRun": data.get("casesRun"), "casesPassed": data.get("casesPassed")}


def consumer_keys(artifact, sui_repo):
    probe = (
        "import json, sys\n"
        "from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload\n"
        "from sui_sensemaking_api.models import DocumentV1\n"
        "a = json.load(open(sys.argv[1], encoding='utf-8'))\n"
        "p = to_documentv1_payload(from_artifact(a), transform={'panX':0.0,'panY':0.0,'zoom':1.0},"
        " created_at='2026-11-03T00:00:00Z', updated_at='2026-11-03T00:00:00Z')\n"
        "DocumentV1.model_validate(p)\n"
        "islands = p.get('islands') or []\n"
        "print(json.dumps({'islandKeys': sorted(islands[0].keys()) if islands else []}))\n"
    )
    completed = subprocess.run(
        [sys.executable, "-c", probe, str(artifact)],
        env={**os.environ, "PYTHONPATH": str(Path(sui_repo) / "03_Implement/backend/src")},
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    lines = (completed.stdout or "").strip().splitlines()
    if not lines:
        return {"exit": completed.returncode, "islandKeys": None}
    return {"exit": completed.returncode, "islandKeys": json.loads(lines[-1])["islandKeys"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--sui-repo", default="")
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(args.workspace).resolve()
    artifact_path = str(Path(args.artifact).resolve())
    workdir = Path(tempfile.mkdtemp(prefix="tei-meaning3-", dir=os.environ.get("GOTMPDIR") or None))
    pilot = workdir / "pilot"
    shutil.copytree(root, pilot)

    baseline = flow(pilot, args.tei_repo, workdir / "baseline.json", workdir / "baseline-artifact.json")
    baseline_keys = consumer_keys(workdir / "baseline-artifact.json", args.sui_repo) if args.sui_repo else {}

    # The meaning change: island.title stops being optional. No field is added.
    island = pilot / "candidates/island-record/contract.json"
    before_contract = island.read_text(encoding="utf-8")
    contract = json.loads(before_contract)
    contract["version"] = "6"
    for field in contract["projection"]["fields"]:
        if field["name"] == "title":
            field.pop("optional", None)
    island.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    contract_lines = changed_lines(before_contract, island.read_text(encoding="utf-8"))
    field_count_before = len(json.loads(before_contract)["projection"]["fields"])
    field_count_after = len(contract["projection"]["fields"])

    regenerated = {}
    for name in CONTRACTS:
        built = run(
            [
                "go", "run", "./tools/reference-generator-selection/cmd/tei-generator-build",
                "-contract", pilot / "candidates" / name / "contract.json",
                "-strategy", "text-record-template", "-out", workdir / "gen" / name,
            ],
            cwd=args.tei_repo,
        )
        regenerated[name] = {"exit": built.returncode, "generated": (workdir / "gen" / name / "main.go").exists()}
    all_generated = all(item["generated"] for item in regenerated.values())

    # No coverage is added first, so this shows whether the suite sees the change.
    conformance_before = flow(pilot, args.tei_repo, workdir / "before.json", workdir / "before-artifact.json")

    island_fixtures = pilot / "candidates/island-record/fixtures.json"
    before_fixtures = island_fixtures.read_text(encoding="utf-8")
    fixtures = json.loads(before_fixtures)
    fixtures["contractVersion"] = "6"
    edited = 0
    for case in fixtures["cases"]:
        if case["id"] == "present-no-title":
            case["want"] = {"state": "missing", "text": "[\"title\"]"}
            edited += 1
    island_fixtures.write_text(json.dumps(fixtures, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fixture_lines = changed_lines(before_fixtures, island_fixtures.read_text(encoding="utf-8"))

    conformance_after = flow(pilot, args.tei_repo, workdir / "after.json", workdir / "after-artifact.json")
    after_keys = consumer_keys(workdir / "after-artifact.json", args.sui_repo) if args.sui_repo else {}

    checks = {
        "baseline": baseline,
        "meaningChange": {
            "contract": "island-record",
            "kind": "optional-to-required",
            "versionAfter": contract["version"],
            "fieldsBefore": field_count_before,
            "fieldsAfter": field_count_after,
            "rewrittenLines": contract_lines,
            "handEditedFiles": 1,
        },
        "regenerated": regenerated,
        "allRegeneratedAutomatically": all_generated,
        "conformanceBeforeFixtureEdit": conformance_before,
        "conformanceDetectedTheChange": conformance_before.get("casesPassed")
        != conformance_before.get("casesRun"),
        "fixtureHandEdit": {"editedCases": edited, "newCases": 0, "rewrittenLines": fixture_lines, "handEditedFiles": 1},
        "conformanceAfterFixtureEdit": conformance_after,
        "conformancePassedAfterFixtureEdit": conformance_after.get("result") == "PASS"
        and conformance_after.get("casesPassed") == conformance_after.get("casesRun"),
        "consumer": {"baselineKeys": baseline_keys, "afterKeys": after_keys},
        "consumerMappingUnchanged": baseline_keys.get("islandKeys") == after_keys.get("islandKeys"),
        "noNewFieldAdded": field_count_before == field_count_after,
    }
    passed = (
        baseline.get("result") == "PASS"
        and all_generated
        and checks["conformanceDetectedTheChange"]
        and checks["conformancePassedAfterFixtureEdit"]
        and checks["noNewFieldAdded"]
        and checks["consumerMappingUnchanged"]
    )
    receipt = {
        "schema": "tai.reference.tei-meaning-change-requiredness/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the TEI reference generator and the pilot's conformance flow on a temporary copy",
        "command": f"python integrations/tools/tei_meaning_change_requiredness.py --tei-repo {args.tei_repo} --workspace integrations/pilot-sui-document --sui-repo <SUI> --artifact {args.artifact} --out evaluations/records/TEI-meaning-change-requiredness-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(artifact_path)},
        "observed": checks,
        "scope": "Copies the pilot, makes island.title required instead of optional, regenerates, and runs the same conformance flow before and after editing one case. It records that this change is visible to the suite without new coverage, costs one edited case and no generated-code edit, and needs no consumer mapping change because the field set is unchanged. It does not change the pilot workspace.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(workdir, ignore_errors=True)
    print(json.dumps({key: checks[key] for key in (
        "allRegeneratedAutomatically", "conformanceDetectedTheChange",
        "conformancePassedAfterFixtureEdit", "consumerMappingUnchanged", "noNewFieldAdded",
    )}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
