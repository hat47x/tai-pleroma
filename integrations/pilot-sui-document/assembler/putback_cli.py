"""CLI: evaluate a read-only projection against the source of truth for Putback."""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

from putback_check import evaluate_putback


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--existing", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    artifact = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    existing = json.loads(Path(args.existing).read_text(encoding="utf-8"))
    result = evaluate_putback(artifact, existing)
    receipt = {
        "schema": "tai.reference.tei-putback-check/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": f"Python {sys.version.split()[0]}",
        "command": (
            f"python integrations/pilot-sui-document/assembler/putback_cli.py "
            f"--artifact {args.artifact} --existing {args.existing}"
        ),
        "result": "REFUSED" if result["decision"] == "refused" else "PASS",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "existing": {"path": args.existing, "digest": digest(args.existing)},
        "observed": result,
        "scope": (
            "Compares a read-only projection with one source-of-truth document and reports the "
            "Putback decision. It does not write, call the SUI API, or prove that a refused "
            "Putback is the only correct business choice."
        ),
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({
        "decision": result["decision"],
        "changes": len(result["changes"]),
        "ambiguous": len(result["ambiguous"]),
    }))
    raise SystemExit(0 if result["decision"] != "refused" else 3)


if __name__ == "__main__":
    main()
