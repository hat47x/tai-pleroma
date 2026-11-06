"""Validate the PoC evaluation template against its schema and its own limits."""

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "evaluations/poc-evaluation.schema.json"
TEMPLATE = ROOT / "evaluations/templates/poc-evaluation.template.json"


def main():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(template), key=lambda e: e.path)
    paths = {run["path"] for run in template.get("runs", [])}
    checks = {
        "schemaValid": not errors,
        "syntheticFlagged": template.get("synthetic") is True,
        "notEvaluated": template.get("evaluated") is False,
        "bothPaths": paths == {"B", "T"},
        "limitsStated": len(template.get("limits", [])) >= 1,
    }
    passed = all(checks.values())
    print(
        json.dumps(
            {
                "passed": passed,
                "checks": checks,
                "errors": [error.message for error in errors],
            }
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
