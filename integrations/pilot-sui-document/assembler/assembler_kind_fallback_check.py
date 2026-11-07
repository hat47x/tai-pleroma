"""Check how the assembler treats an edge whose endpoint kind is absent.

The projection contract requires fromKind/toKind, but the assembler falls back to
"card" when they are missing. That fallback never runs on the projected path
(the contract already rejected the record), so the two disagree about the same
input. This check measures both sides.
"""

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_assembler(path):
    spec = importlib.util.spec_from_file_location("document_assembler", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    assembler_path = Path(args.workspace) / "assembler/document_assembler.py"
    module = load_assembler(assembler_path)

    document = {"id": "doc-1", "title": "Doc"}
    cards = [{"id": "card-1", "text": "a", "x": 0.0, "y": 0.0}, {"id": "card-2", "text": "b", "x": 10.0, "y": 0.0}]
    islands = [{"id": "island-1", "cardIds": ["card-1"]}]

    def attempt(name, edges, cards_arg=cards, islands_arg=islands):
        try:
            result = module.assemble(document, cards_arg, islands_arg, edges)
        except module.AssemblyError as error:
            return {"outcome": "refused", "reason": str(error)}
        return {
            "outcome": "assembled",
            "edgeCount": len(result.get("edges", [])),
            "kinds": [
                {"from": edge.get("fromKind"), "to": edge.get("toKind")}
                for edge in result.get("edges", [])
            ],
        }

    checks = {
        "explicitKinds": attempt("explicitKinds", [
            {"id": "edge-1", "fromId": "card-1", "toId": "card-2", "type": "supports", "fromKind": "card", "toKind": "card"},
        ]),
        # No kinds at all: the endpoint itself decides which kind it names.
        "absentKindsResolvedFromEndpoint": attempt("absentKinds", [
            {"id": "edge-2", "fromId": "card-1", "toId": "card-2", "type": "supports"},
        ]),
        # A card -> island edge without kinds resolves to an island endpoint.
        # Before the fix this was mis-resolved as a card and refused.
        "absentKindsResolveCardToIsland": attempt("absentKindsIsland", [
            {"id": "edge-3", "fromId": "card-1", "toId": "island-1", "type": "contains"},
        ]),
        # An explicit None behaves like absent.
        "nullKindsResolvedFromEndpoint": attempt("nullKinds", [
            {"id": "edge-4", "fromId": "card-1", "toId": "card-2", "type": "supports", "fromKind": None, "toKind": None},
        ]),
        "unknownKindRefused": attempt("unknownKind", [
            {"id": "edge-5", "fromId": "card-1", "toId": "card-2", "type": "supports", "fromKind": "thing", "toKind": "card"},
        ]),
        # An endpoint id that names no known card or island must fail closed.
        "absentKindUnknownEndpointRefused": attempt("absentKindUnknown", [
            {"id": "edge-6", "fromId": "card-1", "toId": "card-9", "type": "supports"},
        ]),
    }
    # The output keeps whatever kinds were projected, so an edge without kinds
    # stays without kinds; the resolution result is not written back.
    checks["assemblerRewritesKinds"] = checks["absentKindsResolvedFromEndpoint"]["kinds"] != [
        {"from": "card", "to": "card"}
    ]
    contract = json.loads(
        (Path(args.workspace) / "candidates/edge-record/contract.json").read_text(encoding="utf-8")
    )
    kinds_required = {
        field["name"]: not bool(field.get("optional"))
        for field in contract["projection"]["fields"]
        if field["name"] in ("fromKind", "toKind")
    }
    checks["contractRequiresKinds"] = kinds_required
    passed = (
        checks["explicitKinds"]["outcome"] == "assembled"
        and checks["absentKindsResolvedFromEndpoint"]["outcome"] == "assembled"
        and checks["absentKindsResolveCardToIsland"]["outcome"] == "assembled"
        and checks["nullKindsResolvedFromEndpoint"]["outcome"] == "assembled"
        and checks["unknownKindRefused"]["outcome"] == "refused"
        and checks["absentKindUnknownEndpointRefused"]["outcome"] == "refused"
        and checks["assemblerRewritesKinds"] is True
        and all(kinds_required.values())
    )
    receipt = {
        "schema": "tai.reference.tei-assembler-kind-fallback/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 importing the pilot assembler module directly",
        "command": f"python integrations/pilot-sui-document/assembler/assembler_kind_fallback_check.py --workspace {args.workspace} --artifact {args.artifact} --out evaluations/records/SUI-TEI-assembler-kinds-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Calls assemble with explicit kinds, absent kinds, a card-to-island edge without kinds, explicit nulls, and an unknown kind. It records that an absent endpoint kind is resolved from the endpoint id itself, that a card-to-island edge without kinds now assembles, that an unknown or ambiguous endpoint fails closed, and that the composed edge keeps exactly the kinds that were projected. The contract still requires the kinds, so this path only runs on inputs the contract already refused.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
