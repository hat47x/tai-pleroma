#!/usr/bin/env python3
"""Check the Owner acceptance record for SCN-002 and SCN-003."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

STATUS = "evaluations/SCN-002-003-review-status.json"
DECISION = "evaluations/SCN-002-003-owner-decision-2026-10-30.md"


def check(root: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        status = json.loads((root / STATUS).read_text(encoding="utf-8"))
        decision = (root / DECISION).read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as error:
        return {"passed": False, "errors": [str(error)], "publicationAllowed": False}
    scenarios = status.get("scenarios", [])
    if [item.get("id") for item in scenarios] != ["SCN-002", "SCN-003"]:
        errors.append("review status does not contain SCN-002 and SCN-003")
    for item in scenarios:
        if item.get("status") != "accepted" or item.get("evidenceKind") != "synthetic":
            errors.append(f"{item.get('id')}: not accepted synthetic evidence")
        for artifact in item.get("artifacts", []):
            if not (root / artifact).is_file():
                errors.append(f"{item.get('id')}: missing artifact {artifact}")
        if not item.get("unresolved"):
            errors.append(f"{item.get('id')}: unresolved list is empty")
    if status.get("publicationAllowed") is not False or not status.get("publicationBlockers"):
        errors.append("publication is not blocked")
    if any(status.get(key) is not False for key in ("humanReviewed", "authorityVerified", "publicationApproved")):
        errors.append("review status claims human, authority, or publication approval")
    for marker in ("SCN-002", "SCN-003", "EKI", "post-synthetic-real-object"):
        if marker not in decision:
            errors.append(f"decision is missing marker: {marker}")
    return {
        "schema": "tai.reference.multi-scenario-review-check/v0",
        "synthetic": True,
        "evidenceKind": "synthetic",
        "scenarios": [item.get("id") for item in scenarios],
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
