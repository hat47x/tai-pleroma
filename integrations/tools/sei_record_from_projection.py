"""Turn the SEI projection artifact into a decision-memory record and validate it."""

import argparse
import hashlib
import json
import time
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", required=True)
    parser.add_argument("--out", default="evaluations/artifacts/sei-decision-memory-record.json")
    parser.add_argument("--receipt-out", default="evaluations/records/SEI-TEI-record-2026-11-03.json")
    args = parser.parse_args()

    artifact_path = ROOT / "evaluations/artifacts/sei-decision-projection.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    decision = artifact["decision"]
    record = {
        "contract": "sei.decision-memory/v1alpha1",
        "record_type": "decision",
        "decision": {
            "ref": {"kind": decision["refKind"], "id": decision["refId"]},
            "statement": decision["statement"],
        },
    }
    if decision.get("rationale"):
        record["decision"]["rationale"] = decision["rationale"]

    schema_path = Path(args.schema).resolve()
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema.setdefault("$id", schema_path.as_uri())
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012

    registry = Registry()
    for sibling in schema_path.parent.glob("*.schema.json"):
        contents = json.loads(sibling.read_text(encoding="utf-8"))
        contents.setdefault("$id", sibling.resolve().as_uri())
        registry = registry.with_resource(
            sibling.resolve().as_uri(), Resource.from_contents(contents, default_specification=DRAFT202012)
        )
    validator = jsonschema.Draft202012Validator(schema, registry=registry)
    errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
    out_path = ROOT / args.out
    out_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    receipt = {
        "schema": "tai.reference.sei-decision-record/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 and jsonschema",
        "command": "python integrations/tools/sei_record_from_projection.py --schema <SEI schema>",
        "result": "PASS" if not errors else "FAIL",
        "artifact": {"path": "evaluations/artifacts/sei-decision-projection.json", "digest": digest(artifact_path)},
        "record": {"path": args.out, "digest": digest(out_path)},
        "observed": {
            "valid": not errors,
            "errors": [error.message for error in errors],
            "refId": decision["refId"],
            "recordType": record["record_type"],
            "schema": args.schema,
        },
        "scope": "Maps one projection artifact to the SEI decision-memory schema and validates it. It does not write to SEI or prove SEI ingestion.",
    }
    Path(args.receipt_out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt["observed"]))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
