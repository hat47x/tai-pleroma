#!/usr/bin/env python3
"""Aggregate SCN-001 and SCN-002 into one practical-capability matrix."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

RECORDS = {
    "scn001": "evaluations/records/SCN-001-process-matrix-2026-10-29.json",
    "scn002": "evaluations/records/SCN-002-slice-2026-10-29.json",
    "scn003": "evaluations/records/SCN-003-slice-2026-10-29.json",
}


def load(root: pathlib.Path, relative: str) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def check(root: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        scn001 = load(root, RECORDS["scn001"])
        scn002 = load(root, RECORDS["scn002"])
        scn003 = load(root, RECORDS["scn003"])
    except (OSError, json.JSONDecodeError) as error:
        return {"passed": False, "errors": [str(error)], "publicationAllowed": False}

    if scn001.get("passed") is not True:
        errors.append("SCN-001 process matrix did not pass")
    if scn002.get("passed") is not True:
        errors.append("SCN-002 slice did not pass")
    if scn003.get("passed") is not True:
        errors.append("SCN-003 slice did not pass")
    if scn001.get("publicationAllowed") is not False or scn002.get("publicationAllowed") is not False or scn003.get("publicationAllowed") is not False:
        errors.append("a scenario did not keep publication blocked")

    products_001 = set(scn001.get("products", {}))
    products_002 = set(scn002.get("steps", []))
    products_003 = set(scn003.get("steps", []))
    required = {"MMI", "TEI", "SEI", "EKI", "SUI"}
    if products_001 != required:
        errors.append(f"SCN-001 product set differs: {sorted(products_001)}")
    for name in ("mmi", "tei", "sei", "eki_inspect", "eki_quote", "sui"):
        if name not in products_002:
            errors.append(f"SCN-002 is missing step: {name}")
    for name in ("mmi", "tei", "sei", "eki", "sui"):
        if name not in products_003:
            errors.append(f"SCN-003 is missing step: {name}")

    return {
        "schema": "tai.reference.cross-scenario/v0",
        "synthetic": True,
        "evidenceKind": "synthetic",
        "scenarios": ["SCN-001", "SCN-002", "SCN-003"],
        "matrix": {
            "SCN-001": {"kind": "facility-reservation", "products": sorted(products_001)},
            "SCN-002": {"kind": "multi-site-maintenance", "products": sorted(products_002)},
            "SCN-003": {"kind": "grant-application-review", "products": sorted(products_003)},
        },
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
