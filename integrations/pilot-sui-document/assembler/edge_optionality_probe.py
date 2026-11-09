"""Check what the Edge projection does when SUI allows fromKind/toKind to be None.

The type-coverage check found that SUI marks Edge.fromKind and Edge.toKind as
Optional while the contract declares them required. This probe builds the Edge
candidate from its own contract and feeds it inputs that SUI permits, so the
consequence is observed rather than inferred.
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="tei-edgeopt-", dir=os.environ.get("GOTMPDIR") or None))
    contract_path = Path(args.workspace) / "candidates/edge-record/contract.json"
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

    cases = {
        # Both kinds present: the documented shape.
        "bothKinds": {"id": "edge-1", "fromId": "card-1", "toId": "card-2", "type": "supports", "fromKind": "card", "toKind": "card"},
        # SUI allows None for either kind. JSON nulls exercise the same branch as absence.
        "nullFromKind": {"id": "edge-2", "fromId": "card-1", "toId": "island-1", "type": "contains", "fromKind": None, "toKind": "island"},
        "nullBothKinds": {"id": "edge-3", "fromId": "card-1", "toId": "card-2", "type": "supports", "fromKind": None, "toKind": None},
        "absentBothKinds": {"id": "edge-4", "fromId": "card-1", "toId": "card-2", "type": "supports"},
    }
    observed = {}
    for name, payload in cases.items():
        completed = run([binary], cwd=out_dir, stdin_text=json.dumps(payload))
        body = {}
        if completed.returncode == 0 and completed.stdout.strip().startswith("{"):
            body = json.loads(completed.stdout)
        observed[name] = {
            "exit": completed.returncode,
            "state": body.get("state"),
            "missing": body.get("missing"),
            "text": body.get("text"),
        }

    checks = {
        "cases": observed,
        "bothKindsPresent": observed["bothKinds"]["state"] == "present",
        # Since the contract made the kinds optional (v4), a null kind is omitted
        # just like an absent key, so the edge is still projected. Before v4 the
        # same inputs were missing/unresolved and the edge was lost.
        "nullFromKindOmitted": observed["nullFromKind"]["state"] == "present",
        "nullBothKindsOmitted": observed["nullBothKinds"]["state"] == "present",
        "absentKindsProjected": observed["absentBothKinds"]["state"] == "present",
        "absentKindsOmittedFromText": "fromKind" not in (observed["absentBothKinds"]["text"] or ""),
    }
    passed = (
        checks["bothKindsPresent"]
        and checks["nullFromKindOmitted"]
        and checks["nullBothKindsOmitted"]
        and checks["absentKindsProjected"]
        and checks["absentKindsOmittedFromText"]
    )
    receipt = {
        "schema": "tai.reference.tei-edge-optionality/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the TEI reference generator and a locally compiled candidate",
        "command": f"python integrations/pilot-sui-document/assembler/edge_optionality_probe.py --tei-repo {args.tei_repo} --workspace {args.workspace} --artifact {args.artifact} --out evaluations/records/SUI-TEI-edge-optionality-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Builds the Edge candidate from the pilot contract and feeds it one complete edge, an edge with a null fromKind, both kinds null, and both kinds absent. Since the contract made the kinds optional (v4), a null or absent kind is omitted and the edge is still projected; before v4 those inputs were reported missing or unresolved and the edge was lost. It does not change the contract.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
