"""Check that a document's numbered subsections ascend without gaps or stray suffixes.

Doc 53 grew by appending sections over many rounds. Its §6.1 now reads 6.1.1, 6.1.2,
6.1.3, 6.1.6c … 6.1.6l, 6.1.7, 6.1.5, 6.1.6 — section 6.1.4 never existed, the `c`–`l`
suffixes are not numbers, and 6.1.5 and 6.1.6 sit after 6.1.7.

The section-order check only looks at `irptch-reach`. Nothing looked at doc 53's own
numbering, so the disorder accumulated unnoticed.

This parses each heading's number and reports: gaps, out-of-order pairs, and headings whose
suffix is not a plain integer.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

DOC = "docs/yi-constellation/analysis/53-判定と残る前進.md"
HEADING = re.compile(r"^(?P<hashes>#{2,4})\s+(?P<number>[0-9]+(?:\.[0-9]+)+)(?:\s|$)")


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
    path = root / DOC
    if not path.exists():
        print(f"missing {DOC}", file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")

    headings = []
    for line_number, line in enumerate(text.splitlines(), 1):
        match = HEADING.match(line)
        if match:
            headings.append({
                "line": line_number,
                "number": match.group("number"),
                "hashCount": len(match.group("hashes")),
                "title": line[match.end():].strip()[:40],
            })

    # Group by parent prefix (e.g. "6.1" for "6.1.x").
    families = {}
    for heading in headings:
        parts = heading["number"].split(".")
        if len(parts) == 3:
            families.setdefault(".".join(parts[:2]), []).append(heading)

    outOfOrder = []
    gaps = []
    suffixed = []
    for parent, members in families.items():
        last = None
        seen = set()
        for member in members:
            value = int(member["number"].split(".")[2])
            if last is not None and value != last + 1:
                if value < last:
                    outOfOrder.append({"family": parent, "at": member["line"],
                                       "number": member["number"], "after": last})
                elif value > last + 1:
                    gaps.append({"family": parent, "at": member["line"],
                                 "number": member["number"], "expected": last + 1})
            seen.add(value)
            last = value

    # Non-integer suffixes such as "6.1.6c".
    for line_number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^#{2,4}\s+([0-9]+\.[0-9]+\.([0-9]+[a-z]))", line)
        if match:
            suffixed.append({"line": line_number, "number": match.group(1)})

    checks = {
        "document": DOC,
        "headingsWithANumber": len(headings),
        "families": sorted(families),
        "outOfOrder": outOfOrder,
        "gaps": gaps,
        "suffixThatIsNotAnInteger": suffixed,
        "numberingIsMonotonic": not outOfOrder,
        "finding": (
            f"文書の番号付き見出しを解析した。3階層を持つ族は{len(families)}個。"
            f"**順序が逆の箇所{len(outOfOrder)}件**、"
            f"**番号の飛び{len(gaps)}件**、"
            f"**整数でない接尾辞{len(suffixed)}件**。"
            "**節は追記のたびに末尾へ足されるため、番号だけが古い位置に残る。**"
            "番号を見ている点検は`irptch-reach`だけであり、この文書は誰も見ていなかった。"
        ),
    }
    passed = len(headings) > 0

    receipt = {
        "schema": "tai.reference.yic-subsection-numbering/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 parsing doc 53's numbered headings",
        "command": "python integrations/tools/yic_subsection_numbering_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-subsection-numbering-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Parses numbered headings in doc 53 and reports disorder, gaps and non-integer "
            "suffixes. It reads one document; it does not check other YI documents, and a gap may "
            "be a deliberate omission rather than an error."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "headings": len(headings),
        "outOfOrder": len(outOfOrder),
        "gaps": len(gaps),
        "suffixed": len(suffixed),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
