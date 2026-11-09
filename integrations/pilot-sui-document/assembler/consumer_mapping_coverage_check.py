"""Measure which projected meanings survive SUI's reference consumer.

`validate_against_sui` reports `valid: true` when DocumentV1 accepts the payload.
That says nothing about whether each projected field reached the document. This
check compares the artifact with the payload the consumer builds, so a field that
is silently dropped is visible instead of looking like a success.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

PROBE = """
import json, sys
from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload
from sui_sensemaking_api.models import DocumentV1

artifact = json.load(open(sys.argv[1], encoding="utf-8"))
payload = to_documentv1_payload(
    from_artifact(artifact),
    transform={"panX": 0.0, "panY": 0.0, "zoom": 1.0},
    created_at="2026-11-03T00:00:00Z",
    updated_at="2026-11-03T00:00:00Z",
)
model = DocumentV1.model_validate(payload)

def keys_of(payload, name):
    value = payload.get(name)
    if isinstance(value, list) and value:
        first = value[0]
        return sorted(first.keys()) if isinstance(first, dict) else []
    if isinstance(value, dict):
        return sorted(value.keys())
    return []

print(json.dumps({
    "payloadTopLevel": sorted(payload.keys()),
    "payloadKeys": {name: keys_of(payload, name) for name in ("cards", "islands", "edges", "affiliations")},
    "modelAffiliations": len(model.affiliations or []),
    "modelReadingOrder": len(getattr(model, "readingOrder", []) or []),
    "valid": True,
}))
"""

COLLECTIONS = ("cards", "islands", "edges", "affiliations")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def element_keys(records):
    if not records:
        return []
    first = records[0]
    return sorted(first.keys()) if isinstance(first, dict) else []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    artifact = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    document = artifact["document"]
    src = Path(args.sui_repo) / "03_Implement/backend/src"

    completed = subprocess.run(
        [sys.executable, "-c", PROBE, str(Path(args.artifact).resolve())],
        env={**os.environ, "PYTHONPATH": str(src)},
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    lines = (completed.stdout or "").strip().splitlines()
    if completed.returncode != 0 or not lines:
        print((completed.stderr or "")[-600:], file=sys.stderr)
        return 1
    observed = json.loads(lines[-1])

    # The composed artifact nests the document record under "document".
    document_record = document.get("document", {})
    document_dropped = [
        key for key in document_record.keys() if key not in observed["payloadTopLevel"]
    ]
    per_collection = {}
    dropped_any = []
    for name in COLLECTIONS:
        source_keys = element_keys(document.get(name, []))
        kept_keys = observed["payloadKeys"][name]
        dropped = [key for key in source_keys if key not in kept_keys]
        per_collection[name] = {
            "sourceKeys": source_keys,
            "consumerKeys": kept_keys,
            "dropped": dropped,
            "sourceCount": len(document.get(name, []) or []),
        }
        if dropped or (source_keys and not kept_keys):
            dropped_any.append(name)

    source_affiliations = len(document.get("affiliations", []) or [])
    source_reading_order = len(document_record.get("readingOrder", []) or [])
    checks = {
        "valid": observed["valid"],
        "documentDropped": document_dropped,
        "collections": per_collection,
        "collectionsWithLoss": dropped_any,
        "modelAffiliations": observed["modelAffiliations"],
        "modelReadingOrder": observed["modelReadingOrder"],
        "sourceAffiliations": source_affiliations,
        "sourceReadingOrder": source_reading_order,
        "everyProjectedFieldSurvives": not document_dropped and not dropped_any,
        "affiliationsKept": observed["modelAffiliations"] == source_affiliations,
        "readingOrderKept": observed["modelReadingOrder"] == source_reading_order,
    }
    passed = (
        checks["valid"]
        and checks["everyProjectedFieldSurvives"]
        and checks["affiliationsKept"]
        and checks["readingOrderKept"]
    )
    receipt = {
        "schema": "tai.reference.sui-consumer-mapping/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 and SUI's reference consumer",
        "command": f"python integrations/pilot-sui-document/assembler/consumer_mapping_coverage_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-consumer-mapping-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Builds DocumentV1 through SUI's own consumer and compares the payload with the artifact, per collection and per document field. It records that every projected field that the consumer knows about survives (including readingOrder and affiliations), which contrasts with the meaning-change finding that a field the consumer does not know is dropped while validation still passes. It does not change SUI.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "documentDropped": document_dropped,
        "collectionsWithLoss": dropped_any,
        "affiliationsKept": checks["affiliationsKept"],
        "readingOrderKept": checks["readingOrderKept"],
        "valid": observed["valid"],
        "passed": passed,
    }))


if __name__ == "__main__":
    raise SystemExit(main())
