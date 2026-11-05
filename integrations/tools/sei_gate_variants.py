"""Check SEI's gate policy variants against the projected decision."""

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "evaluations/artifacts/sei-decision-projection.json"
RECEIPT = ROOT / "evaluations/records/SEI-TEI-gate-variants-2026-11-03.json"


def run(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def gate(binary, store, decision, *extra, cwd):
    completed = run([str(binary), "gate", "check", "-data-root", str(store), "-decision", decision, *extra], cwd)
    body = json.loads(completed.stdout) if completed.stdout.strip().startswith("{") else {}
    return completed.returncode, body


def main():
    sei_repo = Path(os.environ.get("SEI_REPO", r"D:\GIT\hat47x\sei-cognition")) / "runtime" / "go"
    workdir = Path(tempfile.mkdtemp(prefix="tei-sei-gatev-", dir=os.environ.get("GOTMPDIR") or None))
    binary = workdir / ("sei.exe" if os.name == "nt" else "sei")
    build = run(["go", "build", "-o", str(binary), "./cmd/sei"], sei_repo)
    if build.returncode != 0:
        print(build.stderr, file=os.sys.stderr)
        return 1

    record = json.loads(ARTIFACT.read_text(encoding="utf-8"))["decision"]
    store = workdir / "store"
    run([str(binary), "init", "-data-root", str(store)], sei_repo)
    run(
        [
            str(binary), "add", "recommendation", "-data-root", str(store), "-id", "rec-1",
            "-statement", record["statement"], "-rationale", record["rationale"], "-responsible", "person:alice",
        ],
        sei_repo,
    )
    # decision with a recommendation, a responsible party, and one unresolved question
    run(
        [
            str(binary), "add", "decision", "-data-root", str(store), "-id", "d-unresolved",
            "-statement", record["statement"], "-rationale", record["rationale"],
            "-recommendation", "rec-1", "-responsible", "person:alice", "-unresolved", "question:q-1",
        ],
        sei_repo,
    )
    # decision with a responsible party but no recommendation
    run(
        [
            str(binary), "add", "decision", "-data-root", str(store), "-id", "d-no-rec",
            "-statement", record["statement"], "-rationale", record["rationale"], "-responsible", "person:alice",
        ],
        sei_repo,
    )

    allow_code, allow_body = gate(binary, store, "d-unresolved", cwd=sei_repo)
    unresolved_code, unresolved_body = gate(binary, store, "d-unresolved", "--deny-unresolved", cwd=sei_repo)
    missing_rec_code, missing_rec_body = gate(binary, store, "d-no-rec", "--require-recommendation", cwd=sei_repo)

    checks = {
        "allowWithoutPolicy": allow_body.get("verdict") == "allow" and allow_code == 0,
        "denyUnresolved": unresolved_body.get("verdict") == "deny" and unresolved_code == 3,
        "denyMissingRecommendation": missing_rec_body.get("verdict") == "deny" and missing_rec_code == 3,
        "unresolvedReason": any("unresolved" in reason for reason in unresolved_body.get("reasons", [])),
        "recommendationReason": any("recommendation" in reason for reason in missing_rec_body.get("reasons", [])),
    }
    passed = all(checks.values())
    receipt = {
        "schema": "tai.reference.tei-sei-gate-variants/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with a locally built sei CLI and a temporary record store",
        "command": "python integrations/tools/sei_gate_variants.py",
        "result": "PASS" if passed else "FAIL",
        "observed": {
            "checks": checks,
            "allowVerdict": allow_body.get("verdict"),
            "denyUnresolved": unresolved_body.get("reasons"),
            "denyMissingRecommendation": missing_rec_body.get("reasons"),
        },
        "scope": "Exercises deny-unresolved and require-recommendation against recorded decisions. It does not verify Authority.",
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(workdir, ignore_errors=True)
    print(json.dumps({"passed": passed, "checks": checks}))


if __name__ == "__main__":
    raise SystemExit(main())
