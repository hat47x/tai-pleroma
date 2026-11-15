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
import platform
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
# Report both the mapped payload and what DocumentV1 actually retained.
normalized = model.model_dump(exclude_none=True)

def keys_of(payload, name):
    value = payload.get(name)
    if isinstance(value, list):
        return sorted({key for item in value if isinstance(item, dict) for key in item})
    if isinstance(value, dict):
        return sorted(value.keys())
    return []

print(json.dumps({
    "payloadTopLevel": sorted(payload.keys()),
    "payloadKeys": {name: keys_of(payload, name) for name in ("cards", "islands", "edges", "affiliations")},
    "modelTopLevel": sorted(normalized.keys()),
    "modelKeys": {name: keys_of(normalized, name) for name in ("cards", "islands", "edges", "affiliations")},
    "modelAffiliations": len(model.affiliations or []),
    "modelReadingOrder": len(getattr(model, "readingOrder", []) or []),
    "modelReadingOrderValues": list(getattr(model, "readingOrder", []) or []),
    "valid": True,
}))
"""

COLLECTIONS = ("cards", "islands", "edges", "affiliations")
REPO_ROOT = Path(__file__).resolve().parents[3]
HISTORICAL_RECEIPT = REPO_ROOT / "evaluations/records/SUI-consumer-mapping-2026-11-06.json"
CONSUMER_MODULES = (
    "sui_sensemaking_api/documentv1_projection.py",
    "sui_sensemaking_api/models.py",
)


def fresh_output_path(path):
    """A replay is a new attempt; never overwrite an observed historical receipt."""
    output = Path(path).resolve()
    if output == HISTORICAL_RECEIPT.resolve():
        raise ValueError("historical SUI consumer FAIL receipt must remain unchanged")
    if output.exists():
        raise FileExistsError(f"replay receipt already exists: {output}")
    return output


def consumer_source_digests(src):
    """Pin the two SUI Python modules used here; not a full dependency closure."""
    return {name: digest(src / name) for name in CONSUMER_MODULES}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def element_keys(records):
    if not records:
        return []
    return sorted({key for item in records if isinstance(item, dict) for key in item})


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        output = fresh_output_path(args.out)
    except (ValueError, FileExistsError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    artifact_path = Path(args.artifact).resolve()
    src = (Path(args.sui_repo).resolve() / "03_Implement/backend/src")
    artifact_digest = digest(artifact_path)
    source_digests = consumer_source_digests(src)
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    document = artifact["document"]

    completed = subprocess.run(
        [sys.executable, "-c", PROBE, str(artifact_path)],
        env={**os.environ, "PYTHONPATH": str(src)},
        cwd=str(Path(args.sui_repo).resolve()),
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
    if artifact_digest != digest(artifact_path) or source_digests != consumer_source_digests(src):
        print("artifact or SUI consumer source changed during the replay", file=sys.stderr)
        return 1

    # The composed artifact nests the document record under "document".
    document_record = document.get("document", {})
    document_dropped = [
        key for key in document_record.keys() if key not in observed["modelTopLevel"]
    ]
    per_collection = {}
    dropped_any = []
    for name in COLLECTIONS:
        source_keys = element_keys(document.get(name, []))
        kept_keys = observed["modelKeys"][name]
        dropped = [key for key in source_keys if key not in kept_keys]
        per_collection[name] = {
            "sourceKeys": source_keys,
            "payloadKeys": observed["payloadKeys"][name],
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
        "readingOrderKept": observed["modelReadingOrderValues"] == (document_record.get("readingOrder") or []),
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
        "host": platform.platform(),
        "command": " ".join([sys.executable, __file__, "--sui-repo", args.sui_repo,
                             "--artifact", args.artifact, "--out", args.out]),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": artifact_digest},
        "replayProvenance": {
            "pythonVersion": sys.version,
            "pythonExecutable": sys.executable,
            "suiSourceModules": source_digests,
            "checkerDigest": digest(__file__),
            "suiSourceRoot": str(src),
        },
        "observed": checks,
        "scope": "Runs SUI's reference projection and inspects both its input payload and the validated DocumentV1 model; every projected field and the exact readingOrder must survive. This is an isolated consumer replay, not SUI's persistent Save/ReRead or a current authorization/Disclosure grant.",
    }
    # Exclusive creation prevents a second replay from overwriting the first
    # even if the output appeared after fresh_output_path's preflight check.
    try:
        with output.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    except FileExistsError:
        print(f"replay receipt already exists: {output}", file=sys.stderr)
        return 2
    print(json.dumps({
        "documentDropped": document_dropped,
        "collectionsWithLoss": dropped_any,
        "affiliationsKept": checks["affiliationsKept"],
        "readingOrderKept": checks["readingOrderKept"],
        "valid": observed["valid"],
        "passed": passed,
    }))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
