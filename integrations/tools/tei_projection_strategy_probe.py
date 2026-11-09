"""Check whether a projection contract can use a long-running generator strategy.

The Target Profile gap looked like "the generated program only answers once".
This measures the sharper cause: a projection contract is pinned to a projection
strategy, and the long-running templates are not projection strategies.
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


def run(args, cwd):
    return subprocess.run(
        [str(part) for part in args],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def build(tei_repo, contract, strategy, out_dir):
    completed = run(
        ["go", "run", "./tools/reference-generator-selection/cmd/tei-generator-build",
         "-contract", contract, "-strategy", strategy, "-out", out_dir],
        cwd=tei_repo,
    )
    output = (completed.stderr or completed.stdout).strip()
    return {
        "exit": completed.returncode,
        "generated": (Path(out_dir) / "main.go").exists(),
        "tail": output.splitlines()[-1] if output else "",
        "refusedAsProjection": "requires the text-record-template strategy" in output
        or "requires the text-template strategy" in output,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    workdir = Path(tempfile.mkdtemp(prefix="tei-lrstrategy-", dir=os.environ.get("GOTMPDIR") or None))

    record = build(args.tei_repo, workspace / "candidates/card-record/contract.json",
                   "long-running-template", workdir / "record")
    identity = build(args.tei_repo, workspace / "candidates/text-identity/contract.json",
                     "long-running-template", workdir / "identity")
    record_ok = build(args.tei_repo, workspace / "candidates/card-record/contract.json",
                      "text-record-template", workdir / "record-oneshot")
    identity_ok = build(args.tei_repo, workspace / "candidates/text-identity/contract.json",
                        "text-template", workdir / "identity-oneshot")

    checks = {
        "longRunningWithRecordProjection": record,
        "longRunningWithIdentityProjection": identity,
        "recordProjectionWithItsOwnStrategy": record_ok,
        "identityProjectionWithItsOwnStrategy": identity_ok,
        "projectionIsPinnedToOneShotStrategy": record["refusedAsProjection"] and identity["refusedAsProjection"],
        "longRunningCannotCarryAProjection": not record["generated"] and not identity["generated"],
        "oneShotStrategiesStillWork": record_ok["generated"] and identity_ok["generated"],
    }
    passed = (
        checks["projectionIsPinnedToOneShotStrategy"]
        and checks["longRunningCannotCarryAProjection"]
        and checks["oneShotStrategiesStillWork"]
    )
    receipt = {
        "schema": "tai.reference.tei-projection-strategy/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the TEI reference generator selection tool",
        "command": f"python integrations/tools/tei_projection_strategy_probe.py --tei-repo {args.tei_repo} --workspace integrations/pilot-sui-document --artifact {args.artifact} --out evaluations/records/TEI-projection-strategy-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Builds projection contracts with a long-running strategy and with their own strategies. It records that a projection kind is pinned to a projection strategy and that the long-running templates are not projection strategies, so no long-running projection candidate can be produced. It does not change TEI and does not test the line-amount templates.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "projectionIsPinnedToOneShotStrategy": checks["projectionIsPinnedToOneShotStrategy"],
        "recordTail": record["tail"],
        "identityTail": identity["tail"],
        "oneShotStrategiesStillWork": checks["oneShotStrategiesStillWork"],
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
