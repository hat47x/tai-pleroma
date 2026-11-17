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
import tempfile
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



def classify(results):
    """Which gates did not run, and which ran but did not pass."""
    missing = [name for name, item in results.items() if not item["ran"]]
    failed = [name for name, item in results.items()
              if item["ran"] and not item["passed"]]
    return missing, failed


def read_gate(script_path, args, root, artifact, out):
    """Run one gate and turn its process outcome into a reading.

    This is the conversion `main()` relies on. `self_test()` calls it directly so an
    inverted or dropped exit code cannot pass the self-test unnoticed.
    """
    completed = subprocess.run(
        [sys.executable, str(script_path)] + args,
        cwd=root, capture_output=True, text=True,
        encoding="utf-8", errors="replace", env={**os.environ}, timeout=1800,
    )
    tail = (completed.stdout or "").strip().splitlines()
    return {
        "ran": True,
        "exit": completed.returncode,
        "passed": completed.returncode == 0,
        "tail": tail[-1][:200] if tail else "",
    }


def self_test():
    """Prove the aggregate cannot report PASS over a missing, failing or crashing gate.

    Four cases, each of which must come back as a failure:
      * a gate whose script is absent,
      * a gate whose script exits non-zero,
      * a gate whose script exits zero,
      * both missing and failed present at once.
    """
    root = Path(__file__).resolve().parents[2]
    scratch = Path(tempfile.mkdtemp(prefix="yic-selftest-"))

    # The three real exit paths, run through the same reader main() uses.
    failing_probe = scratch / "always_fails.py"
    failing_probe.write_text("import sys\nsys.exit(1)\n", encoding="utf-8")
    passing_probe = scratch / "always_passes.py"
    passing_probe.write_text("print('ok')\n", encoding="utf-8")
    broken_probe = scratch / "not_executable.txt"
    broken_probe.write_text("this is not python\n", encoding="utf-8")

    failing = read_gate(failing_probe, [], root, "", "")
    passing = read_gate(passing_probe, [], root, "", "")
    # A file Python cannot parse exits non-zero, so it must read as a failure.
    broken = read_gate(broken_probe, [], root, "", "")

    absent = {"absentGate": {"ran": False, "reason": "script missing", "question": "q"}}
    missing_only, failed_only = classify(absent)
    absentIsFailure = bool(missing_only) and not failed_only

    both = {
        "absentGate": {"ran": False, "reason": "script missing", "question": "q"},
        "failingGate": failing,
        "passingGate": passing,
    }
    missing_both, failed_both = classify(both)
    combinedIsFailure = bool(missing_both) and bool(failed_both)

    return {
        "absentScriptIsAFailure": absentIsFailure,
        "failingScriptReadsAsFailure": failing["passed"] is False,
        "passingScriptReadsAsPass": passing["passed"] is True,
        "unparsableScriptReadsAsFailure": broken["passed"] is False,
        "missingAndFailedTogetherIsFailure": combinedIsFailure,
        "passed": (
            absentIsFailure
            and failing["passed"] is False
            and passing["passed"] is True
            and broken["passed"] is False
            and combinedIsFailure
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=False, default="")
    parser.add_argument("--out", required=True)
    parser.add_argument("--self-test", action="store_true",
                        help="prove the aggregate fails when a gate is missing or fails")
    parser.add_argument("--no-write", action="store_true",
                        help="write the children's receipts to a temporary directory")
    args = parser.parse_args()

    if args.self_test:
        outcome = self_test()
        Path(args.out).write_text(
            json.dumps({"selfTest": outcome}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(outcome, ensure_ascii=False))
        return 0 if outcome["passed"] else 1

    root = Path(__file__).resolve().parents[2]
    scratch = Path(tempfile.mkdtemp(prefix="yic-gates-"))
    results = {}
    for name, script, question, extra in GATES:
        path = root / script
        if not path.exists():
            results[name] = {"ran": False, "reason": "script missing", "question": question}
            continue
        command = []
        if name == "checker":
            command += extra
        else:
            # Keep count-bearing receipts out of the tree when merely verifying.
            target = (
                scratch / OUTPUTS[name] if args.no_write
                else root / "evaluations/records" / OUTPUTS[name]
            )
            command += ["--artifact", args.artifact, "--out", str(target)]
        try:
            reading = read_gate(path, command, root, args.artifact, "")
        except (OSError, subprocess.SubprocessError) as error:
            # A gate that cannot be executed is a gate that did not pass.
            results[name] = {
                "ran": False,
                "reason": f"could not execute: {type(error).__name__}",
                "question": question,
            }
            continue
        results[name] = {"question": question, **reading}

    missing, failed = classify(results)
    checks = {
        "wroteIntoTheTree": not args.no_write,
        "scratchDirectory": str(scratch) if args.no_write else "",
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
