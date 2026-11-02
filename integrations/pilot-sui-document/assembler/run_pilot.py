"""Run the projection pilot end to end and write one combined receipt."""

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--workspace", default="integrations/pilot-sui-document")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    assembler = Path(__file__).resolve().parent
    workspace = Path(args.workspace).resolve()
    steps = {}
    with tempfile.TemporaryDirectory(prefix="tei-pilot-") as tmp:
        tmp = Path(tmp)
        artifact = tmp / "artifact.json"
        flow_out = tmp / "flow.json"
        flow = subprocess.run(
            [
                sys.executable,
                str(assembler / "integration_flow.py"),
                "--tei-repo",
                args.tei_repo,
                "--workspace",
                str(workspace),
                "--out",
                str(flow_out),
                "--artifact-out",
                str(artifact),
            ],
            capture_output=True,
            text=True,
        )
        steps["flow"] = {
            "returncode": flow.returncode,
            "casesPassed": json.loads(flow_out.read_text(encoding="utf-8"))["casesPassed"]
            if flow_out.exists()
            else None,
        }
        if flow.returncode != 0:
            _write(args.out, artifact, steps, "FAIL")
            return 1

        validate_out = tmp / "validate.json"
        validate = subprocess.run(
            [
                sys.executable,
                str(assembler / "validate_against_sui.py"),
                "--sui-repo",
                args.sui_repo,
                "--artifact",
                str(artifact),
                "--out",
                str(validate_out),
            ],
            capture_output=True,
            text=True,
        )
        steps["documentV1"] = {
            "returncode": validate.returncode,
            "valid": json.loads(validate_out.read_text(encoding="utf-8"))["observed"]["documentV1Valid"]
            if validate_out.exists()
            else False,
        }

        digest_out = tmp / "digest.json"
        digests = subprocess.run(
            [
                sys.executable,
                str(assembler / "verify_contract_digests.py"),
                "--artifact",
                str(artifact),
                "--workspace",
                str(workspace),
                "--out",
                str(digest_out),
            ],
            capture_output=True,
            text=True,
        )
        steps["contractDigests"] = {
            "returncode": digests.returncode,
            "allMatch": json.loads(digest_out.read_text(encoding="utf-8"))["observed"]["allMatch"]
            if digest_out.exists()
            else False,
        }
        result = (
            "PASS"
            if all(step["returncode"] == 0 for step in steps.values())
            and steps["documentV1"]["valid"]
            and steps["contractDigests"]["allMatch"]
            else "FAIL"
        )
        _write(args.out, artifact, steps, result)
        print(json.dumps({"result": result, "steps": steps}))
        return 0 if result == "PASS" else 1


def _write(out, artifact, steps, result):
    receipt = {
        "schema": "tai.reference.tei-pilot-run/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go on PATH and Python 3.12",
        "command": "python integrations/pilot-sui-document/assembler/run_pilot.py",
        "result": result,
        "artifact": {"digest": digest(artifact)} if artifact.exists() else None,
        "steps": steps,
        "scope": "Runs the projection flow, the DocumentV1 validation, and the contract digest check in one command. It does not save documents or prove deployment.",
    }
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


if __name__ == "__main__":
    raise SystemExit(main())
