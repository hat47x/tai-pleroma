#!/usr/bin/env python3
"""Fail if a synthetic reference receipt loses its synthetic labeling.

Fail closed on ambiguous or malformed JSON: duplicate keys and duplicate review
IDs must not silently replace an earlier assertion about review status.
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

RECORDS = (
    "evaluations/records/SUI-api-2026-10-26.json",
    "evaluations/records/TEI-model-2026-10-29.json",
    "evaluations/records/SEI-decision-2026-10-26.json",
    "evaluations/records/SCN-001-synthetic-mmi-2026-10-29.json",
    "evaluations/records/SCN-001-synthetic-facility-2026-10-28.json",
    "evaluations/records/EKI-worker-env-2026-10-28.json",
)
REVIEW_STATUS = "evaluations/SCN-001-review-status.json"


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Refuse JSON members silently overwritten by Python's usual decoder."""
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def _read_object(root: pathlib.Path, relative: str, errors: list[str]) -> dict[str, Any] | None:
    path = root / relative
    if not path.is_file():
        errors.append(f"missing JSON file: {relative}")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, ValueError) as exc:
        errors.append(f"invalid JSON file: {relative}: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"expected JSON object: {relative}")
        return None
    return data


def check(root: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    for relative in RECORDS:
        data = _read_object(root, relative, errors)
        if data is None:
            continue
        if data.get("synthetic") is not True:
            errors.append(f"synthetic is not true: {relative}")
        if data.get("evidenceKind") != "synthetic":
            errors.append(f"evidenceKind is not synthetic: {relative}")

    status = _read_object(root, REVIEW_STATUS, errors)
    if status is not None:
        if status.get("schema") != "tai.reference.scn001-review-status/v0" or status.get("scenario") != "SCN-001":
            errors.append(f"unexpected review status schema/scenario: {REVIEW_STATUS}")
        rows = status.get("items")
        if not isinstance(rows, list):
            errors.append(f"review items must be an array: {REVIEW_STATUS}")
        else:
            items: dict[str, dict[str, Any]] = {}
            for index, row in enumerate(rows):
                if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
                    errors.append(f"invalid review item at index {index}: {REVIEW_STATUS}")
                    continue
                item_id = row["id"]
                if item_id in items:
                    errors.append(f"duplicate review item: {item_id}")
                    continue
                items[item_id] = row
            for item_id in ("R-01", "R-02", "R-03", "R-04", "R-05"):
                item = items.get(item_id)
                if item is None:
                    errors.append(f"missing review item: {item_id}")
                elif item.get("status") != "pending" or item.get("evidenceKind") != "synthetic":
                    errors.append(f"{item_id} is not pending/synthetic")
            for item_id in ("R-06", "R-07"):
                item = items.get(item_id)
                if item is None:
                    errors.append(f"missing review item: {item_id}")
                elif item.get("status") != "pending" or item.get("evidenceKind") != "none":
                    errors.append(f"{item_id} is not pending/none")
                elif item.get("evidence") not in (None, ""):
                    errors.append(f"{item_id} declares evidence despite evidenceKind=none")

    return {"passed": not errors, "errors": errors, "recordCount": len(RECORDS)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    receipt = check(pathlib.Path(args.root))
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
