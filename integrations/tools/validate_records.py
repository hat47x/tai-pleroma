"""Convert every pilot artifact into its product record and check the results."""

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(script, extra, receipt):
    completed = subprocess.run(
        [sys.executable, str(ROOT / script), *extra, "--receipt-out", str(receipt)],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        cwd=ROOT,
    )
    if receipt.exists():
        data = json.loads(receipt.read_text(encoding="utf-8"))
        return completed.returncode, data.get("observed", {}).get("valid"), data.get("observed", {}).get("errors", [])
    return completed.returncode, False, [completed.stderr.strip()[-300:]]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sei-schema", required=True)
    parser.add_argument("--mmi-schema", required=True)
    parser.add_argument("--eki-openapi", required=True)
    parser.add_argument("--out", default="evaluations/records/TEI-records-2026-11-03.json")
    args = parser.parse_args()

    results = {}
    with tempfile.TemporaryDirectory(prefix="tei-records-") as tmp:
        plans = {
            "sei": ("integrations/tools/sei_record_from_projection.py", ["--schema", args.sei_schema]),
            "mmi": ("integrations/tools/mmi_record_from_projection.py", ["--schema", args.mmi_schema]),
            "eki": ("integrations/tools/eki_record_from_projection.py", ["--openapi", args.eki_openapi]),
        }
        for name, (script, extra) in plans.items():
            code, valid, errors = run(script, extra, Path(tmp) / f"{name}.json")
            results[name] = {"valid": bool(valid), "errors": errors, "returncode": code}

    all_valid = all(item["valid"] for item in results.values())
    receipt = {
        "schema": "tai.reference.tei-records/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 and jsonschema",
        "command": "python integrations/tools/validate_records.py --sei-schema <...> --mmi-schema <...> --eki-openapi <...>",
        "result": "PASS" if all_valid else "FAIL",
        "observed": {"records": results, "allValid": all_valid, "count": len(results)},
        "scope": "Converts the SEI, MMI, and EKI projection artifacts into their product records and validates each. It does not write to any product.",
    }
    out = ROOT / args.out
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"allValid": all_valid, "count": len(results)}))
    return 0 if all_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
