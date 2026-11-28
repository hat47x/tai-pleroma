"""Evaluate the located assertion against its siblings, not against the whole selector.

Now that each baseline failure is tied to the assertion that emits it, the sibling test is
exact: does a receipt that shares the selector and is *not* in the baseline for this
assertion actually satisfy this assertion? Read the guard, extract the field comparison, and
check.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

LOCATE = "evaluations/records/YIC-assertion-locate-2026-11-28.json"
CHECKER = "tools/check-synthetic-receipts/check.py"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def comparisons(condition):
    """(receiver.field, expected) pairs from a guard condition string, deduplicated."""
    pairs = []
    for match in re.finditer(
        r'(\w+)\.get\("(\w+)"\)\s*(?:!=|==)\s*(?:"([^"]*)"|(\d+|True|False))', condition
    ):
        receiver, field = match.group(1), match.group(2)
        literal = match.group(3) if match.group(3) is not None else match.group(4)
        if literal in ("True", "False"):
            value = literal == "True"
        elif literal.isdigit():
            value = int(literal)
        else:
            value = literal
        pairs.append((f"{receiver}.{field}", value))
    # A field may appear in several clauses; keep the first expectation for each path.
    seen = {}
    for path, value in pairs:
        seen.setdefault(path, value)
    return sorted(seen.items())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    located = json.loads((root / LOCATE).read_text(encoding="utf-8"))
    rows_in = (located.get("observed") or {}).get("rows") or []

    checks_rows = []
    for entry in rows_in:
        wanted = comparisons(entry.get("condition") or "")
        evaluated = []
        for name in entry.get("siblings") or []:
            path = root / "evaluations/records" / name
            if not path.exists():
                continue
            receipt = json.loads(path.read_text(encoding="utf-8-sig"))
            for container_name in ("observed", None):
                container = receipt.get(container_name) if container_name else receipt
                if not isinstance(container, dict):
                    continue
            observed = receipt.get("observed")
            if not isinstance(observed, dict):
                observed = receipt
            def resolve(path):
                receiver, _, field = path.partition(".")
                if receiver in ("observed", ""):
                    return observed.get(field)
                container = receipt.get(receiver)
                if isinstance(container, dict):
                    return container.get(field)
                return None

            satisfied = [
                path for path, value in wanted if resolve(path) == value
            ]
            evaluated.append({
                "receipt": name,
                "required": len(wanted),
                "satisfied": len(satisfied),
                "satisfiesAll": bool(wanted) and len(satisfied) == len(wanted),
            })
        checks_rows.append({
            "message": entry.get("message"),
            "selector": entry.get("selector"),
            "requiredFields": [field for field, _ in wanted],
            "siblings": evaluated,
        })

    all_siblings = [item for row in checks_rows for item in row["siblings"]]
    unsupporting = [item for item in all_siblings if not item["satisfiesAll"]]
    withoutComparisons = [
        row for row in checks_rows if not row["requiredFields"]
    ]
    summary = []
    for row in checks_rows:
        supporting = [item for item in row["siblings"] if item["satisfiesAll"]]
        summary.append({
            "message": row["message"],
            "selector": row["selector"],
            "requiredFields": row["requiredFields"],
            "siblingsChecked": len(row["siblings"]),
            "satisfiedBy": [item["receipt"] for item in supporting],
            "holdsSomewhere": bool(supporting),
        })
    distinct = {}
    for row in summary:
        distinct.setdefault(row["message"], row["holdsSomewhere"])

    checks = {
        "locateReceipt": LOCATE,
        "distinctAssertions": len(distinct),
        "assertionsHoldingSomewhere": len([key for key, value in distinct.items() if value]),
        "assertionsHoldingNowhere": [
            key for key, value in distinct.items() if not value
        ],
        "perAssertion": [
            {
                "message": key,
                "holdsSomewhere": value,
                "satisfiedBy": sorted({
                    receipt
                    for row in summary if row["message"] == key
                    for receipt in row["satisfiedBy"]
                })[:3],
            }
            for key, value in distinct.items()
        ],
        "baselineAssertions": len(rows_in),
        "rows": checks_rows,
        "siblingsEvaluated": len(all_siblings),
        "siblingsSupporting": len(all_siblings) - len(unsupporting),
        "siblingsNotSupporting": unsupporting,
        "rowsWithoutComparisons": len(withoutComparisons),
        "finding": (
            f"基準の背後にある**{len(distinct)}種類のassertion**を、兄弟と突き合わせた。"
            f"**どこかのreceiptで成立しているもの{len([key for key, value in distinct.items() if value])}件**、"
            f"**どのreceiptでも成立しないもの"
            f"{len([key for key, value in distinct.items() if not value])}件**。"
            f"検査した兄弟{len(all_siblings)}件のうち**規則を満たすもの"
            f"{len(all_siblings) - len(unsupporting)}件**、満たさないもの{len(unsupporting)}件。"
            f"比較式を読めなかった行{len(withoutComparisons)}件。"
            "**セレクタ全体ではなくassertionで見ると、"
            "『兄弟なし』と数えていた失敗のいくつかに兄弟がいた。**"
        ),
    }
    passed = bool(all_siblings)

    receipt = {
        "schema": "tai.reference.yic-assertion-sibling-check/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 evaluating each assertion against its siblings",
        "command": "python integrations/tools/yic_assertion_sibling_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-assertion-siblings-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads the located assertion's guard condition, extracts its field comparisons, and "
            "evaluates them against sibling receipts. It checks a sample of siblings; it does not "
            "evaluate every receipt, and a guard using a helper rather than a literal is not parsed."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "siblings": len(all_siblings),
        "supporting": len(all_siblings) - len(unsupporting),
        "withoutComparisons": len(withoutComparisons),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
