"""Extend the section-order check to the whole YI document set.

The previous check watched one document. A section number that is missing from the
middle of a sequence is a different defect from an out-of-order pair: a reader who
sees 24 then 26 cannot tell whether 25 was removed deliberately or lost by an edit.
This scans every YI document for both, and treats an explicit "this number is absent
and here is why" heading as a resolved hole rather than a failure.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

DOCS = "docs/yi-constellation"
HEADING = re.compile(r"^##\s+(?P<number>[0-9]+(?:\.[0-9]+)?)\.?\s", re.M)
# A heading that states its own absence, e.g. "## 25. （欠番：…）".
DECLARED_ABSENT = re.compile(r"^##\s+([0-9]+)\.?\s*[（(]\s*欠番", re.M)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def as_tuple(number):
    return tuple(int(part) for part in number.split("."))


def scan(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    numbers = [match.group("number") for match in HEADING.finditer(text)]
    declared = {match.group(1) for match in DECLARED_ABSENT.finditer(text)}

    out_of_order = []
    previous_number = None
    previous_tuple = None
    for number in numbers:
        current = as_tuple(number)
        if previous_tuple is not None and current <= previous_tuple:
            out_of_order.append({"number": number, "after": previous_number})
        previous_number = number
        previous_tuple = current

    tops = sorted({int(number) for number in numbers if "." not in number})
    holes = []
    if tops:
        holes = [
            index for index in range(min(tops), max(tops) + 1)
            if index not in tops and str(index) not in declared
        ]
    return {
        "document": path.name,
        "headingCount": len(numbers),
        "outOfOrder": out_of_order,
        "undocumentedHoles": holes,
        "declaredAbsent": sorted(declared),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    folder = root / DOCS
    if not folder.exists():
        print(f"missing {DOCS}", file=sys.stderr)
        return 1

    rows = [scan(path) for path in sorted(folder.glob("*.md"))]
    withProblems = [
        row for row in rows
        if row["outOfOrder"] or row["undocumentedHoles"]
    ]

    checks = {
        "folder": DOCS,
        "documentsScanned": len(rows),
        "documentsWithProblems": len(withProblems),
        "problems": withProblems,
        "declaredAbsences": [
            {"document": row["document"], "numbers": row["declaredAbsent"]}
            for row in rows if row["declaredAbsent"]
        ],
        "everySequenceAscendsAndHasNoUndocumentedHole": not withProblems,
        "finding": (
            "YI文書の番号付き見出しを走査し、降順の対と、"
            "途中の欠番（理由が書かれていないもの）を検出する。"
            "`## 25. （欠番：…）`のように**欠番であることを明示した見出し**は、"
            "解決済みとして扱う。番号を詰めると既存の参照が別の節を指すため、"
            "欠番を残して理由を書く方を選ぶ。"
        ),
    }
    passed = not withProblems

    receipt = {
        "schema": "tai.reference.yic-section-sequence/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 scanning the YI documents",
        "command": "python integrations/tools/yic_section_sequence_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-section-sequence-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Scans every YI document for numbered headings that run backwards, and for numbers "
            "missing from the middle of a sequence without a heading that declares the absence. It "
            "checks numbering only: a well-numbered document can still be wrong, and headings inside "
            "fences or tables are not examined."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "documents": len(rows),
        "withProblems": [row["document"] for row in withProblems],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
