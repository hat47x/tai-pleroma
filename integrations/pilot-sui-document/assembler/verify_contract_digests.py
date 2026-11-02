"""Verify that an artifact's contract digests match the contract files."""

import argparse
import hashlib
import json
import time
from pathlib import Path


def digest(path):
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    artifact = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    workspace = Path(args.workspace)
    checked = {}
    mismatches = []
    for name, expected in artifact.get("source", {}).get("contracts", {}).items():
        path = workspace / "candidates" / name / "contract.json"
        if not path.exists():
            mismatches.append(f"{name}: missing contract")
            continue
        actual = digest(path)
        checked[name] = {"expected": expected.get("contractDigest"), "actual": actual}
        if actual != expected.get("contractDigest"):
            mismatches.append(f"{name}: digest mismatch")

    receipt = {
        "schema": "tai.reference.tei-contract-digest-check/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12",
        "command": f"python integrations/pilot-sui-document/assembler/verify_contract_digests.py --artifact {args.artifact} --workspace {args.workspace}",
        "result": "PASS" if not mismatches else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": {
            "contracts": len(checked),
            "mismatches": mismatches,
            "allMatch": not mismatches,
        },
        "scope": "Compares each contract digest recorded in the artifact with the contract file, normalizing line endings. It does not verify the generator binaries or the TEI repository revision.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(receipt["observed"]))
    raise SystemExit(0 if not mismatches else 1)


if __name__ == "__main__":
    main()
