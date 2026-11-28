"""Check that the seven selectors that reach nothing are dead, or missing a receipt.

The checker reports seven selectors that reach no registered receipt. A selector that
matches nothing is either obsolete (its receipt was renamed or removed) or evidence that
a receipt the checker should know about is not registered. Both are silent.

This reads each inert selector, the rules it guards, and any file on disk whose name
resembles it, so a reader can tell which case each one is.
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

    names = []
    for node in ast.walk(ast.parse(text)):
        if (
            isinstance(node, ast.Assign)
            and node.targets
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in ("RECORDS", "REAL_RECORDS")
            and isinstance(node.value, (ast.Tuple, ast.List))
        ):
            names += [
                element.value for element in node.value.elts
                if isinstance(element, ast.Constant) and isinstance(element.value, str)
            ]

    lines = text.splitlines()
    selectors = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('if "') and "in relative_lower:" in stripped:
            selector = stripped.split('"')[1]
            # The guards this selector protects: the lines until the next selector.
            guards = []
            for follow in lines[index + 1:]:
                follow_stripped = follow.strip()
                if follow_stripped.startswith('if "') and "in relative_lower:" in follow_stripped:
                    break
                if follow_stripped.startswith(("errors.append", "if ", "observed = ")):
                    guards.append(follow_stripped[:90])
            selectors.append({
                "selector": selector,
                "guards": guards[:3],
            })

    disk = [p.name for p in (root / "evaluations/records").glob("*.json")]
    rows = []
    for entry in selectors:
        reach = [name for name in names if entry["selector"].lower() in name.lower()]
        # Files on disk whose name shares the selector's distinguishing tail.
        tail = entry["selector"].split("-")[-1].lower()
        similar = sorted(name for name in disk if tail in name.lower())[:4]
        rows.append({
            "selector": entry["selector"],
            "registeredMatches": len(reach),
            "filesOnDiskResembling": similar,
            "guards": entry["guards"],
        })

    inert = [row for row in rows if row["registeredMatches"] == 0]
    withEvidence = [row["selector"] for row in inert if row["filesOnDiskResembling"]]
    withoutEvidence = [row["selector"] for row in inert if not row["filesOnDiskResembling"]]

    checks = {
        "checker": CHECKER,
        "selectors": len(selectors),
        "inertSelectors": [row["selector"] for row in inert],
        "inertWithAResemblingFile": withEvidence,
        "inertWithNoResemblingFile": withoutEvidence,
        "rows": inert,
        "finding": (
            f"一度も当たらないセレクタ{len(inert)}件について、"
            "**守っている判定**と**ディスク上に似た名前のファイルがあるか**を並べた。"
            f"似た名前があるもの{len(withEvidence)}件は、"
            "**receiptが存在するのに登録されていない**可能性を示す。"
            f"似た名前が無いもの{len(withoutEvidence)}件は、"
            "**receiptが改名・削除された**可能性を示す。"
            "どちらも無音で起きるので、ここで名指しする。"
        ),
    }
    passed = len(inert) > 0

    receipt = {
        "schema": "tai.reference.yic-inert-selectors/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the checker and the records folder",
        "command": "python integrations/tools/yic_inert_selector_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-inert-selectors-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads every inert selector, the guards beneath it, and any file on disk whose name "
            "shares its last segment. It sorts the inert selectors into 'a resembling file exists' "
            "and 'none does'; it does not decide which of them should be repaired, and the "
            "resemblance test is a name match, not a content match."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "inert": len(inert),
        "withFile": len(withEvidence),
        "withoutFile": len(withoutEvidence),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
