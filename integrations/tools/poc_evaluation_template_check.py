"""Validate the PoC evaluation template against its schema and its own limits.

The check avoids third-party packages so it runs in the CI image without extra
installs; it enforces the fields the schema marks as required and the constants
it pins.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "evaluations/poc-evaluation.schema.json"
TEMPLATE = ROOT / "evaluations/templates/poc-evaluation.template.json"

RUN_FIELDS = [
    "path", "order", "startedAt", "endedAt", "durationSeconds",
    "handEdits", "interventions", "attempts", "contextInput", "reviewFindings",
]
CONDITION_FIELDS = ["product", "evaluationSet", "environment", "teiCommit"]


def main():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    errors = []

    if schema.get("properties", {}).get("schema", {}).get("const") != template.get("schema"):
        errors.append("schema constant mismatch")
    for field in schema.get("required", []):
        if field not in template:
            errors.append(f"missing required field: {field}")
    for field in CONDITION_FIELDS:
        if not isinstance(template.get("conditions", {}).get(field), str):
            errors.append(f"conditions.{field} must be a string")

    runs = template.get("runs", [])
    if len(runs) < 2:
        errors.append("runs must have at least two entries")
    for run in runs:
        for field in RUN_FIELDS:
            if field not in run:
                errors.append(f"run missing field: {field}")
        for group in ("handEdits", "interventions", "attempts", "contextInput", "reviewFindings"):
            value = run.get(group)
            if not isinstance(value, dict):
                errors.append(f"{group} must be an object")
                continue
            for key, number in value.items():
                if not isinstance(number, int) or number < 0:
                    errors.append(f"{group}.{key} must be a non-negative integer")

    paths = {run.get("path") for run in runs}
    checks = {
        "schemaFields": not errors,
        "syntheticFlagged": template.get("synthetic") is True,
        "notEvaluated": template.get("evaluated") is False,
        "bothPaths": paths == {"B", "T"},
        "limitsStated": len(template.get("limits", [])) >= 1,
    }
    passed = all(checks.values())
    print(json.dumps({"passed": passed, "checks": checks, "errors": errors}))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
