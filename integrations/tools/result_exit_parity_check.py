"""Audit scripts for a receipt verdict that can disagree with their exit code.

`integration_flow.py` wrote `"result": "PASS"` as a literal while its exit code
depended on the case counts, so a failing run produced a receipt that claimed
PASS. This looks for the same shape: a fixed result literal together with a
conditional exit at the end of the script.
"""

import argparse
import ast
import hashlib
import json
import time
from pathlib import Path

SEARCH_DIRS = ("integrations/tools", "integrations/pilot-sui-document/assembler")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def literal_results(tree):
    """Every string assigned to a "result" key in a dict literal."""
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and key.value == "result":
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    found.append({"value": value.value, "line": value.lineno, "fixed": True})
                else:
                    found.append({"value": None, "line": value.lineno, "fixed": False})
    return found


def conditional_exit(tree):
    """A `return 0 if ... else 1` anywhere in the module."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.IfExp):
            return node.lineno
    return None


def self_test():
    """Confirm the detector fires on the shape that integration_flow.py had."""
    sample = (
        "def f(passed):\n"
        "    receipt = {\"result\": \"PASS\"}\n"
        "    return 0 if passed else 1\n"
    )
    tree = ast.parse(sample)
    fixed = [item for item in literal_results(tree) if item["fixed"] and item["value"] == "PASS"]
    exit_line = conditional_exit(tree)
    return {
        "detectsFixedVerdictWithConditionalExit": bool(fixed) and exit_line is not None,
        "exitLine": exit_line,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    suspects = []
    checked = 0
    for relative in SEARCH_DIRS:
        for path in sorted((root / relative).glob("*.py")):
            if path.name.startswith("test_"):
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            results = literal_results(tree)
            if not results:
                continue
            checked += 1
            exit_line = conditional_exit(tree)
            fixed_pass = [item for item in results if item["fixed"] and item["value"] == "PASS"]
            if exit_line and fixed_pass:
                suspects.append(
                    {
                        "script": f"{relative}/{path.name}",
                        "fixedResultLines": [item["line"] for item in fixed_pass],
                        "conditionalExitLine": exit_line,
                    }
                )

    detected = self_test()
    checks = {
        "scriptsWithVerdict": checked,
        "suspects": suspects,
        "suspectCount": len(suspects),
        "selfTest": detected,
        "everyVerdictFollowsExitCode": not suspects,
        "selfTestDetectsTheShape": detected["detectsFixedVerdictWithConditionalExit"] is True,
    }
    passed = checks["everyVerdictFollowsExitCode"] and checks["selfTestDetectsTheShape"]
    receipt = {
        "schema": "tai.reference.result-exit-parity/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 parsing the tool sources",
        "command": "python integrations/tools/result_exit_parity_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/TEI-result-exit-parity-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Parses the tool sources and flags scripts whose receipt verdict is a fixed PASS literal while the exit code is conditional. A self-test confirms the detector fires on the shape that integration_flow.py had, so a clean result is not vacuous. It is a shape check, so it can miss a mismatch built by other means, and it does not judge whether the verdict is the right one.",
    }
    (root / args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checked": checked, "suspects": suspects, "passed": passed}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
