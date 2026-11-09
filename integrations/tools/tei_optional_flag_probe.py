"""Check whether the contract's `optional` flag changes the generated candidate.

The third meaning-change run made island.title required and the conformance flow
stayed green, which suggests the flag may not reach the generator. This compares
one candidate built from the optional contract with one built from the required
contract, on the same inputs.
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
        cwd=cwd, input=stdin_text, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def build(tei_repo, contract_path, out_dir):
    built = run(
        ["go", "run", "./tools/reference-generator-selection/cmd/tei-generator-build",
         "-contract", contract_path, "-strategy", "text-record-template", "-out", out_dir],
        cwd=tei_repo,
    )
    if built.returncode != 0:
        return {"built": False, "tail": (built.stderr or built.stdout).strip().splitlines()[-1:]}
    binary = Path(out_dir) / ("candidate.exe" if os.name == "nt" else "candidate")
    compiled = run(["go", "build", "-o", binary, "main.go"], cwd=out_dir)
    if compiled.returncode != 0:
        return {"built": False, "tail": compiled.stderr.strip().splitlines()[-1:]}
    return {"built": True, "binary": str(binary)}


def probe(binary, out_dir, payload):
    completed = run([binary], cwd=out_dir, stdin_text=json.dumps(payload))
    body = json.loads(completed.stdout) if completed.returncode == 0 and completed.stdout.strip().startswith("{") else {}
    return {"state": body.get("state"), "text": body.get("text")}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    workdir = Path(tempfile.mkdtemp(prefix="tei-optional-", dir=os.environ.get("GOTMPDIR") or None))

    optional_contract = json.loads((workspace / "candidates/island-record/contract.json").read_text(encoding="utf-8"))
    required_contract = json.loads(json.dumps(optional_contract))
    required_contract["version"] = str(int(optional_contract["version"]) + 1)
    for field in required_contract["projection"]["fields"]:
        if field["name"] == "title":
            field.pop("optional", None)

    paths = {}
    for name, contract in (("optional", optional_contract), ("required", required_contract)):
        path = workdir / f"{name}.json"
        path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        paths[name] = path

    built = {name: build(args.tei_repo, paths[name], workdir / name) for name in ("optional", "required")}
    cases = {
        "titleAbsent": {"id": "island-1", "cardIds": ["card-1"]},
        "titlePresent": {"id": "island-1", "title": "Group A", "cardIds": ["card-1"]},
        "titleNull": {"id": "island-1", "title": None, "cardIds": ["card-1"]},
    }
    observed = {}
    for name in ("optional", "required"):
        if not built[name]["built"]:
            observed[name] = {"built": False, "tail": built[name]["tail"]}
            continue
        observed[name] = {
            "built": True,
            "cases": {case: probe(built[name]["binary"], workdir / name, payload) for case, payload in cases.items()},
        }

    identical = (
        observed["optional"].get("cases") == observed["required"].get("cases")
        if observed["optional"].get("built") and observed["required"].get("built")
        else None
    )
    checks = {
        "built": {name: built[name]["built"] for name in built},
        "observed": observed,
        "casesIdenticalBetweenFlagStates": identical,
        "titleAbsentStateOptional": (observed["optional"].get("cases") or {}).get("titleAbsent", {}).get("state"),
        "titleAbsentStateRequired": (observed["required"].get("cases") or {}).get("titleAbsent", {}).get("state"),
        "flagChangesBehaviour": identical is False,
    }
    passed = bool(checks["built"]["optional"] and checks["built"]["required"]) and identical is not None
    receipt = {
        "schema": "tai.reference.tei-optional-flag/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the TEI reference generator selection tool and two compiled candidates",
        "command": f"python integrations/tools/tei_optional_flag_probe.py --tei-repo {args.tei_repo} --workspace integrations/pilot-sui-document --artifact {args.artifact} --out evaluations/records/TEI-optional-flag-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Builds the island candidate from the optional and the required contract and runs the same three inputs. It records whether the optional flag changes the generated behaviour. It does not judge which behaviour is correct, and it does not change either contract.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil_target = workdir
    import shutil as _shutil
    _shutil.rmtree(shutil_target, ignore_errors=True)
    print(json.dumps({key: checks[key] for key in (
        "casesIdenticalBetweenFlagStates", "titleAbsentStateOptional", "titleAbsentStateRequired", "flagChangesBehaviour",
    )}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
