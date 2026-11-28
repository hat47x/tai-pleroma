"""Check whether a receipt's file-name date matches the `date` field inside it.

A receipt is named `<name>-YYYY-MM-DD.json`. The `date` field inside is supposed to be the
day the run happened. If the two differ, the file name points at one version and the body
at another, and a reader who cites the file name cites a date the receipt does not claim.

This measures the mismatch across all receipts and reports how many are affected, so the
size of the repair is known before any file is renamed.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

NAME_DATE = re.compile(r"-(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})(?:\.validate)?\.json$")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    rows = []
    noDate = 0
    for path in sorted((root / "evaluations/records").glob("*.json")):
        match = NAME_DATE.search(path.name)
        if not match:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        date = data.get("date")
        if not date:
            noDate += 1
            continue
        rows.append({
            "receipt": path.name,
            "nameDate": match.group("date"),
            "fieldDate": str(date),
            "agrees": str(date) == match.group("date"),
        })

    mismatched = [row for row in rows if not row["agrees"]]
    byYear = {}
    for row in mismatched:
        key = f"{row['nameDate']} -> {row['fieldDate']}"
        byYear[key] = byYear.get(key, 0) + 1

    checks = {
        "receiptsWithANameDate": len(rows),
        "receiptsWithoutADate": noDate,
        "agreeing": len(rows) - len(mismatched),
        "mismatched": mismatched[:20],
        "mismatchedCount": len(mismatched),
        "mismatchPatterns": sorted(byYear.items(), key=lambda item: -item[1])[:10],
        "finding": (
            f"ファイル名の日付と`date`欄を持つreceipt{len(rows)}件を比べた。"
            f"一致{len(rows) - len(mismatched)}件・**不一致{len(mismatched)}件**。"
            "**ファイル名が指す版と、中身が主張する版が違う。**"
            "読む人がファイル名で日付を判断すると、receiptの主張と食い違う。"
            "**どちらを正とするかは決めていない**（`date`欄を正とするのが自然だが、"
            "改名はreferencesを壊しうる）。"
        ),
    }
    passed = len(rows) > 0

    receipt = {
        "schema": "tai.reference.yic-receipt-name-date/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading every receipt's name and date field",
        "command": "python integrations/tools/yic_receipt_name_date_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-receipt-name-date-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Parses the date out of each receipt's file name and compares it with the `date` "
            "field. It measures the mismatch; it does not rename any file and does not decide "
            "which side is authoritative."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipts": len(rows),
        "agreeing": len(rows) - len(mismatched),
        "mismatched": len(mismatched),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
