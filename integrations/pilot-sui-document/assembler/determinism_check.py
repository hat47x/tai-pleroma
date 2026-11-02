"""Run the projection flow twice and compare the artifacts."""

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--runs", type=int, default=2)
    args = parser.parse_args()

    assembler = Path(__file__).resolve().parent
    workspace = assembler.parent
    digests = []
    cases = []
    receipts = []
    with tempfile.TemporaryDirectory(prefix="tei-determinism-") as tmp:
        for run in range(1, args.runs + 1):
            artifact = Path(tmp) / f"artifact-{run}.json"
            receipt = Path(tmp) / f"receipt-{run}.json"
            subprocess.run(
                [
                    sys.executable,
                    str(assembler / "integration_flow.py"),
                    "--tei-repo",
                    args.tei_repo,
                    "--workspace",
                    str(workspace),
                    "--out",
                    str(receipt),
                    "--artifact-out",
                    str(artifact),
                ],
                check=True,
                capture_output=True,
            )
            data = json.loads(artifact.read_text(encoding="utf-8"))
            digests.append(digest(artifact))
            cases.append(json.loads(receipt.read_text(encoding="utf-8"))["casesPassed"])
            receipts.append(data["contract"]["version"])

    receipt = {
        "schema": "tai.reference.tei-determinism/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 and Go",
        "command": f"python integrations/pilot-sui-document/assembler/determinism_check.py --tei-repo {args.tei_repo}",
        "result": "PASS" if len(set(digests)) == 1 else "FAIL",
        "observed": {
            "runs": args.runs,
            "identical": len(set(digests)) == 1,
            "digests": digests,
            "casesPassed": cases,
        },
        "scope": "Runs the projection flow repeatedly with the same inputs and compares the artifact digests. It does not prove determinism across hosts or toolchain versions.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(receipt["observed"]))
    if receipt["result"] != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
