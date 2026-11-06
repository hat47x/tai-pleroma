"""Record the current suite timings as a baseline observation for later comparison."""

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUITE_RECEIPT = ROOT / "evaluations/records/TEI-suite-2026-11-03.json"
OUT = ROOT / "evaluations/records/TEI-suite-timing-2026-11-06.json"


def rev(path):
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).stdout.strip()
    except OSError:
        return ""


def main():
    suite = json.loads(SUITE_RECEIPT.read_text(encoding="utf-8"))
    steps = suite.get("steps", {})
    timings = [
        {"name": name, "seconds": step.get("seconds"), "attempts": step.get("attempts")}
        for name, step in steps.items()
    ]
    slowest = sorted(
        (timing for timing in timings if isinstance(timing["seconds"], (int, float))),
        key=lambda timing: timing["seconds"],
        reverse=True,
    )[:5]
    total = sum(timing["seconds"] for timing in timings if isinstance(timing["seconds"], (int, float)))
    receipt = {
        "schema": "tai.reference.suite-timing/v0",
        "synthetic": False,
        "evidenceKind": "observation",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go on PATH, Python 3.12, and the SUI consumer",
        "command": "python integrations/tools/poc_evaluation_baseline.py",
        "result": suite.get("result"),
        "observed": {
            "steps": len(timings),
            "totalSeconds": round(total, 2),
            "slowest": slowest,
            "suiteResult": suite.get("result"),
        },
        "products": {
            "tei": rev(Path(r"D:\GIT\hat47x\tei-wt-latest")),
            "sui": rev(Path(r"D:\GIT\hat47x\sui-wt-latest")),
            "sei": rev(Path(r"D:\GIT\hat47x\sei-cognition")),
            "mmi": rev(Path(r"D:\GIT\hat47x\markdown-matrix-injector")),
            "eki": rev(Path(r"D:\GIT\hat47x\eki-wt-proj")),
        },
        "scope": "Reads the committed suite receipt and records per-step timings and the checked-out product revisions. It is a baseline observation for later comparison, not a productivity measurement.",
    }
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"steps": len(timings), "totalSeconds": round(total, 2), "slowest": [t["name"] for t in slowest]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
