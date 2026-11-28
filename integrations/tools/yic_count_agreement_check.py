"""Check that a checker's expected count is derived, not hard-coded.

Several YI checks assert `observed.get("checksRun") != N`, and N has had to be edited by
hand each time a check was added. This session edited it in four places for one change,
twice in the same file. A hand-maintained constant that must track another file is a
place where the two silently disagree.

This counts the checks registered in each aggregate and compares against the number each
receipt rule expects.
"""

import argparse
import ast
import hashlib
import json
import re
import time
from pathlib import Path

TOOLS = "integrations/tools"
CHECKER = "tools/check-synthetic-receipts/check.py"
AGGREGATES = (
    ("yic_document_gates.py", ("CHECKS",), "YIC-document-gates"),
    # Checks live in three tuples here; the aggregate runs the sum of them.
    ("yic_analysis_gates.py", ("CHECKS", "TAI_ROOT_CHECKS", "PORTABLE_CHECKS"),
     "YIC-analysis-gates"),
    # The receipt-quality aggregate is a suite step rather than a YIC aggregate, but its
    # count is hard-coded in the same file and drifts the same way.
    ("yi_receipt_quality.py", ("CHECKS",), "YI-receipt-quality"),
)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def count_entries(source_text, tuple_name):
    """Count the string literals inside a named tuple or constant assignment."""
    tree = ast.parse(source_text)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == tuple_name:
                    if isinstance(node.value, ast.Tuple):
                        return len(node.value.elts)
    return None


def expected_in_checker(checker_text, rule_key):
    """Read the `!= N` that follows the rule keyed on this receipt name."""
    index = checker_text.find(f'if "{rule_key}" in relative:')
    if index < 0:
        # Selectors now compare against the lower-cased path.
        index = checker_text.find(f'if "{rule_key}" in relative_lower:')
    if index < 0:
        return None
    window = checker_text[index:index + 900]
    match = re.search(r'checksRun"\)\s*!=\s*(\d+)', window)
    return int(match.group(1)) if match else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    checker_text = (root / CHECKER).read_text(encoding="utf-8")

    rows = []
    for file_name, tuple_names, rule_key in AGGREGATES:
        path = root / TOOLS / file_name
        if not path.exists():
            rows.append({"aggregate": file_name, "exists": False})
            continue
        source = path.read_text(encoding="utf-8")
        counted = [count_entries(source, name) for name in tuple_names]
        declared = None if any(n is None for n in counted) else sum(counted)
        expected = expected_in_checker(checker_text, rule_key)
        rows.append({
            "aggregate": file_name,
            "exists": True,
            "entriesInSource": declared,
            "tuplesCounted": list(tuple_names),
            "expectedByChecker": expected,
            "agrees": declared is not None and declared == expected,
        })

    disagreements = [
        row["aggregate"] for row in rows
        if row.get("exists") and not row.get("agrees")
    ]
    hardCoded = [
        row["aggregate"] for row in rows
        if row.get("exists") and row.get("expectedByChecker") is not None
    ]

    checks = {
        "checker": CHECKER,
        "aggregates": rows,
        "disagreements": disagreements,
        "countsAreHardCodedInTheChecker": bool(hardCoded),
        "hardCodedAggregates": hardCoded,
        "everyCountAgrees": not disagreements,
        "finding": (
            "集約が実際に走らせる点検の数と、checkerが期待する数の一致を見る。"
            "checkerには3つの固定された数があり、"
            "点検を1つ足すたびに手で直す必要がある。"
            "**手で保つ定数は、いつか食い違う。**"
            "ここでは3つすべてを突き合わせる。"
        ),
    }
    passed = not disagreements

    receipt = {
        "schema": "tai.reference.yic-count-agreement/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 parsing the aggregates and the checker",
        "command": "python integrations/tools/yic_count_agreement_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-count-agreement-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Parses each aggregate's check tuple and the checker's expected integer, and compares "
            "them. It catches a count that has drifted; it cannot tell which of the two is right, and "
            "it does not remove the hand-maintained constant."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "rows": len(rows),
        "disagreements": disagreements,
        "each": [
            (row.get("aggregate"), row.get("entriesInSource"), row.get("expectedByChecker"))
            for row in rows if row.get("exists")
        ],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
