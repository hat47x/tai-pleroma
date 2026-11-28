"""Check whether a receipt's file-name date matches the `date` field inside it.

A receipt is named `<name>-YYYY-MM-DD.json`. The `date` field inside is supposed to be the
day the run happened. If the two differ, the file name points at one version and the body
at another, and a reader who cites the file name cites a date the receipt does not claim.

This measures the mismatch across all receipts and reports how many are affected, so the
size of the repair is known before any file is renamed.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

# The 141 receipts whose file-name date differs from their `date` field, recorded by
# name. A new name here means a new mismatch was introduced; that is the failure.
BASELINE_MISMATCHES = frozenset((
    # Measured 2026-11-28. A name is the unit, not a count, so fixing one entry
    # cannot quietly hide a different regression.
    "EKI-TEI-budget-aligned-artifact-2026-11-03.json",
    "EKI-TEI-manual-execution-2026-11-03.json",
    "EKI-TEI-multi-worker-2026-11-03.json",
    "EKI-TEI-policy-execution-2026-11-03.json",
    "EKI-TEI-projection-execution-2026-11-03.json",
    "EKI-TEI-revoked-agent-2026-11-03.json",
    "EKI-TEI-submit-2026-11-03.json",
    "EKI-TEI-worker-revoke-2026-11-03.json",
    "MMI-TEI-profile-2026-11-03.json",
    "MMI-delivery-audit-2026-11-03.json",
    "MMI-inspect-2026-11-03.json",
    "MMI-inventory-2026-11-03.json",
    "SCN-003-artifact-links-2026-11-03.json",
    "SCN-003-compose-2026-11-03.json",
    "SCN-003-compose-2026-11-03.validate.json",
    "SEI-TEI-cli-2026-11-03.json",
    "SEI-TEI-doctor-2026-11-06.json",
    "SEI-TEI-gate-2026-11-03.json",
    "SEI-TEI-gate-variants-2026-11-03.json",
    "SEI-TEI-mcp-2026-11-03.json",
    "SEI-TEI-mcp-check-2026-11-03.json",
    "SEI-TEI-resume-2026-11-06.json",
    "SUI-TEI-admin-2026-11-03.json",
    "SUI-TEI-agent-credential-admin-2026-11-06.json",
    "SUI-TEI-agent-guard-2026-11-06.json",
    "SUI-TEI-agent-key-wiring-2026-11-06.json",
    "SUI-TEI-agent-read-path-2026-11-06.json",
    "SUI-TEI-archive-lifecycle-2026-11-06.json",
    "SUI-TEI-assembler-kinds-2026-11-06.json",
    "SUI-TEI-assembler-tests-2026-11-06.json",
    "SUI-TEI-audit-2026-11-03.json",
    "SUI-TEI-audit-pagination-2026-11-06.json",
    "SUI-TEI-auth-assurance-2026-11-06.json",
    "SUI-TEI-builders-2026-11-06.json",
    "SUI-TEI-ca-chain-2026-11-03.json",
    "SUI-TEI-card-move-2026-11-06.json",
    "SUI-TEI-ce4-2026-11-03.json",
    "SUI-TEI-ce4-audit-order-2026-11-06.json",
    "SUI-TEI-context-2026-11-03.json",
    "SUI-TEI-context-bundle-2026-11-03.json",
    "SUI-TEI-dedup-window-2026-11-06.json",
    "SUI-TEI-document-coverage-2026-11-06.json",
    "SUI-TEI-document-types-2026-11-06.json",
    "SUI-TEI-edge-chain-2026-11-06.json",
    "SUI-TEI-edge-optional-contract-2026-11-06.json",
    "SUI-TEI-edge-optionality-2026-11-06.json",
    "SUI-TEI-etag-stability-2026-11-06.json",
    "SUI-TEI-export-dedup-2026-11-06.json",
    "SUI-TEI-failsafe-2026-11-06.json",
    "SUI-TEI-headers-2026-11-06.json",
    "SUI-TEI-integration-flow-2026-11-02.json",
    "SUI-TEI-list-pagination-2026-11-06.json",
    "SUI-TEI-merge-decision-log-2026-11-06.json",
    "SUI-TEI-migrations-2026-11-06.json",
    "SUI-TEI-multi-instance-2026-11-03.json",
    "SUI-TEI-native-action-2026-11-06.json",
    "SUI-TEI-parsers-2026-11-06.json",
    "SUI-TEI-policy-requirements-2026-11-06.json",
    "SUI-TEI-polygon-handoff-2026-11-06.json",
    "SUI-TEI-postgres-2026-11-03.json",
    "SUI-TEI-postgres-concurrency-2026-11-03.json",
    "SUI-TEI-postgres-contention-2026-11-03.json",
    "SUI-TEI-postgres-etag-2026-11-03.json",
    "SUI-TEI-postgres-migrate-2026-11-03.json",
    "SUI-TEI-postgres-multidoc-2026-11-03.json",
    "SUI-TEI-postgres-retry-2026-11-03.json",
    "SUI-TEI-postgres-tls-2026-11-03.json",
    "SUI-TEI-preflight-2026-11-06.json",
    "SUI-TEI-probes-2026-11-06.json",
    "SUI-TEI-profile-policy-2026-11-06.json",
    "SUI-TEI-provision-2026-11-03.json",
    "SUI-TEI-proxy-2026-11-03.json",
    "SUI-TEI-reference-2026-11-03.json",
    "SUI-TEI-reference-multi-2026-11-03.json",
    "SUI-TEI-registry-2026-11-03.json",
    "SUI-TEI-saas-precondition-2026-11-06.json",
    "SUI-TEI-similar-candidates-2026-11-06.json",
    "SUI-TEI-tls-2026-11-03.json",
    "SUI-auth-flow-tests-2026-11-03.json",
    "SUI-consumer-mapping-2026-11-06.json",
    "SUI-docs-tests-2026-11-03.json",
    "SUI-readonly-enforcement-2026-11-06.json",
    "SUI-saas-adapter-contract-2026-11-03.json",
    "SUI-saas-callback-contract-2026-11-03.json",
    "SUI-saas-identity-2026-11-03.json",
    "SUI-saas-login-contract-2026-11-03.json",
    "SUI-saas-oauth-contract-2026-11-03.json",
    "SUI-saas-tests-2026-11-03.json",
    "SUI-session-tests-2026-11-03.json",
    "TAI-TEI-capability-reference-2026-11-11.json",
    "TEI-artifact-digests-2026-11-03.json",
    "TEI-artifacts-crosscheck-2026-11-03.json",
    "TEI-conclusion-integrity-2026-11-06.json",
    "TEI-decimal-fidelity-2026-11-06.json",
    "TEI-decode-divergence-2026-11-06.json",
    "TEI-fixture-coverage-2026-11-06.json",
    "TEI-independent-oracle-2026-11-06.json",
    "TEI-many-primitive-2026-11-06.json",
    "TEI-meaning-change-2026-11-06.json",
    "TEI-meaning-change-required-2026-11-06.json",
    "TEI-meaning-change-requiredness-2026-11-06.json",
    "TEI-nesting-2026-11-06.json",
    "TEI-optional-flag-2026-11-06.json",
    "TEI-projection-strategy-2026-11-06.json",
    "TEI-receipt-consistency-2026-11-06.json",
    "TEI-receipt-scope-2026-11-06.json",
    "TEI-records-2026-11-03.json",
    "TEI-result-exit-parity-2026-11-06.json",
    "TEI-suite-2026-11-03.json",
    "TEI-suite-pipeline-2026-11-03.json",
    "TEI-target-profile-compare-2026-11-06.json",
    "TEI-target-profile-compare-text-2026-11-06.json",
    "YI-artifact-digest-2026-11-11.json",
    "YI-cross-receipt-2026-11-11.json",
    "YI-doc-integrity-2026-11-11.json",
    "YI-pass-consistency-2026-11-11.json",
    "YI-receipt-auditability-2026-11-11.json",
    "YI-receipt-quality-2026-11-11.json",
    "YI-scope-halves-2026-11-11.json",
    "YIC-analysis-gates-2026-11-18.json",
    "YIC-audience-declaration-2026-11-17.json",
    "YIC-authority-limits-2026-11-16.json",
    "YIC-dead-rule-fields-2026-11-18.json",
    "YIC-dead-rule-impact-2026-11-18.json",
    "YIC-document-gates-2026-11-18.json",
    "YIC-qh-field-13-2026-11-16.json",
    "YIC-qh-resolve-09-2026-11-16.json",
    "YIC-qh-revalidate-2026-11-16.json",
    "YIC-reach-table-2026-11-17.json",
    "YIC-rule-liveness-2026-11-18.json",
    "YIC-scope-coverage-2026-11-18.json",
    "YIC-skip-disclosure-2026-11-16.json",
    "YIC-sui-r2-gate-hosts-2026-11-16.json",
    "YIC-suite-step-accounting-2026-11-16.json",
    "YIC-tei-host-skip-2026-11-16.json",
    "YIC-tei-knowledge-disclosure-2026-11-16.json",
    "YIC-tei-linux-regression-2026-11-16.json",
    "YIC-tei-product-read-2026-11-16.json",
    "YIC-tei-readonly-cli-2026-11-16.json",
    "YIC-tei-rooted-source-2026-11-16.json",
    "YIC-tei-selfbuild-observations-2026-11-16.json",
))


NAME_DATE = re.compile(r"-(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})(?:\.validate)?\.json$")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    rows = []
    noDate = 0
    for path in sorted((root / "evaluations/records").glob("*.json")):
        match = NAME_DATE.search(path.name)
        if not match:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        date = data.get("date")
        if not date:
            noDate += 1
            continue
        rows.append({
            "receipt": path.name,
            "nameDate": match.group("date"),
            "fieldDate": str(date),
            "agrees": str(date) == match.group("date"),
        })

    mismatched = [row for row in rows if not row["agrees"]]
    newMismatches = [
        row["receipt"] for row in mismatched
        if BASELINE_MISMATCHES and row["receipt"] not in BASELINE_MISMATCHES
    ]
    byYear = {}
    for row in mismatched:
        key = f"{row['nameDate']} -> {row['fieldDate']}"
        byYear[key] = byYear.get(key, 0) + 1

    checks = {
        "receiptsWithANameDate": len(rows),
        "receiptsWithoutADate": noDate,
        "agreeing": len(rows) - len(mismatched),
        # The full list, so a baseline can name every entry.
        "mismatched": mismatched,
        "mismatchedCount": len(mismatched),
        "baselineRecorded": len(BASELINE_MISMATCHES),
        "newSinceBaseline": newMismatches,
        "mismatchPatterns": sorted(byYear.items(), key=lambda item: -item[1])[:10],
        "finding": (
            f"ファイル名の日付と`date`欄を持つreceipt{len(rows)}件を比べた。"
            f"一致{len(rows) - len(mismatched)}件・**不一致{len(mismatched)}件**。"
            "**ファイル名が指す版と、中身が主張する版が違う。**"
            "読む人がファイル名で日付を判断すると、receiptの主張と食い違う。"
            "**どちらを正とするかは決めていない**（`date`欄を正とするのが自然だが、"
            "改名はreferencesを壊しうる）。"
        ),
    }
    # Until a baseline is recorded the check reports only; once it exists, growth fails.
    passed = len(rows) > 0 and not newMismatches

    receipt = {
        "schema": "tai.reference.yic-receipt-name-date/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading every receipt's name and date field",
        "command": "python integrations/tools/yic_receipt_name_date_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-receipt-name-date-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Parses the date out of each receipt's file name and compares it with the `date` "
            "field. It measures the mismatch; it does not rename any file and does not decide "
            "which side is authoritative."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipts": len(rows),
        "agreeing": len(rows) - len(mismatched),
        "mismatched": len(mismatched),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
