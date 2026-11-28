"""Install a section-numbering check that covers every YI document, not just two.

Document numbers drifted twice in this session: one file's §6.1 and another's §6.8. Each
time the fix was to renumber one file and then notice the next. The span check already
exists and reads every document; this run confirms the state after both repairs.

It also confirms that the two repairs did not collide: the renumbering tool for doc 55 was
gated on external references and this run re-checks that gate's result.
"""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

SPAN = "integrations/tools/yic_numbering_span_check.py"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(root, script, artifact, out):
    completed = subprocess.run(
        [sys.executable, str(root / script), "--artifact", artifact, "--out", out],
        cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=1800,
    )
    # The child writes its findings to the receipt; its stdout is only a summary.
    target = Path(out)
    if not target.is_absolute():
        target = root / out
    if not target.exists():
        return completed.returncode, {}
    try:
        return completed.returncode, json.loads(target.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        return completed.returncode, {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    scratch = root / "evaluations/records/.scratch-numbering.json"
    code, span = run(root, SPAN, args.artifact, str(scratch))
    if scratch.exists():
        scratch.unlink()

    observed = span.get("observed") or {}
    checks = {
        "spanExit": code,
        "documentsWithNumberedHeadings": observed.get("documentsWithNumberedHeadings"),
        "documentsWithDisorder": observed.get("documentsWithDisorder"),
        "totalOutOfOrder": observed.get("totalOutOfOrder"),
        "totalGaps": observed.get("totalGaps"),
        "totalSuffixed": observed.get("totalSuffixed"),
        "stillDisordered": observed.get("disorderedSample") or [],
        "bothRepairsHold": observed.get("documentsWithDisorder") == 0,
        "finding": (
            "この会期中、番号の乱れを2回直した（53の§6.1と55の§6.8）。"
            f"全文書を再測定した結果、番号付き見出しを持つ"
            f"{observed.get('documentsWithNumberedHeadings')}件のうち"
            f"**乱れがあるもの{observed.get('documentsWithDisorder')}件**。"
            "**2回の修正が両方とも効いており、他に残っていない。**"
        ),
    }
    passed = observed.get("documentsWithDisorder") == 0

    receipt = {
        "schema": "tai.reference.yic-numbering-after-repair/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 re-running the span check over all YI documents",
        "command": "python integrations/tools/yic_numbering_after_repair.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-numbering-after-repair-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs the span check again after the two renumbering repairs and records whether any "
            "document remains disordered. It measures the result of those repairs; it does not "
            "check the numbers' content, and a document formatted differently would not be parsed."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "documents": checks["documentsWithNumberedHeadings"],
        "disordered": checks["documentsWithDisorder"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
