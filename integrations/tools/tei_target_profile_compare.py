"""Run the same pilot contract and fixtures on two Target Profiles and compare.

Stage-5 exit 3 asks whether the same conformance passes on another Target
Profile. This runs TEI's own `compare`, which executes one built candidate under
each profile, and records where the two diverge.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args, cwd):
    return subprocess.run(
        [str(part) for part in args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def parse_json(text):
    start = text.find("{")
    if start < 0:
        return None
    try:
        return json.loads(text[start:])
    except json.JSONDecodeError:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--strategy", default="text-record-template")
    parser.add_argument("--contract", default="candidates/card-record/contract.json")
    parser.add_argument("--fixtures", default="candidates/card-record/fixtures.json")
    parser.add_argument("--profile-a", default="profiles/record.json")
    parser.add_argument("--profile-b", default="profiles/record-rolling.json")
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    workdir = Path(tempfile.mkdtemp(prefix="tei-profiles-", dir=os.environ.get("GOTMPDIR") or None))
    candidates = workdir / "candidates"

    built = run(
        [
            "go", "run", "./tools/reference-generator-selection/cmd/tei-generator-build",
            "-contract", workspace / args.contract, "-strategy", args.strategy,
            "-out", candidates / "card-record",
        ],
        cwd=args.tei_repo,
    )
    candidate_built = (candidates / "card-record" / "main.go").exists()

    compared = run(
        [
            "go", "run", "./tools/reference-target-profile/cmd/tei-target-profile", "compare",
            "-profiles", f"{workspace / args.profile_a},{workspace / args.profile_b}",
            "-workspace", workspace,
            "-contract", workspace / args.contract,
            "-fixtures", workspace / args.fixtures,
            "-candidates", candidates,
        ],
        cwd=args.tei_repo,
    )
    comparison = parse_json(compared.stdout or compared.stderr) or {}

    profiles = []
    for item in comparison.get("profiles", []):
        evidence = item.get("processModelEvidence", {})
        profiles.append(
            {
                "id": item.get("id"),
                "processModel": item.get("processModel"),
                "passed": item.get("passed"),
                "mode": evidence.get("mode"),
                "processes": evidence.get("processes"),
                "requests": evidence.get("requests"),
                "responses": evidence.get("responses"),
                "reason": evidence.get("reason"),
            }
        )

    one_shot = next((p for p in profiles if p["processModel"] == "oneshot"), None)
    long_running = next((p for p in profiles if p["processModel"] == "long-running"), None)
    checks = {
        "candidateBuilt": candidate_built,
        "compareExit": compared.returncode,
        "comparisonPassed": comparison.get("passed"),
        "contractId": comparison.get("contractId"),
        "contractVersion": comparison.get("contractVersion"),
        "fixtureDigest": comparison.get("fixtureDigest"),
        "profiles": profiles,
        "oneShotPassed": bool(one_shot and one_shot["passed"]),
        "longRunningRefused": bool(long_running and long_running["passed"] is False),
        "refusalReason": (long_running or {}).get("reason"),
        "refusalIsExecutionModel": bool(
            long_running
            and re.search(
                r"candidate wait failed|exit status|returned 1 of \d+ responses",
                long_running.get("reason") or "",
            )
        ),
        "sameContractBothProfiles": len({p["id"] and comparison.get("contractId") for p in profiles}) == 1,
    }
    expected_id = json.loads((workspace / args.contract).read_text(encoding="utf-8")).get("id")
    checks["expectedContractId"] = expected_id
    checks["sameContractBothProfiles"] = (
        comparison.get("contractId") == expected_id and len(profiles) == 2
    )
    passed = (
        checks["candidateBuilt"]
        and checks["oneShotPassed"]
        and checks["longRunningRefused"]
        and checks["refusalIsExecutionModel"]
        and checks["sameContractBothProfiles"]
    )
    receipt = {
        "schema": "tai.reference.tei-target-profile-compare/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the TEI target-profile tool and one built record candidate",
        "command": f"python integrations/tools/tei_target_profile_compare.py --tei-repo {args.tei_repo} --workspace {args.workspace} --strategy {args.strategy} --contract {args.contract} --fixtures {args.fixtures} --profile-a {args.profile_a} --profile-b {args.profile_b} --artifact {args.artifact} --out <receipt>",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Builds one candidate for the given contract, then runs TEI's compare over a one-shot and a long-running Target Profile with the same contract and fixtures. It records that the one-shot profile passes and that the long-running profile refuses the same candidate because the generated program answers one request per process. It does not prove a real target and does not change the candidate template.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(workdir, ignore_errors=True)
    print(json.dumps({key: checks[key] for key in (
        "candidateBuilt", "oneShotPassed", "longRunningRefused", "refusalReason", "comparisonPassed",
    )}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
