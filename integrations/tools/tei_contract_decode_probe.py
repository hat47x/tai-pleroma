"""Compare how TEI's two entry points decode the same contract.

`tei-generator-select` reads a contract through readJSON, which calls
DisallowUnknownFields. `tei-generator-build` reads it through json.Unmarshal in
renderCandidateBytes, which ignores unknown fields. If that difference is real,
the same nested contract is refused by one entry point and silently accepted by
the other.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

NESTED_CONTRACT = {
    "schema": "tei.reference.generator-contract/v0",
    "id": "sui.nested.decode",
    "version": "1",
    "status": "reference-local",
    "inputs": [
        {"attribute": "sui.island.island_id", "primitive": "std.identifier"},
        {"attribute": "sui.island.card_ids", "primitive": "std.identifier"},
    ],
    "output": {"primitive": "std.text"},
    "projection": {
        "kind": "record",
        "fields": [
            {
                "name": "island",
                "input": "island",
                "attribute": "sui.island.island_id",
                "primitive": "std.identifier",
                "fields": [
                    {
                        "name": "cardIds",
                        "input": "cardIds",
                        "attribute": "sui.island.card_ids",
                        "primitive": "std.identifier",
                        "many": True,
                    }
                ],
            }
        ],
    },
}

FIXTURES = {
    "schema": "tei.reference.generator-fixture/v0",
    "contractId": "sui.nested.decode",
    "contractVersion": "1",
    "cases": [
        {"id": "present", "input": {"island": "island-1"}, "want": {"state": "present"}},
    ],
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args, cwd):
    return subprocess.run(
        [str(part) for part in args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="tei-decode-", dir=os.environ.get("GOTMPDIR") or None))
    contract_path = workdir / "nested.json"
    fixtures_path = workdir / "fixtures.json"
    contract_path.write_text(json.dumps(NESTED_CONTRACT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fixtures_path.write_text(json.dumps(FIXTURES, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    build = run(
        [
            "go", "run", "./tools/reference-generator-selection/cmd/tei-generator-build",
            "-contract", contract_path, "-strategy", "text-record-template", "-out", workdir / "candidate",
        ],
        cwd=args.tei_repo,
    )
    # tei-generator-select needs a TEI Workspace, so point it at the pilot's own
    # workspace instead of the TEI repository root.
    workspace = Path(args.workspace)
    select = run(
        [
            "go", "run", "./tools/reference-generator-selection/cmd/tei-generator-select",
            "-workspace", workspace, "-contract", contract_path,
            "-fixtures", fixtures_path, "-candidates", workdir,
        ],
        cwd=args.tei_repo,
    )

    def tail(completed):
        lines = (completed.stderr or completed.stdout).strip().splitlines()
        return lines[-1] if lines else ""

    def whole(completed):
        return (completed.stderr or completed.stdout).strip()

    checks = {
        "buildExit": build.returncode,
        "buildAccepted": build.returncode == 0,
        "buildTail": tail(build),
        "selectExit": select.returncode,
        "selectRefused": select.returncode != 0,
        "selectTail": tail(select),
        "selectSawUnknownField": "unknown field" in whole(select),
        "prefixDistinguishable": (build.returncode == 0) != (select.returncode == 0),
    }
    passed = (
        checks["buildAccepted"]
        and checks["selectRefused"]
        and checks["prefixDistinguishable"]
        and checks["selectSawUnknownField"]
    )
    receipt = {
        "schema": "tai.reference.tei-contract-decode-divergence/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the TEI reference generator selection tool built by go run",
        "command": f"python integrations/tools/tei_contract_decode_probe.py --tei-repo {args.tei_repo} --workspace {args.workspace} --artifact {args.artifact} --out evaluations/records/TEI-decode-divergence-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Feeds one nested contract to tei-generator-build and tei-generator-select. The build path accepts it (json.Unmarshal ignores unknown fields) while the select path refuses it with `unknown field \"fields\"` through readJSON. The same contract therefore has two answers depending on the command, and the unknown-field policy is not uniform. It does not change TEI.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
