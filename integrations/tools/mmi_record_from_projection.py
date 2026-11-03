"""Try to turn the MMI projection artifact into a full format-profile record."""

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
    parser.add_argument("--out", default="evaluations/artifacts/mmi-format-profile-record.json")
    parser.add_argument("--receipt-out", default="evaluations/mmi-record-attempt-2026-11-03.json")
    args = parser.parse_args()

    artifact_path = ROOT / "evaluations/artifacts/mmi-format-profile-projection.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    profile = artifact["profile"]
    record = {
        "schemaVersion": profile["schemaVersion"],
        "id": profile["id"],
        "label": profile["label"],
        "purpose": profile["purpose"],
        "status": profile["status"],
        "featureVersion": profile["featureVersion"],
        "sourceProfileId": profile["sourceProfileId"],
        "sourceEvidence": list(profile.get("sourceEvidence") or []),
        "features": list(profile.get("features") or []),
        "provenance": {
            "sourceKind": "tei-projection",
            "sourceDigest": artifact["source"]["contract"]["sourceDigest"],
            "generationMethod": "worksheet-prototype-v1",
        },
    }
    schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(record),
        key=lambda error: list(error.path),
    )
    out_path = ROOT / args.out
    out_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "schema": "tai.reference.mmi-format-profile-record/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 and jsonschema",
        "command": "python integrations/tools/mmi_record_from_projection.py --schema <MMI schema>",
        "result": "PASS" if not errors else "FAIL",
        "artifact": {"path": "evaluations/artifacts/mmi-format-profile-projection.json", "digest": digest(artifact_path)},
        "record": {"path": args.out, "digest": digest(out_path)},
        "observed": {
            "valid": not errors,
            "errors": [error.message for error in errors],
            "featureCount": len(record["features"]),
        },
        "scope": "Shows whether the flat format-profile projection can satisfy the MMI format-profile schema. It does not change MMI or claim a valid profile.",
    }
    Path(args.receipt_out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt["observed"]))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
