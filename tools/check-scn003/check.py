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
    "sei": "evaluations/records/SCN-003-sei-2026-10-29.json",
    "eki": "evaluations/records/SCN-003-eki-docs-2026-10-29.json",
    "sui": "evaluations/records/SCN-003-sui-2026-10-29.json",
    "ai_review": "evaluations/records/SCN-003-D-08-ai-review-2026-10-29.json",
}
D08 = "evaluations/artifacts/SCN-003-D-08-first-review.md"


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
    eki = receipts.get("eki", {})
    sui = receipts.get("sui", {})
    ai_review = receipts.get("ai_review", {})
    try:
        d08 = (root / D08).read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"d08: {error}")
        d08 = ""
    if mmi.get("passed") is not True or mmi.get("selectedRows") != 5 or mmi.get("synthetic") is not True:
        errors.append("MMI did not return a passed 5-row synthetic result")
    if tei.get("passed") is not True or tei.get("validation") != "ok" or tei.get("synthetic") is not True:
        errors.append("TEI did not validate the grant model")
    if sei.get("passed") is not True or sei.get("recordCount") != 3 or sei.get("variant") != "scn003":
        errors.append("SEI did not record the SCN-003 decision fixture")
    if eki.get("passed") is not True or eki.get("taskStatus") != "cancelled" or eki.get("resultStatus") != 501:
        errors.append("EKI did not cancel the document-request task")
    if sui.get("passed") is not True or (sui.get("cardCount"), sui.get("islandCount"), sui.get("edgeCount")) != (5, 3, 1):
        errors.append("SUI DocumentV1 is not 5 cards / 3 islands / 1 edge")
    for marker in ("- 状態: `provisional`", "- 採択: **なし**", "- 公開承認: **なし**", "A | 採択候補", "B | 不適格", "C | 通常審査外"):
        if marker not in d08:
            errors.append(f"D-08 is missing marker: {marker}")
    if ai_review.get("quality") != "sufficient-for-first-review" or ai_review.get("passed") is not True:
        errors.append("SCN-003 D-08 AI review is not sufficient-for-first-review")
    if ai_review.get("adoptionGranted") is not False or ai_review.get("humanReviewed") is not False:
        errors.append("SCN-003 D-08 AI review claims adoption")
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
