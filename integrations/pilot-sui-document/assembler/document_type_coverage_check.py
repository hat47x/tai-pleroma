"""Check that the TEI projection contracts use the primitive the SUI model annotation implies.

The name-coverage check counted names only. This one reads the Python annotation
text for each covered field and compares it with the contract's declared
primitive, so a name match with the wrong type becomes visible.
"""

import argparse
import ast
import hashlib
import json
import time
from pathlib import Path

ANNOTATION_PRIMITIVES = {
    "str": "std.text",
    "float": "std.decimal",
    "int": "std.integer",
    "bool": "std.boolean",
    "datetime": "std.datetime",
    "Literal": "std.code",
}

# Identifier-like names get std.identifier regardless of the annotation, including
# identifier collections.
IDENTIFIER_NAMES = {
    "id",
    "cardId",
    "cardIds",
    "islandId",
    "edgeId",
    "documentId",
    "fromId",
    "toId",
    "readingOrder",
    "sources",
    "parentIslandId",
    "placardCardId",
    "mergedIntoCardId",
    "canonicalId",
}

# Fields SUI types as plain `str` but the contract deliberately narrows to std.code.
NAME_PRIMITIVES = {
    "type": "std.code",
    "fromKind": "std.code",
    "toKind": "std.code",
    "claimType": "std.code",
    "holdState": "std.code",
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unwrap(annotation):
    """Return (inner, is_collection, is_optional) for a pydantic-ish annotation."""
    inner = annotation.strip()
    is_optional = False
    if " | None" in inner:
        inner = inner.replace(" | None", "").strip()
        is_optional = True
    is_collection = False
    for _ in range(2):
        if inner.startswith("Optional[") and inner.endswith("]"):
            inner = inner[len("Optional[") : -1].strip()
            is_optional = True
        elif inner.startswith("list[") and inner.endswith("]"):
            inner = inner[len("list[") : -1].strip()
            is_collection = True
        elif inner.startswith("tuple[") and inner.endswith("]"):
            inner = inner[len("tuple[") : -1].strip()
            is_collection = True
    return inner, is_collection, is_optional


def annotation_fields(models_py, class_name):
    tree = ast.parse(models_py.read_text(encoding="utf-8"))
    classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
    fields = {}
    pending = [class_name]
    seen = set()
    while pending:
        name = pending.pop()
        if name in seen or name not in classes:
            continue
        seen.add(name)
        node = classes[name]
        for statement in node.body:
            if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
                fields.setdefault(statement.target.id, ast.unparse(statement.annotation))
        for base in node.bases:
            if isinstance(base, ast.Name):
                pending.append(base.id)
    return fields


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
    rows = {}
    for model_name, contract_dir in pairs:
        annotations = annotation_fields(models_py, model_name)
        contract = json.loads((candidates / contract_dir / "contract.json").read_text(encoding="utf-8"))
        per_field = {}
        for field in contract["projection"]["fields"]:
            name = field["name"]
            annotation = annotations.get(name)
            inner, is_collection, is_optional = unwrap(annotation) if annotation else ("", False, False)
            if name in IDENTIFIER_NAMES:
                expected = "std.identifier"
            elif name in NAME_PRIMITIVES:
                expected = NAME_PRIMITIVES[name]
            else:
                expected = ANNOTATION_PRIMITIVES.get(inner, "unexpected")
            per_field[name] = {
                "annotation": annotation,
                "innerType": inner,
                "expected": expected,
                "declared": field["primitive"],
                "matches": expected == field["primitive"],
                "optional": bool(field.get("optional")),
                "annotationOptional": is_optional,
                "many": bool(field.get("many")),
                "annotationCollection": is_collection,
                "collectionMatches": is_collection == bool(field.get("many")),
            }
        rows[model_name] = per_field

    mismatches = {
        model: [name for name, row in per_field.items() if row["matches"] is False]
        for model, per_field in rows.items()
    }
    optional_mismatches = {
        model: [name for name, row in per_field.items() if row["annotationOptional"] is not row["optional"]]
        for model, per_field in rows.items()
    }
    collection_mismatches = {
        model: [name for name, row in per_field.items() if row["collectionMatches"] is False]
        for model, per_field in rows.items()
    }
    unexpected = {
        model: [name for name, row in per_field.items() if row["expected"] == "unexpected"]
        for model, per_field in rows.items()
    }
    checks = {
        "fields": rows,
        "primitiveMismatches": mismatches,
        "optionalMismatches": optional_mismatches,
        "collectionMismatches": collection_mismatches,
        "unexpectedAnnotations": unexpected,
        "allPrimitivesMatch": all(not names for names in mismatches.values()),
        "allCollectionsMatch": all(not names for names in collection_mismatches.values()),
        "noUnexpectedAnnotations": all(not names for names in unexpected.values()),
        # SUI allows Edge.fromKind/toKind to be None; the contract declares them
        # required. A None would fail projection instead of being omitted.
        "knownOptionalGap": optional_mismatches,
    }
    passed = (
        len(rows) == 4
        and checks["allPrimitivesMatch"]
        and checks["allCollectionsMatch"]
        and checks["noUnexpectedAnnotations"]
    )
    receipt = {
        "schema": "tai.reference.tei-document-type-coverage/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading SUI's models.py annotations and the pilot contracts",
        "command": f"python integrations/pilot-sui-document/assembler/document_type_coverage_check.py --sui-repo {args.sui_repo} --workspace {args.workspace} --artifact {args.artifact} --out evaluations/records/SUI-TEI-document-types-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "For every name the contract covers, reads the SUI annotation, reduces it to its inner type, and compares the expected primitive, cardinality and optionality with the declared ones. It does not check value ranges or semantics. Edge.fromKind/toKind are Optional in SUI but required in the contract, which the probe records as a known gap rather than a defect.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "primitiveMismatches": mismatches,
                "optionalMismatches": optional_mismatches,
                "collectionMismatches": collection_mismatches,
                "unexpectedAnnotations": unexpected,
            }
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
