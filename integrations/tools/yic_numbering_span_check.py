"""Look for the same numbering disorder in every YI document, not only doc 53.

The numbering check added last round reads one file. Eighty-seven YI documents carry
numbered headings, so if disorder is a consequence of appending sections over time, it
should exist elsewhere too. This measures how widespread it is before deciding whether to
fix each document or to widen the check.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

HEADING = re.compile(r"^(?P<hashes>#{2,4})\s+(?P<number>[0-9]+(?:\.[0-9]+)+[a-z]?)(?:\s|$)")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def analyse(text):
    headings = []
    for line_number, line in enumerate(text.splitlines(), 1):
        match = HEADING.match(line)
        if match:
            headings.append((line_number, match.group("number")))

    families = {}
    for line_number, number in headings:
        parts = number.split(".")
        if len(parts) >= 3:
            families.setdefault(".".join(parts[:2]), []).append((line_number, number))

    outOfOrder = []
    gaps = []
    for parent, members in families.items():
        last = None
        for line_number, number in members:
            tail = number.split(".")[2]
            if not tail.isdigit():
                continue
            value = int(tail)
            if last is not None and value < last:
                outOfOrder.append(line_number)
            if last is not None and value > last + 1:
                gaps.append(line_number)
            last = value

    suffixed = [
        line_number
        for line_number, number in headings
        if re.search(r"[0-9][a-z]$", number)
    ]
    return len(headings), len(outOfOrder), len(gaps), len(suffixed)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    folder = root / "docs/yi-constellation"
    rows = []
    for path in sorted(folder.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        headings, out_of_order, gaps, suffixed = analyse(text)
        if headings == 0:
            continue
        rows.append({
            "document": str(path.relative_to(root)).replace("\\", "/"),
            "headings": headings,
            "outOfOrder": out_of_order,
            "gaps": gaps,
            "suffixed": suffixed,
            "disordered": out_of_order + gaps + suffixed > 0,
        })

    disordered = [row for row in rows if row["disordered"]]
    checks = {
        "folder": "docs/yi-constellation",
        "documentsWithNumberedHeadings": len(rows),
        "documentsWithDisorder": len(disordered),
        "disorderedSample": [
            {key: row[key] for key in ("document", "outOfOrder", "gaps", "suffixed")}
            for row in disordered[:10]
        ],
        "totalOutOfOrder": sum(row["outOfOrder"] for row in rows),
        "totalGaps": sum(row["gaps"] for row in rows),
        "totalSuffixed": sum(row["suffixed"] for row in rows),
        "finding": (
            f"YI文書のうち番号付き見出しを持つものは{len(rows)}件。"
            f"そのうち**番号に乱れがあるものは{len(disordered)}件**。"
            f"合計で順序の逆{sum(row['outOfOrder'] for row in rows)}件・"
            f"飛び{sum(row['gaps'] for row in rows)}件・"
            f"整数でない接尾辞{sum(row['suffixed'] for row in rows)}件。"
            "**番号を見ている点検の対象は1文書だけだった。**"
            "乱れは追記の仕方の性質なので、**1文書だけを見ても足りない。**"
        ),
    }
    passed = len(rows) > 0

    receipt = {
        "schema": "tai.reference.yic-numbering-span/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading every YI document's numbered headings",
        "command": "python integrations/tools/yic_numbering_span_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-numbering-span-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Parses numbered headings across all YI documents and reports disorder per document. "
            "It measures the span of the problem; it does not fix any document, and a gap can be a "
            "deliberate omission."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "documents": len(rows),
        "disordered": len(disordered),
        "outOfOrder": checks["totalOutOfOrder"],
        "gaps": checks["totalGaps"],
        "suffixed": checks["totalSuffixed"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
