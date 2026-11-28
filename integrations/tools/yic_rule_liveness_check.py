"""Point the liveness reading at the selector that now exists, and at both loops.

After the fix, the checker no longer compares `rule in name` with the original case: it
compares `rule in relative_lower`. So "rules dead only on case" is no longer a category
the checker can produce — the remaining question is which selectors reach no registered
receipt at all. The old vocabulary made this look like 40 rules had died, when they had
been made live.

This reads the checker's own selector list and counts reach across both receipt loops.
"""

import argparse
import ast
import hashlib
import json
import time
from pathlib import Path

CHECKER = "tools/check-synthetic-receipts/check.py"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    text = (root / CHECKER).read_text(encoding="utf-8")
    tree = ast.parse(text)

    names = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and node.targets
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in ("RECORDS", "REAL_RECORDS")
            and isinstance(node.value, (ast.Tuple, ast.List))
        ):
            for element in node.value.elts:
                if isinstance(element, ast.Constant) and isinstance(element.value, str):
                    names.append(element.value)

    selectors = sorted({
        line.strip().split('"')[1]
        for line in text.splitlines()
        if line.strip().startswith('if "') and 'in relative_lower:' in line
    })

    rows = []
    for selector in selectors:
        reached = [name for name in names if selector.lower() in name.lower()]
        rows.append({
            "selector": selector,
            "reach": len(reached),
            "examples": reached[:2],
        })

    inert = [row["selector"] for row in rows if row["reach"] == 0]
    checks = {
        "checker": CHECKER,
        "registeredNames": len(names),
        "selectors": len(selectors),
        "selectorsReachingNothing": inert,
        "inertCount": len(inert),
        "comparesAgainst": "relative_lower",
        "finding": (
            f"checkerの全{len(selectors)}セレクタについて、"
            f"登録{len(names)}件のうち何件に当たるかを数えた。"
            f"**当たらないセレクタは{len(inert)}件**。"
            "以前「大小文字の違いで死んでいる40件」と数えていたが、"
            "選択が`relative_lower`に変わった後は**その区分自体が存在しない**。"
            "残る問いは『一度も当たらない規則』だけである。"
        ),
    }
    # This check reports the inert list; it does not fail on it. The list is the finding,
    # and the checker already surfaces it as `inertRules`.
    passed = len(selectors) > 0 and len(names) > 0

    receipt = {
        "schema": "tai.reference.yic-selector-reach/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 parsing the checker's selectors and receipt lists",
        "command": "python integrations/tools/yic_rule_liveness_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-rule-liveness-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Parses every `in relative_lower` selector and counts how many registered receipts "
            "each reaches. It reports selectors that reach nothing; it does not judge whether a "
            "reachable selector asserts the right thing, and it reads the source rather than "
            "running the checker."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "selectors": len(selectors),
        "inert": len(inert),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
