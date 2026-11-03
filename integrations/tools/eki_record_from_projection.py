"""Turn the EKI projection artifact into an eki.task-request/v1 record."""

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
    parser.add_argument("--openapi", required=True)
    parser.add_argument("--out", default="evaluations/artifacts/eki-task-request-record.json")
    parser.add_argument("--receipt-out", default="evaluations/records/EKI-TEI-record-2026-11-03.json")
    args = parser.parse_args()

    artifact_path = ROOT / "evaluations/artifacts/eki-task-request-projection.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    task = artifact["taskRequest"]
    record = {
        "schema": task["schema"],
        "executor": {"id": task["executorId"], "version_constraint": task["versionConstraint"]},
        "inputs": [],
        "parameters": {},
        "resources": {
            "cpu_millis": task["cpuMillis"],
            "memory_bytes": task["memoryBytes"],
            "wall_time_seconds": task["wallTimeSeconds"],
            "output_bytes_max": task["outputBytesMax"],
            "network_bytes_max": task["networkBytesMax"],
        },
        "reliability": {
            "retryable": task["retryable"],
            "preemptible": task["preemptible"],
            "checkpointable": task["checkpointable"],
            "deterministic": task["deterministic"],
            "max_attempts": task["maxAttempts"],
            "effect_mode": task["effectMode"],
        },
    }
    if task.get("priority"):
        record["priority"] = task["priority"]
    if task.get("clientRequestId"):
        record["client_request_id"] = task["clientRequestId"]

    openapi_path = Path(args.openapi).resolve()
    openapi = json.loads(openapi_path.read_text(encoding="utf-8"))
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012

    uri = openapi_path.as_uri()
    registry = Registry().with_resource(uri, Resource.from_contents(openapi, default_specification=DRAFT202012))
    task_request_schema = {"$ref": f"{uri}#/components/schemas/TaskRequest"}
    errors = sorted(
        jsonschema.Draft202012Validator(task_request_schema, registry=registry).iter_errors(record),
        key=lambda error: list(error.path),
    )
    out_path = ROOT / args.out
    out_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "schema": "tai.reference.eki-task-request-record/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 and jsonschema",
        "command": "python integrations/tools/eki_record_from_projection.py --openapi <EKI openapi.json>",
        "result": "PASS" if not errors else "FAIL",
        "artifact": {"path": "evaluations/artifacts/eki-task-request-projection.json", "digest": digest(artifact_path)},
        "record": {"path": args.out, "digest": digest(out_path)},
        "observed": {
            "valid": not errors,
            "errors": [error.message for error in errors],
            "executorId": task["executorId"],
            "resourceFields": sorted(record["resources"]),
        },
        "scope": "Reassembles a flat projection into the OpenAPI TaskRequest shape and validates it against EKI's published contract. It does not call eki-control or admit a task.",
    }
    Path(args.receipt_out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt["observed"]))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
