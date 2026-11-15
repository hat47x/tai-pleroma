"""Run the receipt-quality checks in one pass, and refuse to report PASS if any is missing.

Four separate checks now judge the YI receipts: auditability (does each carry the
five fields), scope halves (does each state a limit), cross-receipt (do
overlapping facts agree), artifact digest (is the recorded digest still current),
and pass consistency (does a PASS receipt explain its gaps). Running them one by
one lets one be skipped silently. This runs them together and records each.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Each check, with what it answers.
CHECKS = (
    ("auditability", "yi_receipt_auditability_check.py", "each receipt carries the five fields"),
    ("scopeHalves", "yi_scope_halves_check.py", "each scope states what was and was not measured"),
    ("crossReceipt", "yi_cross_receipt_check.py", "overlapping facts agree"),
    ("artifactDigest", "yi_artifact_digest_check.py", "the recorded artifact digest is current"),
    ("passConsistency", "yi_pass_consistency_check.py", "a PASS receipt explains its gaps"),
)
# The receipts each check writes; the aggregate reads their results.
OUTPUTS = {
    "auditability": "YI-receipt-auditability-2026-11-11.json",
    "scopeHalves": "YI-scope-halves-2026-11-11.json",
    "crossReceipt": "YI-cross-receipt-2026-11-11.json",
    "artifactDigest": "YI-artifact-digest-2026-11-11.json",
    "passConsistency": "YI-pass-consistency-2026-11-11.json",
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    tools = root / "integrations/tools"
    records = root / "evaluations/records"

    results = {}
    for name, script, question in CHECKS:
        script_path = tools / script
        if not script_path.exists():
            results[name] = {"ran": False, "reason": "script missing", "question": question}
            continue
        completed = subprocess.run(
            [
                sys.executable, str(script_path),
                "--artifact", args.artifact,
                "--out", str(records / OUTPUTS[name]),
            ],
            cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
            env={**os.environ},
        )
        output = (completed.stdout or "").strip().splitlines()
        results[name] = {
            "ran": True,
            "question": question,
            "exit": completed.returncode,
            "passed": completed.returncode == 0,
            "tail": output[-1][:160] if output else "",
        }

    missing = [name for name, item in results.items() if not item["ran"]]
    failed = [name for name, item in results.items() if item["ran"] and not item["passed"]]

    checks = {
        "checksRun": len([item for item in results.values() if item["ran"]]),
        "results": results,
        "scriptsMissing": missing,
        "failed": failed,
        "everyQualityCheckRan": not missing,
        "everyQualityCheckPassed": not failed,
    }
    passed = not missing and not failed

    receipt = {
        "schema": "tai.reference.yi-receipt-quality/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 running the five receipt-quality checks",
        "command": "python integrations/tools/yi_receipt_quality.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-receipt-quality-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Runs the five receipt-quality checks in one pass and refuses PASS if any is missing or fails. It records whether each ran and its exit code, not what each concluded; a check that passes can still be measuring the wrong thing, and this aggregate inherits every lexical limit of the five.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ran": checks["checksRun"],
        "failed": failed,
        "missing": missing,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
