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
    "ai_approval": "evaluations/records/SCN-002-D-06-ai-review-2026-10-29.json",
    "approvals": "evaluations/records/SCN-002-approvals-2026-10-29.json",
    "rejections": "evaluations/records/SCN-002-rejections-2026-10-29.json",
    "ai_resubmit": "evaluations/records/SCN-002-D-07-ai-review-2026-10-29.json",
}
D05 = "evaluations/artifacts/SCN-002-D-05-priority-plan.md"
D06 = "evaluations/artifacts/SCN-002-D-06-approval-packet.md"
D07 = "evaluations/artifacts/SCN-002-D-07-resubmission.md"


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
    ai_approval = receipts.get("ai_approval", {})
    approvals = receipts.get("approvals", {})
    rejections = receipts.get("rejections", {})
    ai_resubmit = receipts.get("ai_resubmit", {})
    try:
        d05 = (root / D05).read_text(encoding="utf-8")
        d06 = (root / D06).read_text(encoding="utf-8")
        d07 = (root / D07).read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"artifacts: {error}")
        d05 = ""
        d06 = ""
        d07 = ""
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
    for marker in ("- 状態: `awaiting-approval`", "- 承認: **未完了**", "- 発注: **なし**", "承認は1件も完了していない"):
        if marker not in d06:
            errors.append(f"D-06 is missing marker: {marker}")
    if ai_approval.get("quality") != "sufficient-for-approval-preparation" or ai_approval.get("passed") is not True:
        errors.append("SCN-002 D-06 AI review is not sufficient-for-approval-preparation")
    if ai_approval.get("approvalGranted") is not False or ai_approval.get("humanReviewed") is not False:
        errors.append("SCN-002 D-06 AI review claims approval")
    approval_decisions = approvals.get("approvalDecisions", [])
    if approvals.get("passed") is not True or approvals.get("recordCount") != 4 or len(approval_decisions) != 3:
        errors.append("SEI approval simulation did not record 4 records / 3 pending decisions")
    for decision in approval_decisions:
        if "未完了" not in decision.get("statement", ""):
            errors.append("SEI approval decision does not say 未完了")
    rejection_decisions = rejections.get("rejectionDecisions", [])
    if rejections.get("passed") is not True or rejections.get("recordCount") != 3 or len(rejection_decisions) != 2:
        errors.append("SEI rejection simulation did not record 3 records / 2 rejections")
    for decision in rejection_decisions:
        if "差戻し" not in decision.get("statement", ""):
            errors.append("SEI rejection decision does not say 差戻し")
    for marker in ("- 状態: `revised`", "- 承認: **未完了**", "- 発注: **なし**", "再承認はまだ得られていない", "差戻し2件には対応"):
        if marker not in d07:
            errors.append(f"D-07 is missing marker: {marker}")
    if ai_resubmit.get("quality") != "sufficient-for-resubmission" or ai_resubmit.get("passed") is not True:
        errors.append("SCN-002 D-07 AI review is not sufficient-for-resubmission")
    if ai_resubmit.get("approvalGranted") is not False or ai_resubmit.get("humanReviewed") is not False:
        errors.append("SCN-002 D-07 AI review claims approval")
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
