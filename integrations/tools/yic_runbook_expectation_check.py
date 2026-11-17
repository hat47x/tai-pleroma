"""Check that the runbook's expected-output block matches what the gates report.

The block had drifted to "184 real receipts / 97 steps" while the checker reported
244 and the suite 107. A reader following the runbook would compare their output
against numbers that could never match, and the honest conclusion from that is
"something is wrong", which is the opposite of what a stale block should cause.
This reads the block and compares each number with the live value.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

RUNBOOK = "docs/reproduction-runbook.md"
STATUS = "docs/status.md"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    runbook = (root / RUNBOOK).read_text(encoding="utf-8")

    # The block that tells a reader what a correct run prints.
    block_match = re.search(r"## 4\. 期待する結果\s*\n\s*```text\n(.*?)```", runbook, re.S)
    if not block_match:
        print("expected-result block not found", file=sys.stderr)
        return 1
    block = block_match.group(1)

    claimed_steps = re.search(r"suite:\s*(\d+)段", block)
    claimed_synthetic = re.search(r"checker:\s*合成(\d+)件", block)
    claimed_real = re.search(r"checker:.*実実行(\d+)件", block)
    claimed_doc_steps = re.search(r"doc整合:.*（(\d+)段", block)
    claimed_doc_real = re.search(r"doc整合:.*実実行(\d+)件", block)

    # Live values: the checker reports both counts; the suite receipt reports steps.
    checker = subprocess.run(
        [sys.executable, str(root / "tools/check-synthetic-receipts/check.py"),
         "--root", str(root)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    payload = json.loads(checker.stdout)
    actual_synthetic = payload["recordCount"]
    actual_real = payload["realRecordCount"]

    suite = json.loads(
        (root / "evaluations/records/TEI-suite-2026-11-03.json").read_text(encoding="utf-8")
    )
    actual_steps = len(suite.get("steps") or {})

    status = (root / STATUS).read_text(encoding="utf-8")
    status_counts = re.search(r"実実行receiptは(\d+)件、合成receiptは(\d+)件", status)
    documented_real = int(status_counts.group(1)) if status_counts else None
    documented_synthetic = int(status_counts.group(2)) if status_counts else None

    comparisons = [
        {
            "value": "suite steps",
            "claimed": int(claimed_steps.group(1)) if claimed_steps else None,
            "actual": actual_steps,
        },
        {
            "value": "checker synthetic",
            "claimed": int(claimed_synthetic.group(1)) if claimed_synthetic else None,
            "actual": actual_synthetic,
        },
        {
            "value": "checker real",
            "claimed": int(claimed_real.group(1)) if claimed_real else None,
            "actual": actual_real,
        },
        {
            "value": "doc steps",
            "claimed": int(claimed_doc_steps.group(1)) if claimed_doc_steps else None,
            "actual": actual_steps,
        },
        {
            "value": "doc real (status.md)",
            "claimed": int(claimed_doc_real.group(1)) if claimed_doc_real else None,
            "actual": documented_real,
        },
    ]
    stale = [item for item in comparisons if item["claimed"] != item["actual"]]

    checks = {
        "runbook": RUNBOOK,
        "block": block.strip(),
        "comparisons": comparisons,
        "staleValues": stale,
        "everyExpectedValueMatches": not stale,
        "finding": (
            "runbookの「期待する結果」は、実行した読者が自分の出力と比べる基準である。"
            "ここが古いと、正しく実行した読者が「何かがおかしい」と誤って判断する。"
            "段数とreceipt件数を、checker・suite receipt・status.mdの現在値と突き合わせる。"
        ),
    }
    passed = not stale

    receipt = {
        "schema": "tai.reference.yic-runbook-expectation/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the runbook and the live counts",
        "command": "python integrations/tools/yic_runbook_expectation_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-runbook-expectation-2026-11-17.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Compares the numbers in the runbook's expected-output block with the live checker and "
            "suite counts. It checks those five numbers only; prose elsewhere in the runbook, and "
            "whether the commands themselves would succeed on another host, are not examined."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "stale": [item["value"] for item in stale],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
