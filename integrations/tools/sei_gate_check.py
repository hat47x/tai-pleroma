"""Run SEI's policy gate against the projected decision, for allow and deny cases."""

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "evaluations/artifacts/sei-decision-projection.json"
RECEIPT = ROOT / "evaluations/records/SEI-TEI-gate-2026-11-03.json"


def run(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def main():
    sei_repo = Path(os.environ.get("SEI_REPO", r"D:\GIT\hat47x\sei-cognition")) / "runtime" / "go"
    workdir = Path(tempfile.mkdtemp(prefix="tei-sei-gate-", dir=os.environ.get("GOTMPDIR") or None))
    binary = workdir / ("sei.exe" if os.name == "nt" else "sei")
    build = run(["go", "build", "-o", str(binary), "./cmd/sei"], sei_repo)
    if build.returncode != 0:
        print(build.stderr, file=os.sys.stderr)
        return 1

    record = json.loads(ARTIFACT.read_text(encoding="utf-8"))["decision"]
    decision_id = record["refId"]

    allowed_store = workdir / "allowed"
    run([str(binary), "init", "-data-root", str(allowed_store)], sei_repo)
    run(
        [
            str(binary), "add", "recommendation", "-data-root", str(allowed_store),
            "-id", "rec-projection", "-statement", record["statement"],
            "-rationale", record["rationale"], "-responsible", "person:alice",
        ],
        sei_repo,
    )
    run(
        [
            str(binary), "add", "decision", "-data-root", str(allowed_store),
            "-id", decision_id, "-statement", record["statement"],
            "-rationale", record["rationale"], "-recommendation", "rec-projection",
            "-responsible", "person:alice",
        ],
        sei_repo,
    )
    allow = run(
        [str(binary), "gate", "check", "-data-root", str(allowed_store), "-decision", decision_id, "-require-recommendation"],
        sei_repo,
    )

    denied_store = workdir / "denied"
    run([str(binary), "init", "-data-root", str(denied_store)], sei_repo)
    run(
        [
            str(binary), "add", "decision", "-data-root", str(denied_store),
            "-id", decision_id, "-statement", record["statement"], "-rationale", record["rationale"],
        ],
        sei_repo,
    )
    deny = run([str(binary), "gate", "check", "-data-root", str(denied_store), "-decision", decision_id], sei_repo)

    allow_body = json.loads(allow.stdout) if allow.stdout.strip().startswith("{") else {}
    deny_body = json.loads(deny.stdout) if deny.stdout.strip().startswith("{") else {}
    checks = {
        "allowVerdict": allow_body.get("verdict") == "allow",
        "allowExit": allow.returncode == 0,
        "allowBinding": bool(allow_body.get("binding", {}).get("decision_digest")),
        "denyVerdict": deny_body.get("verdict") == "deny",
        "denyExit": deny.returncode == 3,
        "denyReason": "no responsible party" in " ".join(deny_body.get("reasons", [])),
        "notVerifiedListed": bool(allow_body.get("not_verified")),
    }
    passed = all(checks.values())
    receipt = {
        "schema": "tai.reference.tei-sei-gate/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with a locally built sei CLI and temporary record stores",
        "command": "python integrations/tools/sei_gate_check.py",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": str(ARTIFACT.relative_to(ROOT)).replace("\\", "/")},
        "observed": {
            "checks": checks,
            "allowVerdict": allow_body.get("verdict"),
            "denyVerdict": deny_body.get("verdict"),
            "denyReasons": deny_body.get("reasons"),
            "decisionDigest": allow_body.get("binding", {}).get("decision_digest"),
        },
        "scope": "Runs SEI's policy gate for one allow and one deny case using the projected statement. The gate does not verify Authority or that the action matches the decision.",
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(workdir, ignore_errors=True)
    print(json.dumps({"passed": passed, "checks": checks}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
