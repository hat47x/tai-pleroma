"""Validate a projection artifact and write a receipt."""

import argparse
import hashlib
import json
import time
from pathlib import Path

from validate_artifact import validate


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    errors = validate(payload)
    receipt = {
        "schema": "tai.reference.tei-artifact-validation/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12",
        "command": f"python integrations/pilot-sui-document/assembler/check_artifact.py --artifact {args.artifact}",
        "result": "PASS" if not errors else "FAIL",
        "passed": not errors,
        "errors": errors,
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "scope": "Structural validation of the artifact envelope and element shapes. It does not validate meaning against SUI's DocumentV1 model.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"passed": not errors, "errors": errors}))
    return 0 if not errors else 1


if __name__ == "__main__":
    main()
