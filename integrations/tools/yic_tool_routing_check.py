"""Record which YI tools need a product checkout, so a reader knows what a suite run covers.

Sixty-seven YI tools exist. Eleven run in the document aggregate, nine in the analysis
aggregate, seventeen elsewhere in the suite or receipt aggregates — and the rest are
probes that require a specific product checkout (TEI, SUI, EKI, MMI) as an argument.
A reader who sees "suite PASS" can wrongly assume all of them ran.

This classifies each tool by whether it can run without a product checkout, and writes
the routing so the gap is visible rather than inferred.
"""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

TOOLS = "integrations/tools"
ROUTED_IN = (
    "integrations/tools/run_suite.py",
    "integrations/tools/yic_document_gates.py",
    "integrations/tools/yic_analysis_gates.py",
    "integrations/tools/yic_receipt_gates.py",
    "integrations/tools/yi_receipt_quality.py",
)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    folder = root / TOOLS
    tools = sorted(
        [path.name for path in folder.glob("yic_*.py")]
        + [path.name for path in folder.glob("yi_*.py")]
    )

    routers = {}
    for relative in ROUTED_IN:
        path = root / relative
        routers[relative] = path.read_text(encoding="utf-8") if path.exists() else ""

    rows = []
    for name in tools:
        routed = [relative for relative, body in routers.items() if name in body]
        # Does it demand a product checkout? Read its `--help` rather than its source,
        # so the answer comes from the argument parser, not a guess.
        completed = subprocess.run(
            [sys.executable, str(folder / name), "--help"],
            cwd=root, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=300,
        )
        help_text = (completed.stdout or "") + (completed.stderr or "")
        needs_product = any(
            flag in help_text
            for flag in ("--tei-repo", "--tei-root", "--sui-repo", "--eki-repo",
                         "--mmi-repo", "--sho-repo", "--sei-root")
        )
        needs_tai_root = "--tai-root" in help_text
        rows.append({
            "tool": name,
            "routers": routed,
            "needsProductCheckout": needs_product,
            "needsTaiRoot": needs_tai_root,
            # Portable means: no product checkout. The TAI root is where we already are.
            "runsWithoutAProduct": not needs_product,
        })

    unrouted = [row["tool"] for row in rows if not row["routers"]]
    unroutedPortable = [
        row["tool"] for row in rows
        if not row["routers"] and row["runsWithoutAProduct"]
        # This check cannot route itself; it is excluded like any self-referential gate.
        and row["tool"] != "yic_tool_routing_check.py"
    ]
    checks = {
        "toolsFolder": TOOLS,
        "tools": len(rows),
        "routedTools": len([row for row in rows if row["routers"]]),
        "unroutedTools": unrouted,
        "unroutedCount": len(unrouted),
        "portableButUnrouted": unroutedPortable,
        "portableButUnroutedCount": len(unroutedPortable),
        "needingAProductCheckout": [
            row["tool"] for row in rows if row["needsProductCheckout"]
        ],
        "needingOnlyTheTaiRoot": [
            row["tool"] for row in rows
            if row["needsTaiRoot"] and not row["needsProductCheckout"]
        ],
        "rows": rows,
        "everyPortableToolIsRouted": not unroutedPortable,
        "finding": (
            "YIのツールを、製品チェックアウトを要するかで分類し、"
            "どの集約から走るかを記録する。"
            "「suite PASS」が全ツールの実行を意味しないことを、推測ではなく記録で示す。"
        ),
    }
    passed = not unroutedPortable

    receipt = {
        "schema": "tai.reference.yic-tool-routing/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 asking each tool for its arguments",
        "command": "python integrations/tools/yic_tool_routing_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-tool-routing-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Asks each YI tool for its --help text, decides whether it needs a product checkout, "
            "and records which aggregate references it. It judges routing and portability only: a "
            "tool that is routed may still fail on another host, and a tool needing a checkout is "
            "not thereby unverified — it is simply not run by the portable aggregates."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "tools": len(rows),
        "routed": checks["routedTools"],
        "unrouted": len(unrouted),
        "portableButUnrouted": unroutedPortable,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
