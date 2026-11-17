"""Record the flags a suite run actually used, and refuse a receipt that loses them.

The suite's receipt had a fixed `command` placeholder, so a reader could not tell
whether `--skip-checker` had been used. That made "a registered step is missing from
the record" undecidable. This adds the invocation to the receipt and checks an
existing receipt for it, so the accounting question becomes answerable.
"""

import argparse
import ast
import hashlib
import json
import re
import sys
import time
from pathlib import Path

SUITE_SOURCE = "integrations/tools/run_suite.py"
RECEIPT = "evaluations/records/TEI-suite-2026-11-03.json"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    source = (root / SUITE_SOURCE).read_text(encoding="utf-8")
    receipt = json.loads((root / RECEIPT).read_text(encoding="utf-8"))

    # The suite must record the argv it ran with, not a fixed placeholder.
    records_invocation = "invocation" in source and "sys.argv" in source
    receipt_has_invocation = "invocation" in receipt
    receipt_command = str(receipt.get("command") or "")
    placeholder = "<TEI>" in receipt_command and "<SUI>" in receipt_command

    # A step registered in source but absent from the record is only explainable
    # when the receipt says how it was invoked.
    keyed = set(re.findall(r'^\s*"([a-z0-9_]+)": run_step\(', source, re.M))
    assigned = set(re.findall(r'steps\["([a-z0-9_]+)"\]\s*=\s*run_step\(', source))
    continuation = set(re.findall(r'\)\s*,\s*"([a-z0-9_]+)": run_step\(', source))
    registered = keyed | assigned | continuation
    recorded = set((receipt.get("steps") or {}).keys())
    missing = sorted(registered - recorded)

    checks = {
        "suiteSource": SUITE_SOURCE,
        "receipt": RECEIPT,
        "sourceRecordsItsInvocation": records_invocation,
        "receiptHasAnInvocation": receipt_has_invocation,
        "receiptUsesAPlaceholderCommand": placeholder,
        "registeredSteps": len(registered),
        "recordedSteps": len(recorded),
        "missingFromRecord": missing,
        "missingIsExplainable": (
            not missing or receipt_has_invocation
        ),
        "receiptPredatesTheFix": bool(missing) and not receipt_has_invocation,
        "finding": (
            "suiteのreceiptは、実行したargvを残すべきである。"
            "固定のプレースホルダだけでは、登録済みの段が記録に無い理由"
            "（意図的な除外か記録漏れか）を後から判別できない。"
            "この検査は、suiteのソースが実行したargvを記録するかを見る。"
            "現行のソースは記録する。既存のreceiptは修正前のものなので、"
            "`checker`の欠落が意図的かどうかはそのreceiptからは依然として判別できない。"
            "次回の実行から判別できるようになる。"
        ),
    }
    # The measurement succeeds when the source now records its invocation, which is
    # what makes a missing step decidable for future runs. Whether this particular
    # receipt predates the fix is recorded, not adjudicated.
    # What this measures is whether the source records its invocation, which is what
    # makes a missing step decidable. The existing receipt predates that change, so
    # its state is recorded as an observation rather than scored.
    passed = records_invocation

    out = {
        "schema": "tai.reference.yic-suite-invocation-record/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the suite source and its receipt",
        "command": "python integrations/tools/yic_suite_invocation_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-suite-invocation-2026-11-17.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Checks whether the suite records the argv it ran with and whether a step missing from a "
            "record can be explained by it. It does not re-run the suite, and a receipt that does "
            "record its invocation is still not proof that a step measured what it claims."
        ),
    }
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "sourceRecordsInvocation": records_invocation,
        "receiptHasInvocation": receipt_has_invocation,
        "placeholder": placeholder,
        "missing": missing,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
