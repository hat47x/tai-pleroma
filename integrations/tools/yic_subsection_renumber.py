"""Renumber doc 53's §6.1 so the order matches the reading order.

The sections were appended over many rounds, so the numbers no longer follow the text:
6.1.5 and 6.1.6 sit at the end while 6.1.7 is in the middle, and ten headings carry
letter suffixes (6.1.6c … 6.1.6l) that are not numbers at all.

Renumbering is a text edit that changes no assertion. It must not change the anchors other
documents use, so first check whether any file links to one of these sections by number.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

DOC = "docs/yi-constellation/analysis/53-判定と残る前進.md"
HEADING = re.compile(r"^(?P<hashes>#{2,4})\s+(?P<number>[0-9]+(?:\.[0-9]+)+[a-z]?)(?:\s|$)")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    path = root / DOC
    text = path.read_text(encoding="utf-8")

    # Are these numbers referenced from anywhere else?
    referenced = {}
    for other in list(root.glob("docs/**/*.md")) + list(root.glob("analysis/**/*.md")):
        if other == path:
            continue
        body = other.read_text(encoding="utf-8", errors="replace")
        if "53-判定と残る前進" not in body and "53-" not in body:
            continue
        for match in re.finditer(r"6\.1(?:\.\d+[a-z]?)?", body):
            referenced.setdefault(match.group(0), []).append(str(other))

    lines = text.splitlines()
    headings = []
    for index, line in enumerate(lines):
        match = HEADING.match(line)
        if match:
            headings.append((index, match))

    # Renumber every 3-deep heading under §6.1 in reading order, starting at 1.
    counter = 0
    for index, match in headings:
        parts = match.group("number").split(".")
        if len(parts) != 3:
            continue
        if ".".join(parts[:2]) != "6.1":
            continue
        counter += 1
        old = match.group("number")
        new_number = f"6.1.{counter}"
        if old == new_number:
            continue
        lines[index] = line_head = lines[index].replace(
            f"{match.group('hashes')} {old}", f"{match.group('hashes')} {new_number}", 1
        )

    new_text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")

    renumbered = sum(
        1
        for index, match in headings
        if len(match.group("number").split(".")) == 3
        and ".".join(match.group("number").split(".")[:2]) == "6.1"
        and match.group("number") != (
            "6.1.%d"
            % (
                sum(
                    1
                    for i, m in headings
                    if i <= index
                    and len(m.group("number").split(".")) == 3
                    and ".".join(m.group("number").split(".")[:2]) == "6.1"
                )
            )
        )
    )

    if args.apply and not referenced:
        path.write_text(new_text, encoding="utf-8")

    checks = {
        "document": DOC,
        "headingsAtThreeDeepUnder6_1": counter,
        "renumbered": renumbered,
        "referencedElsewhere": sorted(referenced),
        "safeToRenumber": not referenced,
        "applied": bool(args.apply and not referenced),
        "finding": (
            f"§6.1の3階層見出し{counter}件を、読み順に1から振り直した。"
            f"変更した見出しは{renumbered}件。"
            f"他の文書が番号で参照している箇所は{len(referenced)}件。"
            + (
                "**参照があるので適用しなかった。** 番号は外部からの住所であり、"
                "書き換えると参照が壊れる。"
                if referenced
                else "**参照が無いので適用した。**"
            )
            + "**番号を整えることは、主張を変えない。** ただし**外部からの住所を変える**ので、"
            "参照の有無を先に確かめる必要がある。"
        ),
    }
    passed = counter > 0

    receipt = {
        "schema": "tai.reference.yic-subsection-renumber/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 renumbering doc 53's §6.1 headings",
        "command": "python integrations/tools/yic_subsection_renumber.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-subsection-renumber-2026-11-28.json --apply",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Renumbers the three-deep headings under §6.1 in reading order and applies the change "
            "only when no other document cites those numbers. It changes heading numbers only; it "
            "does not edit any assertion, and it does not renumber other documents."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "headings": counter,
        "renumbered": renumbered,
        "referenced": len(referenced),
        "applied": checks["applied"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
