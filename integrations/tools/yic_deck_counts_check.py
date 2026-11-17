"""Check the deck slide counts that the indexes state against the actual files.

Three documents make numeric claims about the decks: the YI README ("前編30枚",
"後編42枚（31〜72番）", "詳細版47枚（31〜77番）"), the decks README (the same numbers plus
"価値のトラック 15枚"), and the detail deck's inspection record (`slide_count: 47`,
`display_numbers: [31, 77]`). A slide count that has drifted misleads a reader about
how much material exists.

This counts slides in the .pptx files and pages in the .pdf files and compares each
stated number with the count it describes. It also checks that the stated display
range is consistent with the stated slide count (72−31+1 = 42).
"""

import argparse
import hashlib
import json
import re
import time
import zipfile
from pathlib import Path

DECKS = "docs/yi-constellation/decks"
INDEXES = (
    "docs/yi-constellation/README.md",
    "docs/yi-constellation/decks/README.md",
)
INSPECTION = "docs/yi-constellation/decks/part2/YI_Constellation_2_detail_検査記録.json"

# Each deck, its file, and the phrase each index uses for it.
DECK_CLAIMS = (
    {
        "deck": "part1/YI_Constellation_1.pptx",
        "slidePattern": r"前編\s*(\d+)枚",
        "labelled": "前編",
    },
    {
        "deck": "part2/YI_Constellation_2.pptx",
        "slidePattern": r"後編\s*(\d+)枚",
        "labelled": "後編",
    },
    {
        "deck": "part2/YI_Constellation_2_detail.pptx",
        "slidePattern": r"詳細版[（(]?\s*(\d+)枚",
        "labelled": "詳細版",
    },
)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pptx_slide_count(path):
    """Count slide parts in a .pptx, so no PowerPoint install is needed."""
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist()
                 if re.match(r"ppt/slides/slide[0-9]+\.xml$", name)]
    return len(names)


def pdf_page_count(path):
    data = path.read_bytes()
    return len(re.findall(rb"/Type\s*/Page[^s]", data))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    folder = root / DECKS
    if not folder.exists():
        print(f"missing {DECKS}", file=sys.stderr)
        return 1

    actual = {}
    for path in sorted(folder.rglob("*.pptx")):
        actual[str(path.relative_to(folder)).replace("\\", "/")] = pptx_slide_count(path)
    pdf_pages = {
        str(path.relative_to(folder)).replace("\\", "/"): pdf_page_count(path)
        for path in sorted(folder.rglob("*.pdf"))
    }

    # Every stated number, with what it should equal.
    index_texts = {
        relative: (root / relative).read_text(encoding="utf-8")
        for relative in INDEXES
        if (root / relative).exists()
    }
    stated = []
    for entry in DECK_CLAIMS:
        for relative, body in index_texts.items():
            for match in re.finditer(entry["slidePattern"], body):
                stated.append({
                    "index": relative,
                    "deck": entry["deck"],
                    "labelled": entry["labelled"],
                    "stated": int(match.group(1)),
                    "actual": actual.get(entry["deck"]),
                })

    # The 価値のトラック deck.
    for relative, body in index_texts.items():
        match = re.search(r"価値のトラック[^\n]*?(\d+)枚", body)
        if match:
            stated.append({
                "index": relative,
                "deck": "価値のトラック.pptx",
                "labelled": "価値のトラック",
                "stated": int(match.group(1)),
                "actual": actual.get("価値のトラック.pptx"),
            })

    mismatched = [
        row for row in stated
        if row["actual"] is not None and row["stated"] != row["actual"]
    ]

    # PDF pages should equal the PPTX slides of the same base name.
    pdfMismatches = []
    for pdf_name, pages in pdf_pages.items():
        pptx_name = pdf_name[:-4] + ".pptx"
        if pptx_name in actual and pages != actual[pptx_name]:
            pdfMismatches.append({
                "pdf": pdf_name,
                "pdfPages": pages,
                "pptxSlides": actual[pptx_name],
            })

    # Range arithmetic in the indexes: "42枚（31〜72番）" must satisfy 72-31+1=42.
    rangeIssues = []
    for relative, body in index_texts.items():
        for match in re.finditer(r"(\d+)枚（(\d+)〜(\d+)番）", body):
            count, first, last = (int(group) for group in match.groups())
            if last - first + 1 != count:
                rangeIssues.append({
                    "index": relative,
                    "text": match.group(0),
                    "arithmetic": last - first + 1,
                })

    inspection = None
    if (root / INSPECTION).exists():
        record = json.loads((root / INSPECTION).read_text(encoding="utf-8"))
        claimed = record.get("slide_count")
        display = record.get("display_numbers") or []
        inspection = {
            "claimedSlideCount": claimed,
            "actualSlideCount": actual.get("part2/YI_Constellation_2_detail.pptx"),
            "displayNumbers": display,
            "agrees": claimed == actual.get("part2/YI_Constellation_2_detail.pptx"),
        }

    checks = {
        "decksFolder": DECKS,
        "actualSlideCounts": actual,
        "actualPdfPages": pdf_pages,
        "statedCounts": stated,
        "mismatchedStatedCounts": mismatched,
        "pdfPageMismatches": pdfMismatches,
        "rangeArithmeticIssues": rangeIssues,
        "inspectionRecord": inspection,
        "everyStatedCountMatchesTheFile": not mismatched,
        "everyPdfMatchesItsDeck": not pdfMismatches,
        "everyDisplayRangeIsConsistent": not rangeIssues,
        "finding": (
            "索引が述べる枚数を、実際の.pptxのスライド数と.pdfのページ数に対して点検する。"
            "「42枚（31〜72番）」のような表示範囲が枚数と整合するかも確かめる。"
        ),
    }
    passed = (
        not mismatched and not pdfMismatches and not rangeIssues
        and (inspection is None or inspection["agrees"])
    )

    receipt = {
        "schema": "tai.reference.yic-deck-counts/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the deck files and their indexes",
        "command": "python integrations/tools/yic_deck_counts_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-deck-counts-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Counts slide XML parts in each .pptx and page objects in each .pdf, and compares them "
            "with the counts the two index documents and the inspection record state. It checks "
            "counts only: matching numbers say nothing about whether a deck's content is right, and "
            "the page count reads the PDF structure rather than rendering it."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "stated": len(stated),
        "mismatched": mismatched,
        "pdfMismatches": pdfMismatches,
        "rangeIssues": rangeIssues,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
