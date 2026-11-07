#!/usr/bin/env python3
"""Fail if a synthetic reference receipt loses its synthetic labeling.

Fail closed on ambiguous or malformed JSON: duplicate keys and duplicate review
IDs must not silently replace an earlier assertion about review status.
"""

from __future__ import annotations

import argparse
import hashlib
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
    "evaluations/records/SUI-TEI-large-doc-2026-11-03.json",
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
    "evaluations/records/SUI-TEI-affiliation-2026-11-02.json",
    "evaluations/records/SUI-TEI-island-cardids-2026-11-02.json",
    "evaluations/records/SUI-TEI-artifact-2026-11-02.json",
    "evaluations/records/SUI-TEI-sui-reader-2026-11-02.json",
    "evaluations/records/SUI-TEI-binding-2026-11-02.json",
    "evaluations/records/SUI-TEI-coordinates-2026-11-02.json",
    "evaluations/records/SUI-TEI-optional-2026-11-02.json",
    "evaluations/records/SUI-TEI-reviewed-2026-11-02.json",
    "evaluations/records/SUI-TEI-artifact-validation-2026-11-02.json",
    "evaluations/records/SUI-TEI-optional-core-2026-11-02.json",
    "evaluations/records/SUI-TEI-admin-path-2026-11-02.json",
    "evaluations/records/SUI-TEI-consumer-2026-11-02.json",
    "evaluations/records/SUI-TEI-adapter-2026-11-02.json",
    "evaluations/records/SUI-TEI-http-route-2026-11-02.json",
    "evaluations/records/SUI-TEI-auth-2026-11-02.json",
    "evaluations/records/SUI-TEI-tenant-route-2026-11-03.json",
    "evaluations/records/SUI-TEI-containment-2026-11-03.json",
    "evaluations/records/SUI-TEI-documentv1-validation-2026-11-03.json",
    "evaluations/records/SUI-TEI-save-plan-2026-11-03.json",
    "evaluations/records/SUI-TEI-multi-doc-2026-11-03.json",
    "evaluations/records/SUI-TEI-etag-2026-11-03.json",
    "evaluations/records/SUI-TEI-save-merge-2026-11-03.json",
    "evaluations/records/SUI-TEI-save-plan-merge-2026-11-03.json",
    "evaluations/records/SUI-TEI-save-plan-cli-2026-11-03.json",
    "evaluations/records/SUI-TEI-save-contract-2026-11-03.json",
    "evaluations/records/SUI-TEI-save-e2e-2026-11-03.json",
    "evaluations/records/SUI-TEI-save-auth-2026-11-03.json",
    "evaluations/records/SUI-TEI-save-roundtrip-2026-11-03.json",
    "evaluations/records/SUI-TEI-server-2026-11-03.json",
    "evaluations/records/SUI-TEI-determinism-2026-11-03.json",
    "evaluations/records/SUI-TEI-sources-2026-11-03.json",
    "evaluations/records/SUI-TEI-sources-validation-2026-11-03.json",
    "evaluations/records/SUI-TEI-reading-order-2026-11-03.json",
    "evaluations/records/SUI-TEI-reading-order-validation-2026-11-03.json",
    "evaluations/records/SUI-TEI-fields-roundtrip-2026-11-03.json",
    "evaluations/records/SUI-TEI-contract-versions-2026-11-03.json",
    "evaluations/records/SUI-TEI-contract-versions-validation-2026-11-03.json",
    "evaluations/records/SUI-TEI-contract-digest-2026-11-03.json",
    "evaluations/records/SUI-TEI-contract-digest-check-2026-11-03.json",
    "evaluations/records/SUI-TEI-pipeline-run-2026-11-03.json",
    "evaluations/records/SUI-TEI-compat-2026-11-03.json",
    "evaluations/records/SUI-TEI-pipeline-save-2026-11-03.json",
    "evaluations/records/SEI-TEI-decision-selection-2026-11-03.json",
    "evaluations/records/SUI-TEI-artifact-schema-2026-11-03.json",
    "evaluations/records/SEI-TEI-artifact-2026-11-03.json",
    "evaluations/records/MMI-TEI-format-profile-selection-2026-11-03.json",
    "evaluations/records/MMI-TEI-artifact-2026-11-03.json",
    "evaluations/records/MMI-TEI-profile-2026-11-03.json",
    "evaluations/records/MMI-inspect-2026-11-03.json",
    "evaluations/records/MMI-inventory-2026-11-03.json",
    "evaluations/records/MMI-delivery-audit-2026-11-03.json",
    "evaluations/records/SUI-TEI-audit-2026-11-03.json",
    "evaluations/records/SUI-TEI-admin-2026-11-03.json",
    "evaluations/records/SUI-TEI-context-2026-11-03.json",
    "evaluations/records/SUI-TEI-context-bundle-2026-11-03.json",
    "evaluations/records/SUI-TEI-ce4-2026-11-03.json",
    "evaluations/records/SUI-TEI-registry-2026-11-03.json",
    "evaluations/records/SUI-TEI-agent-guard-2026-11-06.json",
    "evaluations/records/SUI-TEI-agent-credential-admin-2026-11-06.json",
    "evaluations/records/SUI-TEI-audit-pagination-2026-11-06.json",
    "evaluations/records/SUI-TEI-etag-stability-2026-11-06.json",
    "evaluations/records/SUI-TEI-archive-lifecycle-2026-11-06.json",
    "evaluations/records/SUI-TEI-merge-decision-log-2026-11-06.json",
    "evaluations/records/SUI-TEI-ce4-audit-order-2026-11-06.json",
    "evaluations/records/SUI-TEI-polygon-handoff-2026-11-06.json",
    "evaluations/records/SUI-TEI-similar-candidates-2026-11-06.json",
    "evaluations/records/SUI-TEI-export-dedup-2026-11-06.json",
    "evaluations/records/SUI-TEI-native-action-2026-11-06.json",
    "evaluations/records/SUI-TEI-list-pagination-2026-11-06.json",
    "evaluations/records/SUI-TEI-agent-read-path-2026-11-06.json",
    "evaluations/records/SUI-TEI-agent-key-wiring-2026-11-06.json",
    "evaluations/records/SUI-TEI-saas-precondition-2026-11-06.json",
    "evaluations/records/SUI-TEI-dedup-window-2026-11-06.json",
    "evaluations/records/SUI-TEI-profile-policy-2026-11-06.json",
    "evaluations/records/SUI-TEI-probes-2026-11-06.json",
    "evaluations/records/SUI-TEI-auth-assurance-2026-11-06.json",
    "evaluations/records/SUI-TEI-headers-2026-11-06.json",
    "evaluations/records/SUI-TEI-card-move-2026-11-06.json",
    "evaluations/records/SUI-TEI-migrations-2026-11-06.json",
    "evaluations/records/SUI-TEI-preflight-2026-11-06.json",
    "evaluations/records/SUI-TEI-policy-requirements-2026-11-06.json",
    "evaluations/records/SUI-TEI-builders-2026-11-06.json",
    "evaluations/records/SUI-TEI-failsafe-2026-11-06.json",
    "evaluations/records/SUI-TEI-parsers-2026-11-06.json",
    "evaluations/records/SEI-TEI-doctor-2026-11-06.json",
    "evaluations/records/SEI-TEI-resume-2026-11-06.json",
    "evaluations/records/SUI-TEI-provision-2026-11-03.json",
    "evaluations/records/SUI-TEI-reference-2026-11-03.json",
    "evaluations/records/SUI-TEI-reference-multi-2026-11-03.json",
    "evaluations/records/TEI-artifacts-crosscheck-2026-11-03.json",
    "evaluations/records/EKI-TEI-task-request-selection-2026-11-03.json",
    "evaluations/records/EKI-TEI-artifact-2026-11-03.json",
    "evaluations/records/SEI-TEI-consumer-2026-11-03.json",
    "evaluations/records/SEI-TEI-real-artifact-2026-11-03.json",
    "evaluations/records/SEI-TEI-record-2026-11-03.json",
    "evaluations/records/MMI-TEI-consumer-2026-11-03.json",
    "evaluations/records/MMI-TEI-real-artifact-2026-11-03.json",
    "evaluations/records/MMI-TEI-record-2026-11-03.json",
    "evaluations/records/EKI-TEI-consumer-2026-11-03.json",
    "evaluations/records/EKI-TEI-record-2026-11-03.json",
    "evaluations/records/SEI-TEI-cli-2026-11-03.json",
    "evaluations/records/SEI-TEI-gate-2026-11-03.json",
    "evaluations/records/SEI-TEI-gate-variants-2026-11-03.json",
    "evaluations/records/SEI-TEI-mcp-2026-11-03.json",
    "evaluations/records/SEI-TEI-mcp-check-2026-11-03.json",
    "evaluations/records/EKI-TEI-submit-2026-11-03.json",
    "evaluations/records/EKI-TEI-dispatch-running-2026-11-03.json",
    "evaluations/records/EKI-TEI-http-execution-2026-11-03.json",
    "evaluations/records/EKI-TEI-projection-execution-2026-11-03.json",
    "evaluations/records/EKI-TEI-policy-execution-2026-11-03.json",
    "evaluations/records/EKI-TEI-manual-execution-2026-11-03.json",
    "evaluations/records/EKI-TEI-worker-revoke-2026-11-03.json",
    "evaluations/records/EKI-TEI-revoked-agent-2026-11-03.json",
    "evaluations/records/EKI-TEI-multi-worker-2026-11-03.json",
    "evaluations/records/EKI-TEI-budget-aligned-artifact-2026-11-03.json",
    "evaluations/records/TEI-records-2026-11-03.json",
    "evaluations/records/TEI-artifact-digests-2026-11-03.json",
    "evaluations/records/SUI-saas-adapter-contract-2026-11-03.json",
    "evaluations/records/SUI-saas-oauth-contract-2026-11-03.json",
    "evaluations/records/SUI-saas-login-contract-2026-11-03.json",
    "evaluations/records/SUI-saas-callback-contract-2026-11-03.json",
    "evaluations/records/SUI-saas-identity-2026-11-03.json",
    "evaluations/records/SUI-saas-tests-2026-11-03.json",
    "evaluations/records/SUI-docs-tests-2026-11-03.json",
    "evaluations/records/SUI-auth-flow-tests-2026-11-03.json",
    "evaluations/records/SUI-session-tests-2026-11-03.json",
    "evaluations/records/TEI-artifacts-determinism-2026-11-03.json",
    "evaluations/records/SCN-003-artifact-links-2026-11-03.json",
    "evaluations/records/SCN-003-compose-2026-11-03.json",
    "evaluations/records/SCN-003-save-2026-11-03.json",
    "evaluations/records/TEI-suite-pipeline-2026-11-03.json",
    "evaluations/records/TEI-suite-2026-11-03.json",
    "evaluations/records/SUI-TEI-tls-2026-11-03.json",
    "evaluations/records/SUI-TEI-postgres-2026-11-03.json",
    "evaluations/records/SUI-TEI-postgres-tls-2026-11-03.json",
    "evaluations/records/SUI-TEI-proxy-2026-11-03.json",
    "evaluations/records/SUI-TEI-ca-chain-2026-11-03.json",
    "evaluations/records/SUI-TEI-multi-instance-2026-11-03.json",
    "evaluations/records/SUI-TEI-postgres-migrate-2026-11-03.json",
    "evaluations/records/SUI-TEI-postgres-etag-2026-11-03.json",
    "evaluations/records/SUI-TEI-postgres-concurrency-2026-11-03.json",
    "evaluations/records/SUI-TEI-postgres-contention-2026-11-03.json",
    "evaluations/records/SUI-TEI-postgres-retry-2026-11-03.json",
    "evaluations/records/SUI-TEI-postgres-retry-evidence-2026-11-03.json",
    "evaluations/records/SUI-TEI-workflow-2026-11-02.json",
    "evaluations/records/SUI-TEI-multi-attribute-2026-11-02.json",
)



def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Refuse JSON members silently overwritten by Python's usual decoder."""
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj

def _read_json(path: pathlib.Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    """Read one JSON receipt; malformed or duplicate-key input fails closed."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, ValueError) as exc:
        errors.append(f"invalid JSON file: {label}: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"expected JSON object: {label}")
        return None
    return data

def check(root: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    for relative in RECORDS:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing receipt: {relative}")
            continue
        data = _read_json(path, relative, errors)
        if data is None:
            continue
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
        data = _read_json(path, relative, errors)
        if data is None:
            continue
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
        if "tei-affiliation" in relative:
            if data.get("composed", {}).get("affiliations") != 1:
                errors.append(f"TEI affiliation receipt did not compose one affiliation: {relative}")
        if "tei-large-doc" in relative:
            observed = data.get("observed", {})
            if data.get("synthetic") is not True or observed.get("savedCards") != 300:
                errors.append(f"TEI large-doc synthetic receipt is mislabeled or incomplete: {relative}")
        if "tei-sui-etag" in relative:
            observed = data.get("observed", {})
            if observed.get("staleIfMatchStatus") != 409 or observed.get("matchingIfMatchStatus") != 200:
                errors.append(f"TEI ETag receipt did not record 409/200: {relative}")
        if "tei-multi-doc" in relative:
            observed = data.get("observed", {})
            if observed.get("documents") != 10 or observed.get("isolatedIds") is not True:
                errors.append(f"TEI multi-doc receipt did not record ten isolated documents: {relative}")
        if "tei-sui-save-plan" in relative:
            observed = data.get("observed", {})
            if observed.get("planAction") != "update" or observed.get("roundTrip") is not True:
                errors.append(f"TEI save plan receipt did not record an idempotent update: {relative}")
        if "tei-determinism" in relative:
            observed = data.get("observed", {})
            if observed.get("identical") is not True or len(set(observed.get("digests", []))) != 1:
                errors.append(f"TEI determinism receipt did not record identical digests: {relative}")
        if "SUI-TEI-multi-instance" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("crossUpdateStatus") != 200 or observed.get("staleUpdateStatus") != 409:
                errors.append(f"SUI multi-instance check did not hold: {relative}")
        if "SUI-TEI-ca-chain" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("roundTrip") is not True or observed.get("untrustedRefused") is not True:
                errors.append(f"SUI CA chain check did not hold: {relative}")
        if "SUI-TEI-proxy" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("roundTrip") is not True or observed.get("anonymousStatus") not in (401, 403):
                errors.append(f"SUI behind the proxy did not round-trip or refuse anonymous writes: {relative}")
        if "SUI-TEI-postgres-tls" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("roundTrip") is not True or observed.get("anonymousStatus") not in (401, 403):
                errors.append(f"SUI over PostgreSQL+TLS did not round-trip or refuse anonymous writes: {relative}")
        if "SUI-TEI-postgres-retry-evidence" in relative:
            observed = data.get("observed", {})
            if observed.get("retries", 0) < 1 or data.get("result") != "PASS":
                errors.append(f"SUI Postgres retry evidence did not record a recovered retry: {relative}")
        if "SUI-TEI-postgres-retry" in relative:
            rounds = data.get("observed", {}).get("rounds", [])
            terminal = all(all(status in (200, 409) for status in item.get("statuses", [])) for item in rounds)
            if data.get("result") != "PASS" or not terminal:
                errors.append(f"SUI Postgres retry run left a transient status: {relative}")
        if "SUI-TEI-postgres-contention" in relative:
            rounds = data.get("observed", {}).get("rounds", [])
            settled = bool(rounds) and all(
                sum(1 for status in item.get("statuses", []) if status == 200) == 1 for item in rounds
            )
            if data.get("result") != "PASS" or not settled:
                errors.append(f"SUI Postgres contention did not settle every round: {relative}")
        if "SUI-TEI-postgres-concurrency" in relative:
            observed = data.get("observed", {})
            if observed.get("winners") != 1 or observed.get("conflicts") != 1:
                errors.append(f"SUI Postgres concurrency check did not settle on one winner: {relative}")
        if "SUI-TEI-postgres-etag" in relative:
            observed = data.get("observed", {})
            if observed.get("staleStatus") != 409 or observed.get("matchingStatus") != 200:
                errors.append(f"SUI Postgres ETag check did not enforce preconditions: {relative}")
        if "SUI-TEI-postgres-migrate" in relative:
            observed = data.get("observed", {})
            if observed.get("roundTrip") is not True or observed.get("migration") != "alembic upgrade head":
                errors.append(f"SUI Postgres migration run did not persist through alembic: {relative}")
        if "SUI-TEI-postgres" in relative and "etag" not in relative and "migrate" not in relative and "concurrency" not in relative and "contention" not in relative and "retry" not in relative and "tls" not in relative:
            observed = data.get("observed", {})
            expected = "PASS" if observed.get("roundTrip") is True else "FAIL"
            if data.get("result") != expected:
                errors.append(f"SUI Postgres receipt result does not match roundTrip: {relative}")
        if "SUI-TEI-postgres-retry-evidence" in relative:
            observed = data.get("observed", {})
            if observed.get("retries", 0) < 1 or data.get("result") != "PASS":
                errors.append(f"SUI Postgres retry evidence did not record a recovered retry: {relative}")
        if "SUI-TEI-postgres-retry" in relative:
            rounds = data.get("observed", {}).get("rounds", [])
            terminal = all(all(status in (200, 409) for status in item.get("statuses", [])) for item in rounds)
            if data.get("result") != "PASS" or not terminal:
                errors.append(f"SUI Postgres retry run left a transient status: {relative}")
        if "SUI-TEI-postgres-contention" in relative:
            rounds = data.get("observed", {}).get("rounds", [])
            settled = bool(rounds) and all(
                sum(1 for status in item.get("statuses", []) if status == 200) == 1 for item in rounds
            )
            if data.get("result") != "PASS" or not settled:
                errors.append(f"SUI Postgres contention did not settle every round: {relative}")
        if "SUI-TEI-postgres-concurrency" in relative:
            observed = data.get("observed", {})
            if observed.get("winners") != 1 or observed.get("conflicts") != 1:
                errors.append(f"SUI Postgres concurrency check did not settle on one winner: {relative}")
        if "SUI-TEI-postgres-etag" in relative:
            observed = data.get("observed", {})
            if observed.get("staleStatus") != 409 or observed.get("matchingStatus") != 200:
                errors.append(f"SUI Postgres ETag check did not enforce preconditions: {relative}")
        if "SUI-TEI-postgres-migrate" in relative:
            observed = data.get("observed", {})
            if observed.get("roundTrip") is not True or observed.get("migration") != "alembic upgrade head":
                errors.append(f"SUI Postgres migration run did not persist through alembic: {relative}")
        if "SUI-TEI-postgres" in relative and "etag" not in relative and "migrate" not in relative and "concurrency" not in relative and "contention" not in relative and "retry" not in relative and "tls" not in relative:
            observed = data.get("observed", {})
            if observed.get("roundTrip") is not True or observed.get("documentRows") != 1:
                errors.append(f"SUI Postgres save did not persist one document: {relative}")
        if "SUI-TEI-tls" in relative:
            observed = data.get("observed", {})
            if observed.get("tls") is not True or observed.get("authenticatedStatus") != 200:
                errors.append(f"SUI TLS check did not succeed: {relative}")
        if "TEI-suite-2026" in relative:
            steps = data.get("steps", {})
            if data.get("result") != "PASS" or any(step.get("returncode") != 0 for step in steps.values()):
                errors.append(f"TEI suite did not pass every step: {relative}")
        if "SCN-003-save" in relative:
            observed = data.get("observed", {})
            if observed.get("roundTrip") is not True or observed.get("cards") != 5:
                errors.append(f"SCN-003 save did not round trip three cards: {relative}")
        if "SCN-003-compose" in relative:
            observed = data.get("observed", {})
            if observed.get("valid") is not True:
                errors.append(f"SCN-003 compose did not validate: {relative}")
        if "SCN-003-artifact-links" in relative:
            observed = data.get("observed", {})
            if observed.get("allFound") is not True or observed.get("count") != 4:
                errors.append(f"SCN-003 artifact links were not all found: {relative}")
        if "artifacts-determinism" in relative:
            observed = data.get("observed", {})
            if observed.get("allIdentical") is not True or observed.get("count") != 3:
                errors.append(f"artifact determinism check did not confirm three artifacts: {relative}")
        if "SUI-session-tests" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("failed") != 0 or observed.get("passed", 0) < 1:
                errors.append(f"SUI session test subset did not pass: {relative}")
        if "SUI-auth-flow-tests" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("failed") != 0 or observed.get("passed", 0) < 1:
                errors.append(f"SUI auth flow tests did not pass: {relative}")
        if "SUI-docs-tests" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("failed") != 0 or observed.get("passed", 0) < 1:
                errors.append(f"SUI docs test subset did not pass: {relative}")
        if "SUI-saas-tests" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("failed") != 0 or observed.get("passed", 0) < 1:
                errors.append(f"SUI SaaS test subset did not pass: {relative}")
        if "SUI-saas-identity" in relative:
            checks = data.get("observed", {}).get("checks", {})
            if data.get("result") != "PASS" or not checks or not all(checks.values()):
                errors.append(f"SUI broker identity checks did not all pass: {relative}")
        if "SUI-saas-callback-contract" in relative:
            checks = data.get("observed", {}).get("checks", {})
            if data.get("result") != "PASS" or not checks or not all(checks.values()):
                errors.append(f"SUI callback rejection checks did not all pass: {relative}")
        if "SUI-saas-login-contract" in relative:
            checks = data.get("observed", {}).get("checks", {})
            if data.get("result") != "PASS" or not checks or not all(checks.values()):
                errors.append(f"SUI login initiation contract checks did not all pass: {relative}")
        if "SUI-saas-oauth-contract" in relative:
            checks = data.get("observed", {}).get("checks", {})
            if data.get("result") != "PASS" or not checks or not all(checks.values()):
                errors.append(f"SUI OAuth broker contract checks did not all pass: {relative}")
        if "SUI-saas-adapter-contract" in relative:
            checks = data.get("observed", {}).get("checks", {})
            if data.get("result") != "PASS" or not checks or not all(checks.values()):
                errors.append(f"SUI SaaS adapter contract checks did not all pass: {relative}")
        if "TEI-artifact-digests" in relative:
            observed = data.get("observed", {})
            if observed.get("allMatch") is not True or observed.get("count") != 4:
                errors.append(f"artifact contract digests did not all match: {relative}")
        if "TEI-records" in relative:
            observed = data.get("observed", {})
            if observed.get("allValid") is not True or observed.get("count") != 4:
                errors.append(f"product record conversions did not all validate: {relative}")
        if "EKI-TEI-multi-worker" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or len(observed.get("workers", [])) != 2 or observed.get("executed", 0) < 1:
                errors.append(f"EKI multi-worker evidence did not hold: {relative}")
        if "EKI-TEI-revoked-agent" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("executed") is not False or observed.get("refusedStatus") not in (401, 403):
                errors.append(f"EKI refused-agent evidence did not hold: {relative}")
        if "EKI-TEI-worker-revoke" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("eventualState") is not True or observed.get("reregisterRefused") is not True:
                errors.append(f"EKI worker revocation evidence did not hold: {relative}")
        if "EKI-TEI-manual-execution" in relative:
            observed = data.get("observed", {})
            body = observed.get("resultBody") or {}
            if data.get("result") != "PASS" or observed.get("executed") is not True or observed.get("claimed") is not True or not observed.get("taskId"):
                errors.append(f"EKI manual execution evidence did not hold: {relative}")
            elif observed.get("resultStatus") != 409 or body.get("code") != "RESULT_NOT_READY":
                errors.append(f"EKI result acceptance changed; update the finding: {relative}")
        if "EKI-TEI-policy-execution" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("projectedSubmissionRejected") is not False or not observed.get("claimDigest"):
                errors.append(f"EKI policy-aligned execution evidence did not hold: {relative}")
        if "EKI-TEI-projection-execution" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or not observed.get("taskId") or not observed.get("claimDigest"):
                errors.append(f"EKI projection execution evidence did not hold: {relative}")
        if "EKI-TEI-http-execution" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("executed") is not True or observed.get("claimDigest") != observed.get("acceptedResultDigest"):
                errors.append(f"EKI execution evidence did not hold: {relative}")
        if "EKI-TEI-dispatch-running" in relative:
            observed = data.get("observed", {})
            if observed.get("taskStatus") != "running" or observed.get("taskExecuted") is not False:
                errors.append(f"EKI task did not reach running without executing: {relative}")
        if "EKI-TEI-submit" in relative:
            observed = data.get("observed", {})
            if observed.get("submitStatus") != 202 or observed.get("taskStatus") != "queued":
                errors.append(f"EKI did not accept the projected TaskRequest: {relative}")
        if "SEI-TEI-mcp-check" in relative:
            checks = data.get("observed", {}).get("checks", {})
            if data.get("result") != "PASS" or not checks or not all(checks.values()):
                errors.append(f"SEI MCP check_decision allow/deny pair did not hold: {relative}")
        if "SEI-TEI-mcp" in relative and "mcp-check" not in relative:
            observed = data.get("observed", {})
            checks = observed.get("checks", {})
            if data.get("result") != "PASS" or not checks or not all(checks.values()) or observed.get("tools") != ["resume", "add_recommendation", "check_decision"]:
                errors.append(f"SEI MCP probe did not expose the expected tools: {relative}")
        if "SEI-TEI-resume" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("humanViewHasNoRawBidi") is not True:
                errors.append(f"SEI resume view leaked a raw bidi control: {relative}")
        if "SEI-TEI-doctor" in relative:
            observed = data.get("observed", {})
            lock = observed.get("withStaleLock", {}).get("lines", {}).get("lock", {})
            if data.get("result") != "PASS" or lock.get("status") != "warn":
                errors.append(f"SEI doctor lock handling changed: {relative}")
        if "SEI-TEI-gate-variants" in relative:
            checks = data.get("observed", {}).get("checks", {})
            if data.get("result") != "PASS" or not checks or not all(checks.values()):
                errors.append(f"SEI gate variant checks did not all pass: {relative}")
        if "SEI-TEI-gate" in relative and "gate-variants" not in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("allowVerdict") != "allow" or observed.get("denyVerdict") != "deny":
                errors.append(f"SEI gate allow/deny pair did not hold: {relative}")
        if "SEI-TEI-cli" in relative:
            checks = data.get("observed", {}).get("checks", {})
            if data.get("result") != "PASS" or not checks or not all(checks.values()):
                errors.append(f"SEI CLI recording did not pass: {relative}")
        if "EKI-TEI-record" in relative:
            observed = data.get("observed", {})
            if observed.get("valid") is not True:
                errors.append(f"EKI task-request record did not validate: {relative}")
        if "EKI-TEI-consumer" in relative:
            observed = data.get("observed", {})
            if observed.get("passed") != 4 or observed.get("callsControl") is not False:
                errors.append(f"EKI consumer receipt did not record four non-calling tests: {relative}")
        if "MMI-TEI-record" in relative:
            observed = data.get("observed", {})
            if observed.get("valid") is not True:
                errors.append(f"MMI format-profile record did not validate: {relative}")
        if "MMI-TEI-real-artifact" in relative:
            observed = data.get("observed", {})
            if observed.get("passed") != 5 or observed.get("profileId") != "profile-a":
                errors.append(f"MMI real artifact receipt did not parse profile-a: {relative}")
        if "MMI-TEI-consumer" in relative:
            observed = data.get("observed", {})
            if observed.get("passed") != 5 or observed.get("writes") is not False:
                errors.append(f"MMI consumer receipt did not record four non-writing tests: {relative}")
        if "SEI-TEI-record" in relative:
            observed = data.get("observed", {})
            if observed.get("valid") is not True or observed.get("refId") != "decision-1":
                errors.append(f"SEI decision-memory record did not validate: {relative}")
        if "SEI-TEI-real-artifact" in relative:
            observed = data.get("observed", {})
            if observed.get("passed") is not True or observed.get("refId") != "decision-1":
                errors.append(f"SEI real artifact receipt did not parse decision-1: {relative}")
        if "SEI-TEI-consumer" in relative:
            observed = data.get("observed", {})
            if observed.get("passed") != 3 or observed.get("writes") is not False:
                errors.append(f"SEI consumer receipt did not record three non-writing tests: {relative}")
        if "EKI-TEI-artifact" in relative:
            observed = data.get("observed", {})
            if observed.get("taskRequestValid") is not True:
                errors.append(f"EKI artifact did not validate: {relative}")
        if "EKI-TEI-task-request-selection" in relative:
            observed = data.get("observed", {})
            if observed.get("passed") is not True:
                errors.append(f"EKI task request selection did not pass: {relative}")
        if "artifacts-crosscheck" in relative:
            observed = data.get("observed", {})
            if observed.get("allValid") is not True or observed.get("count") != 4:
                errors.append(f"TEI artifacts crosscheck did not validate three artifacts: {relative}")
        if "SUI-TEI-reference-multi" in relative:
            checks = data.get("observed", {})
            if data.get("result") != "PASS" or checks.get("firstStatus") != 200 or checks.get("secondStatus") != 200 or checks.get("firstNotSei") is not True:
                errors.append(f"SUI did not isolate two TEI artifacts: {relative}")
        if "SUI-TEI-reference" in relative and "-multi" not in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("projectionStatus") != 200 or observed.get("artifactEchoed") is not True:
                errors.append(f"SUI did not serve the bound TEI artifact: {relative}")
        if "SUI-TEI-provision" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("createStatus") != 201 or observed.get("auditEvents", 0) < 1:
                errors.append(f"SUI provision check did not hold: {relative}")
        if "SUI-TEI-parsers" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("visibility", {}).get("caseMismatch") is not None:
                errors.append(f"SUI visibility parsing became case-insensitive: {relative}")
        if "SUI-TEI-failsafe" in relative:
            cases = data.get("observed", {}).get("cases", {})
            if data.get("result") != "PASS" or cases.get("safeModeExport", {}).get("reason") != "safe_mode":
                errors.append(f"SUI local fail-safe ladder changed: {relative}")
        if "SUI-TEI-builders" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("unknownAdapterFallsBackToNoop") is not True:
                errors.append(f"SUI policy component fallbacks changed: {relative}")
        if "SUI-TEI-policy-requirements" in relative:
            cases = data.get("observed", {}).get("cases", {})
            broken = cases.get("allTenBroken", {}).get("reason", "")
            if data.get("result") != "PASS" or broken.count(", ") < 8:
                errors.append(f"SUI SaaS policy requirement list changed: {relative}")
        if "SUI-TEI-preflight" in relative:
            observed = data.get("observed", {}).get("results", {})
            if data.get("result") != "PASS" or observed.get("withAdapters:local-dev", {}).get("outcome") != "refused":
                errors.append(f"SUI trusted runtime preflight rule changed: {relative}")
        if "SUI-TEI-migrations" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("singleHead") is not True:
                errors.append(f"SUI migration heads are not linear: {relative}")
        if "SUI-TEI-card-move" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("noOp", {}).get("outcome") != "refused":
                errors.append(f"SUI card-move domain changed: {relative}")
        if "SUI-TEI-headers" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("readHeaders", {}).get("nosniff") != "nosniff":
                errors.append(f"SUI security headers missing: {relative}")
        if "SUI-TEI-auth-assurance" in relative:
            cases = data.get("observed", {}).get("cases", {})
            if data.get("result") != "PASS" or cases.get("aalLowWinsOverAcrHigh", {}).get("assuranceLevel") != "low":
                errors.append(f"SUI auth assurance precedence changed: {relative}")
        if "SUI-TEI-probes" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("healthzBody") != {"status": "ok"}:
                errors.append(f"SUI probe endpoints changed: {relative}")
        if "SUI-TEI-profile-policy" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("sessionRequiredProfiles") != ["saas-multitenant"]:
                errors.append(f"SUI profile policy table changed: {relative}")
        if "SUI-TEI-dedup-window" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("immediateSent") is not False:
                errors.append(f"SUI audit dedup window did not suppress an immediate repeat: {relative}")
        if "SUI-TEI-saas-precondition" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("updateMissing") != [428, "document_precondition_required"]:
                errors.append(f"SUI SaaS precondition helper did not demand If-Match: {relative}")
        if "SUI-TEI-agent-key-wiring" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("agentRequestStatus") != 503:
                errors.append(f"SUI agent key wiring probe did not observe the local-dev 503: {relative}")
        if "SUI-TEI-agent-read-path" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("writeAttemptStatus") != 403:
                errors.append(f"SUI agent read path did not refuse a write: {relative}")
        if "SUI-TEI-list-pagination" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("allSeenOnce") is not True:
                errors.append(f"SUI document list pagination missed or repeated a document: {relative}")
        if "SUI-TEI-native-action" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("disabledStatus") != 404:
                errors.append(f"SUI native action was not disabled by default: {relative}")
        if "SUI-TEI-export-dedup" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("repeatSuppressed") is not True:
                errors.append(f"SUI export audit dedup did not suppress a repeat: {relative}")
        if "SUI-TEI-similar-candidates" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("mergedCardExcluded") is not True:
                errors.append(f"SUI similar candidates included an ineligible card: {relative}")
        if "SUI-TEI-polygon-handoff" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("paddingDecision") != "rollback_required":
                errors.append(f"SUI polygon handoff did not require rollback: {relative}")
        if "SUI-TEI-ce4-audit-order" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("applyBeforeAnyEventStatus") != 409:
                errors.append(f"SUI CE4 audit order did not refuse an early apply: {relative}")
        if "SUI-TEI-merge-decision-log" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("duplicateStatus") != 409:
                errors.append(f"SUI merge decision log accepted a duplicate: {relative}")
        if "SUI-TEI-archive-lifecycle" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("writeArchivedStatus") != 423:
                errors.append(f"SUI archive gate did not refuse the write: {relative}")
        if "SUI-TEI-etag-stability" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("etagStableAcrossReads") is not True:
                errors.append(f"SUI document ETag was not stable: {relative}")
            if observed.get("etagChangedAfterSave") is not True:
                errors.append(f"SUI document ETag did not change after a save: {relative}")
        if "SUI-TEI-audit-pagination" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("noOverlap") is not True or observed.get("hasCursor") is not True:
                errors.append(f"SUI admin audit pagination did not hold: {relative}")
        if "SUI-TEI-agent-credential-admin" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("anonymousStatus") not in (401, 403):
                errors.append(f"SUI agent credential admin did not refuse anonymous callers: {relative}")
        if "SUI-TEI-agent-guard" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("guardRaised") is not True or observed.get("auditExportedClearsGuard") is not True:
                errors.append(f"SUI agent credential guard did not hold: {relative}")
        if "SUI-TEI-registry" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("listStatus") != 200 or observed.get("createStatus") != 201:
                errors.append(f"SUI model registry did not hold: {relative}")
        if "SUI-TEI-ce4" in relative and "-audit-order" not in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("dryStatus") != 200 or observed.get("hasBundleHash") is not True:
                errors.append(f"SUI CE4 resolve did not hold: {relative}")
        if "SUI-TEI-context-bundle" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("firstStatus") != 200 or observed.get("deterministic") is not True:
                errors.append(f"SUI context bundle did not hold: {relative}")
        if "SUI-TEI-context" in relative and "-bundle" not in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("acceptedStatus") != 200 or observed.get("previewStatus") != 422:
                errors.append(f"SUI context query contract did not hold: {relative}")
        if "SUI-TEI-admin" in relative and "admin-path" not in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("adminStatus") != 200 or observed.get("anonymousStatus") not in (401, 403) or observed.get("businessKeyStatus") not in (401, 403):
                errors.append(f"SUI admin plane check did not hold: {relative}")
        if "SUI-TEI-audit" in relative and "-pagination" not in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("eventCount", 0) < 1 or observed.get("viewStatus") != 200:
                errors.append(f"SUI audit export did not deliver an event: {relative}")
        if "MMI-delivery-audit" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("exitCode") != 1 or observed.get("referentialCompleteness") != "empty":
                errors.append(f"MMI delivery audit observation changed: {relative}")
        if "MMI-inventory" in relative:
            checks = data.get("observed", {}).get("checks", {})
            if data.get("result") != "PASS" or not checks or not all(checks.values()):
                errors.append(f"MMI inventory checks did not all pass: {relative}")
        if "MMI-inspect" in relative:
            checks = data.get("observed", {}).get("checks", {})
            if data.get("result") != "PASS" or not checks or not all(checks.values()):
                errors.append(f"MMI inspect contract checks did not all pass: {relative}")
        if "MMI-TEI-profile" in relative:
            observed = data.get("observed", {})
            if data.get("result") != "PASS" or observed.get("accepted") is not True:
                errors.append(f"MMI did not accept the projected format profile: {relative}")
        if "MMI-TEI-artifact" in relative:
            observed = data.get("observed", {})
            if observed.get("profileValid") is not True:
                errors.append(f"MMI artifact did not validate: {relative}")
        if "MMI-TEI-format-profile-selection" in relative:
            observed = data.get("observed", {})
            if observed.get("passed") is not True:
                errors.append(f"MMI format profile selection did not pass: {relative}")
        if "SEI-TEI-artifact" in relative:
            observed = data.get("observed", {})
            if observed.get("decisionValid") is not True:
                errors.append(f"SEI artifact did not validate: {relative}")
        if "artifact-schema" in relative:
            observed = data.get("observed", {})
            if observed.get("valid") is not True:
                errors.append(f"TEI artifact schema check did not validate: {relative}")
        if "SEI-TEI-decision-selection" in relative:
            observed = data.get("observed", {})
            if observed.get("passed") is not True:
                errors.append(f"SEI decision selection did not pass: {relative}")
        if "tei-pipeline-save" in relative:
            steps = data.get("steps", {})
            if data.get("result") != "PASS" or steps.get("save", {}).get("roundTrip") is not True:
                errors.append(f"TEI pipeline save did not pass with a round trip: {relative}")
        if "SUI-TEI-compat" in relative:
            steps = data.get("steps", {})
            if data.get("result") != "PASS" or steps.get("flow", {}).get("casesPassed") != 21:
                errors.append(f"SUI pipeline did not pass against the newer TEI: {relative}")
        if "tei-pipeline-run" in relative:
            steps = data.get("steps", {})
            if data.get("result") != "PASS" or steps.get("flow", {}).get("casesPassed") != 21:
                errors.append(f"TEI pilot run did not pass all steps: {relative}")
        if "tei-contract-digest-check" in relative:
            observed = data.get("observed", {})
            if observed.get("allMatch") is not True:
                errors.append(f"TEI contract digest check found a mismatch: {relative}")
        if "tei-contract-versions-validation" in relative:
            observed = data.get("observed", {})
            if observed.get("documentV1Valid") is not True:
                errors.append(f"TEI contract versions validation did not validate DocumentV1: {relative}")
        elif "tei-contract-versions" in relative:
            contracts = data.get("contracts", {})
            if not contracts or not all(item.get("contractVersion") for item in contracts.values()):
                errors.append(f"TEI contract versions receipt is missing contract versions: {relative}")
        if "tei-fields-roundtrip" in relative:
            observed = data.get("observed", {})
            checks = observed.get("roundTripChecks", {})
            if observed.get("roundTrip") is not True or not checks or not all(checks.values()):
                errors.append(f"TEI fields roundtrip receipt has failing checks: {relative}")
        if "tei-reading-order-validation" in relative:
            observed = data.get("observed", {})
            if observed.get("documentV1Valid") is not True:
                errors.append(f"TEI reading order validation did not validate DocumentV1: {relative}")
        elif "tei-reading-order" in relative:
            if data.get("result") != "PASS":
                errors.append(f"TEI reading order receipt did not pass: {relative}")
        if "tei-sources-validation" in relative:
            observed = data.get("observed", {})
            if observed.get("documentV1Valid") is not True:
                errors.append(f"TEI sources validation did not validate DocumentV1: {relative}")
        elif "tei-sources" in relative:
            if data.get("result") != "PASS":
                errors.append(f"TEI sources receipt did not pass: {relative}")
        if "tei-sui-server" in relative:
            observed = data.get("observed", {})
            if observed.get("serverReady") is not True or observed.get("anonymousStatus") != 401:
                errors.append(f"TEI server receipt did not record readiness and 401: {relative}")
            if observed.get("transport") != "uvicorn on 127.0.0.1":
                errors.append(f"TEI server receipt must disclose the transport: {relative}")
        if "tei-save-roundtrip" in relative:
            observed = data.get("observed", {})
            if observed.get("roundTrip") is not True:
                errors.append(f"TEI roundtrip receipt did not record a matching round trip: {relative}")
            checks = observed.get("roundTripChecks", {})
            if not checks or not all(checks.values()):
                errors.append(f"TEI roundtrip receipt has failing checks: {relative}")
        if "tei-save-auth" in relative:
            observed = data.get("observed", {})
            if observed.get("unauthorizedStatus") != 401 or observed.get("finalReadStatus") != 200:
                errors.append(f"TEI save auth receipt did not record 401 then 200: {relative}")
            if observed.get("apiKey") != "configured":
                errors.append(f"TEI save auth receipt must disclose the configured key: {relative}")
        if "tei-save-e2e" in relative:
            observed = data.get("observed", {})
            if observed.get("writes") is not True or observed.get("finalReadStatus") != 200:
                errors.append(f"TEI save e2e receipt did not record a successful write: {relative}")
            if observed.get("database") != "temporary SQLite":
                errors.append(f"TEI save e2e receipt must disclose the temporary database: {relative}")
        if "tei-save-contract" in relative:
            observed = data.get("observed", {})
            if observed.get("contractValid") is not True or observed.get("writes") is not False or observed.get("existingValidated") is not True:
                errors.append(f"TEI save contract receipt did not validate the payload: {relative}")
        if "tei-save-plan-cli" in relative:
            observed = data.get("observed", {})
            if observed.get("writes") is not False or observed.get("action") != "update":
                errors.append(f"TEI save plan CLI receipt did not record a non-writing update: {relative}")
        if "tei-sui-save-plan-merge" in relative:
            observed = data.get("observed", {})
            if observed.get("passed") != 6 or observed.get("writes") is not False:
                errors.append(f"TEI save plan merge receipt did not record six non-writing tests: {relative}")
        if "tei-sui-save-merge" in relative:
            observed = data.get("observed", {})
            if observed.get("passed") != 5 or observed.get("writes") is not False:
                errors.append(f"TEI save merge receipt did not record five non-writing tests: {relative}")
        if "tei-large-doc" in relative:
            observed = data.get("observed", {})
            if data.get("synthetic") is not True or observed.get("savedCards") != 300:
                errors.append(f"TEI large-doc synthetic receipt is mislabeled or incomplete: {relative}")
        if "tei-sui-etag" in relative:
            observed = data.get("observed", {})
            if observed.get("staleIfMatchStatus") != 409 or observed.get("matchingIfMatchStatus") != 200:
                errors.append(f"TEI ETag receipt did not record 409/200: {relative}")
        if "tei-multi-doc" in relative:
            observed = data.get("observed", {})
            if observed.get("documents") != 10 or observed.get("isolatedIds") is not True:
                errors.append(f"TEI multi-doc receipt did not record ten isolated documents: {relative}")
        if "tei-sui-save-plan" in relative:
            observed = data.get("observed", {})
            if observed.get("passed") != 5 or observed.get("writes") is not False:
                errors.append(f"TEI save plan receipt did not record four non-writing tests: {relative}")
        if "documentv1-validation" in relative:
            observed = data.get("observed", {})
            if observed.get("documentV1Valid") is not True or observed.get("cards") != 2:
                errors.append(f"DocumentV1 validation receipt did not validate two cards: {relative}")
        if "tei-tenant-route" in relative:
            observed = data.get("observed", {})
            if observed.get("boundArtifactStatus") != 200 or observed.get("agentCredentialStatus") != 403:
                errors.append(f"TEI tenant route receipt did not record 200/403: {relative}")
            if observed.get("authorizationStubbed") is not True:
                errors.append(f"TEI tenant route receipt did not disclose the authorization stub: {relative}")
        if "tei-auth" in relative:
            observed = data.get("observed", {})
            if observed.get("authorizedStatus") != 200 or observed.get("anonymousStatus") != 401:
                errors.append(f"TEI auth receipt did not record 200/401: {relative}")
            if observed.get("authEnabled") is not True:
                errors.append(f"TEI auth receipt did not enable authorization: {relative}")
        if "tei-http-route" in relative:
            observed = data.get("observed", {})
            if observed.get("passed") != 2 or observed.get("status") != 200:
                errors.append(f"TEI HTTP route receipt did not pass two requests: {relative}")
            if observed.get("authOverridden") is not True:
                errors.append(f"TEI HTTP route receipt did not disclose the auth override: {relative}")
        if "tei-adapter" in relative:
            observed = data.get("observed", {})
            if observed.get("passed") != 9 or observed.get("savesAnything") is not False:
                errors.append(f"TEI adapter receipt did not record nine non-saving tests: {relative}")
        if "tei-consumer" in relative:
            observed = data.get("observed", {})
            if observed.get("passed") != 6 or observed.get("readOnly") is not True:
                errors.append(f"TEI consumer receipt did not record six read-only tests: {relative}")
        if "tei-admin-path" in relative:
            if data.get("adminPathOk") is not True or data.get("readOk") is not True:
                errors.append(f"TEI admin path receipt did not read the artifact: {relative}")
        if "tei-binding" in relative:
            if data.get("bindingResolved") is not True or data.get("readOk") is not True:
                errors.append(f"TEI binding receipt did not resolve and read: {relative}")
        if "tei-sui-reader" in relative:
            if data.get("readOk") is not True or data.get("tenantIsolationRejected") is not True:
                errors.append(f"TEI SUI reader receipt did not read and isolate: {relative}")
        if "tei-artifact-validation" in relative:
            if data.get("passed") is not True or data.get("errors"):
                errors.append(f"TEI artifact validation receipt did not pass: {relative}")
        if "tei-artifact" in relative:
            artifact = data.get("artifact") or {}
            if artifact.get("schema") != "tai.reference.tei-documentv1-projection/v0":
                errors.append(f"TEI artifact receipt has no projection schema: {relative}")
            else:
                artifact_path = root / artifact["path"]
                if not artifact_path.is_file():
                    errors.append(f"TEI artifact receipt points at a missing file: {relative}")
                elif hashlib.sha256(artifact_path.read_bytes()).hexdigest() != artifact["digest"].removeprefix("sha256:"):
                    errors.append(f"TEI artifact digest does not match the file: {relative}")
        if "tei-integration-flow" in relative:
            if data.get("casesPassed") != data.get("casesRun"):
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
        status = _read_json(status_path, REVIEW_STATUS, errors)
        if status is None:
            status = {}
        rows = status.get("items")
        if not isinstance(rows, list):
            errors.append(f"review items must be an array: {REVIEW_STATUS}")
            rows = []
        items: dict[str, dict[str, Any]] = {}
        for index, item in enumerate(rows):
            if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
                errors.append(f"invalid review item at index {index}: {REVIEW_STATUS}")
                continue
            if item["id"] in items:
                errors.append(f"duplicate review item: {item['id']}")
                continue
            items[item["id"]] = item
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
                continue
            if item.get("evidence") not in (None, ""):
                errors.append(f"{item_id} declares evidence despite evidenceKind=none")
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
