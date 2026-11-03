"""Build and select a reference generator for one contract, then record it.

Shared by the pilot integrations. Windows needs TMP/TEMP to point at a
writable directory; the script passes that environment through to `go run`.
"""

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--fixtures", required=True)
    parser.add_argument("--strategy", default="text-record-template")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="tei-select-") as tmp:
        candidates = Path(tmp)
        build = subprocess.run(
            [
                "go",
                "run",
                "./tools/reference-generator-selection/cmd/tei-generator-build",
                "-contract",
                args.contract,
                "-strategy",
                args.strategy,
                "-out",
                str(candidates / args.strategy),
            ],
            cwd=args.tei_repo,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        if build.returncode != 0:
            print(build.stderr, file=sys.stderr)
            return 1
        select = subprocess.run(
            [
                "go",
                "run",
                "./tools/reference-generator-selection/cmd/tei-generator-select",
                "-workspace",
                str(Path(args.workspace).resolve()),
                "-contract",
                args.contract,
                "-fixtures",
                args.fixtures,
                "-candidates",
                str(candidates),
            ],
            cwd=args.tei_repo,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        if select.returncode != 0:
            print(select.stderr, file=sys.stderr)
            return 1
        result = json.loads(select.stdout)

    passed = bool(result.get("passed"))
    receipt = {
        "schema": "tai.reference.tei-selection/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go on PATH and Python 3.12",
        "command": f"python {Path(__file__)} --tei-repo {args.tei_repo} --workspace {args.workspace} --contract {args.contract}",
        "result": "PASS" if passed else "FAIL",
        "observed": {
            "contract": args.contract,
            "strategy": args.strategy,
            "passed": passed,
            "cases": len(result.get("candidates", [{}])[0].get("results", [])),
        },
        "scope": "Builds one reference generator and runs the fixture selection for the given contract. It does not compose a document or touch a product.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(receipt["observed"]))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
