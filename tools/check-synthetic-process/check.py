#!/usr/bin/env python3
"""Aggregate the synthetic process matrix across all reference products."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

RECORDS = {
    "variants": "evaluations/records/SCN-001-variant-matrix-2026-10-29.json",
    "negative": "evaluations/records/SCN-001-negative-matrix-2026-10-29.json",
    "sui_contract": "evaluations/records/SCN-001-sui-contract-2026-10-29.json",
    "sei_negative": "evaluations/records/SCN-001-invalid-sei-2026-10-29.json",
    "flow": "evaluations/records/SCN-001-synthetic-flow-2026-10-29.json",
}


def load(root: pathlib.Path, relative: str) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def check(root: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        variants = load(root, RECORDS["variants"])
        negative = load(root, RECORDS["negative"])
        sui_contract = load(root, RECORDS["sui_contract"])
        sei_negative = load(root, RECORDS["sei_negative"])
        flow = load(root, RECORDS["flow"])
    except (OSError, json.JSONDecodeError) as error:
        return {"passed": False, "errors": [str(error)], "publicationAllowed": False}

    if variants.get("passed") is not True:
        errors.append("variant matrix did not pass")
    for name, result in variants.get("results", {}).items():
        if not all(result.values()):
            errors.append(f"{name}: not all products passed")
    if negative.get("passed") is not True or negative.get("expectedRejection") is not True:
        errors.append("negative matrix did not verify rejection")
    for name, result in negative.get("results", {}).items():
        if result.get("rejected") is not True:
            errors.append(f"{name}: invalid input was not rejected")
    if sui_contract.get("passed") is not True or sui_contract.get("unknownEdgePreserved") is not True:
        errors.append("SUI did not preserve the unknown edge type")
    if sei_negative.get("passed") is not True or sei_negative.get("duplicateRejected") is not True:
        errors.append("SEI did not reject the duplicate decision")
    if flow.get("passed") is not True or flow.get("publicationAllowed") is not False:
        errors.append("synthetic flow did not pass with publication blocked")

    products = {
        "MMI": {"normal": variants.get("results", {}).get("variant-b", {}).get("mmi", False), "rejection": negative.get("results", {}).get("mmi", {}).get("rejected", False), "limitation": "5-row preview"},
        "TEI": {"normal": variants.get("results", {}).get("variant-b", {}).get("tei", False), "rejection": negative.get("results", {}).get("tei", {}).get("rejected", False)},
        "SEI": {"normal": variants.get("results", {}).get("variant-b", {}).get("sei", False), "rejection": sei_negative.get("duplicateRejected", False)},
        "EKI": {"normal": variants.get("results", {}).get("variant-b", {}).get("eki", False), "rejection": negative.get("results", {}).get("eki", {}).get("rejected", False)},
        "SUI": {"normal": variants.get("results", {}).get("variant-b", {}).get("sui", False), "rejection": negative.get("results", {}).get("sui", {}).get("rejected", False), "unknownEdgePreserved": sui_contract.get("unknownEdgePreserved", False)},
    }
    return {
        "schema": "tai.reference.scn001-process-matrix/v0",
        "synthetic": True,
        "evidenceKind": "synthetic",
        "products": products,
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
