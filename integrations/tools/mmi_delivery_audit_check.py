"""Run MMI's delivery audit on a sample document and record what it observes."""

import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "evaluations/records/MMI-delivery-audit-2026-11-03.json"


def main():
    repo = Path(os.environ.get("MMI_REPO", r"D:\GIT\hat47x\markdown-matrix-injector"))
    cli_dir = repo / "03_Implement"
    document = repo / "04_Documentation/samples/practical/03-workflow.md"
    directory = repo / "04_Documentation/samples/practical/data"
    completed = subprocess.run(
        [
            "node", "--import", "tsx", "src/cli/mmi.ts", "delivery-audit", str(document), str(directory),
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
        print(completed.stdout[-1000:])
        print(completed.stderr[-1000:])
        return 1
    delivery = payload.get("delivery", {})
    counts = delivery.get("counts", {})
    checks = {
        "schema": payload.get("schema") == "mmi.delivery-audit/v0",
        "fileScope": payload.get("scope") == "file-only-excel-mmi-embeds",
        "emptyCompleteness": delivery.get("referentialCompleteness") == "empty",
        "zeroReferences": counts.get("references") == 0,
        "exitIndeterminate": completed.returncode == 1,
    }
    passed = all(checks.values())
    receipt = {
        "schema": "tai.reference.mmi-delivery-audit/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Node 24 and MMI's tsx CLI",
        "command": "python integrations/tools/mmi_delivery_audit_check.py",
        "result": "PASS" if passed else "FAIL",
        "observed": {
            "checks": checks,
            "exitCode": completed.returncode,
            "referentialCompleteness": delivery.get("referentialCompleteness"),
            "counts": counts,
        },
        "scope": "Runs MMI's delivery audit over one sample document. The audit only covers whole-file Excel references, so this document's range references count as none and the audit exits 1 (indeterminate). It does not assert delivery completeness.",
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "checks": checks, "exit": completed.returncode}))


if __name__ == "__main__":
    raise SystemExit(main())
