"""Check that the documented suite size and receipt counts match the records."""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUITE_RECEIPT = ROOT / "evaluations/records/TEI-suite-2026-11-03.json"


def recorded_suite():
    payload = json.loads(SUITE_RECEIPT.read_text(encoding="utf-8"))
    return len(payload.get("steps", {})), payload.get("result")


def documented_step_count():
    readme = (ROOT / "integrations/tools/README.md").read_text(encoding="utf-8")
    match = re.search(r"(\d+)段", readme)
    return int(match.group(1)) if match else None


def receipt_counts():
    checker = ROOT / "tools/check-synthetic-receipts/check.py"
    completed = subprocess.run(
        [sys.executable, str(checker), "--root", str(ROOT)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    payload = json.loads(completed.stdout)
    return payload["recordCount"], payload["realRecordCount"]


def documented_receipt_counts():
    status = (ROOT / "docs/status.md").read_text(encoding="utf-8")
    match = re.search(r"実実行receiptは(\d+)件、合成receiptは(\d+)件", status)
    if not match:
        return None
    return int(match.group(2)), int(match.group(1))


def main():
    recorded_steps, recorded_result = recorded_suite()
    documented_steps = documented_step_count()
    synthetic, real = receipt_counts()
    documented = documented_receipt_counts()

    checks = {
        "recordedSteps": recorded_steps,
        "recordedResult": recorded_result,
        "documentedSteps": documented_steps,
        "records": synthetic,
        "realRecords": real,
        "documentedSynthetic": documented[0] if documented else None,
        "documentedReal": documented[1] if documented else None,
    }
    passed = (
        recorded_result == "PASS"
        and documented_steps is not None
        and documented_steps == recorded_steps
        and documented is not None
        and documented[0] == synthetic
        and documented[1] == real
    )
    print(json.dumps({"passed": passed, "checks": checks}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
