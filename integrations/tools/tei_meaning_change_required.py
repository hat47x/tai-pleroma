"""Second meaning-change run: add a required field instead of an optional one.

The first run added an optional field, which cost one coverage case. A required
field is the harder shape: every case that expects a present record now lacks it.
This run measures that cost, and also checks the ordering rule from the stage-5
plan -- the coverage check must fail before the fixtures are extended.
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
        return {"result": None, "casesRun": None, "casesPassed": None, "tail": (completed.stderr or "").strip().splitlines()[-1:]}
    data = json.loads(Path(out).read_text(encoding="utf-8"))
    return {
        "result": data.get("result"),
        "casesRun": data.get("casesRun"),
        "casesPassed": data.get("casesPassed"),
    }


def coverage(pilot, out, digest_target):
    completed = run(
        [
            sys.executable, str(pilot.parent / "coverage_tool.py"),
            "--workspace", pilot, "--artifact", digest_target, "--out", out,
        ],
        cwd=pilot,
    )
    if not Path(out).exists():
        return {"passed": None, "uncoveredRequired": None, "tail": (completed.stderr or "").strip().splitlines()[-1:]}
    data = json.loads(Path(out).read_text(encoding="utf-8"))
    observed = data.get("observed", {})
    return {
        "passed": data.get("result") == "PASS",
        "uncoveredRequired": observed.get("uncoveredRequiredFields"),
        "uncoveredOptional": observed.get("uncoveredOptionalFields"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--sui-repo", default="")
    parser.add_argument("--coverage-tool", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(args.workspace).resolve()
    # The coverage tool runs with the copied pilot as its cwd, so the artifact
    # it digests must be absolute.
    artifact_path = str(Path(args.artifact).resolve())
    workdir = Path(tempfile.mkdtemp(prefix="tei-meaning2-", dir=os.environ.get("GOTMPDIR") or None))
    pilot = workdir / "pilot"
    shutil.copytree(root, pilot)
    # The coverage tool is run against the copy, so keep a copy of it beside the pilot.
    shutil.copy2(args.coverage_tool, workdir / "coverage_tool.py")

    baseline = flow(pilot, args.tei_repo, workdir / "baseline.json")

    # The meaning change: card gains a required revision.
    card_contract = pilot / "candidates/card-record/contract.json"
    before_contract = card_contract.read_text(encoding="utf-8")
    contract = json.loads(before_contract)
    contract["version"] = "9"
    contract["inputs"].append({"attribute": "sui.card.revision", "primitive": "std.integer"})
    contract["projection"]["fields"].append(
        {
            "name": "revision",
            "input": "revision",
            "attribute": "sui.card.revision",
            "primitive": "std.integer",
        }
    )
    card_contract.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    contract_lines = changed_lines(before_contract, card_contract.read_text(encoding="utf-8"))

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
        regenerated[name] = {"exit": built.returncode, "generated": (out_dir / "main.go").exists()}
    all_generated = all(item["generated"] for item in regenerated.values())

    # Ordering rule: the coverage check must fail before the fixtures are extended.
    coverage_before = coverage(pilot, workdir / "coverage-before.json", artifact_path)
    conformance_before = flow(pilot, args.tei_repo, workdir / "before.json")

    # Extend every case that expects a present record, plus one absence case.
    card_fixtures = pilot / "candidates/card-record/fixtures.json"
    before_fixtures = card_fixtures.read_text(encoding="utf-8")
    fixtures = json.loads(before_fixtures)
    fixtures["contractVersion"] = "9"
    touched = 0
    for case in fixtures["cases"]:
        want = case.get("want", {})
        if want.get("state") != "present":
            continue
        case["input"]["revision"] = 7
        expected = json.loads(want["text"])
        expected["revision"] = 7
        want["text"] = json.dumps(expected, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        touched += 1
    for case in fixtures["cases"]:
        # Keep the existing missing-text case about text alone.
        if case["id"] == "missing-text":
            case["input"]["revision"] = 7
    fixtures["cases"].append(
        {"id": "missing-revision", "input": {"id": "card-1", "text": "a", "x": 1, "y": 2}, "want": {"state": "missing", "text": "[\"revision\"]"}}
    )
    card_fixtures.write_text(json.dumps(fixtures, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fixture_lines = changed_lines(before_fixtures, card_fixtures.read_text(encoding="utf-8"))

    coverage_after = coverage(pilot, workdir / "coverage-after.json", artifact_path)
    conformance_after = flow(pilot, args.tei_repo, workdir / "after.json", workdir / "artifact.json")

    # Does the product consumer keep a field it does not know?
    consumer = {"ran": False}
    if args.sui_repo and (workdir / "artifact.json").exists():
        probe = (
            "import json, sys\n"
            "from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload\n"
            "from sui_sensemaking_api.models import DocumentV1\n"
            "a = json.load(open(sys.argv[1], encoding='utf-8'))\n"
            "p = to_documentv1_payload(from_artifact(a), transform={'panX':0.0,'panY':0.0,'zoom':1.0},"
            " created_at='2026-11-03T00:00:00Z', updated_at='2026-11-03T00:00:00Z')\n"
            "m = DocumentV1.model_validate(p)\n"
            "cards = p.get('cards') or []\n"
            "print(json.dumps({'valid': True, 'cardKeys': sorted(cards[0].keys()) if cards else [],"
            " 'keepsRevision': bool(cards and 'revision' in cards[0])}))\n"
        )
        completed = subprocess.run(
            [sys.executable, "-c", probe, str(workdir / "artifact.json")],
            env={**os.environ, "PYTHONPATH": str(Path(args.sui_repo) / "03_Implement/backend/src")},
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        lines = (completed.stdout or "").strip().splitlines()
        consumer = {"ran": True, "exit": completed.returncode}
        if lines:
            parsed = json.loads(lines[-1])
            consumer.update({"valid": parsed["valid"], "keepsRevision": parsed["keepsRevision"], "cardKeys": parsed["cardKeys"]})

    checks = {
        "baseline": baseline,
        "meaningChange": {
            "contract": "card-record",
            "versionAfter": contract["version"],
            "semanticsAdded": {"inputs": 1, "fields": 1, "versionBump": 1, "required": True},
            "rewrittenLines": contract_lines,
            "handEditedFiles": 1,
        },
        "regenerated": regenerated,
        "allRegeneratedAutomatically": all_generated,
        "coverageBeforeFixtureEdit": coverage_before,
        "coverageFailedBeforeFixtureEdit": coverage_before.get("passed") is False,
        "coverageNamesTheField": any(
            name.endswith(".revision") for name in (coverage_before.get("uncoveredRequired") or [])
        ),
        "conformanceBeforeFixtureEdit": conformance_before,
        "conformanceBrokeBeforeFixtureEdit": conformance_before.get("result") is None,
        "fixtureHandEdit": {"touchedCases": touched, "newCases": 1, "rewrittenLines": fixture_lines, "handEditedFiles": 1},
        "coverageAfterFixtureEdit": coverage_after,
        "coveragePassedAfterFixtureEdit": coverage_after.get("passed") is True,
        "conformanceAfterFixtureEdit": conformance_after,
        "conformancePassedAfterFixtureEdit": conformance_after.get("result") == "PASS"
        and conformance_after.get("casesPassed") == conformance_after.get("casesRun"),
        "consumer": consumer,
        "consumerDropsRequiredField": consumer.get("keepsRevision") is False,
    }
    passed = (
        baseline.get("result") == "PASS"
        and all_generated
        and checks["coverageFailedBeforeFixtureEdit"]
        and checks["coverageNamesTheField"]
        and checks["coveragePassedAfterFixtureEdit"]
        and checks["conformancePassedAfterFixtureEdit"]
        and checks["consumerDropsRequiredField"]
    )
    receipt = {
        "schema": "tai.reference.tei-meaning-change-required/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the TEI reference generator and the pilot's conformance flow on a temporary copy",
        "command": f"python integrations/tools/tei_meaning_change_required.py --tei-repo {args.tei_repo} --workspace integrations/pilot-sui-document --coverage-tool integrations/tools/fixture_field_coverage_check.py --sui-repo <SUI> --artifact {args.artifact} --out evaluations/records/TEI-meaning-change-required-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(artifact_path)},
        "observed": checks,
        "scope": "Copies the pilot, adds a required revision to the card meaning, regenerates all five candidates, then measures the coverage check, the conformance flow, and the hand edits needed. It records that a required addition costs an edit in every present case instead of one added case, and that the product consumer still validates while dropping the field. It does not change the pilot workspace.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: checks[key] for key in (
        "allRegeneratedAutomatically",
        "coverageFailedBeforeFixtureEdit",
        "coverageNamesTheField",
        "coveragePassedAfterFixtureEdit",
        "conformancePassedAfterFixtureEdit",
        "consumerDropsRequiredField",
    )}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
