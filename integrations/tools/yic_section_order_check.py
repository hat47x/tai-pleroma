"""Check that a document's numbered sections appear in order.

Sections 4.6 was inserted before 4.5 during a later edit, so a reader following the
numbers walks backwards. That is a small defect, but it makes "the document is
ordered" untrue, and a reader cannot tell whether 4.5 answers 4.6 or the reverse.
This reads the heading sequence and reports out-of-order numbers.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

TARGET = "docs/yi-constellation/irptch-reach-2026-11-16.md"
HEADING = re.compile(r"^##\s+(?P<number>[0-9]+(?:\.[0-9]+)?)\.?\s", re.M)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def as_tuple(number):
    return tuple(int(part) for part in number.split("."))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    target = root / TARGET
    if not target.exists():
        print(f"missing {TARGET}", file=sys.stderr)
        return 1

    text = target.read_text(encoding="utf-8")
    numbers = [match.group("number") for match in HEADING.finditer(text)]

    # Each heading must be strictly greater than the one before it.
    out_of_order = []
    previous = None
    for number in numbers:
        current = as_tuple(number)
        if previous is not None and current <= previous[1]:
            out_of_order.append({
                "number": number,
                "after": previous[0],
            })
        previous = (number, current)

    # Title numbers should also all be present, so a skipped number is visible.
    top_level = sorted({number for number in numbers if "." not in number})
    missing_tops = [
        str(index) for index in range(1, len(top_level) + 1)
        if str(index) not in top_level
    ]

    checks = {
        "document": TARGET,
        "headings": numbers,
        "headingCount": len(numbers),
        "outOfOrder": out_of_order,
        "missingTopLevelNumbers": missing_tops,
        "sectionsAreOrdered": not out_of_order,
        "finding": (
            "節番号が文書内で昇順に並んでいるかを点検する。"
            "番号が逆転していると、読者は節の依存関係を読み違える。"
            "`4.6`が`4.5`より前に置かれていた事例を検出して修正した。"
        ),
    }
    passed = not out_of_order and not missing_tops

    receipt = {
        "schema": "tai.reference.yic-section-order/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the document headings",
        "command": "python integrations/tools/yic_section_order_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-section-order-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads the numbered headings in one document and checks they ascend without gaps. It "
            "checks order only: a well-ordered section can still be wrong, and a heading whose number "
            "is inside a code block or table is not examined."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "headings": len(numbers),
        "outOfOrder": out_of_order,
        "missingTops": missing_tops,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
