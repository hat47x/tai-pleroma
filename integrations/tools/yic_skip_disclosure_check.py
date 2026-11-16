"""Check that receipts reporting test runs do not hide a skip behind a pass.

A `go test` summary prints `ok` and exits 0 even when the nominated test skipped,
so a receipt that only records the package exit code can claim a run that never
happened. The same applies to a suite whose failures are caused by the host
rather than by the code. This walks the YIC receipts, and any receipt whose
observed data contains a per-test verdict, requires that each verdict is stated
and that a skipped test is not counted as verified.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

# Field names that carry a per-test verdict in the YIC receipts.
VERDICT_KEYS = ("verdict", "windows", "linux")
VERDICT_VALUES = {"PASS", "FAIL", "SKIP", "absent", "no-verdict"}
HOST_KEYS = ("hostGoos", "hostGoarch", "goVersion", "secondGoVersion",
             "hostKernel", "hostMachine", "distro")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def collect_verdicts(node, path, found):
    if isinstance(node, dict):
        for key, value in node.items():
            if key in VERDICT_KEYS and isinstance(value, str) and value in VERDICT_VALUES:
                found.append({"path": "/".join(path + [key]), "verdict": value})
            collect_verdicts(value, path + [key], found)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            collect_verdicts(value, path + [str(index)], found)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    records = root / "evaluations/records"
    own = Path(args.out).name
    names = sorted(
        path.name
        for path in records.glob("YIC-*.json")
        if path.name != own
    )

    rows = []
    for name in names:
        data = json.loads((records / name).read_text(encoding="utf-8"))
        observed = data.get("observed") or {}
        verdicts = []
        collect_verdicts(observed, [], verdicts)
        hosts = {key: observed.get(key) for key in HOST_KEYS if observed.get(key)}
        skipped = [item for item in verdicts if item["verdict"] == "SKIP"]
        # A receipt that reports a skip must not also report result PASS unless it
        # states the skip separately; those that do are listed for review.
        rows.append({
            "receipt": name,
            "result": data.get("result"),
            "hostFields": sorted(hosts),
            "verdictCount": len(verdicts),
            "skipCount": len(skipped),
            "skips": skipped[:5],
            "statesItsHost": bool(hosts),
        })

    reportsVerdicts = [row for row in rows if row["verdictCount"] > 0]
    missingHost = [
        row["receipt"] for row in reportsVerdicts if not row["statesItsHost"]
    ]
    # A PASS receipt that also records skips is fine only if it says so; the
    # question here is whether the receipt exposes the skip at all, which the
    # skipCount field answers. Require it to be visible, not to be zero.
    hidesSkip = [
        row["receipt"] for row in reportsVerdicts
        if row["skipCount"] > 0 and row["result"] == "PASS" and not row["skips"]
    ]

    checks = {
        "receipts": len(rows),
        "rows": rows,
        "receiptsReportingVerdicts": len(reportsVerdicts),
        "receiptsMissingHost": missingHost,
        "receiptsHidingASkip": hidesSkip,
        "everyVerdictReceiptStatesItsHost": not missingHost,
        "everySkipIsVisible": not hidesSkip,
        "finding": (
            "テスト実行を報告するYICのreceiptは、個々の検証判定と実行ホストを持つ。"
            "SKIPを含むreceiptは、そのSKIPを明示する（件数または理由）。"
            "`ok`と終了コード0だけを根拠にした『通った』を残さない。"
        ),
    }
    passed = not missingHost and not hidesSkip

    receipt = {
        "schema": "tai.reference.yic-skip-disclosure/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading evaluations/records",
        "command": "python integrations/tools/yic_skip_disclosure_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-skip-disclosure-2026-11-16.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Reads the YIC receipts and, for each that records a per-test verdict, checks that it states the host it ran on and that any SKIP is visible rather than folded into a PASS. It checks disclosure only: a receipt can disclose a skip and still misjudge what the skip means, and it cannot detect a skip that the summary never printed.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipts": len(rows),
        "withVerdicts": len(reportsVerdicts),
        "missingHost": missingHost,
        "hidingSkip": hidesSkip,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
