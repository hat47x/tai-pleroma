#!/usr/bin/env python3
"""Check that the synthetic SCN-001 development flow is connected end to end."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

RECORDS = {
    "facility": "evaluations/records/SCN-001-synthetic-facility-2026-10-28.json",
    "mmi": "evaluations/records/SCN-001-synthetic-mmi-2026-10-29.json",
    "sei": "evaluations/records/SEI-decision-2026-10-26.json",
    "tei": "evaluations/records/TEI-model-2026-10-29.json",
    "sui": "evaluations/records/SUI-api-2026-10-26.json",
    "ai_review": "evaluations/records/SCN-001-ai-review-2026-10-29.json",
    "gate": "evaluations/records/SCN-001-publication-gate-2026-10-29.json",
}
D04 = "evaluations/artifacts/SCN-001-D-04-provisional.md"


def load(root: pathlib.Path, relative: str) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def check(root: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        facility = load(root, RECORDS["facility"])
        mmi = load(root, RECORDS["mmi"])
        sei = load(root, RECORDS["sei"])
        tei = load(root, RECORDS["tei"])
        sui = load(root, RECORDS["sui"])
        ai_review = load(root, RECORDS["ai_review"])
        gate = load(root, RECORDS["gate"])
        d04 = (root / D04).read_text(encoding="utf-8")
    except (OSError, KeyError, json.JSONDecodeError) as error:
        return {"passed": False, "errors": [str(error)], "publicationAllowed": False}

    if facility.get("passed") is not True or facility.get("synthetic") is not True:
        errors.append("facility check is not a passed synthetic check")
    if mmi.get("selectedRows") != 5 or mmi.get("passed") is not True:
        errors.append("MMI did not return 5 rows")
    if sei.get("recordCount") != 3 or sei.get("passed") is not True:
        errors.append("SEI record count is not 3")
    if tei.get("validation") != "ok" or tei.get("passed") is not True:
        errors.append("TEI validation is not ok")
    if (sui.get("documentCardCount"), sui.get("documentIslandCount"), sui.get("documentEdgeCount")) != (5, 3, 1):
        errors.append("SUI shape is not 5 cards / 3 islands / 1 edge")
    if ai_review.get("quality") != "sufficient-for-development" or ai_review.get("passed") is not True:
        errors.append("AI development review is not sufficient-for-development")
    if ai_review.get("humanReviewed") is not False or ai_review.get("publicationApproved") is not False:
        errors.append("AI review claims human or publication approval")
    expected = ["R-01", "R-02", "R-03", "R-04", "R-05"]
    if gate.get("allowed") is not False or gate.get("developmentAccepted") != expected:
        errors.append("gate did not keep publication blocked with 5 development-accepted items")
    for marker in ("| O-08 |", "| unavailable |", "- 状態: `provisional`", "- 公開承認: **なし**"):
        if marker not in d04:
            errors.append(f"D-04 is missing marker: {marker}")

    return {
        "schema": "tai.reference.scn001-synthetic-flow/v0",
        "synthetic": True,
        "evidenceKind": "synthetic",
        "flow": "synthetic-documents->MMI->SEI->TEI->SUI->D-04->AI-review->publication-gate",
        "steps": list(RECORDS),
        "developmentReview": "accepted",
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
