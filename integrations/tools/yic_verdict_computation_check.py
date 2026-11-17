"""Check that every YI receipt writer computes its verdict rather than asserting one.

Last round showed a claims module whose verdicts were literals. The same failure would
be worse in a receipt writer: a script that always writes `"result": "PASS"` reports
success even when its own check failed. `result_exit_parity_check` looks for the
simplest version of this; this checks the YI tools for a literal verdict with no
conditional.

A writer that picks between PASS and FAIL from a computed boolean is fine. A writer
whose `result` is a fixed string is not.
"""

import argparse
import ast
import hashlib
import json
import re
import time
from pathlib import Path

TOOLS = "integrations/tools"
FIXED = re.compile(r'"?result"?\s*:\s*(?P<quote>"|\')(?P<value>PASS|FAIL)(?P=quote)')
CONDITIONAL = re.compile(r'"?result"?\s*:\s*"PASS"\s+if')


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verdict_shape(source):
    text = source.read_text(encoding="utf-8", errors="replace")
    fixed = [match.group("value") for match in FIXED.finditer(text)]
    conditional = bool(CONDITIONAL.search(text))
    # A ternary or an f-string is a computation; a bare literal is not.
    has_ternary = "if passed" in text or "if ok" in text or "if success" in text
    return {
        "fixedVerdicts": fixed,
        "hasConditionalVerdict": conditional,
        "hasTernary": has_ternary,
        "computesItsVerdict": conditional or has_ternary,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    folder = root / TOOLS
    tools = sorted(
        [path for path in folder.glob("yic_*.py")]
        + [path for path in folder.glob("yi_*.py")]
    )

    rows = []
    for path in tools:
        shape = verdict_shape(path)
        rows.append({"tool": path.name, **shape})

    # A tool that writes a receipt must compute its verdict. Probe scripts that never
    # write a `result` are out of scope for this question.
    writers = [row for row in rows if row["fixedVerdicts"] or row["computesItsVerdict"]]
    fixedOnly = [
        row for row in writers
        if row["fixedVerdicts"] and not row["computesItsVerdict"]
    ]
    fixedPassOnly = [
        row for row in fixedOnly if set(row["fixedVerdicts"]) == {"PASS"}
    ]

    checks = {
        "toolsFolder": TOOLS,
        "toolsScanned": len(rows),
        "toolsThatWriteAVerdict": len(writers),
        "toolsWithAFixedVerdict": [
            {"tool": row["tool"], "value": row["fixedVerdicts"]} for row in fixedOnly
        ],
        "fixedVerdictCount": len(fixedOnly),
        "fixedPassOnly": [row["tool"] for row in fixedPassOnly],
        "everyVerdictIsComputed": not fixedOnly,
        "finding": (
            "YIのreceipt書き出し部が、判定を計算しているのか、リテラルで主張しているのかを調べる。"
            "`\"result\": \"PASS\"`という固定文字列は、自分の検査が失敗してもPASSを報告しうる。"
            "`\"PASS\" if ... else \"FAIL\"`のような条件式は対象外とする。"
        ),
    }
    passed = not fixedOnly

    receipt = {
        "schema": "tai.reference.yic-verdict-computation/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the YI tool sources",
        "command": "python integrations/tools/yic_verdict_computation_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-verdict-computation-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads the YI tool sources and flags writers whose verdict is a fixed string with no "
            "conditional. It checks the shape of the writer only: a computed verdict can still "
            "compute from the wrong comparison, and a tool that writes no verdict is not examined."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "tools": len(rows),
        "writers": len(writers),
        "fixedVerdicts": [row["tool"] for row in fixedOnly],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
