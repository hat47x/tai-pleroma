"""Run the analysis-level YI checks in one pass.

Eight further checks judge the analysis itself: the candidate fields G1 needs, the
gate-1 status and evidence, the requirement citations, document integrity, deck
figure agreement, the CSW return, the five danger units, and the acceptance authority.
None needs a product checkout, all run in seconds, and none is wired into the suite.
Running them individually from memory is how one gets skipped.

This runs them together and refuses PASS if any is missing or fails.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CHECKS = (
    ("candidateFields", "yi_candidate_fields_check.py",
     "every candidate carries the six fields a decision needs"),
    ("g1Evidence", "yi_g1_evidence_check.py",
     "each cross-cutting decision has an observation or a named gap"),
    ("g1Status", "yi_g1_status_check.py",
     "the decision fields are unfilled and no document claims acceptance"),
    ("citation", "yi_citation_check.py",
     "every cited requirement is defined and every candidate counted once"),
    ("docIntegrity", "yi_doc_integrity_check.py",
     "the analysis files are indexed and their links resolve"),
    ("deckFigures", "yi_deck_proposal_figures_check.py",
     "the deck's figures still agree with the receipts"),
    ("cswReturn", "yi_csw_return_check.py",
     "the edits returned to CSW are still present"),
    ("dangerUnits", "yi_danger_units_check.py",
     "each of the five danger units has evidence"),
    ("acceptanceAuthority", "yi_acceptance_authority_check.py",
     "each product names who accepts a requirement"),
    ("centreKeyOptions", "yi_centre_key_options.py",
     "exactly one typed place can carry the centre units"),
    ("ekiMeasurement", "yi_eki_measurement_probe.py",
     "the EKI ADR names the measurement it requires"),
    ("g2Landing", "yi_g2_landing_check.py",
     "each product has a place and a free number for landed requirements"),
    ("landingPaths", "yi_landing_paths_check.py",
     "the landing paths exist in the product repositories"),
    ("shoActual", "yi_sho_actual_check.py",
     "SHO carries the commits and files the plan assumes"),
    ("stage3Inventory", "yi_stage3_inventory.py",
     "the stage-3 items and their not-run states are enumerated"),
    ("namingBlastRadius", "yi_naming_blast_radius.py",
     "a naming change touches a bounded set of files"),
)

# Checks that also need the TAI root; the aggregate supplies this checkout.
TAI_ROOT_CHECKS = (
    ("contextHandoffProbe", "yi_context_handoff_probe.py",
     "a context handoff carries the three units"),
    ("foldWithDissentProbe", "yi_fold_with_dissent_probe.py",
     "a fold keeps its dissent"),
    ("publicationRefusalProbe", "yi_publication_refusal_probe.py",
     "receipts that declare publication held state a reason"),
    ("stateClassification", "yi_state_classification.py",
     "each record's state is classified, not inferred"),
)

PORTABLE_CHECKS = (
    ("verdictComputation", "yic_verdict_computation_check.py",
     "every receipt writer computes its verdict rather than asserting one"),
    ("claimCeiling", "yic_claim_ceiling_check.py",
     "claims that are literals cannot be reached by re-running"),
    ("handoffConditions", "yic_handoff_conditions_check.py",
     "each stage states whether it has an instrument and what would count as a handoff"),
    ("audienceInstrument", "yic_audience_instrument_probe.py",
     "the request type has no recipient field and roles do not change the decision"),
    ("shareGuard", "yic_share_guard_probe.py",
     "the share action keys on visibility and mode, not on a recipient"),
    ("pdpPayload", "yic_pdp_payload_probe.py",
     "the external PDP body carries no recipient and the field would need three edits"),
    ("recipientSearch", "yic_recipient_search_probe.py",
     "a package-wide search for recipient terms, classified, with unclassified hits kept"),
    ("auditRecipient", "yic_audit_recipient_probe.py",
     "the audit envelope has no recipient field but metadata can carry one"),
    ("ekiRecipient", "yic_eki_recipient_check.py",
     "EKI verifies the Lease recipient against the local Worker"),
    ("audienceFieldReading", "yic_audience_declaration_check.py",
     "the handoff envelope has an audience field that nothing decides against"),
    ("perContractClaims", "yic_per_contract_claims_check.py",
     "the document names each contract and carries no blanket claim"),
    ("audienceExecution", "yic_audience_execution_probe.py",
     "running the envelope validator: shape refused, an unrelated recipient accepted"),
    ("audienceConsumer", "yic_audience_consumer_probe.py",
     "running the consumer CLI: a ticket naming a third party is still accepted"),
    ("receiptReview", "yic_receipt_review_probe.py",
     "running the producer's receipt review: audience is not consulted"),
    ("scopeCoverage", "yic_scope_coverage_check.py",
     "both receipt naming families state a measured half and a limit half"),
    ("countAgreement", "yic_count_agreement_check.py",
     "each aggregate's check count matches what the checker expects"),
    ("inertRemainder", "yic_inert_remainder_check.py",
     "the two remaining inert selectors: one has no receipt, one must not match"),
    ("citedPath", "yic_cited_path_check.py",
     "how many receipts cite a checkout path that no longer exists"),
    ("commitField", "yic_commit_field_check.py",
     "how many real receipts carry a commit, against the proposal to require one"),
    ("citationDates", "yic_citation_date_check.py",
     "whether the unresolvable citations are all historical"),
    ("citationForm", "yic_citation_form_check.py",
     "whether receipts written now still cite a local checkout path"),
    ("ruleLiveness", "yic_rule_liveness_check.py",
     "which rules can never fire because of case"),
    ("deadRuleImpact", "yic_dead_rule_impact_probe.py",
     "running the checker with the dead rules made live"),
    ("deadRuleFields", "yic_dead_rule_fields_check.py",
     "each failing rule's field: missing, or present with a different value"),
    ("hConditionsParser", "yic_h_conditions_parser_check.py",
     "each adapter can parse a terminal event and holds a session identifier"),
)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def classify(results):
    missing = [name for name, item in results.items() if not item["ran"]]
    failed = [name for name, item in results.items()
              if item["ran"] and not item["passed"]]
    return missing, failed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    scratch = Path(tempfile.mkdtemp(prefix="yic-analysis-gates-"))
    results = {}
    for name, script, question in CHECKS + TAI_ROOT_CHECKS + PORTABLE_CHECKS:
        path = root / "integrations/tools" / script
        if not path.exists():
            results[name] = {"ran": False, "reason": "script missing", "question": question}
            continue
        extra = []
        if (name, script, question) in TAI_ROOT_CHECKS:
            extra = ["--tai-root", str(root)]
        elif name == "claimCeiling":
            extra = ["--sho-repo", str(root.parent / "sho-composer")]
        elif name in ("audienceInstrument", "shareGuard", "pdpPayload",
                      "recipientSearch", "auditRecipient"):
            # These two take the SUI checkout as a third positional argument.
            extra = []
        completed = subprocess.run(
            (
                [sys.executable, str(path), args.artifact, str(scratch / f"{name}.json"),
                 str(root.parent / "sui-sensemaking")]
                if name in ("audienceInstrument", "shareGuard", "pdpPayload",
                            "recipientSearch", "auditRecipient")
                else [sys.executable, str(path), *extra,
                      "--artifact", args.artifact,
                      "--out", str(scratch / f"{name}.json")]
            ),
            cwd=root, capture_output=True, text=True,
            encoding="utf-8", errors="replace", env={**os.environ}, timeout=900,
        )
        tail = (completed.stdout or "").strip().splitlines()
        results[name] = {
            "ran": True,
            "question": question,
            "exit": completed.returncode,
            "passed": completed.returncode == 0,
            "tail": tail[-1][:200] if tail else "",
        }

    missing, failed = classify(results)
    checks = {
        "checksRequested": len(CHECKS) + len(TAI_ROOT_CHECKS) + len(PORTABLE_CHECKS),
        "checksRun": len([item for item in results.values() if item["ran"]]),
        "results": results,
        "scriptsMissing": missing,
        "failed": failed,
        "wroteIntoTheTree": False,
        "everyAnalysisCheckRan": not missing,
        "everyAnalysisCheckPassed": not failed,
        "finding": (
            "分析水準のYI点検9種を1コマンドで実行し、1つでも欠ければPASSを返さない。"
            "いずれも製品チェックアウトを要さず、数秒で終わるが、"
            "suiteにもreceipt集約にも入っていないため個別に呼ぶしかなかった。"
        ),
    }
    passed = not missing and not failed

    receipt = {
        "schema": "tai.reference.yic-analysis-gates/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 running the analysis checks together",
        "command": "python integrations/tools/yic_analysis_gates.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-analysis-gates-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs nine analysis-level YI checks in one pass and refuses PASS if any is missing or "
            "fails. It records whether each ran and its exit code, not what each concluded; a check "
            "that passes can still judge the wrong thing, and this aggregate inherits every limit of "
            "the nine."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ran": checks["checksRun"],
        "failed": failed,
        "missing": missing,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
