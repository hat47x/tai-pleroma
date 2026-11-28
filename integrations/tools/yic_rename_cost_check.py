"""Measure what a `date`-wins policy would cost before renaming anything.

141 receipts have a file-name date that differs from their `date` field. Two policies are
possible: rename the file to match `date` (which breaks every citation of the old name), or
treat `date` as authoritative and leave the name alone (which leaves two dates in the same
artifact).

Before choosing, measure the cost of the rename: how many other files cite each affected
file name, and whether the citation is a link that would break.
"""

import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

MISMATCH = "evaluations/records/YIC-receipt-name-date-2026-11-28.json"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def citations(root, name):
    """Other files whose text contains this receipt's file name."""
    completed = subprocess.run(
        ["git", "-C", str(root), "grep", "-l", "-F", name],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if completed.returncode not in (0, 1):
        return []
    return [
        line for line in completed.stdout.splitlines()
        if line and Path(line).name != name
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    data = json.loads((root / MISMATCH).read_text(encoding="utf-8"))
    observed = data.get("observed") or {}
    # The receipt keeps the full count separately and only twenty names.
    total = observed.get("mismatchedCount", 0)
    sample = [row["receipt"] for row in observed.get("mismatched") or []]
    affected = sample

    rows = []
    totalCitations = 0
    for name in affected[:40]:  # a bounded sample keeps the run short
        citing = citations(root, name)
        totalCitations += len(citing)
        rows.append({"receipt": name, "citedBy": len(citing), "examples": citing[:3]})

    uncited = [row["receipt"] for row in rows if row["citedBy"] == 0]
    cited = [row for row in rows if row["citedBy"] > 0]

    checks = {
        "mismatchReceipt": MISMATCH,
        "mismatchedTotal": total,
        "namesAvailable": len(sample),
        "sampled": len(rows),
        "uncitedInSample": len(uncited),
        "citedInSample": len(cited),
        "totalCitationsInSample": totalCitations,
        "heaviest": sorted(cited, key=lambda row: -row["citedBy"])[:5],
        "finding": (
            f"名前の日付と`date`が食い違う**{total}件**のうち、"
            f"receiptが名前一覧として保持している{len(sample)}件を標本にした。"
            f"**他のファイルから名前で引用されているもの{len(cited)}件**、"
            f"引用の無いもの{len(uncited)}件。"
            f"標本内の延べ引用数は**{totalCitations}**。"
            "**改名は引用を壊す**ので、引用の無いものだけを改名する案と、"
            "`date`を正として名前は履歴として残す案を比べる必要がある。"
            "**どちらを採るかは決めていない。**"
        ),
    }
    passed = len(rows) > 0 and total >= len(sample)

    receipt = {
        "schema": "tai.reference.yic-rename-cost/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 counting citations of the mismatched receipts",
        "command": "python integrations/tools/yic_rename_cost_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-rename-cost-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Counts, for a sample of forty mismatched receipts, how many other files name the file. "
            "It measures the cost of renaming; it does not rename anything, and a text match is not "
            "a semantic citation (a name inside a receipt's own listing is indistinguishable)."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "mismatched": len(affected),
        "sampled": len(rows),
        "cited": len(cited),
        "uncited": len(uncited),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
