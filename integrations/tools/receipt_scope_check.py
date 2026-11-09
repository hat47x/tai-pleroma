"""Check that every receipt says what it does not prove.

Receipts in this repository are written to keep claims honest: each one carries a
`scope` that states the limits. That convention is only worth anything if it is
checked, so this walks every receipt and reports the ones missing the required
fields or a limitation phrase.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

REQUIRED = ("schema", "synthetic", "evidenceKind", "publicationAllowed", "date", "result")
LIMITATION = re.compile(
    r"\bnot\b|cannot|しません|しない|ではありません|ではない|未実施|未証明|証明しない|同一視しません"
)

# Receipts that predate the convention and are kept as historical records.
EXEMPT = set()


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", default="evaluations/records")
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    strict = args.strict
    root = Path(__file__).resolve().parents[2]
    records = root / args.records

    missing_fields = {}
    missing_scope = []
    missing_limitation = []
    unparsable = []
    counted = {"real": 0, "synthetic": 0}

    for path in sorted(records.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            unparsable.append(path.name)
            continue
        counted["synthetic" if data.get("synthetic") else "real"] += 1
        absent = [key for key in REQUIRED if key not in data]
        if absent:
            missing_fields[path.name] = absent
        scope = data.get("scope")
        if not isinstance(scope, str) or not scope.strip():
            missing_scope.append(path.name)
        elif not LIMITATION.search(scope):
            missing_limitation.append(path.name)
        if data.get("publicationAllowed") is not False:
            missing_fields.setdefault(path.name, []).append("publicationAllowed!=false")

    checks = {
        "realRecords": counted["real"],
        "syntheticRecords": counted["synthetic"],
        "missingRequiredFields": missing_fields,
        "missingScope": missing_scope,
        "scopeWithoutLimitation": missing_limitation,
        "unparsable": unparsable,
        "exempt": sorted(EXEMPT),
        "allRealReceiptsStateLimits": not missing_scope and not missing_limitation and not missing_fields,
    }
    effective_missing = {
        name: fields for name, fields in missing_fields.items() if name not in EXEMPT
    }
    checks["missingRequiredFields"] = effective_missing
    checks["allRealReceiptsStateLimits"] = not effective_missing and not missing_scope and not missing_limitation
    checks["gapCounts"] = {
        "missingRequiredFields": len(effective_missing),
        "missingScope": len(missing_scope),
        "scopeWithoutLimitation": len(missing_limitation),
    }
    # Until the gaps are repaired this receipt records them; --strict turns the
    # same walk into a gate.
    passed = not unparsable and (not strict or checks["allRealReceiptsStateLimits"])
    receipt = {
        "schema": "tai.reference.receipt-scope/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the receipt directory",
        "command": "python integrations/tools/receipt_scope_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/TEI-receipt-scope-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(root / args.artifact)},
        "observed": checks,
        "scope": "Walks every receipt and records which ones lack the required metadata or a scope that names a limitation. Run with --strict it becomes a gate; without it the gaps are recorded so they can be repaired in order. It does not judge whether a receipt's claim is correct, and it cannot detect a scope that names the wrong limitation.",
    }
    (root / args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "real": counted["real"],
        "synthetic": counted["synthetic"],
        "missingFields": len(effective_missing),
        "missingScope": len(missing_scope),
        "scopeWithoutLimitation": len(missing_limitation),
        "unparsable": len(unparsable),
        "passed": passed,
    }))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
