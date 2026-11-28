"""Classify the known rule failures: is the rule current, or is the receipt historical?

Twenty-eight baseline entries say "this receipt fails this assertion". Two explanations are
possible, and they differ in what should be done:

  * the rule is current and the receipt is old, written before the field existed — the
    failure is historical and should be retired, not repaired;
  * no receipt of that kind ever satisfies the rule — the rule may be stale, and the
    failure is a rule defect.

The distinguishing test is measurable: for each failing rule, is there *another* receipt of
the same kind that does satisfy it? If yes, the rule is live somewhere and the failing
receipt is the outlier. If no receipt satisfies it, the rule has never held.
"""

import argparse
import ast
import hashlib
import json
import re
import time
from pathlib import Path

CHECKER = "tools/check-synthetic-receipts/check.py"
BASELINE_NAME = "KNOWN_RULE_FAILURE_BASELINE"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def baseline(root):
    tree = ast.parse((root / CHECKER).read_text(encoding="utf-8"))
    pairs = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and node.targets
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == BASELINE_NAME
        ):
            values = node.value
            # Unwrap `BASE + (...)` chains down to the literal tuples.
            stack = [values]
            while stack:
                current = stack.pop()
                if isinstance(current, ast.BinOp) and isinstance(current.op, ast.Add):
                    stack.append(current.left)
                    stack.append(current.right)
                elif isinstance(current, (ast.Tuple, ast.List)):
                    for element in current.elts:
                        if isinstance(element, ast.Tuple) and len(element.elts) == 2:
                            left, right = element.elts
                            if (
                                isinstance(left, ast.Constant) and isinstance(left.value, str)
                                and isinstance(right, ast.Constant) and isinstance(right.value, str)
                            ):
                                pairs.append((left.value, right.value))
    return sorted(set(pairs))


def selectors(root):
    """The `if "<selector>" in relative_lower:` guards and their assertion text."""
    text = (root / CHECKER).read_text(encoding="utf-8")
    lines = text.splitlines()
    guards = []
    for index, line in enumerate(lines):
        match = re.match(r'\s*if "(\S+)" in relative_lower:', line)
        if not match:
            continue
        selector = match.group(1)
        body = []
        for follow in lines[index + 1:index + 12]:
            if re.match(r'\s*if "\S+" in relative_lower:', follow):
                break
            body.append(follow.strip())
        guards.append({"selector": selector, "body": body})
    return guards


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    entries = baseline(root)
    guard_list = selectors(root)

    # Which receipts of the same "kind" satisfy the same selector?
    registered = sorted(
        set(re.findall(r'"(evaluations/records/[^"]+\.json)"',
                      (root / CHECKER).read_text(encoding="utf-8")))
    )

    baseline_receipts = {Path(relative).name for _, relative in entries}

    rows = []
    for message, failing in entries:
        citing = [
            guard for guard in guard_list
            if any(message.split(":")[0][:40] in line for line in guard["body"])
        ]
        selector = citing[0]["selector"] if citing else None
        # A sibling counts as evidence only if it is NOT itself a baseline entry: a receipt
        # that is not in the baseline produced no failure for this selector.
        siblings = [
            name for name in registered
            if selector and selector.lower() in name.lower()
            and name != failing
            and Path(name).name not in baseline_receipts
        ]
        rows.append({
            "message": message[:70],
            "receipt": Path(failing).name,
            "selector": selector,
            "siblingsOfSameKind": len(siblings),
            "siblings": [Path(name).name for name in siblings[:4]],
            "ruleIsLiveElsewhere": bool(siblings),
        })

    historical = [row for row in rows if row["ruleIsLiveElsewhere"]]
    unsupported = [row for row in rows if not row["ruleIsLiveElsewhere"]]

    checks = {
        "baselineEntries": len(entries),
        "failingRulesLocated": len([row for row in rows if row["selector"]]),
        "failuresWithARuleThatHoldsElsewhere": len(historical),
        "failuresWhoseRuleHoldsNowhere": len(unsupported),
        "unsupported": unsupported,
        "historicalSample": historical[:5],
        "finding": (
            f"基準{len(entries)}件のうち、**同じ規則が別のreceiptでは成立している**"
            f"（そのreceiptは基準に無く、失敗を出さない）ものが"
            f"{len(historical)}件、**どのreceiptでも成立しない**ものが{len(unsupported)}件。"
            "前者は**receiptが古い（規則は現行）**、後者は**規則が現行のreceiptに合わない**"
            "可能性が高い。**どちらを直すかは製品Ownerの判断だが、"
            "どちらの種類かは測れる。**"
        ),
    }
    passed = len(entries) > 0

    receipt = {
        "schema": "tai.reference.yic-baseline-classification/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 classifying the known rule failures",
        "command": "python integrations/tools/yic_baseline_classify.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-baseline-classify-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads the checker's baseline and, for each entry, finds the selector behind the "
            "message and whether any other registered receipt of the same kind satisfies it. It "
            "sorts failures into 'rule holds elsewhere' and 'rule holds nowhere'; it does not "
            "decide which receipt or rule is wrong."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "baseline": len(entries),
        "ruleHoldsElsewhere": len(historical),
        "ruleHoldsNowhere": len(unsupported),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
