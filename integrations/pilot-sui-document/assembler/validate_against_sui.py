"""Validate a projection artifact against SUI's DocumentV1 model."""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    src = Path(args.sui_repo) / "03_Implement/backend/src"
    sys.path.insert(0, str(src))
    from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload
    from sui_sensemaking_api.models import DocumentV1
    import pydantic

    payload = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    document = from_artifact(payload)
    documentv1 = to_documentv1_payload(
        document,
        transform={"panX": 0.0, "panY": 0.0, "zoom": 1.0},
        created_at="2026-11-03T00:00:00Z",
        updated_at="2026-11-03T00:00:00Z",
    )
    model = DocumentV1.model_validate(documentv1)

    receipt = {
        "schema": "tai.reference.tei-documentv1-validation/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": f"Windows with Python and pydantic {pydantic.VERSION}",
        "command": f"python integrations/pilot-sui-document/assembler/validate_against_sui.py --sui-repo {args.sui_repo} --artifact {args.artifact}",
        "result": "PASS",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": {
            "documentId": model.id,
            "cards": len(model.cards),
            "islands": len(model.islands),
            "affiliations": len(model.affiliations or []),
            "documentV1Valid": True,
        },
        "scope": "The artifact is read by SUI's consumer and validated by SUI's DocumentV1 model with caller-supplied transform and timestamps. It does not save, call the API, or prove human acceptance.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"valid": True, "documentId": model.id}))


if __name__ == "__main__":
    main()
