#!/usr/bin/env python3
"""Fail if a synthetic reference receipt loses its synthetic labeling."""

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
    "evaluations/records/SCN-001-large-mmi-2026-10-29.json",
    "evaluations/records/SCN-001-synthetic-facility-2026-10-28.json",
    "evaluations/records/SCN-001-variant-b-mmi-2026-10-29.json",
    "evaluations/records/SCN-001-variant-b-tei-2026-10-29.json",
    "evaluations/records/SCN-001-variant-b-sei-2026-10-29.json",
    "evaluations/records/SCN-001-variant-c-mmi-2026-10-29.json",
    "evaluations/records/SCN-001-variant-c-tei-2026-10-29.json",
    "evaluations/records/SCN-001-variant-c-sei-2026-10-29.json",
    "evaluations/records/SCN-001-variant-b-eki-2026-10-29.json",
    "evaluations/records/SCN-001-variant-c-eki-2026-10-29.json",
    "evaluations/records/SCN-001-variant-b-eki-cancel-2026-10-29.json",
    "evaluations/records/SCN-001-variant-c-eki-cancel-2026-10-29.json",
    "evaluations/records/SCN-001-variant-b-sui-2026-10-29.json",
    "evaluations/records/SCN-001-variant-c-sui-2026-10-29.json",
    "evaluations/records/SCN-001-variant-matrix-2026-10-29.json",
    "evaluations/records/SCN-001-invalid-tei-2026-10-29.json",
    "evaluations/records/SCN-001-invalid-mmi-2026-10-29.json",
    "evaluations/records/SCN-001-invalid-eki-2026-10-29.json",
    "evaluations/records/SCN-001-invalid-sui-2026-10-29.json",
    "evaluations/records/SCN-001-negative-matrix-2026-10-29.json",
    "evaluations/records/SCN-001-sui-unknown-edge-2026-10-29.json",
    "evaluations/records/SCN-001-sui-contract-2026-10-29.json",
    "evaluations/records/SCN-001-invalid-sei-2026-10-29.json",
    "evaluations/records/SCN-001-process-matrix-2026-10-29.json",
    "evaluations/records/SCN-002-mmi-2026-10-29.json",
    "evaluations/records/SCN-002-tei-2026-10-29.json",
    "evaluations/records/SCN-002-sei-2026-10-29.json",
    "evaluations/records/SCN-002-eki-inspect-a-2026-10-29.json",
    "evaluations/records/SCN-002-eki-quote-b-2026-10-29.json",
    "evaluations/records/SCN-002-slice-2026-10-29.json",
    "evaluations/records/EKI-worker-env-2026-10-28.json",
    "evaluations/records/SCN-001-ai-review-2026-10-29.json",
    "evaluations/records/SCN-001-eki-feasibility-2026-10-29.json",
    "evaluations/records/SCN-001-synthetic-flow-2026-10-29.json",
)
REVIEW_STATUS = "evaluations/SCN-001-review-status.json"


def check(root: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    for relative in RECORDS:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing receipt: {relative}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("synthetic") is not True:
            errors.append(f"synthetic is not true: {relative}")
        if data.get("evidenceKind") != "synthetic":
            errors.append(f"evidenceKind is not synthetic: {relative}")
        if "ai-review" in relative:
            if data.get("evaluatorKind") != "generative-ai":
                errors.append(f"evaluatorKind is not generative-ai: {relative}")
            if data.get("humanReviewed") is not False or data.get("publicationApproved") is not False:
                errors.append(f"AI review claims human or publication approval: {relative}")
            if data.get("outcome") != "uncertainty-preserved" or data.get("userNextStep") != "confirm-with-authority":
                errors.append(f"AI review does not preserve the business outcome: {relative}")
    status_path = root / REVIEW_STATUS
    if not status_path.is_file():
        errors.append(f"missing review status: {REVIEW_STATUS}")
    else:
        status = json.loads(status_path.read_text(encoding="utf-8"))
        items = {item["id"]: item for item in status.get("items", [])}
        for item_id in ("R-01", "R-02", "R-03", "R-04", "R-05"):
            item = items.get(item_id)
            if not item:
                errors.append(f"missing review item: {item_id}")
                continue
            if item.get("status") != "accepted" or item.get("evidenceKind") != "synthetic":
                errors.append(f"{item_id} is not accepted/synthetic")
        for item_id in ("R-06", "R-07"):
            item = items.get(item_id)
            if not item or item.get("status") != "pending" or item.get("evidenceKind") != "none":
                errors.append(f"{item_id} is not pending/none")
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
