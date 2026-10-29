#!/usr/bin/env python3
"""Run SEI against an invalid duplicate decision and record the rejection."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import tempfile


def run(go: str, runtime: pathlib.Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [go, "run", "./cmd/sei", *args],
        cwd=runtime,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sei-root", default="../../../sei-cognition")
    parser.add_argument("--go", default="go")
    parser.add_argument("--out")
    args = parser.parse_args()
    runtime = pathlib.Path(args.sei_root).resolve() / "runtime" / "go"
    receipt: dict[str, object] = {
        "schema": "tai.reference.sei-negative/v0",
        "synthetic": True,
        "evidenceKind": "synthetic",
        "duplicateRejected": False,
        "passed": False,
    }
    with tempfile.TemporaryDirectory() as store:
        steps = [
            ("init", "--data-root", store, "--bundle-id", "scn001-negative"),
            ("add", "recommendation", "--data-root", store, "--id", "rec-01",
             "--statement", "negative fixture", "--source", "tai", "--basis", "observation:O-02"),
            ("add", "decision", "--data-root", store, "--id", "dec-01",
             "--statement", "negative fixture", "--source", "tai", "--unresolved", "authority:unknown",
             "--recommendation", "rec-01", "--responsible", "role:facility-owner"),
        ]
        for step in steps:
            result = run(args.go, runtime, *step)
            receipt["setupExitCode"] = result.returncode
            if result.returncode != 0:
                receipt["reason"] = f"setup failed: {step[0]} {result.stderr.strip()}"
                break
        else:
            duplicate = run(
                args.go, runtime, "add", "decision", "--data-root", store, "--id", "dec-01",
                "--statement", "duplicate", "--source", "tai", "--unresolved", "authority:unknown",
                "--recommendation", "rec-01", "--responsible", "role:facility-owner",
            )
            receipt["duplicateExitCode"] = duplicate.returncode
            receipt["duplicateRejected"] = duplicate.returncode != 0
            receipt["passed"] = duplicate.returncode != 0
            if duplicate.returncode == 0:
                receipt["reason"] = "duplicate decision was accepted"
            else:
                receipt["reason"] = duplicate.stderr.strip().splitlines()[-1] if duplicate.stderr.strip() else "duplicate rejected"
    encoded = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        pathlib.Path(args.out).write_text(encoded, encoding="utf-8", newline="\n")
    print(encoded, end="")
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
