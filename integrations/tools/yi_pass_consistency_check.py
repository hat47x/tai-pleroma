"""Check that a PASS receipt's own observations do not contradict its verdict.

A receipt whose result is PASS while one of its own invariant fields is false is
the "green but wrong" shape: the verdict says the measurement succeeded, and the
observed data says a gap exists. Both can be legitimate -- a measurement of a
gap legitimately passes -- but then the receipt must say which is which, or a
reader will take PASS as "no gap".
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

HISTORICAL = {"yi-constellation-structure-2026-11-01.json"}
# Observation keys that read as "all of X is in order".
INVARIANT = re.compile(r"^(every|all|no[A-Z]|keptPlusMoved)")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    own = Path(args.out).name
    records = root / "evaluations/records"
    names = sorted(
        {
            path.name
            for path in records.glob("*.json")
            if path.name.lower().startswith(("yi-", "yi_"))
            and path.name not in HISTORICAL
            and path.name != own
        }
    )

    rows = []
    unexplained = []
    for name in names:
        data = json.loads((records / name).read_text(encoding="utf-8"))
        observed = data.get("observed") or {}
        failed = [
            key for key, value in observed.items()
            if INVARIANT.match(key) and value is False
        ]
        # A receipt that reports a gap should say so in a finding or by listing
        # what is missing, so PASS is not read as "nothing is missing".
        explains = "finding" in observed or any(
            key.lower().startswith(("missing", "without", "unexpect", "gap"))
            and isinstance(value, list) and value
            for key, value in observed.items()
        )
        rows.append({
            "receipt": name,
            "result": data.get("result"),
            "failedInvariants": failed,
            "explainsTheGap": explains,
            "consistent": (not failed) or explains,
        })
        if failed and not explains:
            unexplained.append({"receipt": name, "failed": failed})

    checks = {
        "receipts": len(names),
        "rows": rows,
        "unexplainedPassWithGap": unexplained,
        "everyPassExplainsItsGaps": not unexplained,
    }
    passed = not unexplained

    receipt = {
        "schema": "tai.reference.yi-pass-consistency/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading evaluations/records",
        "command": "python integrations/tools/yi_pass_consistency_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-pass-consistency-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "For each YI receipt that reports PASS, looks for an invariant field observed as false and records whether the receipt also explains the gap, either in a finding or in a list of what is missing. It checks the receipt's own bookkeeping, not the world: a receipt that explains its gap can still have measured the wrong thing.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipts": len(names),
        "unexplained": unexplained,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
