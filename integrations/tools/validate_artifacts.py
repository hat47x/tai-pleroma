"""Validate every pilot projection artifact against its JSON Schema."""

import hashlib
import json
import time
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = {
    "sui": (
        "evaluations/artifacts/documentv1-projection.json",
        "integrations/pilot-sui-document/artifact.schema.json",
    ),
    "sei": (
        "evaluations/artifacts/sei-decision-projection.json",
        "integrations/pilot-sei-decision/artifact.schema.json",
    ),
    "mmi": (
        "evaluations/artifacts/mmi-format-profile-projection.json",
        "integrations/pilot-mmi-format-profile/artifact.schema.json",
    ),
    "eki": (
        "evaluations/artifacts/eki-task-request-projection.json",
        "integrations/pilot-eki-task-request/artifact.schema.json",
    ),
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    results = {}
    for name, (artifact_path, schema_path) in ARTIFACTS.items():
        artifact_file = ROOT / artifact_path
        schema_file = ROOT / schema_path
        if not artifact_file.exists() or not schema_file.exists():
            results[name] = {"valid": False, "errors": ["missing artifact or schema"]}
            continue
        artifact = json.loads(artifact_file.read_text(encoding="utf-8"))
        schema = json.loads(schema_file.read_text(encoding="utf-8"))
        errors = sorted(
            jsonschema.Draft202012Validator(schema).iter_errors(artifact),
            key=lambda error: list(error.path),
        )
        results[name] = {
            "valid": not errors,
            "errors": [error.message for error in errors],
            "artifact": {"path": artifact_path, "digest": digest(artifact_file)},
            "schema": {"path": schema_path, "digest": digest(schema_file)},
            "schemaId": artifact.get("schema"),
        }

    all_valid = all(item["valid"] for item in results.values())
    receipt = {
        "schema": "tai.reference.tei-artifacts-crosscheck/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 and jsonschema",
        "command": "python integrations/tools/validate_artifacts.py",
        "result": "PASS" if all_valid else "FAIL",
        "observed": {"artifacts": results, "allValid": all_valid, "count": len(results)},
        "scope": "Validates each pilot artifact against its own JSON Schema. It does not compare semantics across products or validate against product code.",
    }
    out = ROOT / "evaluations/records/TEI-artifacts-crosscheck-2026-11-03.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"allValid": all_valid, "count": len(results)}))
    return 0 if all_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
