"""Correct the annotation-readiness detector: the checker has no global field allow-list.

The first version reported `forbidsUnknown: true` because the regex matched a *per-receipt*
rule (`TEI document record receipt has unexpected fields`), which pins the inner
`observed.fields` list of one receipt type. That is not a global prohibition on adding a
top-level note.

This measures the two things separately: whether a global required/allowed-key set exists,
and which per-receipt rules pin an exact field list that an annotation must avoid.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

PATH_CITE = "evaluations/records/YIC-cited-path-2026-11-28.json"
CHECKER = "tools/check-synthetic-receipts/check.py"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    cited = json.loads((root / PATH_CITE).read_text(encoding="utf-8"))
    affected = (cited.get("observed") or {}).get("receiptsAffected") or []

    rows = []
    for name in affected:
        path = root / "evaluations/records" / name
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        rows.append({
            "receipt": name,
            "hasNoteField": any(
                key in data for key in ("note", "notes", "annotation", "limitations")
            ),
        })

    checker_text = (root / CHECKER).read_text(encoding="utf-8")

    # A global allow-list would appear as a set of permitted top-level keys compared with
    # the receipt's keys. Look for that specific shape, not for the word "unexpected".
    globalAllowList = bool(
        re.search(r"ALLOWED_?FIELDS", checker_text)
        or re.search(r"set\(data\)\s*-\s*", checker_text)
        or re.search(r"for key in data:\s*\n\s*if key not in", checker_text)
    )

    # Per-receipt rules that pin an exact inner list a note must not disturb.
    pinnedLists = [
        match.group(1)
        for match in re.finditer(r'observed\.get\[\?\("(\w+)"\)\]?', checker_text)
    ]
    exactFieldRules = sorted(set(re.findall(
        r'observed\.get\("fields"\) != \[(.*?)\]', checker_text
    )))
    unexpectedFieldMessages = [
        line.strip()[:100]
        for line in checker_text.splitlines()
        if "unexpected fields" in line and "errors.append" in line
    ]

    hasNote = [row["receipt"] for row in rows if row["hasNoteField"]]
    checks = {
        "citedPathReceipt": PATH_CITE,
        "affectedReceipts": len(rows),
        "alreadyHaveANoteField": len(hasNote),
        "withoutOne": len(rows) - len(hasNote),
        "globalFieldAllowList": globalAllowList,
        "rulesPinningAnExactFieldList": exactFieldRules,
        "rulesPinningAnExactFieldListCount": len(exactFieldRules),
        "unexpectedFieldMessages": unexpectedFieldMessages,
        "finding": (
            f"注記を要するreceiptは{len(rows)}件で、注記欄を持つものは**{len(hasNote)}件**。"
            f"checkerに**トップレベル欄の全体許可リストは"
            f"{'ある' if globalAllowList else '無い'}**。"
            f"一方、**内側の`observed.fields`を完全一致で固定する規則が"
            f"{len(exactFieldRules)}件**あり、そちらは注記の置き場所に制約を与える。"
            "最初の版は`unexpected fields`という語だけで『全体で拒否』と判定し、"
            "**1つのreceipt種別の内側規則を全体規則と読み違えた**。"
        ),
    }
    passed = len(rows) > 0

    receipt = {
        "schema": "tai.reference.yic-annotation-readiness/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the affected receipts and the checker",
        "command": "python integrations/tools/yic_annotation_readiness_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-annotation-readiness-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads the receipts named by the path check for a field that could carry a note, and "
            "reads the checker for a global field allow-list and for rules pinning an exact inner "
            "field list. It readies an annotation pass; it does not write the annotation, and a "
            "rule-pinned inner list is a constraint on placement, not a rejection of all notes."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "affected": len(rows),
        "withNote": len(hasNote),
        "globalAllowList": globalAllowList,
        "exactListRules": len(exactFieldRules),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
