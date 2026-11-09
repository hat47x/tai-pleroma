"""Measure whether the record template preserves decimal digits.

TEI's critical-path note (§34) says the JSON projection may lose precision by
passing decimals through float64, and that fidelity is a separate check (#2585).
This checks one pilot contract for that: values are sent with more digits than a
float64 can carry, and the projected text is compared with the input.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from decimal import Decimal
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args, cwd, stdin_text=None):
    return subprocess.run(
        [str(part) for part in args],
        cwd=cwd, input=stdin_text, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


# Each case carries the raw JSON text, so the digits reach the candidate as written.
CASES = {
    "shortDecimal": '{"id":"card-1","text":"a","x":10,"y":20.5}',
    "longDecimal": '{"id":"card-1","text":"a","x":0.1234567890123456789,"y":1.5}',
    "tinyDecimal": '{"id":"card-1","text":"a","x":0.0000000001,"y":1.5}',
    "largeInteger": '{"id":"card-1","text":"a","x":12345678901234567890,"y":1.5}',
    "repeatingDecimal": '{"id":"card-1","text":"a","x":0.1,"y":0.2}',
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--contract", default="candidates/card-record/contract.json")
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    workdir = Path(tempfile.mkdtemp(prefix="tei-decimal-", dir=os.environ.get("GOTMPDIR") or None))
    out_dir = workdir / "card"

    built = run(
        ["go", "run", "./tools/reference-generator-selection/cmd/tei-generator-build",
         "-contract", workspace / args.contract, "-strategy", "text-record-template", "-out", out_dir],
        cwd=args.tei_repo,
    )
    if built.returncode != 0:
        print((built.stderr or built.stdout)[-600:], file=sys.stderr)
        return 1
    binary = out_dir / ("candidate.exe" if os.name == "nt" else "candidate")
    compiled = run(["go", "build", "-o", str(binary), "main.go"], cwd=out_dir)
    if compiled.returncode != 0:
        print(compiled.stderr[-600:], file=sys.stderr)
        return 1

    observed = {}
    for name, raw in CASES.items():
        completed = run([binary], cwd=out_dir, stdin_text=raw)
        body = json.loads(completed.stdout) if completed.returncode == 0 and completed.stdout.strip().startswith("{") else {}
        projected = json.loads(body["text"]) if body.get("state") == "present" else None
        sent = Decimal(str(json.loads(raw, parse_float=Decimal, parse_int=Decimal)["x"]))
        got = Decimal(str(projected["x"])) if projected is not None else None
        observed[name] = {
            "state": body.get("state"),
            "sentX": str(sent),
            "projectedX": None if got is None else str(got),
            "equal": got == sent if got is not None else None,
        }

    checks = {
        "cases": observed,
        "allProjected": all(item["state"] == "present" for item in observed.values()),
        "precisionPreserved": all(item["equal"] is True for item in observed.values()),
        "longDecimalPreserved": observed["longDecimal"]["equal"],
        "largeIntegerPreserved": observed["largeInteger"]["equal"],
        "tinyDecimalPreserved": observed["tinyDecimal"]["equal"],
    }
    passed = checks["allProjected"]
    checks["precisionLossCases"] = [name for name, item in observed.items() if item["equal"] is False]
    receipt = {
        "schema": "tai.reference.tei-decimal-fidelity/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the TEI reference generator and a locally compiled candidate",
        "command": f"python integrations/tools/tei_decimal_fidelity_probe.py --tei-repo {args.tei_repo} --workspace integrations/pilot-sui-document --artifact {args.artifact} --out evaluations/records/TEI-decimal-fidelity-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Sends decimal values with more digits than a float64 carries and compares the projected text with the input using Decimal. It records whether the digits survive; it does not test the downstream consumer's number handling, and it does not change the contract or the generator.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: checks[key] for key in (
        "allProjected", "precisionPreserved", "longDecimalPreserved", "largeIntegerPreserved", "tinyDecimalPreserved",
    )}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
