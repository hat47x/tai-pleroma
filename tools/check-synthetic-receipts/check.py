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
    "evaluations/records/SCN-002-sui-2026-10-29.json",
    "evaluations/records/SCN-002-ai-review-2026-10-29.json",
    "evaluations/records/SCN-002-D-06-ai-review-2026-10-29.json",
    "evaluations/records/SCN-002-D-07-ai-review-2026-10-29.json",
    "evaluations/records/SCN-002-approvals-2026-10-29.json",
    "evaluations/records/SCN-002-rejections-2026-10-29.json",
    "evaluations/records/SCN-002-slice-2026-10-29.json",
    "evaluations/records/SCN-cross-scenario-2026-10-29.json",
    "evaluations/records/SCN-003-mmi-2026-10-29.json",
    "evaluations/records/SCN-003-tei-2026-10-29.json",
    "evaluations/records/SCN-003-sei-2026-10-29.json",
    "evaluations/records/SCN-003-eki-docs-2026-10-29.json",
    "evaluations/records/SCN-003-sui-2026-10-29.json",
    "evaluations/records/SCN-003-D-08-ai-review-2026-10-29.json",
    "evaluations/records/SCN-003-slice-2026-10-29.json",
    "evaluations/records/SCN-002-003-review-2026-10-30.json",
    "evaluations/records/EKI-worker-env-2026-10-28.json",
    "evaluations/records/EKI-execution-2026-10-31.json",
    "evaluations/records/EKI-acceptance-2026-10-31.json",
    "evaluations/records/EKI-runtime-limits-2026-11-01.json",
    "evaluations/records/TEI-product-capabilities-2026-10-31.json",
    "evaluations/records/TEI-capability-chain-2026-10-31.json",
    "evaluations/records/SW-01-S1-harness-2026-10-31.json",
    "evaluations/records/SW-01-S1-harnessA-rerun-2026-10-31.json",
    "evaluations/records/SCN-001-ai-review-2026-10-29.json",
    "evaluations/records/SCN-001-eki-feasibility-2026-10-29.json",
    "evaluations/records/SCN-001-synthetic-flow-2026-10-29.json",
)
REVIEW_STATUS = "evaluations/SCN-001-review-status.json"

# Real-execution receipts are kept separate from synthetic ones so that a test
# run on a host is never counted as synthetic evidence.
REAL_RECORDS = (
    "evaluations/records/EKI-linux-process-2026-11-01.json",
    "evaluations/records/EKI-bwrap-linux-2026-11-01.json",
    "evaluations/records/TEI-EKI-live-2026-11-01.json",
    "evaluations/records/SUI-live-2026-11-01.json",
    "evaluations/records/SEI-live-2026-11-01.json",
    "evaluations/records/MMI-live-2026-11-01.json",
    "evaluations/records/EKI-http-agent-2026-11-01.json",
    "evaluations/records/SUI-auth-2026-11-01.json",
    "evaluations/records/SUI-TEI-pilot-2026-11-01.json",
    "evaluations/records/SUI-TEI-generation-spike-2026-11-01.json",
    "evaluations/records/SUI-TEI-selection-2026-11-01.json",
    "evaluations/records/SUI-TEI-text-generation-2026-11-01.json",
    "evaluations/records/SUI-TEI-target-2026-11-01.json",
    "evaluations/records/SUI-TEI-target-document-id-2026-11-02.json",
    "evaluations/records/SUI-TEI-card-record-2026-11-02.json",
    "evaluations/records/SUI-TEI-compare-2026-11-02.json",
    "evaluations/records/SUI-TEI-deploy-2026-11-02.json",
    "evaluations/records/SUI-TEI-island-edge-2026-11-02.json",
    "evaluations/records/SUI-TEI-document-record-2026-11-02.json",
    "evaluations/records/SUI-TEI-assembler-2026-11-02.json",
    "evaluations/records/SUI-TEI-integration-flow-2026-11-02.json",
    "evaluations/records/SUI-TEI-alignment-2026-11-02.json",
    "evaluations/records/SUI-TEI-workflow-2026-11-02.json",
    "evaluations/records/SUI-TEI-multi-attribute-2026-11-02.json",
)


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
            if "D-08" in relative:
                expected_outcome, expected_next = "candidate-with-unresolved-eligibility", "confirm-eligibility-and-quota"
            elif "D-07" in relative:
                expected_outcome, expected_next = "revised-after-rejection", "resubmit-approvals"
            elif "D-06" in relative:
                expected_outcome, expected_next = "approval-ready-with-conditions", "obtain-approvals"
            elif "SCN-002" in relative:
                expected_outcome, expected_next = "budget-constrained-proposal", "confirm-quotes-and-approval"
            else:
                expected_outcome, expected_next = "uncertainty-preserved", "confirm-with-authority"
            if data.get("outcome") != expected_outcome or data.get("userNextStep") != expected_next:
                errors.append(f"AI review does not preserve the business outcome: {relative}")
    for relative in REAL_RECORDS:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing real-execution receipt: {relative}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("synthetic") is not False:
            errors.append(f"real-execution receipt claims synthetic: {relative}")
        if data.get("evidenceKind") != "real-execution":
            errors.append(f"evidenceKind is not real-execution: {relative}")
        if data.get("publicationAllowed") is not False:
            errors.append(f"real-execution receipt allows publication: {relative}")
        if not data.get("host") or not data.get("command"):
            errors.append(f"real-execution receipt lacks host or command: {relative}")
        if data.get("result") != "PASS":
            errors.append(f"real-execution receipt is not PASS: {relative}")
        if "TEI-EKI-live" in relative:
            accepted = data.get("accepted", {})
            if accepted.get("resultStatus") != 202:
                errors.append(f"live receipt did not record 202: {relative}")
            if not str(accepted.get("observedTaskId", "")).startswith("tsk_"):
                errors.append(f"live receipt has no accepted task id: {relative}")
            if data.get("idempotentReplay", {}).get("replayTaskId") != accepted.get("observedTaskId"):
                errors.append(f"live receipt replay differs from the accepted task: {relative}")
            if data.get("rejected", {}).get("resultStatus") != 400:
                errors.append(f"live receipt did not record a 400 rejection: {relative}")
            conflict = data.get("idempotencyConflict", {})
            if conflict.get("resultStatus") != 409 or conflict.get("code") != "IDEMPOTENCY_KEY_CONFLICT":
                errors.append(f"live receipt did not record the idempotency conflict: {relative}")
        if "SUI-live" in relative:
            document = data.get("document", {})
            if document.get("putStatus") != 200 or document.get("read") is not True:
                errors.append(f"SUI live receipt has no document round trip: {relative}")
            if document.get("cardCount") != 1:
                errors.append(f"SUI live receipt card count differs: {relative}")
            if not str(document.get("digest", "")).startswith("sha256:"):
                errors.append(f"SUI live receipt has no document digest: {relative}")
        if "tei-integration-flow" in relative:
            if data.get("casesPassed") != data.get("casesRun") or data.get("casesPassed") != 17:
                errors.append(f"TEI integration flow receipt did not pass all cases: {relative}")
            if data.get("danglingReferenceRejected") is not True:
                errors.append(f"TEI integration flow receipt did not reject a dangling reference: {relative}")
            if data.get("composed", {}).get("cards") != 2:
                errors.append(f"TEI integration flow receipt did not compose two cards: {relative}")
        if "tei-assembler" in relative:
            observed = data.get("observed", {})
            if observed.get("assemblerPassed") != 6 or observed.get("assemblerTests") != 6:
                errors.append(f"TEI assembler receipt did not pass 6 tests: {relative}")
            if observed.get("cardCases") != 4 or observed.get("cardQualified") != "text-record-template":
                errors.append(f"TEI assembler receipt did not bind the card record: {relative}")
        if "tei-document-record" in relative:
            observed = data.get("observed", {})
            if observed.get("cases") != 4 or observed.get("profilePassed") is not True:
                errors.append(f"TEI document record receipt did not pass 4 cases and the profile: {relative}")
            if observed.get("fields") != ["documentId", "title", "digest"]:
                errors.append(f"TEI document record receipt has unexpected fields: {relative}")
        if "tei-island-edge" in relative:
            contracts = data.get("observed", {}).get("contracts", [])
            if len(contracts) != 2:
                errors.append(f"TEI island/edge receipt did not cover two contracts: {relative}")
            for item in contracts:
                if item.get("cases") != 4 or item.get("targetPassed") is not True:
                    errors.append(f"TEI island/edge receipt did not pass 4 cases for {item.get('id')}: {relative}")
        if "tei-deploy" in relative:
            observed = data.get("observed", {})
            if observed.get("rollback", {}).get("passed") is not True:
                errors.append(f"TEI deploy receipt did not pass rollback: {relative}")
            if observed.get("secondDeploy", {}).get("rollbackAvailable") is not True:
                errors.append(f"TEI deploy receipt did not record rollback availability: {relative}")
        if "tei-comparison" in relative:
            if data.get("evaluationSet", {}).get("cases") != 4:
                errors.append(f"TEI comparison receipt did not use 4 cases: {relative}")
            if data.get("tei", {}).get("passed") is not True or data.get("baseline", {}).get("passed") is not True:
                errors.append(f"TEI comparison receipt did not pass both paths: {relative}")
        if "tei-card-record" in relative:
            observed = data.get("observed", {})
            if observed.get("kind") != "record" or observed.get("passedCases") != 4:
                errors.append(f"TEI card record receipt did not pass a record contract: {relative}")
            if "text-record-template" not in observed.get("qualified", []):
                errors.append(f"TEI card record receipt did not qualify the record candidate: {relative}")
            if observed.get("profilePassed") is not True:
                errors.append(f"TEI card record receipt did not run the profile: {relative}")
        if "tei-multi-attribute" in relative:
            observed = data.get("observed", {})
            if observed.get("attributeCount") != 2 or observed.get("passedCases") != 4:
                errors.append(f"TEI multi-attribute receipt did not cover two attributes: {relative}")
            if "text-template" not in observed.get("qualified", []):
                errors.append(f"TEI multi-attribute receipt did not qualify the candidate: {relative}")
        if "tei-workflow" in relative:
            if data.get("passed") is not True or data.get("cases") != 4:
                errors.append(f"TEI workflow receipt did not pass 4 cases: {relative}")
            if data.get("humanInterventions") != 0:
                errors.append(f"TEI workflow receipt recorded human interventions: {relative}")
        if "tei-target" in relative:
            observed = data.get("observed", {})
            if observed.get("processModel") != "oneshot" or observed.get("profilePassed") is not True:
                errors.append(f"TEI target receipt did not pass the oneshot profile: {relative}")
            if observed.get("passedCases") != 4:
                errors.append(f"TEI target receipt did not pass 4 cases: {relative}")
        if "tei-text-generation" in relative:
            observed = data.get("observed", {})
            if observed.get("strategy") != "text-template" or observed.get("passedCases") != 4:
                errors.append(f"TEI text generation receipt did not pass 4 cases with text-template: {relative}")
            if "text-template" not in observed.get("qualified", []):
                errors.append(f"TEI text generation receipt did not qualify the generated candidate: {relative}")
        if "tei-text-selection" in relative:
            observed = data.get("observed", {})
            if observed.get("cases") != 4 or observed.get("passedCases") != 4:
                errors.append(f"TEI text selection receipt did not pass 4 cases: {relative}")
            if "text-identity" not in observed.get("qualified", []):
                errors.append(f"TEI text selection receipt did not qualify the candidate: {relative}")
        if "tei-generation-spike" in relative:
            observed = data.get("observed", {})
            if observed.get("cases") != 4 or observed.get("passedCases") != 4:
                errors.append(f"TEI generation spike receipt did not pass 4 cases: {relative}")
            if not str(observed.get("contractDigest", "")).startswith("sha256:"):
                errors.append(f"TEI generation spike receipt has no contract digest: {relative}")
        if "SUI-TEI-pilot" in relative:
            observed = data.get("observed", {})
            if observed.get("validate") != "ok":
                errors.append(f"TEI pilot receipt did not record validate ok: {relative}")
            if not str(observed.get("sourceIndexFingerprint", "")).startswith("sha256:"):
                errors.append(f"TEI pilot receipt has no source index fingerprint: {relative}")
            if observed.get("dataTypes", 0) < 4:
                errors.append(f"TEI pilot receipt has too few data types: {relative}")
        if "SUI-auth" in relative:
            observed = data.get("observed", {})
            if observed.get("passed", 0) < 40 or observed.get("failed") != 0:
                errors.append(f"SUI auth receipt does not record 40 passing tests: {relative}")
            if not str(data.get("suiCommit", "")):
                errors.append(f"SUI auth receipt has no commit: {relative}")
        if "EKI-http-agent" in relative:
            observed = data.get("observed", {})
            if observed.get("submitStatus") != 202:
                errors.append(f"EKI HTTP/agent receipt has no 202: {relative}")
            if not str(observed.get("taskID", "")).startswith("tsk_"):
                errors.append(f"EKI HTTP/agent receipt has no task id: {relative}")
            if not str(observed.get("claimDigest", "")):
                errors.append(f"EKI HTTP/agent receipt has no claim digest: {relative}")
            if observed.get("acceptedOutcome") != "accepted":
                errors.append(f"EKI HTTP/agent receipt has no accepted result: {relative}")
            if not str(observed.get("acceptedResultDigest", "")):
                errors.append(f"EKI HTTP/agent receipt has no accepted result digest: {relative}")
        if "MMI-live" in relative:
            observed = data.get("observed", {})
            if observed.get("exitCode") != 0:
                errors.append(f"MMI live receipt did not record exit 0: {relative}")
            if not isinstance(observed.get("candidateCount"), int) or observed.get("candidateCount") < 1:
                errors.append(f"MMI live receipt has no candidates: {relative}")
            if not str(observed.get("sourceDigest", "")).startswith("sha256:"):
                errors.append(f"MMI live receipt has no source digest: {relative}")
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
    return {
        "passed": not errors,
        "errors": errors,
        "recordCount": len(RECORDS),
        "realRecordCount": len(REAL_RECORDS),
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
