#!/usr/bin/env python3
"""Check the first synthetic SCN-002 maintenance slice through MMI and TEI."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

RECORDS = {
    "mmi": "evaluations/records/SCN-002-mmi-2026-10-29.json",
    "tei": "evaluations/records/SCN-002-tei-2026-10-29.json",
    "sei": "evaluations/records/SCN-002-sei-2026-10-29.json",
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
    sei = receipts.get("sei", {})
    if mmi.get("passed") is not True or mmi.get("selectedRows") != 5:
        errors.append("MMI did not return 5 rows")
    if mmi.get("synthetic") is not True:
        errors.append("MMI receipt is not synthetic")
    if tei.get("passed") is not True or tei.get("validation") != "ok":
        errors.append("TEI did not validate the maintenance model")
    if tei.get("synthetic") is not True:
        errors.append("TEI receipt is not synthetic")
    if sei.get("passed") is not True or sei.get("recordCount") != 3 or sei.get("variant") != "scn002":
        errors.append("SEI did not record the SCN-002 decision fixture")
    if sei.get("synthetic") is not True:
        errors.append("SEI receipt is not synthetic")
    return {
        "schema": "tai.reference.scn002/v0",
        "scenario": "SCN-002",
        "synthetic": True,
        "evidenceKind": "synthetic",
        "slice": "multi-site-maintenance-prioritization",
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
