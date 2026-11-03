"""Build an MMI format profile projection artifact from the selection fixture."""

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import jsonschema


def digest_bytes(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--workspace", default="integrations/pilot-mmi-format-profile")
    parser.add_argument("--out", required=True)
    parser.add_argument("--receipt-out", required=True)
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    contract_path = workspace / "candidates/format-profile-record/contract.json"
    fixtures_path = workspace / "candidates/format-profile-record/fixtures.json"
    contract_bytes = contract_path.read_bytes().replace(b"\r\n", b"\n")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    fixtures = json.loads(fixtures_path.read_text(encoding="utf-8"))
    present = next(case for case in fixtures["cases"] if case["id"] == "present")

    with tempfile.TemporaryDirectory(prefix="tei-mmi-") as tmp:
        candidate = Path(tmp) / "candidate"
        build = subprocess.run(
            [
                "go",
                "run",
                "./tools/reference-generator-selection/cmd/tei-generator-build",
                "-contract",
                str(contract_path),
                "-strategy",
                "text-record-template",
                "-out",
                str(candidate),
            ],
            cwd=args.tei_repo,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        if build.returncode != 0:
            print(build.stderr, file=sys.stderr)
            return 1
        manifest = json.loads(build.stdout)[0]
        binary = Path(tmp) / "candidate.exe"
        compiled = subprocess.run(
            ["go", "build", "-o", str(binary), "main.go"],
            cwd=candidate,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        if compiled.returncode != 0:
            print(compiled.stderr, file=sys.stderr)
            return 1
        executed = subprocess.run(
            [str(binary)],
            cwd=candidate,
            input=json.dumps(present["input"]),
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        if executed.returncode != 0:
            print(executed.stderr, file=sys.stderr)
            return 1
        record = json.loads(json.loads(executed.stdout)["text"])

    tei_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=args.tei_repo, capture_output=True, text=True
    ).stdout.strip()
    artifact = {
        "schema": "tai.reference.tei-mmi-format-profile-projection/v0",
        "contract": {"id": "mmi.format-profile.projection", "version": "1"},
        "source": {
            "teiCommit": tei_commit,
            "contract": {
                "contractId": contract.get("id"),
                "contractVersion": contract.get("version"),
                "contractDigest": digest_bytes(contract_bytes),
                "sourceDigest": manifest.get("SourceDigest")
                or manifest.get("Manifest", {}).get("sourceDigest"),
                "cases": len(fixtures["cases"]),
            },
        },
        "profile": record,
    }
    schema = json.loads((workspace / "artifact.schema.json").read_text(encoding="utf-8"))
    errors = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(artifact)]
    if errors:
        print(json.dumps(errors), file=sys.stderr)
        return 1

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(artifact, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    receipt = {
        "schema": "tai.reference.tei-mmi-artifact/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go on PATH, Python 3.12, and jsonschema",
        "command": f"python integrations/pilot-mmi-format-profile/build_artifact.py --tei-repo {args.tei_repo} --out {args.out}",
        "result": "PASS",
        "artifact": {"path": args.out, "digest": digest_bytes(Path(args.out).read_bytes())},
        "observed": {
            "profileValid": True,
            "cases": len(fixtures["cases"]),
            "profileId": record.get("id"),
        },
        "scope": "Builds one Format Profile record from the fixture and validates the artifact against its JSON Schema. It does not connect to MMI or save anything.",
    }
    with open(args.receipt_out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(receipt["observed"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
