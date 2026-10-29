#!/usr/bin/env python3
"""Check the first synthetic SCN-003 grant-review slice through MMI and TEI."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

RECORDS = {
    "mmi": "evaluations/records/SCN-003-mmi-2026-10-29.json",
    "tei": "evaluations/records/SCN-003-tei-2026-10-29.json",
}


def check(root: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    receipts: dict[str, Any] = {}
    for name, relative in RECORDS.items():
        try:
            receipts[name] = json.loads((root / relative).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{name}: {error}")
    mmi = receipts.get("mmi", {})
    tei = receipts.get("tei", {})
    if mmi.get("passed") is not True or mmi.get("selectedRows") != 5 or mmi.get("synthetic") is not True:
        errors.append("MMI did not return a passed 5-row synthetic result")
    if tei.get("passed") is not True or tei.get("validation") != "ok" or tei.get("synthetic") is not True:
        errors.append("TEI did not validate the grant model")
    return {
        "schema": "tai.reference.scn003/v0",
        "scenario": "SCN-003",
        "synthetic": True,
        "evidenceKind": "synthetic",
        "slice": "grant-application-first-review",
        "steps": list(RECORDS),
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
