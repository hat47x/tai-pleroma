"""Run MMI's inspect CLI on a repository workbook and check the candidate contract."""

import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "evaluations/records/MMI-inspect-2026-11-03.json"


def main():
    mmi_repo = Path(os.environ.get("MMI_REPO", r"D:\GIT\hat47x\markdown-matrix-injector")) / "03_Implement"
    workbook = mmi_repo.parent / "04_Documentation/samples/practical/data/design.xlsx"
    completed = subprocess.run(
        ["node", "--import", "tsx", "src/cli/mmi.ts", "inspect", str(workbook), "--json"],
        cwd=mmi_repo,
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
    candidates = payload.get("candidates", [])
    checks = {
        "exitOk": completed.returncode == 0,
        "contract": payload.get("candidateContract") == "mmi.semantic-candidate/v1",
        "hasCandidates": len(candidates) >= 1,
        "digestsPresent": all(
            isinstance(candidate.get("locator", {}).get("sourceDigest"), str)
            and candidate["locator"]["sourceDigest"].startswith("sha256:")
            for candidate in candidates
        ),
        "hasTableRange": any(candidate.get("kind") == "table-range" for candidate in candidates),
    }
    passed = all(checks.values())
    receipt = {
        "schema": "tai.reference.mmi-inspect/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Node 24 and MMI's tsx CLI",
        "command": "python integrations/tools/mmi_inspect_check.py",
        "result": "PASS" if passed else "FAIL",
        "observed": {
            "checks": checks,
            "candidates": len(candidates),
            "sheets": sorted({c.get("locator", {}).get("sheet") for c in candidates if c.get("locator", {}).get("sheet")}),
            "sourceDigests": sorted({c.get("locator", {}).get("sourceDigest") for c in candidates if c.get("locator", {}).get("sourceDigest")}),
        },
        "scope": "Runs MMI's read-only inspect on one repository workbook and checks the semantic-candidate contract. It does not apply a format profile or write to the workbook.",
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "checks": checks, "candidates": len(candidates)}))


if __name__ == "__main__":
    raise SystemExit(main())
