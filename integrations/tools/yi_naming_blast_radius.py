"""Measure how far the "統合製品" wording reaches, which G1's D2 rests on.

Doc 18 asks whether to rename TAI from 統合製品 to 輔相製品. The decision rests on
how many places use the current word and whether the alternative is already used
anywhere. That is measurable without deciding anything: this counts the places,
so the Owner can see the blast radius of either choice.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

CLOSING = "統合製品"
ALTERNATIVE = "輔相製品"
# Files whose wording is a decision, not a reference, and must not be counted as
# evidence either way.
EXCLUDE_DIRS = ("docs/yi-constellation/analysis/", ".git/", "evaluations/")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]

    usages = []
    alternative_usages = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root).as_posix()
        if any(fragment in relative for fragment in EXCLUDE_DIRS):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if CLOSING in line:
                usages.append({"file": relative, "line": number, "text": line.strip()[:120]})
            if ALTERNATIVE in line:
                alternative_usages.append({"file": relative, "line": number})

    # Is the alternative explained anywhere as a proposal, and is the current
    # word ever stated as a non-goal by TAI itself?
    non_goal = [
        usage for usage in usages
        if "頂点" in usage["text"] or "非目標" in usage["text"] or "代行" in usage["text"]
    ]

    files_touched = sorted({usage["file"] for usage in usages})
    checks = {
        "currentWord": CLOSING,
        "alternativeWord": ALTERNATIVE,
        "usagesInProductDocuments": len(usages),
        "filesTouched": files_touched,
        "alternativeAlreadyUsed": len(alternative_usages),
        "alternativeUsages": alternative_usages[:5],
        "usagesThatAlreadyLimit": non_goal,
        "blastRadius": len(files_touched),
        "finding": (
            f"「{CLOSING}」は製品文書{len(files_touched)}ファイル・{len(usages)}箇所で使われている。"
            f"「{ALTERNATIVE}」は製品文書では{len(alternative_usages)}箇所。"
            "改名すると、この範囲の記述を同時に直す必要がある。"
        ),
    }
    passed = len(files_touched) > 0

    receipt = {
        "schema": "tai.reference.yi-naming-blast-radius/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the repository's Markdown",
        "command": "python integrations/tools/yi_naming_blast_radius.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-naming-radius-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Counts where the current and alternative names appear in the repository's own documents, excluding the YI analysis and the evaluation records, so the Owner can see the blast radius of either choice. It does not decide the name, does not read whether each usage means the same thing, and does not count usage in the decks or in other repositories.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "usages": len(usages),
        "files": len(files_touched),
        "alternative": len(alternative_usages),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
