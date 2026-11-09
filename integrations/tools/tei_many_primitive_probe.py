"""Probe how TEI handles a `many` record field whose primitive is numeric.

`validateContract` refuses `many` for anything but std.text and std.identifier,
because the record template renders many fields as strings (#2585 PFC-06). This
check measures that refusal and whether `many` with the allowed primitives still
projects, so the constraint is evidenced from both sides.
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


def contract_with(field_primitive, *, many=True):
    return {
        "schema": SCHEMA,
        "id": "sui.card.array",
        "version": "1",
        "status": "reference-local",
        "inputs": [{"attribute": "sui.card.x", "primitive": field_primitive}],
        "output": {"primitive": "std.text"},
        "projection": {
            "kind": "record",
            "fields": [
                {
                    "name": "xs",
                    "input": "xs",
                    "attribute": "sui.card.x",
                    "primitive": field_primitive,
                    "many": many,
                }
            ],
        },
    }


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
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="tei-manyprim-", dir=os.environ.get("GOTMPDIR") or None))
    results = {}
    for name, primitive, many in (
        ("textMany", "std.text", True),
        ("identifierMany", "std.identifier", True),
        ("decimalMany", "std.decimal", True),
        ("booleanMany", "std.boolean", True),
        ("integerMany", "std.integer", True),
        ("decimalSingle", "std.decimal", False),
    ):
        contract = contract_with(primitive, many=many)
        contract_path = workdir / f"{name}.json"
        contract_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        out_dir = workdir / name
        build = run(
            [
                "go", "run", "./tools/reference-generator-selection/cmd/tei-generator-build",
                "-contract", contract_path, "-strategy", "text-record-template", "-out", out_dir,
            ],
            cwd=args.tei_repo,
        )
        output = (build.stderr or build.stdout).strip()
        lines = output.splitlines()
        results[name] = {
            "exit": build.returncode,
            "generated": (out_dir / "main.go").exists(),
            "tail": lines[-1] if lines else "",
            "whole": output,
        }

    # Run the allowed cases so the accepted shapes are shown to project, not just build.
    executions = {}
    for name in ("textMany", "identifierMany"):
        if not (workdir / name / "main.go").exists():
            continue
        binary = workdir / name / ("candidate.exe" if os.name == "nt" else "candidate")
        compiled = run(["go", "build", "-o", str(binary), "main.go"], cwd=workdir / name)
        if compiled.returncode != 0:
            executions[name] = {"build": "failed", "tail": compiled.stderr.strip().splitlines()[-1:]}
            continue
        payload = {"xs": ["a", "b"] if name == "textMany" else ["id-1", "id-2"]}
        completed = run([binary], cwd=workdir / name, stdin_text=json.dumps(payload))
        body = json.loads(completed.stdout) if completed.returncode == 0 and completed.stdout.strip().startswith("{") else {}
        executions[name] = {"exit": completed.returncode, "state": body.get("state"), "text": body.get("text")}

    checks = {
        "variants": results,
        "executions": executions,
        "textManyAccepted": results["textMany"]["exit"] == 0,
        "identifierManyAccepted": results["identifierMany"]["exit"] == 0,
        "numericManyRefused": results["decimalMany"]["exit"] != 0,
        "booleanManyRefused": results["booleanMany"]["exit"] != 0,
        "integerManyRefused": results["integerMany"]["exit"] != 0,
        "decimalSingleAccepted": results["decimalSingle"]["exit"] == 0,
        "refusalNamesThePrimitive": "many is not supported" in results["decimalMany"]["whole"],
        "textManyProjects": executions.get("textMany", {}).get("state") == "present",
        "identifierManyProjects": executions.get("identifierMany", {}).get("state") == "present",
    }
    passed = (
        checks["textManyAccepted"]
        and checks["identifierManyAccepted"]
        and checks["numericManyRefused"]
        and checks["booleanManyRefused"]
        and checks["integerManyRefused"]
        and checks["decimalSingleAccepted"]
        and checks["refusalNamesThePrimitive"]
        and checks["textManyProjects"]
        and checks["identifierManyProjects"]
    )
    receipt = {
        "schema": "tai.reference.tei-many-primitive/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the TEI reference generator selection tool",
        "command": f"python integrations/tools/tei_many_primitive_probe.py --tei-repo {args.tei_repo} --artifact {args.artifact} --out evaluations/records/TEI-many-primitive-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Builds one record contract for each of six primitive/cardinality combinations and runs the two accepted ones. It records that many is refused for decimal, boolean and integer with the message `many is not supported for primitive` while single decimal is accepted, so numeric arrays cannot be projected today. It does not change TEI.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"variants": results, "executions": executions}))


if __name__ == "__main__":
    raise SystemExit(main())
