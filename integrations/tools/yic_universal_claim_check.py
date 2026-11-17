"""Check that a "every X is true" receipt also says how many X it examined.

A verdict like `everyClaimIsPinnedByAPassingTest: true` is worthless without the
population: true over 3 items and true over 300 are different findings. The receipts
written for the YI probes mostly record both, but not all. This reports receipts that
state an "every …" verdict with no integer count anywhere in their observed data, so
a reader can see which claims rest on an unstated number.

This is a disclosure check only. A receipt with a count can still have counted the
wrong thing, and a receipt without one may describe a single object truthfully.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

RECORDS = "evaluations/records"
PREFIXES = ("YI-", "YIC-")
# Keys whose name starts like this assert a universal claim over a population.
UNIVERSAL_PREFIXES = ("every", "all", "no")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def counts_and_universals(observed):
    """Population sizes stated as integers or as list lengths, plus universal claims."""
    counts = {}
    universals = {}
    for key, value in observed.items():
        name = str(key).lower()
        if isinstance(value, bool) and name.startswith(UNIVERSAL_PREFIXES):
            universals[key] = value
        elif isinstance(value, int):
            counts[key] = value
        elif isinstance(value, list):
            # A list of the examined items is a population statement.
            counts[f"{key}[]"] = len(value)
        elif isinstance(value, dict):
            for inner_key, inner_value in value.items():
                if isinstance(inner_value, bool) and str(inner_key).lower().startswith(UNIVERSAL_PREFIXES):
                    universals[f"{key}.{inner_key}"] = inner_value
    return counts, universals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    folder = root / RECORDS
    own = Path(args.out).name

    rows = []
    for path in sorted(folder.glob("*.json")):
        if path.name == own:
            continue
        if not path.name.startswith(PREFIXES):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        observed = data.get("observed") or {}
        if not isinstance(observed, dict):
            continue
        counts, universals = counts_and_universals(observed)
        if not universals:
            continue
        rows.append({
            "receipt": path.name,
            "result": data.get("result"),
            "universalClaims": sorted(universals),
            "counts": counts,
            "populationStatements": counts,
            "statesAPopulationSize": bool(counts),
        })

    withoutCount = [
        {"receipt": row["receipt"], "claims": row["universalClaims"]}
        for row in rows if not row["statesAPopulationSize"]
    ]

    checks = {
        "folder": RECORDS,
        "receiptsScanned": len([
            name for name in folder.glob("*.json")
            if name.name.startswith(PREFIXES) and name.name != own
        ]),
        "receiptsWithUniversalClaims": len(rows),
        "receiptsWithoutACount": withoutCount,
        "withoutCountTotal": len(withoutCount),
        "everyUniversalClaimStatesItsPopulation": not withoutCount,
        "rows": rows,
        "finding": (
            "「すべてのXが…」という判定を持つreceiptが、"
            "検査した対象の個数を記録しているかを点検する。"
            "個数が無いreceiptは、3件を見たのか300件を見たのか読者に分からない。"
        ),
    }
    passed = not withoutCount

    receipt = {
        "schema": "tai.reference.yic-universal-claim-population/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the YI receipts",
        "command": "python integrations/tools/yic_universal_claim_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-universal-claim-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads the YI receipts and flags those that assert an 'every …' verdict without any "
            "integer count in their observed data. It checks disclosure of a population size only: a "
            "counted receipt may still have counted the wrong population, and an uncounted one may "
            "describe a single object truthfully."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receiptsWithUniversalClaims": len(rows),
        "withoutCount": len(withoutCount),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
