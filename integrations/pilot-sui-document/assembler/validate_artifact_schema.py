"""Validate a projection artifact against its JSON Schema."""

import argparse
import hashlib
import json
import time
from pathlib import Path

import jsonschema


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    artifact = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(artifact), key=lambda error: list(error.path))

    receipt = {
        "schema": "tai.reference.tei-artifact-schema-check/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 and jsonschema",
        "command": f"python integrations/pilot-sui-document/assembler/validate_artifact_schema.py --artifact {args.artifact} --schema {args.schema}",
        "result": "PASS" if not errors else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "schemaFile": {"path": args.schema, "digest": digest(args.schema)},
        "observed": {
            "errors": [error.message for error in errors],
            "valid": not errors,
        },
        "scope": "Validates the artifact envelope and element shapes against the JSON Schema. It does not validate semantic references or DocumentV1.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(receipt["observed"]))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
