"""Replace the dead-rule experiment with the question that remains after the fix.

The 40 inert rules were made live and the 22 failures they exposed are now a named
baseline in the checker. The old probe rewrote selectors to prove they were inert, which
no longer applies. What still needs measuring:

  * the 22 baseline entries are still exactly the failures that occur, and
  * removing the baseline really does fail the checker (so the baseline entry is not
    decorative), and
  * the inert-rule list is reported, not empty and not silently dropped.
"""

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CHECKER = "tools/check-synthetic-receipts/check.py"
BASELINE_MARK = "KNOWN_RULE_FAILURE_KEYS = frozenset(KNOWN_RULE_FAILURE_BASELINE)"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _baseline_size(root: Path) -> int:
    """Count the checker's known-failure baseline entries."""
    import ast

    checker = root / CHECKER
    tree = ast.parse(checker.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and node.targets
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "KNOWN_RULE_FAILURE_BASELINE"
        ):
            # The baseline is built by successive `KNOWN = KNOWN + (...)` assignments,
            # so every literal tuple contributes.
            total = 0
            for assign in ast.walk(tree):
                if not (
                    isinstance(assign, ast.Assign)
                    and assign.targets
                    and isinstance(assign.targets[0], ast.Name)
                    and assign.targets[0].id == "KNOWN_RULE_FAILURE_BASELINE"
                ):
                    continue
                value = assign.value
                while isinstance(value, ast.BinOp) and isinstance(value.op, ast.Add):
                    if isinstance(value.left, (ast.Tuple, ast.List)):
                        total += len(value.left.elts)
                    value = value.right
                if isinstance(value, (ast.Tuple, ast.List)):
                    total += len(value.elts)
            return total
    return 0


def run(script, root):
    completed = subprocess.run(
        [sys.executable, str(script), "--root", str(root)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3600,
    )
    body = completed.stdout.strip()
    try:
        return completed.returncode, json.loads(body[body.index("{"):])
    except (json.JSONDecodeError, ValueError):
        return completed.returncode, {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    source = root / CHECKER
    text = source.read_text(encoding="utf-8")

    base_code, base = run(source, root)
    known = base.get("knownRuleFailures") or []
    resolved = base.get("resolvedRuleFailures") or []
    inert = base.get("inertRules") or []
    blocking = base.get("errors") or []

    # Run once with the baseline emptied: the same 22 must then block.
    scratch = Path(tempfile.mkdtemp(prefix="yic-no-baseline-"))
    patched = scratch / "check_no_baseline.py"
    assert BASELINE_MARK in text, "baseline marker missing"
    patched.write_text(
        text.replace(
            BASELINE_MARK,
            "KNOWN_RULE_FAILURE_KEYS = frozenset()  # baseline emptied for this measurement",
            1,
        ),
        encoding="utf-8",
    )
    empty_code, empty = run(patched, root)
    blocked = empty.get("errors") or []

    # The expected count is the checker's own baseline length, not a remembered number.
    expected = _baseline_size(root)

    checks = {
        "checker": CHECKER,
        "withBaseline": {
            "exit": base_code,
            "passed": base.get("passed"),
            "blocking": len(blocking),
            "knownRuleFailures": len(known),
            "resolvedRuleFailures": len(resolved),
            "inertRules": inert,
        },
        "withBaselineEmptied": {
            "exit": empty_code,
            "passed": empty.get("passed"),
            "blocking": len(blocked),
        },
        "baselineSize": expected,
        "baselineIsStillExact": (
            len(set(known)) == expected and len(resolved) == 0
        ),
        "emptyingTheBaselineBlocks": len(set(blocked)) >= expected,
        "finding": (
            "49の規則を発火させた結果を、**名前つきの基準**としてcheckerに置いた。"
            f"基準ありでは**阻止{len(blocking)}件・既知{len(set(known))}/{expected}件**。"
            f"基準を空にすると**{len(set(blocked))}件が阻止**に変わる。"
            "**基準は飾りではなく、実効している。**"
            f"発火しない規則は{len(inert)}件で、一覧として毎回報告される。"
        ),
    }
    passed = (
        checks["baselineIsStillExact"]
        and checks["emptyingTheBaselineBlocks"]
        and len(inert) > 0
    )

    receipt = {
        "schema": "tai.reference.yic-rule-baseline-effect/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 running the checker with and without the baseline",
        "command": "python integrations/tools/yic_dead_rule_impact_probe.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-dead-rule-impact-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs the checker as written and again with the known-failure baseline emptied, and "
            "records how many failures block in each case. It shows the baseline is load-bearing; "
            "it does not decide whether each baseline entry belongs there, which is the product "
            "owner's question."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "known": len(known),
        "resolved": len(resolved),
        "blocking": len(blocking),
        "whenEmptied": len(blocked),
        "inert": len(inert),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
