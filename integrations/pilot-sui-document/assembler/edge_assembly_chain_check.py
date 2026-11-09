"""Check that the optional-edge contract and the assembler agree end to end.

The pilot's Edge contract now allows fromKind/toKind to be absent, and the
assembler resolves a missing kind from the endpoint id. This check exercises the
two together: an edge projected without kinds must still compose into a
document, and an edge whose endpoint cannot be resolved must fail closed.
"""

import argparse
import hashlib
import importlib.util
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


def load_assembler(path):
    spec = importlib.util.spec_from_file_location("document_assembler", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workspace = Path(args.workspace)
    workdir = Path(tempfile.mkdtemp(prefix="tei-edge-chain-", dir=os.environ.get("GOTMPDIR") or None))
    contract_path = workspace / "candidates/edge-record/contract.json"
    out_dir = workdir / "edge"

    build = run(
        [
            "go", "run", "./tools/reference-generator-selection/cmd/tei-generator-build",
            "-contract", str(contract_path), "-strategy", "text-record-template", "-out", str(out_dir),
        ],
        cwd=args.tei_repo,
    )
    if build.returncode != 0:
        print(build.stderr, file=sys.stderr)
        return 1
    binary = out_dir / ("candidate.exe" if os.name == "nt" else "candidate")
    compiled = run(["go", "build", "-o", str(binary), "main.go"], cwd=out_dir)
    if compiled.returncode != 0:
        print(compiled.stderr, file=sys.stderr)
        return 1

    module = load_assembler(workspace / "assembler/document_assembler.py")
    document = {"id": "doc-1", "title": "Notes"}
    cards = [{"id": "card-1", "text": "a", "x": 0.0, "y": 0.0}, {"id": "card-2", "text": "b", "x": 10.0, "y": 0.0}]
    islands = [{"id": "island-1", "cardIds": ["card-1"]}]

    def project(payload):
        completed = run([binary], cwd=out_dir, stdin_text=json.dumps(payload))
        body = json.loads(completed.stdout) if completed.returncode == 0 and completed.stdout.strip().startswith("{") else {}
        if body.get("state") != "present":
            return None, body
        return json.loads(body["text"]), body

    def compose(edge):
        try:
            composed_doc = module.assemble(document, cards, islands, [edge])
        except module.AssemblyError as error:
            return {"outcome": "refused", "reason": str(error)}
        return {"outcome": "assembled", "edge": dict(edge), "edges": composed_doc["edges"]}

    # 1. An edge projected without kinds, pointing at an island, must compose.
    projection, body = project({"id": "edge-3", "fromId": "card-1", "toId": "island-1", "type": "contains"})
    composed = compose(projection) if projection else {"outcome": "not projected", "reason": body.get("state")}

    # 2. The same edge with an unresolvable endpoint must be refused.
    bad_projection, bad_body = project({"id": "edge-6", "fromId": "card-1", "toId": "card-9", "type": "supports"})
    refused = compose(bad_projection) if bad_projection else {"outcome": "not projected", "reason": bad_body.get("state")}

    # 3. A kind-less edge between two cards still composes.
    card_projection, card_body = project({"id": "edge-2", "fromId": "card-1", "toId": "card-2", "type": "supports"})
    card_composed = compose(card_projection) if card_projection else {"outcome": "not projected"}

    checks = {
        "absentKindsProjectionState": body.get("state"),
        "absentKindsProjectionOmitsKinds": projection is not None
        and "fromKind" not in projection
        and "toKind" not in projection,
        "cardToIslandComposes": composed.get("outcome") == "assembled",
        "cardToIslandKeepsNoKinds": composed.get("outcome") == "assembled"
        and composed["edges"][0].get("fromKind") is None
        and composed["edges"][0].get("toKind") is None,
        "unknownEndpointRefused": refused.get("outcome") == "refused",
        "unknownEndpointReason": refused.get("reason"),
        "cardToCardComposes": card_composed.get("outcome") == "assembled",
    }
    passed = (
        checks["absentKindsProjectionState"] == "present"
        and checks["absentKindsProjectionOmitsKinds"]
        and checks["cardToIslandComposes"]
        and checks["cardToIslandKeepsNoKinds"]
        and checks["unknownEndpointRefused"]
        and checks["cardToCardComposes"]
    )
    receipt = {
        "schema": "tai.reference.tei-edge-assembly-chain/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the TEI reference generator and the pilot assembler",
        "command": f"python integrations/pilot-sui-document/assembler/edge_assembly_chain_check.py --tei-repo {args.tei_repo} --workspace {args.workspace} --artifact {args.artifact} --out evaluations/records/SUI-TEI-edge-chain-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Projects kind-less edges with the optional contract, then composes them. It checks that a card-to-island edge without kinds survives projection and assembly, that an unresolvable endpoint is refused, and that the composed edge keeps no kinds. It does not save the document.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
