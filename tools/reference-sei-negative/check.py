#!/usr/bin/env python3
"""Check that SEI rejected the duplicate decision fixture."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

RECORD = "evaluations/records/SCN-001-invalid-sei-2026-10-29.json"


def check(root: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        receipt = json.loads((root / RECORD).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {"passed": False, "errors": [str(error)], "publicationAllowed": False}
    if receipt.get("synthetic") is not True:
        errors.append("receipt is not synthetic")
    if receipt.get("duplicateRejected") is not True or receipt.get("passed") is not True:
        errors.append("duplicate decision was not rejected")
    if receipt.get("duplicateExitCode") != 1:
        errors.append("duplicate decision exit code is not 1")
    return {
        "schema": "tai.reference.sei-negative-check/v0",
        "synthetic": True,
        "evidenceKind": "synthetic",
        "duplicateRejected": receipt.get("duplicateRejected") is True,
        "publicationAllowed": False,
        "passed": not errors,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    receipt = check(pathlib.Path(args.root))
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
