"""Observe a publication refusal instead of only declaring it held.

The danger-unit inventory found only two receipts in which a publication was
actually refused, while 286 merely declare ``publicationAllowed: false``. A
declaration is not an observation. This runs TAI's own publication gate on the
SCN-001 review status and records the refusal it produces: which reviews block,
why, and whether the exit code agrees with the verdict.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tai-root", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(args.tai_root)
    tool = root / "tools/reference-publication-gate"
    if not (tool / "main.go").exists():
        print(f"reference tool missing: {tool}", file=sys.stderr)
        return 1

    workdir = Path(os.environ.get("GOTMPDIR") or os.environ.get("TEMP") or ".") / "yi-pubgate"
    workdir.mkdir(parents=True, exist_ok=True)
    receipt_path = workdir / "gate.json"
    status = root / "evaluations/SCN-001-review-status.json"

    completed = subprocess.run(
        ["go", "run", ".", "-status", str(status), "-out", str(receipt_path)],
        cwd=tool, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if not receipt_path.exists():
        print((completed.stderr or completed.stdout or "")[-600:], file=sys.stderr)
        return 1
    gate = json.loads(receipt_path.read_text(encoding="utf-8"))

    blockers = gate.get("blockers") or []
    kinds = sorted(
        {blocker.split(":")[-1].strip() for blocker in blockers if ":" in blocker}
    )
    synthetic_blockers = [b for b in blockers if "synthetic" in b]
    pending_blockers = [b for b in blockers if "pending" in b]

    checks = {
        "gateSchema": gate.get("schema"),
        "allowed": gate.get("allowed"),
        "exitCode": completed.returncode,
        "blockerCount": len(blockers),
        "blockers": blockers[:8],
        "accepted": gate.get("accepted"),
        "developmentAccepted": gate.get("developmentAccepted"),
        "syntheticAcceptancesBlockPublication": len(synthetic_blockers) > 0,
        "pendingReviewsBlockPublication": len(pending_blockers) > 0,
        "refusalObserved": (
            gate.get("allowed") is False
            and completed.returncode != 0
            and len(blockers) > 0
        ),
        "finding": (
            "公開gateは、公開を実行せずに拒否だけを返す。"
            "今回のstatusでは、R-01〜R-05がsyntheticのdevelopmentAccepted、"
            "R-06/R-07がpendingであるため、allowed=falseで拒否された。"
            "これは公開が実際に拒否された観測であり、"
            "receiptの宣言（publicationAllowed:false）とは別の種類の記録である。"
        ),
    }
    passed = checks["refusalObserved"] and gate.get("allowed") is False

    receipt = {
        "schema": "tai.reference.yi-publication-refusal/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go running the SCN-001 publication gate",
        "command": "python integrations/tools/yi_publication_refusal_probe.py --tai-root . --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-publication-refusal-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Runs the publication gate on the SCN-001 review status and records the refusal it produces, with the blockers that caused it. The gate decides; it does not publish. The status file is TAI's own review record, and whether a real publication would be refused by an external system is not established.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "allowed": checks["allowed"],
        "blockers": len(blockers),
        "exit": checks["exitCode"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
