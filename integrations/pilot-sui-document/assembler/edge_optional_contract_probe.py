"""Try the contract-side option for Edge endpoint kinds: make fromKind/toKind optional.

SUI allows Edge.fromKind/toKind to be None while the pilot contract requires
them. The product's model is the reference, so this probe tries the other side:
an optional contract that omits the kinds when absent, and checks whether the
generator accepts it and what it emits.
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


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args, cwd, stdin_text=None):
    return subprocess.run(
        [str(part) for part in args],
        cwd=cwd,
        input=stdin_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def optional_edge_contract(version="6"):
    return {
        "schema": "tei.reference.generator-contract/v0",
        "id": "sui.edge.record",
        "version": version,
        "status": "reference-local",
        "note": "SUIのEdge.fromKind/toKindは任意なので、契約側も任意にして欠落時は出力から省略する試作。",
        "inputs": [
            {"attribute": "sui.edge.edge_id", "primitive": "std.identifier"},
            {"attribute": "sui.edge.from_id", "primitive": "std.identifier"},
            {"attribute": "sui.edge.to_id", "primitive": "std.identifier"},
            {"attribute": "sui.edge.relation", "primitive": "std.code"},
            {"attribute": "sui.edge.from_kind", "primitive": "std.code"},
            {"attribute": "sui.edge.to_kind", "primitive": "std.code"},
        ],
        "output": {"primitive": "std.text"},
        "projection": {
            "kind": "record",
            "fields": [
                {"name": "id", "input": "id", "attribute": "sui.edge.edge_id", "primitive": "std.identifier"},
                {"name": "fromId", "input": "fromId", "attribute": "sui.edge.from_id", "primitive": "std.identifier"},
                {"name": "toId", "input": "toId", "attribute": "sui.edge.to_id", "primitive": "std.identifier"},
                {"name": "type", "input": "type", "attribute": "sui.edge.relation", "primitive": "std.code"},
                {
                    "name": "fromKind",
                    "input": "fromKind",
                    "attribute": "sui.edge.from_kind",
                    "primitive": "std.code",
                    "optional": True,
                },
                {
                    "name": "toKind",
                    "input": "toKind",
                    "attribute": "sui.edge.to_kind",
                    "primitive": "std.code",
                    "optional": True,
                },
            ],
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="tei-edgeoptcontract-", dir=os.environ.get("GOTMPDIR") or None))
    contract_path = workdir / "edge-optional.json"
    contract_path.write_text(
        json.dumps(optional_edge_contract(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    out_dir = workdir / "edge"

    build = run(
        [
            "go", "run", "./tools/reference-generator-selection/cmd/tei-generator-build",
            "-contract", str(contract_path), "-strategy", "text-record-template", "-out", str(out_dir),
        ],
        cwd=args.tei_repo,
    )
    if build.returncode != 0:
        message = (build.stderr or build.stdout).strip().splitlines()
        receipt = {
            "schema": "tai.reference.tei-edge-optional-contract/v0",
            "synthetic": False,
            "evidenceKind": "real-execution",
            "publicationAllowed": False,
            "date": time.strftime("%Y-%m-%d"),
            "host": "Windows with the TEI reference generator selection tool",
            "command": f"python integrations/pilot-sui-document/assembler/edge_optional_contract_probe.py --tei-repo {args.tei_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-edge-optional-contract-2026-11-06.json",
            "result": "FAIL",
            "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
            "observed": {"buildExit": build.returncode, "stderrTail": message[-1] if message else ""},
            "scope": "Attempts an optional Edge contract and records the generator's refusal. It does not change the pilot contract.",
        }
        Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(receipt["observed"]))
        return 1

    binary = out_dir / ("candidate.exe" if os.name == "nt" else "candidate")
    compiled = run(["go", "build", "-o", str(binary), "main.go"], cwd=out_dir)
    if compiled.returncode != 0:
        print(compiled.stderr, file=sys.stderr)
        return 1

    cases = {
        "bothKinds": {"id": "edge-1", "fromId": "card-1", "toId": "card-2", "type": "supports", "fromKind": "card", "toKind": "card"},
        "absentKinds": {"id": "edge-2", "fromId": "card-1", "toId": "card-2", "type": "supports"},
        "nullKinds": {"id": "edge-3", "fromId": "card-1", "toId": "island-1", "type": "contains", "fromKind": None, "toKind": "island"},
    }
    observed = {}
    for name, payload in cases.items():
        completed = run([binary], cwd=out_dir, stdin_text=json.dumps(payload))
        body = json.loads(completed.stdout) if completed.returncode == 0 and completed.stdout.strip().startswith("{") else {}
        text = body.get("text")
        parsed = json.loads(text) if isinstance(text, str) and text.startswith("{") else None
        observed[name] = {
            "exit": completed.returncode,
            "state": body.get("state"),
            "omitsKinds": parsed is not None and "fromKind" not in parsed and "toKind" not in parsed,
            "kinds": {key: parsed.get(key) for key in ("fromKind", "toKind")} if parsed else None,
        }

    checks = {
        "cases": observed,
        "contractAccepted": True,
        "bothKindsProjected": observed["bothKinds"]["state"] == "present"
        and observed["bothKinds"]["kinds"] == {"fromKind": "card", "toKind": "card"},
        "absentKindsProjectedWithoutThem": observed["absentKinds"]["state"] == "present"
        and observed["absentKinds"]["omitsKinds"] is True,
        "partialKindsKeepThePresentOne": observed["nullKinds"]["state"] == "present"
        and observed["nullKinds"]["omitsKinds"] is False
        and observed["nullKinds"]["kinds"] == {"fromKind": None, "toKind": "island"},
    }
    passed = (
        checks["contractAccepted"]
        and checks["bothKindsProjected"]
        and checks["absentKindsProjectedWithoutThem"]
        and checks["partialKindsKeepThePresentOne"]
    )
    receipt = {
        "schema": "tai.reference.tei-edge-optional-contract/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the TEI reference generator selection tool and a locally compiled candidate",
        "command": f"python integrations/pilot-sui-document/assembler/edge_optional_contract_probe.py --tei-repo {args.tei_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-edge-optional-contract-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Builds an optional-kind Edge contract, then feeds it a complete edge, an edge without kinds, and an edge with one null kind. It records that the optional contract projects the kind-less edge by omitting the kinds. It does not change the pilot contract itself.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
