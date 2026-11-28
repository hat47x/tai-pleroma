"""Renumber doc 55's §6.8 so the letter suffixes become numbers.

Doc 55's §6.8 reads 6.8.1, 6.8.2, 6.8.2b, 6.8.2c, 6.8.2d, 6.8.3, then a second 6.8.3 whose
content was meant for a different section. Sections were inserted between existing ones
and given letters instead of being renumbered.

No other document cites these numbers, so renumbering changes addresses that nobody uses.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

DOC = "docs/yi-constellation/analysis/55-受信者の欄.md"
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

    # External references to these numbers.
    referenced = []
    for other in list((root / "docs").rglob("*.md")) + list((root / "analysis").rglob("*.md")):
        if other == path:
            continue
        body = other.read_text(encoding="utf-8", errors="replace")
        # A cross-document section reference names this document or uses a § marker.
        # A bare "6.8.0" in another document is a version, not a pointer.
        if "55-受信者の欄" not in body:
            continue
        if re.search(r"(?:§|第)\s*6\.8", body):
            referenced.append(str(other.relative_to(root)))

    lines = text.splitlines()
    counter = 0
    changes = []
    for index, line in enumerate(lines):
        match = HEADING.match(line)
        if not match:
            continue
        parts = match.group("number").split(".")
        if len(parts) != 3 or ".".join(parts[:2]) != "6.8":
            continue
        counter += 1
        new_number = f"6.8.{counter}"
        old = match.group("number")
        if old == new_number:
            continue
        lines[index] = line.replace(
            f"{match.group('hashes')} {old}", f"{match.group('hashes')} {new_number}", 1
        )
        changes.append({"line": index + 1, "old": old, "new": new_number})

    new_text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    if args.apply and not referenced:
        path.write_text(new_text, encoding="utf-8")

    checks = {
        "document": DOC,
        "headingsUnder6_8": counter,
        "changed": changes,
        "referencedElsewhere": referenced,
        "safeToRenumber": not referenced,
        "applied": bool(args.apply and not referenced),
        "finding": (
            f"§6.8の見出し{counter}件を読み順に振り直した。変更{len(changes)}件。"
            f"他の文書からの番号参照は{len(referenced)}件。"
            + ("**参照があるので適用しなかった。**" if referenced else "**参照が無いので適用した。**")
            + "**挿入した節に文字を振るのではなく、全体を振り直すのが番号の規則である。**"
        ),
    }
    passed = counter > 0

    receipt = {
        "schema": "tai.reference.yic-doc55-renumber/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 renumbering doc 55's §6.8 headings",
        "command": "python integrations/tools/yic_doc55_renumber.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-doc55-renumber-2026-11-28.json --apply",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Renumbers the three-deep headings under §6.8 of doc 55 in reading order, applying only "
            "when no other document cites those numbers. It changes heading numbers only and edits "
            "no assertion."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "headings": counter,
        "changed": len(changes),
        "referenced": len(referenced),
        "applied": checks["applied"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
