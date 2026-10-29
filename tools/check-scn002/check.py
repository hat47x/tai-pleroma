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
    "eki_inspect": "evaluations/records/SCN-002-eki-inspect-a-2026-10-29.json",
    "eki_quote": "evaluations/records/SCN-002-eki-quote-b-2026-10-29.json",
    "sui": "evaluations/records/SCN-002-sui-2026-10-29.json",
    "ai_review": "evaluations/records/SCN-002-ai-review-2026-10-29.json",
}
D05 = "evaluations/artifacts/SCN-002-D-05-priority-plan.md"


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
    eki_inspect = receipts.get("eki_inspect", {})
    eki_quote = receipts.get("eki_quote", {})
    sui = receipts.get("sui", {})
    ai_review = receipts.get("ai_review", {})
    try:
        d05 = (root / D05).read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"d05: {error}")
        d05 = ""
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
    for name, eki in (("inspect-a", eki_inspect), ("quote-b", eki_quote)):
        if eki.get("passed") is not True:
            errors.append(f"EKI {name} did not pass admission/cancel")
        if eki.get("taskStatus") != "cancelled" or eki.get("resultStatus") != 501:
            errors.append(f"EKI {name} is not cancelled with result 501")
        if eki.get("workerResult") is not False or eki.get("taskExecuted") is not False:
            errors.append(f"EKI {name} claims Task execution")
    if sui.get("passed") is not True or (sui.get("cardCount"), sui.get("islandCount"), sui.get("edgeCount")) != (7, 4, 2):
        errors.append("SUI DocumentV1 is not 7 cards / 4 islands / 2 edges")
    if sui.get("edgeType") != "depends":
        errors.append("SUI edge type is not depends")
    for marker in ("- 状態: `provisional`", "- 公開承認: **なし**", "- 発注: **なし**", "見積が確定していない"):
        if marker not in d05:
            errors.append(f"D-05 is missing marker: {marker}")
    if ai_review.get("quality") != "sufficient-for-development" or ai_review.get("passed") is not True:
        errors.append("SCN-002 AI review is not sufficient-for-development")
    if ai_review.get("humanReviewed") is not False or ai_review.get("publicationApproved") is not False:
        errors.append("SCN-002 AI review claims human or publication approval")
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
