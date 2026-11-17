"""Check that running the gates twice in a row produces the same receipts.

The gates are re-run whenever a receipt is added, and each run rewrites its own
receipt. If those rewrites differ between runs, a reviewer cannot tell a real
change from regeneration churn, and the diff noise hides the change that mattered.
This runs the aggregate twice and compares the receipts it writes.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

GATES = "integrations/tools/yic_receipt_gates.py"
# Read from the aggregate so this list cannot drift from what it actually writes.
GATES_SOURCE = "integrations/tools/yic_receipt_gates.py"
AGGREGATE_RECEIPT = "evaluations/records/YIC-receipt-gates-2026-11-17.json"


def receipts_written_by_gates(root):
    """Every receipt the aggregate writes, taken from its own OUTPUTS table."""
    source = (root / GATES_SOURCE).read_text(encoding="utf-8")
    match = re.search(r"OUTPUTS = \{(.*?)\}", source, re.S)
    if not match:
        raise SystemExit("could not read OUTPUTS from the aggregate")
    # Entries look like `"gate": "receipt.json"; take the right-hand side only.
    files = re.findall(r'"[^"]+"\s*:\s*"([^"]+\.json)"', match.group(1))
    if not files:
        raise SystemExit("OUTPUTS in the aggregate has no receipt filenames")
    return tuple(f"evaluations/records/{name}" for name in files)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def snapshot(root, names):
    return {name: digest(root / name) for name in names}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    gates = root / GATES
    if not gates.exists():
        print(f"missing {GATES}", file=sys.stderr)
        return 1

    outputs = []
    for run in (1, 2):
        target = root / "evaluations/records/YIC-receipt-gates-2026-11-17.json"
        completed = subprocess.run(
            [sys.executable, str(gates), "--artifact", args.artifact, "--out", str(target)],
            cwd=root, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        if completed.returncode != 0:
            print(completed.stdout, completed.stderr, file=sys.stderr)
            return 1
        names = receipts_written_by_gates(root)
        outputs.append({
            "run": run,
            "receipts": snapshot(root, names + (AGGREGATE_RECEIPT,)),
        })

    first, second = outputs[0]["receipts"], outputs[1]["receipts"]
    unstable = sorted(
        name for name in first
        if first[name] != second.get(name)
    )

    checks = {
        "gatesScript": GATES,
        "receiptsCompared": len(first),
        "receiptsFromAggregateTable": len(first) - 1,
        "run1": first,
        "run2": second,
        "unstableReceipts": unstable,
        "runsAreReproducible": not unstable,
        "finding": (
            "ゲートを2回続けて実行し、書き出されるreceiptが同じかを見る。"
            "同じreceiptを再実行のたびに書き換えると、"
            "本物の変更と再生成のゆらぎを差分から区別できない。"
            "安定していないreceiptは、内容が走行ごとに変わる（件数など）。"
        ),
    }
    passed = not unstable

    receipt = {
        "schema": "tai.reference.yic-gate-reproducibility/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 running the gate aggregate twice",
        "command": "python integrations/tools/yic_gate_reproducibility.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-gate-reproducibility-2026-11-17.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs the receipt-gate aggregate twice and compares the digests of the receipts each run "
            "writes, reporting which receipts are not reproducible. It says nothing about whether the "
            "gates judged correctly, and an unstable receipt may be legitimate when its content records "
            "a growing count rather than a run-specific fact."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "compared": checks["receiptsCompared"],
        "unstable": unstable,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
