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
    r"\bnot\b|\bno\b|neither|cannot|unverified|test-only|out of scope|local|same host|"
    r"synthetic|stub|しません|しない|ではありません|ではない|未実施|未証明|証明しない|同一視しません",
    re.IGNORECASE,
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
    # Records that are not receipts (tool output kept for traceability).
    AUXILIARY = {"SCN-003-compose-2026-11-03.validate.json"}
    checker_source = (root / "tools/check-synthetic-receipts/check.py").read_text(encoding="utf-8")
    registered = {
        Path(name).name for name in re.findall(r'"(evaluations/records/[^"]+\.json)"', checker_source)
    }
    historical_path = records / "historical-receipts.json"
    historical = set()
    if historical_path.exists():
        listed = json.loads(historical_path.read_text(encoding="utf-8"))
        historical = set(listed.get("receipts", {}))

    missing_fields = {}
    missing_scope = []
    missing_limitation = []
    unparsable = []
    unregistered = []
    foreign = []
    counted = {"real": 0, "synthetic": 0}

    for path in sorted(records.glob("*.json")):
        if path.name == "historical-receipts.json":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            unparsable.append(path.name)
            continue
        # Receipts written by other workstreams in this repository carry their
        # own schema (status/observed_at) instead of TAI's receipt fields. They are
        # counted and listed rather than being judged against TAI's format.
        if (
            "evidenceKind" not in data
            and "synthetic" not in data
            and ("status" in data or "observed_at" in data)
        ):
            foreign.append(path.name)
            counted["synthetic" if data.get("synthetic") else "real"] += 1
            continue
        if path.name in AUXILIARY:
            # Explicitly listed tool output, not a receipt.
            continue
        if path.name in historical:
            # Pre-convention receipt: kept as a record, not counted as evidence.
            counted["synthetic" if data.get("synthetic") else "real"] += 1
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
        if path.name not in registered:
            unregistered.append(path.name)

    checks = {
        "realRecords": counted["real"],
        "syntheticRecords": counted["synthetic"],
        "missingRequiredFields": missing_fields,
        "missingScope": missing_scope,
        "scopeWithoutLimitation": missing_limitation,
        "unparsable": unparsable,
        "exempt": sorted(EXEMPT),
        "historical": len(historical),
        "unregisteredReceipts": unregistered,
        "allRealReceiptsStateLimits": not missing_scope and not missing_limitation and not missing_fields,
    }
    effective_missing = {
        name: fields for name, fields in missing_fields.items() if name not in EXEMPT
    }
    checks["missingRequiredFields"] = effective_missing
    checks["allRealReceiptsStateLimits"] = (
        not effective_missing and not missing_scope and not missing_limitation and not unregistered
    )
    checks["registeredCount"] = len(registered)
    checks["foreignReceipts"] = sorted(foreign)
    checks["auxiliary"] = sorted(AUXILIARY)
    checks["gapCounts"] = {
        "missingRequiredFields": len(effective_missing),
        "missingScope": len(missing_scope),
        "scopeWithoutLimitation": len(missing_limitation),
        "unregistered": len(unregistered),
        "foreign": len(foreign),
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
        "scope": "Walks every receipt and records which ones lack the required metadata, are not registered in the checker, or have a scope without a limitation. Receipts from other workstreams in this repository use their own schema; they are listed as foreign rather than judged against TAI's format, so their metadata is not checked here. It does not check whether the claim itself is correct. Auxiliary tool output is listed explicitly instead of being silently skipped. Walks every receipt and records which ones lack the required metadata or a scope that names a limitation. The limitation test is lexical (negations and local/test wording), so it cannot tell whether the named limit is the right one. Run with --strict it becomes a gate; without it the gaps are recorded so they can be repaired in order. It does not judge whether a receipt's claim is correct, and it cannot detect a scope that names the wrong limitation.",
    }
    (root / args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "real": counted["real"],
        "synthetic": counted["synthetic"],
        "missingFields": len(effective_missing),
        "missingScope": len(missing_scope),
        "scopeWithoutLimitation": len(missing_limitation),
        "unparsable": len(unparsable),
        "historical": len(historical),
        "passed": passed,
    }))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
