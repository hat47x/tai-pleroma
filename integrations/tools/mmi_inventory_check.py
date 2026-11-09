"""Run MMI's source inventory and check its contract and digests."""

import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "evaluations/records/MMI-inventory-2026-11-03.json"


def main():
    repo = Path(os.environ.get("MMI_REPO", r"D:\GIT\hat47x\markdown-matrix-injector"))
    cli_dir = repo / "03_Implement"
    target = repo / "04_Documentation/samples/practical/data"
    completed = subprocess.run(
        [
            "node", "--import", "tsx", "src/cli/mmi.ts", "inventory", str(target),
            "--root", str(repo), "--json",
        ],
        cwd=cli_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        print(completed.stderr[-2000:])
        return 1
    entries = payload.get("entries", [])
    checks = {
        "exitOk": completed.returncode == 0,
        "contract": payload.get("contract") == "mmi.source-inventory/v0",
        "complete": payload.get("status") == "complete",
        "hasEntries": len(entries) >= 1,
        "anyDigest": any(isinstance(entry.get("identity", {}).get("digest"), str) for entry in entries),
        "digestsWellFormed": all(
            entry["identity"]["digest"].startswith("sha256:")
            for entry in entries
            if isinstance(entry.get("identity", {}).get("digest"), str)
        ),
    }
    passed = all(checks.values())
    receipt = {
        "schema": "tai.reference.mmi-inventory/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Node 24 and MMI's tsx CLI",
        "command": "python integrations/tools/mmi_inventory_check.py",
        "result": "PASS" if passed else "FAIL",
        "observed": {
            "checks": checks,
            "entries": len(entries),
            "scope": payload.get("scope"),
            "consistency": payload.get("consistency"),
        },
        "scope": "Runs MMI's read-only source inventory over one repository directory and checks the inventory contract, status and per-entry digests. It does not inspect document contents or write anything.",
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "checks": checks, "entries": len(entries)}))


if __name__ == "__main__":
    raise SystemExit(main())
