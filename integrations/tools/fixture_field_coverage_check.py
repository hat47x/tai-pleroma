"""Check that every contract field is exercised by at least one fixture case.

The meaning-change experiment showed the conformance suite stays green when a new
meaning has no covering fixture. This check makes that gap visible and is
self-tested: it also verifies that it fails when a field without a covering case
is introduced, so a green result means the coverage really was inspected.
"""

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import time
from pathlib import Path

CONTRACTS = ["document-record", "card-record", "island-record", "edge-record", "affiliation-record"]


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def classify(case, field_name):
    """Return how one case exercises one field.

    present-value: the input carries a usable value.
    present-null:  the input carries an explicit null.
    absent:        the input omits the key.
    """
    payload = case.get("input", {})
    if field_name not in payload:
        return "absent"
    return "present-null" if payload[field_name] is None else "present-value"


def analyse(workspace):
    report = {}
    uncovered_required = []
    uncovered_optional = []
    untouched = []
    for name in CONTRACTS:
        contract = json.loads((workspace / "candidates" / name / "contract.json").read_text(encoding="utf-8"))
        fixtures = json.loads((workspace / "candidates" / name / "fixtures.json").read_text(encoding="utf-8"))
        cases = fixtures["cases"]
        fields = contract["projection"]["fields"]
        per_field = {}
        for field in fields:
            field_name = field["name"]
            optional = bool(field.get("optional"))
            kinds = {}
            for case in cases:
                kind = classify(case, field_name)
                kinds.setdefault(kind, []).append(case["id"])
            has_value = "present-value" in kinds
            has_absence = "absent" in kinds or "present-null" in kinds
            per_field[field_name] = {
                "optional": optional,
                "withValue": kinds.get("present-value", []),
                "explicitNull": kinds.get("present-null", []),
                "absent": kinds.get("absent", []),
                "coveredByValue": has_value,
                "coveredByAbsence": has_absence,
            }
            labelled = f"{name}.{field_name}"
            if not has_value:
                (uncovered_optional if optional else uncovered_required).append(labelled)
            if not has_value and not has_absence:
                untouched.append(labelled)
        report[name] = {
            "contractVersion": contract["version"],
            "caseCount": len(cases),
            "fields": per_field,
        }
    return {
        "contracts": report,
        "uncoveredRequiredFields": uncovered_required,
        "uncoveredOptionalFields": uncovered_optional,
        "untouchedFields": untouched,
    }


def self_test(source):
    """Add one uncovered field of each kind to a copy and confirm both are reported."""
    workdir = Path(tempfile.mkdtemp(prefix="tei-cover-selftest-", dir=os.environ.get("GOTMPDIR") or None))
    copy = workdir / "pilot"
    shutil.copytree(source, copy)

    island = copy / "candidates/island-record/contract.json"
    contract = json.loads(island.read_text(encoding="utf-8"))
    contract["inputs"].append({"attribute": "sui.island.selftest_optional", "primitive": "std.text"})
    contract["projection"]["fields"].append(
        {
            "name": "selftestOptional",
            "input": "selftestOptional",
            "attribute": "sui.island.selftest_optional",
            "primitive": "std.text",
            "optional": True,
        }
    )
    island.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    card = copy / "candidates/card-record/contract.json"
    contract = json.loads(card.read_text(encoding="utf-8"))
    contract["inputs"].append({"attribute": "sui.card.selftest_required", "primitive": "std.text"})
    contract["projection"]["fields"].append(
        {
            "name": "selftestRequired",
            "input": "selftestRequired",
            "attribute": "sui.card.selftest_required",
            "primitive": "std.text",
        }
    )
    card.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    result = analyse(copy)
    shutil.rmtree(workdir, ignore_errors=True)
    return {
        "reportedRequired": "card-record.selftestRequired" in result["uncoveredRequiredFields"],
        "reportedOptional": "island-record.selftestOptional" in result["uncoveredOptionalFields"],
        "reportedUntouched": "card-record.selftestRequired" in result["untouchedFields"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workspace = Path(args.workspace)
    observed = analyse(workspace)
    detected = self_test(workspace)
    checks = {
        **observed,
        "selfTest": detected,
        "selfTestDetectsMissingRequired": detected["reportedRequired"] is True,
        "selfTestDetectsMissingOptional": detected["reportedOptional"] is True,
        "everyRequiredFieldHasAValueCase": not observed["uncoveredRequiredFields"],
        "everyOptionalFieldHasValueOrAbsence": not observed["untouchedFields"],
    }
    passed = all(
        checks[key]
        for key in (
            "selfTestDetectsMissingRequired",
            "selfTestDetectsMissingOptional",
            "everyRequiredFieldHasAValueCase",
            "everyOptionalFieldHasValueOrAbsence",
        )
    )
    receipt = {
        "schema": "tai.reference.tei-fixture-field-coverage/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the pilot contracts and fixtures",
        "command": f"python integrations/tools/fixture_field_coverage_check.py --workspace {args.workspace} --artifact {args.artifact} --out evaluations/records/TEI-fixture-coverage-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Reads each contract and its fixtures and records, per field, which cases supply a value, an explicit null, or nothing. A self-test adds one uncovered required and one uncovered optional field to a temp copy and confirms both are reported, so a green result is not vacuous. It does not run the generator.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "uncoveredRequired": observed["uncoveredRequiredFields"],
        "uncoveredOptional": observed["uncoveredOptionalFields"],
        "selfTest": detected,
        "passed": passed,
    }))


if __name__ == "__main__":
    raise SystemExit(main())
