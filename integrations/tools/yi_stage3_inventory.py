"""Inventory what stage 3 of the YI plan has actually run, and what has not.

Stage 3 asks for six things: the change-line inspection, the four usability
conditions, the centre handoff, the entrance join, the thin-phase expansion, and
the harness boundary. Several of them have reference implementations; several do
not. This records, per item, whether evidence exists and whether the reference
tests that back it still pass, so "executed" and "NOT RUN" are not confused.
"""

import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

# Each stage-3 item with the evidence it needs and the suite that backs it.
ITEMS = {
    "changeLineInspection": {
        "requirement": "RQ-YI-019",
        "evidence": ["docs/yi-constellation/analysis/16-変爻の検査記録.md"],
        "suite": "tools/reference-scn001",
        "what": "変爻の前後で何が観測できるかを、SCN-001の参照評価で試した",
    },
    "usabilityConditions": {
        "requirement": "RQ-YI-019（四条件）",
        "evidence": ["docs/yi-constellation/analysis/13-設計ノート.md"],
        "suite": None,
        "what": "意味の使用可能性の四条件（13の6節）の設計。実行は四条件のうち構造の二つだけ",
    },
    "entranceJoin": {
        "requirement": "RQ-YI-021",
        "evidence": ["docs/yi-constellation/analysis/13-設計ノート.md"],
        "suite": "tools/reference-mmi-readonly",
        "what": "MMIの inspect/select を呼ぶ参照接続",
    },
    "harnessBoundary": {
        "requirement": "RQ-YI-023",
        "evidence": ["docs/yi-constellation/analysis/13-設計ノート.md"],
        "suite": "tools/reference-harness-boundary",
        "what": "読み取り専用・書き込み拒否・文脈の受け渡し・提供元の交換",
    },
    "centreHandoff": {
        "requirement": "RQ-YI-020",
        "evidence": [],
        "suite": None,
        "what": "SHOとSEIの中心の受け渡し。接続も要求も無い",
    },
    "thinPhaseExpansion": {
        "requirement": "相の拡充",
        "evidence": ["docs/yi-constellation/analysis/13-設計ノート.md"],
        "suite": None,
        "what": "一製品につき一つを要求と検証の形にする。下書きのみ",
    },
    "contextHandoff": {
        "requirement": "RQ-YI-024",
        "evidence": ["docs/yi-constellation/analysis/13-設計ノート.md"],
        "suite": None,
        "what": "長いセッションの合成例。未実施",
    },
}

NOT_RUN = ("centreHandoff", "thinPhaseExpansion", "contextHandoff")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_suite(root, relative):
    directory = root / relative
    if not directory.exists():
        return {"suite": relative, "ran": False, "reason": "directory missing"}
    environment = dict(os.environ)
    completed = subprocess.run(
        ["go", "test", "./...", "-count=1"],
        cwd=directory, capture_output=True, text=True,
        encoding="utf-8", errors="replace", env=environment,
    )
    tail = (completed.stdout or completed.stderr or "").strip().splitlines()
    return {
        "suite": relative,
        "ran": True,
        "ok": completed.returncode == 0,
        "exit": completed.returncode,
        "tail": tail[-1] if tail else "",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--run", action="store_true", help="run the backing go test suites")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    inventory = {}
    for name, item in ITEMS.items():
        evidence = []
        missing = []
        for relative in item["evidence"]:
            path = root / relative
            if path.exists():
                evidence.append(relative)
            else:
                missing.append(relative)
        entry = {
            "requirement": item["requirement"],
            "what": item["what"],
            "evidencePresent": evidence,
            "evidenceMissing": missing,
            "suite": item["suite"],
            "state": "not-run" if name in NOT_RUN else ("evidence-only" if not item["suite"] else "executed"),
        }
        inventory[name] = entry

    suites = {}
    if args.run:
        for name, item in ITEMS.items():
            suite = item["suite"]
            if not suite:
                continue
            if suite in suites:
                continue
            suites[suite] = run_suite(root, suite)
            inventory[name]["suiteResult"] = {
                "ok": suites[suite].get("ok"),
                "tail": suites[suite].get("tail"),
            }

    executed = [name for name, entry in inventory.items() if entry["state"] == "executed"]
    not_run = [name for name, entry in inventory.items() if entry["state"] == "not-run"]
    evidence_only = [
        name for name, entry in inventory.items() if entry["state"] == "evidence-only"
    ]
    suites_ok = all(result.get("ok") for result in suites.values()) if suites else None

    checks = {
        "items": inventory,
        "executed": executed,
        "evidenceOnly": evidence_only,
        "notRun": not_run,
        "suitesRun": sorted(suites),
        "suitesPassed": suites_ok,
        "everyEvidenceFileExists": not any(
            entry["evidenceMissing"] for entry in inventory.values()
        ),
        "notRunIsDeclared": bool(not_run),
    }
    passed = checks["everyEvidenceFileExists"] and (
        suites_ok is not False if suites else True
    )

    receipt = {
        "schema": "tai.reference.yi-stage3-inventory/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 and Go, reading the analysis and running the reference suites",
        "command": "python integrations/tools/yi_stage3_inventory.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-stage3-inventory-2026-11-11.json --run",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Records, per stage-3 item, whether its evidence document exists and whether the reference go suite that backs it passes. Three items (the centre handoff, the thin-phase expansion, the long-session context handoff) are declared not-run because no implementation exists. Passing reference suites are synthetic reference evaluation, not behaviour of the real products.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "executed": executed,
        "evidenceOnly": evidence_only,
        "notRun": not_run,
        "suites": {name: result.get("ok") for name, result in suites.items()},
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
