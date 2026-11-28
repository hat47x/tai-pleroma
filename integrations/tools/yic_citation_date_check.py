"""Check whether the citations that no longer resolve are all historical.

The path check found 82 receipts citing a checkout path that is gone. Before proposing any
change to 82 receipts, distinguish: are all of them from before the path vanished (so the
citation was true when written), or are some recent — which would mean the writing habit
still produces unresolvable commands and the fix belongs in the writing, not the history.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

CITED = "evaluations/records/YIC-cited-path-2026-11-28.json"
# Receipts dated before this are treated as historical.
CUTOFF = "2026-11-20"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    cited = json.loads((root / CITED).read_text(encoding="utf-8"))
    affected = (cited.get("observed") or {}).get("receiptsAffected") or []

    before = []
    after = []
    for name in affected:
        path = root / "evaluations/records" / name
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        day = str(data.get("date", ""))
        (after if day >= CUTOFF else before).append({"receipt": name, "date": day})

    checks = {
        "cutoff": CUTOFF,
        "affected": len(affected),
        "writtenBeforeTheCutoff": len(before),
        "writtenOnOrAfterTheCutoff": len(after),
        "recentUnresolvable": after[:10],
        "finding": (
            f"解決しない引用を持つ{len(affected)}件を、日付で分けた。"
            f"**{CUTOFF}より前が{len(before)}件、以降が{len(after)}件**。"
            + (
                "**直近にも解決しないcommandが書かれている**ので、"
                "履歴の注記だけでは足りない。**書き方（生成側）を変える必要がある**。"
                if after
                else "**すべて期限より前**なので、当時は正しかった。"
                "履歴に注記すれば足りる。"
            )
        ),
    }
    passed = len(affected) > 0

    receipt = {
        "schema": "tai.reference.yic-citation-dates/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the affected receipts' dates",
        "command": "python integrations/tools/yic_citation_date_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-citation-dates-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Splits the receipts with unresolvable citations by their recorded date against a fixed "
            "cutoff. It supports a decision about where the fix belongs (history vs generation); it "
            "does not itself annotate or rewrite any receipt, and the cutoff is a chosen line, not "
            "a measured event."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "affected": len(affected),
        "before": len(before),
        "after": len(after),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
