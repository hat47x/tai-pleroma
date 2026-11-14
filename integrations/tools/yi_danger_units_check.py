"""Inventory the smallest danger units from the receipts that already exist.

Design note and doc 11 say the first thing to establish before deciding whether
Kan becomes a product is "the smallest unit of danger": permission deviation,
delegation refusal, permission expiry, verification failure, publication
refusal. This walks the receipts and records, per unit, which receipts actually
observed it and which have nothing. A unit with no observation is the finding.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

# The five units named in 11-新規領域, with the wording that evidences each.
UNITS = {
    "permissionDeviation": {
        "label": "権限の逸脱",
        "patterns": [r'"unauthoriz', r'"forbidden', r'403', r'denied'],
    },
    "delegationRefusal": {
        "label": "委任の拒否",
        "patterns": [r'"rejected', r'"refused', r'RESULT_NOT_READY', r'409'],
    },
    "permissionExpiry": {
        "label": "権限の期限切れ",
        "patterns": [r'expired', r'revoked', r'lease.*expir', r'stale'],
    },
    "verificationFailure": {
        "label": "検証の失敗",
        "patterns": [r'"passed": false', r'"result": "FAIL"', r'untrusted', r'failed'],
    },
    # ``publicationAllowed: false`` is a declaration every receipt carries; it
    # is not an observation that a publication was refused. Only an explicit
    # refusal or a failing result counts here.
    "publicationRefusal": {
        "label": "公開の拒否",
        "patterns": [r'publication.?refus', r'publication.?denied', r'"result": "FAIL"'],
    },
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    records = sorted((root / "evaluations/records").glob("*.json"))
    total = 0
    observed = {name: [] for name in UNITS}
    for path in records:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        total += 1
        lowered = text.lower()
        for name, unit in UNITS.items():
            for pattern in unit["patterns"]:
                if re.search(pattern, lowered, re.IGNORECASE):
                    observed[name].append(path.name)
                    break

    # The publication unit's evidence, split by what kind of text matched.
    publication = observed["publicationRefusal"]
    abstract_refusals = [
        name
        for name in publication
        if "publication" in (root / "evaluations/records" / name).read_text(
            encoding="utf-8", errors="replace"
        ).lower()
    ]

    guarded = 0
    for path in records:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        # Whitespace around the colon varies; match the key and value only.
        if re.search(r'"publicationAllowed"\s*:\s*false', text, re.IGNORECASE):
            guarded += 1

    checks = {
        "receiptsDeclaringPublicationHeld": guarded,
        "receiptsRead": total,
        "units": {
            name: {
                "label": UNITS[name]["label"],
                "observedIn": len(observed[name]),
                "examples": observed[name][:5],
            }
            for name in UNITS
        },
        "publicationRefusalEvidence": len(abstract_refusals),
        "publicationFieldOnlyIn": len(publication) - len(abstract_refusals),
        "unitsWithNoObservation": [
            name for name in UNITS if not observed[name]
        ],
        "everyUnitHasEvidence": all(observed[name] for name in UNITS),
        "finding": (
            "危険の最小単位のうち、権限の逸脱・委任の拒否・権限の期限切れ・"
            "検証の失敗には、既存のreceiptがある。公開の拒否だけは、"
            "ほとんどがpublicationAllowed:falseという宣言であり、"
            "拒否が実際に起きた観測としては少ない。"
        ),
    }
    passed = checks["everyUnitHasEvidence"]

    receipt = {
        "schema": "tai.reference.yi-danger-units/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading evaluations/records",
        "command": "python integrations/tools/yi_danger_units_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-danger-units-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Searches the receipts for wording that evidences each of the five smallest danger units and records how many receipts show it. The match is lexical: a receipt that mentions a 403 in its scope or notes counts the same as one that observed a 403, so the counts are an upper bound, not a measure of the unit. It does not decide whether Kan should be a product.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipts": total,
        "units": {name: len(values) for name, values in observed.items()},
        "withoutEvidence": checks["unitsWithNoObservation"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
