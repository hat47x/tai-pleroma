"""Re-run the SCN-001 publication gate and require that it stays blocked."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "tools/reference-publication-gate"
STATUS = ROOT / "evaluations/SCN-001-review-status.json"
OUT = ROOT / "evaluations/SCN-001-publication-gate-recheck-2026-11-03.json"


def main():
    completed = subprocess.run(
        ["go", "run", ".", "-status", str(STATUS), "-out", str(OUT)],
        cwd=GATE,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if not OUT.exists():
        print(completed.stderr, file=sys.stderr)
        return 1
    receipt = json.loads(OUT.read_text(encoding="utf-8"))
    blocked = receipt.get("allowed") is False and bool(receipt.get("blockers"))
    print(json.dumps({"allowed": receipt.get("allowed"), "blockers": len(receipt.get("blockers", []))}))
    return 0 if blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
