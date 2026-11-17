"""Run the gates a new receipt must survive, in one command.

A receipt was merged twice while only the syntax checker had been run: it passed
`check.py` but broke `receipt_consistency`, which lives inside the suite and is
easy to forget outside it. These gates are cheap, they judge receipts, and a new
receipt can break any of them. This runs them together and refuses to report PASS
if one is skipped.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Gate, script, and the question it answers about a receipt.
GATES = (
    ("checker", "tools/check-synthetic-receipts/check.py",
     "the receipt is registered and shaped as declared", ["--root", "."]),
    ("scope", "integrations/tools/receipt_scope_check.py",
     "the scope states what was measured and what was not", []),
    ("consistency", "integrations/tools/receipt_consistency_check.py",
     "a PASS receipt does not contradict its own observations", []),
    ("auditability", "integrations/tools/yi_receipt_auditability_check.py",
     "the receipt carries the five required fields", []),
    ("crossReceipt", "integrations/tools/yi_cross_receipt_check.py",
     "facts shared with other receipts agree", []),
    ("artifactDigest", "integrations/tools/yi_artifact_digest_check.py",
     "the recorded artifact digest is still current", []),
    ("limitsKept", "integrations/tools/yic_authority_limits_check.py",
     "Product-declared limits are not dropped", []),
    ("skipDisclosure", "integrations/tools/yic_skip_disclosure_check.py",
     "a skip is visible rather than folded into a pass", []),
)
# Each gate writes its own receipt; the aggregate reads their exit codes.
OUTPUTS = {
    "scope": "TEI-receipt-scope-2026-11-06.json",
    "consistency": "TEI-receipt-consistency-2026-11-06.json",
    "auditability": "YI-receipt-auditability-2026-11-11.json",
    "crossReceipt": "YI-cross-receipt-2026-11-11.json",
    "artifactDigest": "YI-artifact-digest-2026-11-11.json",
    "limitsKept": "YIC-authority-limits-2026-11-16.json",
    "skipDisclosure": "YIC-skip-disclosure-2026-11-16.json",
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    results = {}
    for name, script, question, extra in GATES:
        path = root / script
        if not path.exists():
            results[name] = {"ran": False, "reason": "script missing", "question": question}
            continue
        command = [sys.executable, str(path)]
        if name == "checker":
            command += extra
        else:
            command += ["--artifact", args.artifact,
                        "--out", str(root / "evaluations/records" / OUTPUTS[name])]
        completed = subprocess.run(
            command, cwd=root, capture_output=True, text=True,
            encoding="utf-8", errors="replace", env={**os.environ},
        )
        tail = (completed.stdout or "").strip().splitlines()
        results[name] = {
            "ran": True,
            "question": question,
            "exit": completed.returncode,
            "passed": completed.returncode == 0,
            "tail": tail[-1][:200] if tail else "",
        }

    missing = [name for name, item in results.items() if not item["ran"]]
    failed = [name for name, item in results.items() if item["ran"] and not item["passed"]]
    checks = {
        "gatesRequested": len(GATES),
        "gatesRun": len([item for item in results.values() if item["ran"]]),
        "results": results,
        "scriptsMissing": missing,
        "failed": failed,
        "everyGateRan": not missing,
        "everyGatePassed": not failed,
        "finding": (
            "新しいreceiptは、構文checkerだけでなく、scope・一貫性・監査可能性・"
            "相互整合・artifact digest・限界保持・SKIP開示の各ゲートを通す必要がある。"
            "過去にcheckerだけ通してマージし、suite内でしか走らない一貫性検査を"
            "壊した事例があるため、これらを1コマンドにまとめた。"
        ),
    }
    passed = not missing and not failed

    receipt = {
        "schema": "tai.reference.yic-receipt-gates/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 running the receipt gates together",
        "command": "python integrations/tools/yic_receipt_gates.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-receipt-gates-2026-11-17.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs eight receipt gates in one pass and refuses PASS if any is missing or fails. It "
            "records whether each gate ran and its exit code, not what each concluded; a gate that "
            "passes can still judge the wrong thing, and this aggregate inherits every limit of the "
            "eight."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gates": checks["gatesRun"],
        "failed": failed,
        "missing": missing,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
