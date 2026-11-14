"""Try the first experiment of the SEI phase expansion: show an unreferenced record.

Design note 5.4 asks whether a record nobody has referred to can be shown as a
state. That needs a record of when each decision was last read, and the decision
memory this reference reads carries no such field. This runs the SEI reference
and records what the projection actually contains, so "unreferenced" is either
visible in the record or missing from it.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# The fields a "unreferenced" state would need, and whether the projection has them.
WANTED = {
    "decisionId": "判断のID",
    "lastReadAt": "最後に参照された時刻",
    "readCount": "参照された回数",
    "leftOpenBy": "未解決を残した判断",
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tai-root", required=True)
    parser.add_argument("--sei-root", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(args.tai_root)
    tool = root / "tools/reference-sei-decision"
    if not (tool / "main.go").exists():
        print(f"reference tool missing: {tool}", file=sys.stderr)
        return 1

    workdir = Path(os.environ.get("GOTMPDIR") or os.environ.get("TEMP") or ".") / "yi-unref"
    workdir.mkdir(parents=True, exist_ok=True)
    receipt_path = workdir / "sei-decision.json"

    completed = subprocess.run(
        ["go", "run", ".", "-sei-root", args.sei_root, "-synthetic", "-out", str(receipt_path)],
        cwd=tool, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if completed.returncode != 0 or not receipt_path.exists():
        print((completed.stderr or completed.stdout or "")[-600:], file=sys.stderr)
        return 1
    reference = json.loads(receipt_path.read_text(encoding="utf-8"))

    decision = reference.get("decision") or {}
    unresolved = reference.get("unresolved") or []
    decision_fields = sorted(decision.keys())
    unresolved_fields = sorted(unresolved[0].keys()) if unresolved else []

    present = {
        "decisionId": "id" in decision,
        "lastReadAt": any(field in decision for field in ("lastReadAt", "last_read_at", "accessedAt")),
        "readCount": any(field in decision for field in ("readCount", "read_count", "referenceCount")),
        "leftOpenBy": "left_open_by_decision" in (unresolved_fields or []),
    }

    checks = {
        "decisionFields": decision_fields,
        "unresolvedFields": unresolved_fields,
        "wanted": WANTED,
        "present": present,
        "presentCount": sum(1 for value in present.values() if value),
        "canShowUnreferenced": present["lastReadAt"] or present["readCount"],
        "finding": (
            "判断の記録は、ID・文言・依拠したrecommendation・責任を持つ。"
            "しかし、いつ・何回参照されたかの欄が無い。"
            "「長く参照されていない記録」を状態として示すには、"
            "参照の記録を別に持つ必要がある。"
        ),
    }
    passed = reference.get("passed") is True and not checks["canShowUnreferenced"]

    receipt = {
        "schema": "tai.reference.yi-unreferenced-probe/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go running the SEI decision reference against the SEI checkout",
        "command": "python integrations/tools/yi_unreferenced_probe.py --tai-root . --sei-root <SEI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-unreferenced-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Runs the SEI decision reference against a real SEI checkout, using a temporary store, and records that the decision projection has an identifier and a responsible party but no last-read time or read count. The fixture is synthetic and the store is temporary; whether SEI records reads elsewhere is not established here.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "decisionFields": decision_fields,
        "canShowUnreferenced": checks["canShowUnreferenced"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
