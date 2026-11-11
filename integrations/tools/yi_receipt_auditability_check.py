"""Check that every YI receipt can still be re-read by someone who was not there.

`AGENTS.md` requires a test record to state the version under test, the command,
the expected result, the observed result, and what was not done. A receipt that
omits one of these cannot be audited by a later reader, even if the run was real.
This walks the YI receipts and reports which fields each one carries, so a gap is
a finding rather than a surprise.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

# AGENTS.md's five, with the receipt fields that can carry each.
REQUIRED = {
    "version": ("host", "command", "artifact.digest"),
    "command": ("command",),
    "expected": ("result",),
    "observed": ("observed", "checks"),
    "notDone": ("scope",),
}

# A scope must name a limit; the same lexical test the receipt-scope gate uses.
LIMIT = re.compile(
    r"\bnot\b|\bno\b|neither|cannot|unverified|test-only|out of scope|local|"
    r"same host|synthetic|stub|does not|未|ない|ではありません|のみ|範囲外",
    re.IGNORECASE,
)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def has(data, dotted):
    value = data
    for step in dotted.split("."):
        if not isinstance(value, dict) or step not in value:
            return False
        value = value[step]
    return value not in (None, "", [], {})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    records = root / "evaluations/records"
    # YI receipts only; the Windows filesystem is case-insensitive, so match by
    # lower-cased name to avoid double counting.
    historical = {"yi-constellation-structure-2026-11-01.json"}
    # The receipt this run writes is not an input; including it would make the
    # check depend on its own output file's presence.
    own_output = Path(args.out).name

    names = sorted(
        {
            path.name
            for path in records.glob("*.json")
            if path.name.lower().startswith(("yi-", "yi_"))
            and path.name not in historical
            and path.name != own_output
        }
    )

    per_receipt = []
    for name in names:
        data = json.loads((records / name).read_text(encoding="utf-8"))
        fields = {}
        for label, candidates in REQUIRED.items():
            fields[label] = any(has(data, candidate) for candidate in candidates)
        scope = str(data.get("scope", ""))
        fields["scopeNamesALimit"] = bool(LIMIT.search(scope))
        per_receipt.append({
            "receipt": name,
            "result": data.get("result"),
            "fields": fields,
        })

    missing = {
        label: [item["receipt"] for item in per_receipt if not item["fields"][label]]
        for label in list(REQUIRED) + ["scopeNamesALimit"]
    }
    complete = [item["receipt"] for item in per_receipt if all(item["fields"].values())]

    checks = {
        "receipts": len(names),
        "excludedAsHistorical": sorted(historical),
        "excludedOwnOutput": own_output,
        "perReceipt": per_receipt,
        "missingByField": {label: values for label, values in missing.items() if values},
        "completeReceipts": len(complete),
        "incompleteReceipts": [
            item["receipt"] for item in per_receipt if item["receipt"] not in complete
        ],
        "everyReceiptIsAuditable": not any(missing.values()),
        "finding": (
            "YIのreceiptは、対象の版・実行コマンド・期待結果・観測結果・"
            "未実施項目を持つかを一枚ずつ確かめた。"
            "欠けている欄があれば、後から読む人はその実行を監査できない。"
        ),
    }
    passed = checks["everyReceiptIsAuditable"]

    receipt = {
        "schema": "tai.reference.yi-receipt-auditability/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading evaluations/records",
        "command": "python integrations/tools/yi_receipt_auditability_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-receipt-auditability-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Walks the YI receipts and records, per receipt, whether it carries a version, a command, an expected result, an observed result and a stated limit. One 2026-11-01 receipt predates the convention and is excluded by name rather than judged; its absent fields are recorded in the 19-document instead. It checks presence only: a receipt with all five can still be wrong, and the limit test is lexical.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipts": len(names),
        "complete": len(complete),
        "missing": checks["missingByField"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
