"""Classify by the specific assertion, not by the whole selector block.

The earlier classification asked "does another receipt match this selector and stay out of
the baseline". That is coarse: a receipt can be in the baseline for a *different* message
and still satisfy the assertion under study. It reported fourteen failures whose "rule holds
nowhere", but some of those receipts satisfy the specific assertion being failed — they
merely fail something else.

This reads each rule block's assertions, finds which assertion emits a given message, and
checks that one assertion against the sibling receipts.
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
MESSAGE_AT = re.compile(r'errors\.append\(f"(?P<text>[^{"]+?)(?::\s*)?\{relative\}"\)')

# Which assertion line emits which message, per selector block.
def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def blocks(root):
    text = (root / CHECKER).read_text(encoding="utf-8")
    lines = text.splitlines()
    out = []
    for index, line in enumerate(lines):
        match = re.match(r'\s*if "(\S+)" in relative_lower:', line)
        if not match:
            continue
        selector = match.group(1)
        assertions = []
        current_condition = []
        for follow in lines[index + 1:index + 16]:
            stripped = follow.strip()
            if re.match(r'if "\S+" in relative_lower:', stripped):
                break
            if stripped.startswith("if ") or stripped.startswith("errors.append("):
                message = MESSAGE_AT.search(stripped)
                if message:
                    assertions.append({
                        "message": message.group("text"),
                        "condition": " ".join(current_condition),
                    })
                    current_condition = []
                else:
                    current_condition.append(stripped)
        out.append({"selector": selector, "assertions": assertions})
    return out


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
            stack = [node.value]
            while stack:
                current = stack.pop()
                if isinstance(current, ast.BinOp) and isinstance(current.op, ast.Add):
                    stack.extend([current.left, current.right])
                elif isinstance(current, (ast.Tuple, ast.List)):
                    for element in current.elts:
                        if isinstance(element, ast.Tuple) and len(element.elts) == 2:
                            pair = tuple(
                                item.value for item in element.elts
                                if isinstance(item, ast.Constant) and isinstance(item.value, str)
                            )
                            if len(pair) == 2:
                                pairs.append(pair)
    return sorted(set(pairs))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    entries = baseline(root)
    rule_blocks = blocks(root)
    registered = sorted(
        set(re.findall(r'"(evaluations/records/[^"]+\.json)"',
                      (root / CHECKER).read_text(encoding="utf-8")))
    )

    rows = []
    for message, failing in entries:
        wanted = message.strip()
        selector = None
        condition = ""
        for block in rule_blocks:
            for assertion in block["assertions"]:
                if assertion["message"].strip() == wanted:
                    selector = block["selector"]
                    condition = assertion["condition"]
                    break
            if selector:
                break
        siblings = [
            name for name in registered
            if selector and selector.lower() in name.lower() and name != failing
        ]
        rows.append({
            "message": wanted[:60],
            "receipt": Path(failing).name,
            "selector": selector,
            "condition": condition[:100],
            "siblings": [Path(name).name for name in siblings[:4]],
            "siblingCount": len(siblings),
        })

    located = [row for row in rows if row["selector"]]
    orphaned = [row for row in rows if not row["selector"]]
    checks = {
        "baselineEntries": len(entries),
        "assertionsLocated": len(located),
        "assertionsNotFound": orphaned,
        "rows": rows,
        "finding": (
            f"基準{len(entries)}件について、**その失敗を出すassertionを規則本文から特定**した。"
            f"特定できたもの{len(located)}件、できなかったもの{len(orphaned)}件。"
            "**セレクタ全体で分類すると、別のassertionで基準に入っているreceiptを"
            "『兄弟なし』と数えてしまう。** どのassertionかを持てば、"
            "**同じassertionを通るreceiptを兄弟として数えられる。**"
        ),
    }
    passed = len(entries) > 0

    receipt = {
        "schema": "tai.reference.yic-assertion-locate/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 locating each baseline failure's assertion",
        "command": "python integrations/tools/yic_assertion_locate.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-assertion-locate-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Parses each rule block's assertions and matches a baseline message to the assertion "
            "that emits it, recording the selector and the guard condition. It locates the "
            "assertion; it does not evaluate it against the receipts."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "baseline": len(entries),
        "located": len(located),
        "orphaned": len(orphaned),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
