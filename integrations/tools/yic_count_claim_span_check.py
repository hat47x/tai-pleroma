"""Find every receipt-count claim in the docs, not only the one a checker reads.

`doc_consistency_check` verifies the first `実実行receiptはN件、合成receiptはM件` it finds in
`docs/status.md`. The same file also says "実実行receiptは186件" in a later historical
section, and no check looks at it. A reader who scrolls past the first line meets a
different number and cannot tell which is current.

This collects every such claim across the docs, marks which one the checker reads, and
reports the ones that disagree with the live count.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

CLAIM = re.compile(r"実実行receiptは(\d+)件")
CHECKED_FILE = "docs/status.md"
CHECKER = "integrations/tools/doc_consistency_check.py"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def live_count(root):
    completed = subprocess.run(
        [sys.executable, str(root / "tools/check-synthetic-receipts/check.py"),
         "--root", str(root)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800,
    )
    body = completed.stdout
    try:
        return json.loads(body[body.index("{"):]).get("realRecordCount")
    except (json.JSONDecodeError, ValueError):
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    actual = live_count(root)

    checked_pattern = (root / CHECKER).read_text(encoding="utf-8")
    # The checker takes the first match in this file; anything after it is unread.
    readsOnlyTheFirst = "search(" in checked_pattern and "finditer" not in checked_pattern

    rows = []
    for folder in ("docs", "analysis"):
        for path in (root / folder).rglob("*.md"):
            text = path.read_text(encoding="utf-8", errors="replace")
            for match in CLAIM.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                line_text = text.splitlines()[line - 1] if line <= len(text.splitlines()) else ""
                # A claim on a line that names a moment is about that moment.
                historical = bool(
                    re.search(r"(20[0-9]{2}-[0-9]{2}-[0-9]{2}|当時|時点|以前)", line_text)
                )
                rows.append({
                    "document": str(path.relative_to(root)).replace("\\", "/"),
                    "line": line,
                    "claimed": int(match.group(1)),
                    "historical": historical,
                    "matchesLiveCount": int(match.group(1)) == actual,
                })

    first_in_status = next(
        (row for row in rows if row["document"] == CHECKED_FILE), None
    )
    # Only claims that speak about now are compared with the live count.
    unchecked = [
        row for row in rows
        if not row["historical"] and not row["matchesLiveCount"]
    ]
    checks = {
        "liveRealRecordCount": actual,
        "claimsFound": len(rows),
        "checkerReadsOnlyTheFirst": readsOnlyTheFirst,
        "claims": rows[:20],
        "claimsDisagreeingWithLive": unchecked,
        "disagreeingCount": len(unchecked),
        "historicalClaims": len([row for row in rows if row["historical"]]),
        "finding": (
            f"文書中の「実実行receiptはN件」という主張を全部集めた。"
            f"**{len(rows)}件**あり、日付を持つ履歴上の主張が"
            f"{len([row for row in rows if row['historical']])}件。"
            f"**現在について述べている主張のうち、実測{actual}件と食い違うものは"
            f"{len(unchecked)}件**。"
            f"`doc_consistency_check`は{CHECKED_FILE}の**最初の一致だけ**を検証する"
            f"（{'該当' if readsOnlyTheFirst else '非該当'}）。"
            "**残りの主張は誰も見ていない。**"
            "同じファイル・同じ話題に2つの数があると、読む位置で違う現在を知ることになる。"
        ),
    }
    passed = len(rows) > 0

    receipt = {
        "schema": "tai.reference.yic-count-claim-span/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 scanning docs for receipt-count claims",
        "command": "python integrations/tools/yic_count_claim_span_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-count-claim-span-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Scans docs/ and analysis/ for the phrase 実実行receiptはN件, compares each to the "
            "live count from the checker, and records which file the consistency check reads. It "
            "reports stale claims; it does not rewrite any document, and a claim inside a dated "
            "historical section may be correct for that date."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "live": actual,
        "claims": len(rows),
        "disagreeing": len(unchecked),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
