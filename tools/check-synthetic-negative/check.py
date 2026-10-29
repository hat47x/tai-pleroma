#!/usr/bin/env python3
"""Verify that TEI and MMI reject intentionally invalid synthetic inputs."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

RECORDS = {
    "tei": "evaluations/records/SCN-001-invalid-tei-2026-10-29.json",
    "mmi": "evaluations/records/SCN-001-invalid-mmi-2026-10-29.json",
    "eki": "evaluations/records/SCN-001-invalid-eki-2026-10-29.json",
    "sui": "evaluations/records/SCN-001-invalid-sui-2026-10-29.json",
}


def check(root: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    results: dict[str, Any] = {}
    for name, relative in RECORDS.items():
        try:
            receipt = json.loads((root / relative).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{name}: {error}")
            continue
        if receipt.get("synthetic") is not True:
            errors.append(f"{name}: not marked synthetic")
        if receipt.get("passed") is not False:
            errors.append(f"{name}: invalid input was accepted")
        reason = str(receipt.get("reason", ""))
        if not reason:
            errors.append(f"{name}: rejection reason is empty")
        if name == "eki" and receipt.get("submitStatus") != 400:
            errors.append("eki: rejection status is not 400")
        if name == "sui" and receipt.get("putStatus") != 422:
            errors.append("sui: rejection status is not 422")
        results[name] = {"rejected": receipt.get("passed") is False, "reason": reason}
    return {
        "schema": "tai.reference.scn001-negative-matrix/v0",
        "synthetic": True,
        "evidenceKind": "synthetic",
        "expectedRejection": True,
        "results": results,
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
