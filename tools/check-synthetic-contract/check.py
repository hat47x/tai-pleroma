#!/usr/bin/env python3
"""Verify SUI preserves an unknown edge type instead of rejecting it."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

RECORD = "evaluations/records/SCN-001-sui-unknown-edge-2026-10-29.json"


def check(root: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        receipt = json.loads((root / RECORD).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {"passed": False, "errors": [str(error)], "publicationAllowed": False}
    if receipt.get("passed") is not True:
        errors.append("SUI did not accept the DocumentV1")
    if receipt.get("edgeType") != "bogus":
        errors.append(f"unknown edge type was not preserved: {receipt.get('edgeType')}")
    if (receipt.get("cardCount"), receipt.get("islandCount"), receipt.get("edgeCount")) != (5, 3, 1):
        errors.append("DocumentV1 shape is not 5 cards / 3 islands / 1 edge")
    return {
        "schema": "tai.reference.scn001-contract/v0",
        "synthetic": True,
        "evidenceKind": "synthetic",
        "contract": "sui unknown edge type is preserved",
        "unknownEdgePreserved": not errors,
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
