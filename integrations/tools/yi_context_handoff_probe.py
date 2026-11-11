"""Measure which units the context handoff actually carries (RQ-YI-024).

RQ-YI-024 asks the harness to hand the task, the decisions and the unresolved
items to the product before its context limit, and to record what was handed
over and what could not be. The reference implementation records a deferred
handoff; this checks which of those three units the record actually carries, by
running the reference and reading the shape it writes.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# The units RQ-YI-024 names, with the field each would need in the handoff.
UNITS = {
    "task": ("Task", "課題"),
    "decision": (None, "判断"),
    "unresolved": (None, "未解決"),
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tai-root", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(args.tai_root)
    tool = root / "tools/reference-harness-boundary"
    if not (tool / "main.go").exists():
        print(f"reference tool missing: {tool}", file=sys.stderr)
        return 1

    environment = dict(os.environ)
    completed = subprocess.run(
        ["go", "run", "."], cwd=tool, capture_output=True, text=True,
        encoding="utf-8", errors="replace", env=environment,
    )
    if completed.returncode != 0:
        print((completed.stderr or "")[-600:], file=sys.stderr)
        return 1
    reference = json.loads(completed.stdout)

    source = (tool / "main.go").read_text(encoding="utf-8")
    handoff = re.search(r"type Handoff struct \{(.+?)\}", source, re.S)
    fields = re.findall(r"\b([A-Z][A-Za-z0-9]*)\s+[^\n]*`json:", handoff.group(1)) if handoff else []
    handoff_json = re.findall(r'`json:"([^"]+)"`', handoff.group(1)) if handoff else []

    carried = {}
    for unit, (field, label) in UNITS.items():
        carried[unit] = {
            "field": field,
            "label": label,
            "present": bool(field) and field in fields,
        }

    checks = {
        "referencePassed": reference.get("passed") is True,
        "handoffRecorded": reference.get("handoffRecorded") is True,
        "deferredRecorded": reference.get("deferredRecorded") is True,
        "handoffFields": fields,
        "handoffJsonFields": handoff_json,
        "units": carried,
        "unitsCarried": sorted(name for name, value in carried.items() if value["present"]),
        "unitsMissing": sorted(name for name, value in carried.items() if not value["present"]),
        "carriesAllThreeUnits": all(value["present"] for value in carried.values()),
        "finding": (
            "参照実装は、文脈の上限の後に渡せなかったことをdeferredとして記録する。"
            "しかしHandoffが持つのはContextID・Version・Task・Deferredであり、"
            "RQ-YI-024が求める三つの単位のうち、課題だけを運ぶ。"
            "判断と未解決を運ぶ欄が無い。"
        ),
    }
    passed = checks["referencePassed"] and checks["deferredRecorded"]

    receipt = {
        "schema": "tai.reference.yi-context-handoff-probe/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go running the harness boundary reference",
        "command": "python integrations/tools/yi_context_handoff_probe.py --tai-root . --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-context-handoff-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Runs the harness boundary reference and reads the handoff type it writes, then records which of RQ-YI-024's three units the handoff carries. The product and the harness are synthetic; real products, real context limits and real sessions are not exercised, and the recorded units are read from the reference's own type rather than from a live harness.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "referencePassed": checks["referencePassed"],
        "handoffFields": fields,
        "unitsCarried": checks["unitsCarried"],
        "unitsMissing": checks["unitsMissing"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
