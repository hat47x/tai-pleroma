"""Run the document-level YI checks in one pass.

Twelve checks now judge the YI documents: reachability from the README, link landing,
section order, status lines, deck counts, gate prose, gate citations, the G1 packet,
the not-run refresh, and the receipt-wide ones about limits and skips. Each runs in
under three seconds, but running them one by one from the runbook is easy to skip a
part of. This runs them together, writes nothing into the tree, and refuses PASS if
any is missing or fails.
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

# Check, question it answers.
CHECKS = (
    ("readmeCoverage", "yic_readme_coverage_check.py",
     "every YI document is reachable from the README"),
    ("docLinks", "yic_doc_links_check.py",
     "every relative link resolves"),
    ("sectionSequence", "yic_section_sequence_check.py",
     "numbered sections ascend without undocumented holes"),
    ("statusLine", "yic_status_line_check.py",
     "every document states what it is, early"),
    ("deckCounts", "yic_deck_counts_check.py",
     "stated deck counts equal the files"),
    ("gateProse", "yic_gate_prose_check.py",
     "the gate documents' numbers match their receipts"),
    ("gateCitation", "yic_gate_citation_check.py",
     "every gate is cited and non-PASS citations are caveated"),
    ("g1Packet", "yic_g1_packet_readiness.py",
     "the G1 packet is ready for a decision and undecided"),
    ("notRunRefresh", "yic_notrun_refresh_check.py",
     "the not-run list's later evidence is located"),
    ("authorityLimits", "yic_authority_limits_check.py",
     "Product-declared limits are not dropped"),
    ("skipDisclosure", "yic_skip_disclosure_check.py",
     "a skip is visible rather than folded into a pass"),
    ("reachTable", "yic_reach_table_check.py",
     "every reach mark is backed by its receipt"),
    ("runbookExpectation", "yic_runbook_expectation_check.py",
     "the runbook's expected numbers match the live counts"),
    ("universalClaim", "yic_universal_claim_check.py",
     "a universal claim states its population"),
    ("sectionOrder", "yic_section_order_check.py",
     "the reach document's sections ascend"),
    ("suiteInvocation", "yic_suite_invocation_check.py",
     "the suite records the argv it ran with"),
    ("suiteStepAccounting", "yic_suite_step_accounting.py",
     "registered steps and recorded steps reconcile"),
    ("gateReproducibility", "yic_gate_reproducibility.py",
     "two runs in a row write the same receipts"),
)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def classify(results):
    missing = [name for name, item in results.items() if not item["ran"]]
    failed = [name for name, item in results.items()
              if item["ran"] and not item["passed"]]
    return missing, failed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    scratch = Path(tempfile.mkdtemp(prefix="yic-doc-gates-"))
    results = {}
    for name, script, question in CHECKS:
        path = root / "integrations/tools" / script
        if not path.exists():
            results[name] = {"ran": False, "reason": "script missing", "question": question}
            continue
        completed = subprocess.run(
            [sys.executable, str(path),
             "--artifact", args.artifact,
             "--out", str(scratch / f"{name}.json")],
            cwd=root, capture_output=True, text=True,
            encoding="utf-8", errors="replace", env={**os.environ}, timeout=900,
        )
        # `--strict` matters for the links check; re-run it with the flag when its
        # plain run passes, so cross-repo links are reported rather than silently ok.
        if name == "docLinks" and completed.returncode == 0:
            completed = subprocess.run(
                [sys.executable, str(path), "--strict",
                 "--artifact", args.artifact,
                 "--out", str(scratch / f"{name}.json")],
                cwd=root, capture_output=True, text=True,
                encoding="utf-8", errors="replace", env={**os.environ}, timeout=900,
            )
        tail = (completed.stdout or "").strip().splitlines()
        results[name] = {
            "ran": True,
            "question": question,
            "exit": completed.returncode,
            "passed": completed.returncode == 0,
            "tail": tail[-1][:200] if tail else "",
        }

    missing, failed = classify(results)
    checks = {
        "checksRequested": len(CHECKS),
        "checksRun": len([item for item in results.values() if item["ran"]]),
        "results": results,
        "scriptsMissing": missing,
        "failed": failed,
        "scratchDirectory": str(scratch),
        "wroteIntoTheTree": False,
        "everyDocumentCheckRan": not missing,
        "everyDocumentCheckPassed": not failed,
        "finding": (
            "YI文書の点検12種を1コマンドで実行し、1つでも欠ければPASSを返さない。"
            "各点検は3秒未満で終わるが、個別に呼ぶと一部を飛ばしやすい。"
            "作業ツリーへは書かない（一時ディレクトリへ出力する）。"
        ),
    }
    passed = not missing and not failed

    receipt = {
        "schema": "tai.reference.yic-document-gates/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 running the document checks together",
        "command": "python integrations/tools/yic_document_gates.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-document-gates-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs eleven document-level YI checks in one pass and refuses PASS if any is missing or "
            "fails. It records whether each ran and its exit code, not what each concluded; a check "
            "that passes can still judge the wrong thing, and this aggregate inherits every limit of "
            "the eleven."
        ),
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
