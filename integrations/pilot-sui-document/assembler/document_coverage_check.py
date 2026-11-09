"""Measure how much of SUI's DocumentV1 the TEI projection contracts actually cover.

The gap document claims a set of unmodelled fields. This check recomputes the
coverage from the live SUI models and the live contract files, so the claim is
evidence rather than prose that can drift.
"""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def model_fields(models_py, class_name):
    """Return the declared field names of one pydantic class, following one base."""
    import ast

    tree = ast.parse(models_py.read_text(encoding="utf-8"))
    classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
    collected = []
    seen = set()
    pending = [class_name]
    while pending:
        name = pending.pop()
        if name in seen or name not in classes:
            continue
        seen.add(name)
        node = classes[name]
        for statement in node.body:
            if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
                collected.append(statement.target.id)
            elif isinstance(statement, ast.Assign):
                for target in statement.targets:
                    if isinstance(target, ast.Name):
                        collected.append(target.id)
        for base in node.bases:
            base_name = base.id if isinstance(base, ast.Name) else None
            if base_name:
                pending.append(base_name)
    return collected


def contract_fields(contract_path):
    payload = json.loads(contract_path.read_text(encoding="utf-8"))
    return {
        "version": payload.get("version"),
        "fields": [field["name"] for field in payload["projection"].get("fields", [])],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    models_py = Path(args.sui_repo) / "03_Implement/backend/src/sui_sensemaking_api/models.py"
    candidates = Path(args.workspace) / "candidates"

    pairs = [
        ("DocumentV1", "document-record"),
        ("Card", "card-record"),
        ("Island", "island-record"),
        ("Edge", "edge-record"),
    ]
    coverage = {}
    for model_name, contract_dir in pairs:
        fields = model_fields(models_py, model_name)
        contract = contract_fields(candidates / contract_dir / "contract.json")
        covered = sorted(set(fields) & set(contract["fields"]))
        missing = sorted(set(fields) - set(contract["fields"]))
        extra = sorted(set(contract["fields"]) - set(fields))
        coverage[model_name] = {
            "modelFieldCount": len(fields),
            "contractVersion": contract["version"],
            "contractFields": contract["fields"],
            "covered": covered,
            "missing": missing,
            "pilotOnly": extra,
            "coverageRatio": round(len(covered) / len(fields), 3) if fields else None,
        }

    affiliation_contract = contract_fields(candidates / "affiliation-record" / "contract.json")
    checks = {
        "coverage": coverage,
        "affiliationContractFields": affiliation_contract["fields"],
        # DocumentV1 must not appear as a field of itself: the model is the document.
        "documentMissingIncludesCollections": all(
            name in coverage["DocumentV1"]["missing"]
            for name in ("cards", "edges", "islands", "affiliations")
        ),
        "pilotOnlyFields": sorted(
            {name for block in coverage.values() for name in block["pilotOnly"]}
        ),
        "cardCoordinatesCovered": "x" in coverage["Card"]["covered"] and "y" in coverage["Card"]["covered"],
        "islandCardIdsCovered": "cardIds" in coverage["Island"]["covered"],
        "edgeKindsCovered": "fromKind" in coverage["Edge"]["covered"]
        and "toKind" in coverage["Edge"]["covered"],
    }
    passed = (
        len(coverage) == 4
        and checks["documentMissingIncludesCollections"]
        and checks["cardCoordinatesCovered"]
        and checks["islandCardIdsCovered"]
        and checks["edgeKindsCovered"]
        and coverage["DocumentV1"]["coverageRatio"] is not None
    )
    receipt = {
        "schema": "tai.reference.tei-document-coverage/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading SUI's models.py and the pilot contracts",
        "command": f"python integrations/pilot-sui-document/assembler/document_coverage_check.py --sui-repo {args.sui_repo} --workspace {args.workspace} --artifact {args.artifact} --out evaluations/records/SUI-TEI-document-coverage-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Reads each model class and its bases with AST, intersects with the contract field names, and reports covered, missing and pilot-only fields. It measures names only, not semantics or types.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({name: {"ratio": block["coverageRatio"], "missing": block["missing"]} for name, block in coverage.items()}))


if __name__ == "__main__":
    raise SystemExit(main())
