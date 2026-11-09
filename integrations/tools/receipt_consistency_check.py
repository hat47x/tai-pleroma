"""Check that a PASS receipt does not also report a failed success flag.

A receipt can say `result: PASS` while its own observed values contain a flag
named like a success condition (`passed`, `valid`, `comparisonPassed`, ...) set to
false. That is sometimes the intended finding -- the receipt records a negative
observation -- so those receipts are listed here with the reason. A new one that
is not listed is treated as a mistake.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

# Receipts whose whole point is a negative observation.
EXPECTED_NEGATIVE = {
    "TEI-meaning-change-required-2026-11-06.json": (
        "coverageBeforeFixtureEdit/passed is false on purpose: the receipt records "
        "that the coverage check fails before the fixtures are extended."
    ),
    "TEI-target-profile-compare-2026-11-06.json": (
        "comparisonPassed is false on purpose: the receipt records that the same "
        "contract does not pass on the long-running profile."
    ),
    "TEI-target-profile-compare-text-2026-11-06.json": (
        "comparisonPassed is false on purpose: the text template shows the same "
        "asymmetry as the record template."
    ),
}

SUCCESS_KEYS = {
    "passed", "ok", "valid", "allmatch", "success", "succeeded", "matched",
    "allpassed", "everypassed", "kept", "roundtrip", "identical",
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def walk(node, path, hits):
    if isinstance(node, dict):
        for key, value in node.items():
            lowered = str(key).lower().replace("_", "")
            if lowered in SUCCESS_KEYS or lowered.endswith("passed") or lowered.endswith("valid"):
                if value is False:
                    hits.append("/".join(path + [str(key)]))
            walk(value, path + [str(key)], hits)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            walk(item, path + [str(index)], hits)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    records = root / "evaluations/records"

    checked = 0
    unexpected = {}
    confirmed_negative = {}
    for path in sorted(records.glob("*.json")):
        if path.name == "historical-receipts.json":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if data.get("result") != "PASS":
            continue
        checked += 1
        hits = []
        walk(data.get("observed"), [], hits)
        if not hits:
            continue
        if path.name in EXPECTED_NEGATIVE:
            confirmed_negative[path.name] = hits
        else:
            unexpected[path.name] = hits

    checks = {
        "passReceiptsChecked": checked,
        "expectedNegative": confirmed_negative,
        "unexpected": unexpected,
        "unexpectedCount": len(unexpected),
        "declaredNegativeCount": len(confirmed_negative),
        "everyPassIsConsistent": not unexpected,
    }
    passed = checks["everyPassIsConsistent"]
    receipt = {
        "schema": "tai.reference.receipt-consistency/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the receipt directory",
        "command": "python integrations/tools/receipt_consistency_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/TEI-receipt-consistency-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Walks the PASS receipts and flags a false value under a success-named key. The three receipts where that is the finding are listed with the reason, so a green result means no undeclared contradiction, not that every claim was independently verified. It does not check the claims themselves.",
    }
    (records / Path(args.out).name).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "checked": checked,
        "unexpected": unexpected,
        "declaredNegative": sorted(confirmed_negative),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
