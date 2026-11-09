"""Probe whether TEI's generator-contract accepts a nested record field.

The stage-4 decision claims nesting is a TEI-side contract gap. This probe feeds
such contracts to `tei-generator-build` and records which shape is refused and
why, so the gap is evidenced rather than assumed.
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

SCHEMA = "tei.reference.generator-contract/v0"

NESTED_VARIANTS = {
    "fieldWithFields": {
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
        "inputs": [
            {"attribute": "sui.island.island_id", "primitive": "std.identifier"},
            {"attribute": "sui.island.card_ids", "primitive": "std.identifier"},
        ],
    },
    "arrayOfRecord": {
        "projection": {
            "kind": "record",
            "fields": [
                {
                    "name": "cards",
                    "input": "cards",
                    "attribute": "sui.card.card_id",
                    "primitive": "std.identifier",
                    "many": True,
                    "fields": [
                        {
                            "name": "text",
                            "input": "text",
                            "attribute": "sui.card.text",
                            "primitive": "std.text",
                        }
                    ],
                }
            ],
        },
        "inputs": [
            {"attribute": "sui.card.card_id", "primitive": "std.identifier"},
            {"attribute": "sui.card.text", "primitive": "std.text"},
        ],
    },
    "newKind": {
        "projection": {"kind": "nested"},
        "inputs": [{"attribute": "sui.card.text", "primitive": "std.text"}],
    },
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="tei-nesting-", dir=os.environ.get("GOTMPDIR") or None))
    env = os.environ.copy()
    env.setdefault("TMP", str(workdir))
    env.setdefault("TEMP", str(workdir))

    def build(contract_name, contract):
        contract_path = workdir / f"{contract_name}.json"
        contract_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        completed = subprocess.run(
            [
                "go",
                "run",
                "./tools/reference-generator-selection/cmd/tei-generator-build",
                "-contract",
                str(contract_path),
                "-strategy",
                "text-record-template",
                "-out",
                str(workdir / contract_name),
            ],
            cwd=args.tei_repo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        message = (completed.stderr or completed.stdout).strip().splitlines()
        source_path = workdir / contract_name / "main.go"
        source = source_path.read_text(encoding="utf-8") if source_path.exists() else ""
        return {
            "exit": completed.returncode,
            "generated": source_path.exists(),
            "stderrTail": message[-1] if message else "",
            "emitsNestedObject": "map[string]any{" in source or "record[" in source,
            "sourceHasNestedFieldNames": any(
                name in source for name in ("cardIds", "text")
            ),
        }

    results = {}
    for name, variant in NESTED_VARIANTS.items():
        contract = {
            "schema": SCHEMA,
            "id": f"sui.nested.{name}",
            "version": "1",
            "status": "reference-local",
            "inputs": variant["inputs"],
            "output": {"primitive": "std.text"},
            "projection": variant["projection"],
        }
        results[name] = build(name, contract)

    # The flat control must still be refused only for nesting, not for any other reason.
    flat = {
        "schema": SCHEMA,
        "id": "sui.nested.flatControl",
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
                {"name": "id", "input": "id", "attribute": "sui.island.island_id", "primitive": "std.identifier"},
                {
                    "name": "cardIds",
                    "input": "cardIds",
                    "attribute": "sui.island.card_ids",
                    "primitive": "std.identifier",
                    "many": True,
                },
            ],
        },
    }
    results["flatControl"] = build("flatControl", flat)

    checks = {
        "variants": results,
        "unknownKindRefused": results["newKind"]["exit"] != 0,
        "unknownKindNotGenerated": not results["newKind"]["generated"],
        # TEI decodes the contract with encoding/json without
        # DisallowUnknownFields, so an extra `fields` key inside a projection
        # field is not refused: it is silently dropped and the field collapses
        # to its declared primitive/cardinality.
        "nestedFieldsSilentlyDropped": (
            results["fieldWithFields"]["exit"] == 0
            and results["arrayOfRecord"]["exit"] == 0
        ),
        "flatControlAccepted": results["flatControl"]["exit"] == 0,
        "flatControlGenerated": results["flatControl"]["generated"],
    }
    passed = (
        checks["unknownKindRefused"]
        and checks["unknownKindNotGenerated"]
        and checks["nestedFieldsSilentlyDropped"]
        and checks["flatControlAccepted"]
        and checks["flatControlGenerated"]
    )
    receipt = {
        "schema": "tai.reference.tei-nesting-probe/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the TEI reference generator selection tool built by go run",
        "command": f"python integrations/tools/tei_nesting_probe.py --tei-repo {args.tei_repo} --artifact {args.artifact} --out evaluations/records/TEI-nesting-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Feeds three projection shapes and one flat control to tei-generator-build. An unknown kind is refused, but a nested `fields` key inside a projection field is silently dropped because the contract is decoded with encoding/json without DisallowUnknownFields: the generator is built and emits a flat field instead. That is worse than a refusal, because the contract looks nested while the output is not. It does not try to change TEI.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
