"""Run the TAI-side verification steps in one command and record the result."""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_step(name, args, timeout=900, retries=2, env=None):
    started = time.time()
    attempts = 0
    while True:
        attempts += 1
        completed = subprocess.run(
            [sys.executable, *args],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            cwd=ROOT,
            env={**os.environ, **(env or {})},
        )
        if completed.returncode == 0 or attempts > retries:
            break
        time.sleep(3)
    return {
        "returncode": completed.returncode,
        "attempts": attempts,
        "seconds": round(time.time() - started, 2),
        "stdoutTail": completed.stdout.strip().splitlines()[-3:],
        "stderrTail": completed.stderr.strip().splitlines()[-3:],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--sei-schema", default="")
    parser.add_argument("--mmi-schema", default="")
    parser.add_argument("--eki-openapi", default="")
    parser.add_argument("--eki-control", default="")
    parser.add_argument("--eki-agent", default="")
    parser.add_argument("--skip-checker", action="store_true")
    parser.add_argument("--sei-repo", default="")
    parser.add_argument("--mmi-repo", default="")
    parser.add_argument("--out", default="evaluations/records/TEI-suite-2026-11-03.json")
    args = parser.parse_args()
    if args.sei_repo:
        os.environ["SEI_REPO"] = args.sei_repo

    steps = {
        "checker": run_step("checker", ["tools/check-synthetic-receipts/check.py", "--root", str(ROOT)]),
        "artifacts": run_step("artifacts", ["integrations/tools/validate_artifacts.py"]),
        "digests": run_step("digests", ["integrations/tools/verify_artifact_digests.py"]),
        "mmi_profile": run_step("mmi_profile", ["integrations/tools/mmi_profile_assert.py"]),
        "mmi_consumer": run_step("mmi_consumer", ["integrations/tools/mmi_consumer_tests.py"]),
        "mmi_inspect": run_step("mmi_inspect", ["integrations/tools/mmi_inspect_check.py"]),
        "mmi_inventory": run_step("mmi_inventory", ["integrations/tools/mmi_inventory_check.py"]),
        "mmi_delivery": run_step("mmi_delivery", ["integrations/tools/mmi_delivery_audit_check.py"]),
        "sei_gate_variants": run_step("sei_gate_variants", ["integrations/tools/sei_gate_variants.py"]),
        "sui_tei_multi": run_step("sui_tei_multi", ["integrations/pilot-sui-document/assembler/tei_reference_multi_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--sei-artifact", "evaluations/artifacts/sei-decision-projection.json", "--out", "evaluations/records/SUI-TEI-reference-multi-2026-11-03.json"]),
        "saas_adapters": run_step("saas_adapters", ["integrations/tools/sui_saas_adapter_contract.py", "--sui-src", f"{args.sui_repo}/03_Implement/backend/src"]),
        "saas_oauth": run_step("saas_oauth", ["integrations/tools/sui_saas_oauth_contract.py", "--sui-src", f"{args.sui_repo}/03_Implement/backend/src"]),
        "saas_login": run_step("saas_login", ["integrations/tools/sui_saas_login_contract.py", "--sui-src", f"{args.sui_repo}/03_Implement/backend/src"]),
        "saas_callback": run_step("saas_callback", ["integrations/tools/sui_saas_callback_contract.py", "--sui-src", f"{args.sui_repo}/03_Implement/backend/src"]),
        "saas_identity": run_step("saas_identity", ["integrations/tools/sui_saas_identity_contract.py", "--sui-src", f"{args.sui_repo}/03_Implement/backend/src"]),
        "sui_saas_tests": run_step("sui_saas_tests", ["integrations/tools/sui_saas_tests.py", "--sui-repo", args.sui_repo]),
        "sui_docs_tests": run_step("sui_docs_tests", ["integrations/tools/sui_docs_tests.py", "--sui-repo", args.sui_repo]),
        "sui_auth_flow_tests": run_step("sui_auth_flow_tests", ["integrations/tools/sui_auth_flow_tests.py", "--sui-repo", args.sui_repo]),
        "sui_session_tests": run_step("sui_session_tests", ["integrations/tools/sui_session_tests.py", "--sui-repo", args.sui_repo]),
        "sei_cli": run_step("sei_cli", ["integrations/tools/sei_cli_record.py"]),
        "sei_gate": run_step("sei_gate", ["integrations/tools/sei_gate_check.py"]),
        "sei_mcp": run_step("sei_mcp", ["integrations/tools/sei_mcp_probe.py"]),
        "sei_mcp_check": run_step("sei_mcp_check", ["integrations/tools/sei_mcp_check_decision.py"]),
        "scenario": run_step("scenario", ["integrations/tools/check_scenario_artifacts.py"]),
        "pipeline": run_step(
            "pipeline",
            [
                "integrations/pilot-sui-document/assembler/run_pilot.py",
                "--tei-repo",
                args.tei_repo,
                "--sui-repo",
                args.sui_repo,
                "--workspace",
                str(ROOT / "integrations/pilot-sui-document"),
                "--out",
                "evaluations/records/TEI-suite-pipeline-2026-11-03.json",
            ],
        ),
        "compose": run_step(
            "compose",
            ["integrations/tools/compose_scn_003.py", "--sui-repo", args.sui_repo],
        ),
        "tls": run_step(
            "tls",
            [
                "integrations/pilot-sui-document/assembler/tls_check.py",
                "--sui-repo",
                args.sui_repo,
                "--out",
                "evaluations/records/SUI-TEI-tls-2026-11-03.json",
            ],
        ),
        "postgres": run_step(
            "postgres",
            [
                "integrations/pilot-sui-document/assembler/postgres_save.py",
                "--sui-repo",
                args.sui_repo,
                "--artifact",
                "evaluations/artifacts/scn-003-document.json",
                "--out",
                "evaluations/records/SUI-TEI-postgres-2026-11-03.json",
            ],
        ),
        "postgres_migrate": run_step(
            "postgres_migrate",
            [
                "integrations/pilot-sui-document/assembler/postgres_migrate_save.py",
                "--sui-repo",
                args.sui_repo,
                "--artifact",
                "evaluations/artifacts/scn-003-document.json",
                "--out",
                "evaluations/records/SUI-TEI-postgres-migrate-2026-11-03.json",
            ],
        ),        "postgres_etag": run_step(
            "postgres_etag",
            [
                "integrations/pilot-sui-document/assembler/postgres_etag_check.py",
                "--sui-repo",
                args.sui_repo,
                "--artifact",
                "evaluations/artifacts/scn-003-document.json",
                "--out",
                "evaluations/records/SUI-TEI-postgres-etag-2026-11-03.json",
            ],
        ),        "postgres_concurrency": run_step(
            "postgres_concurrency",
            [
                "integrations/pilot-sui-document/assembler/postgres_concurrency_check.py",
                "--sui-repo",
                args.sui_repo,
                "--artifact",
                "evaluations/artifacts/scn-003-document.json",
                "--out",
                "evaluations/records/SUI-TEI-postgres-concurrency-2026-11-03.json",
            ],
        ),        "postgres_contention": run_step(
            "postgres_contention",
            [
                "integrations/pilot-sui-document/assembler/postgres_contention_check.py",
                "--sui-repo",
                args.sui_repo,
                "--artifact",
                "evaluations/artifacts/scn-003-document.json",
                "--retry-transient",
                "0",
                "--out",
                "evaluations/records/SUI-TEI-postgres-contention-2026-11-03.json",
            ],
        ),        "postgres_retry": run_step(
            "postgres_retry",
            [
                "integrations/pilot-sui-document/assembler/postgres_contention_check.py",
                "--sui-repo",
                args.sui_repo,
                "--artifact",
                "evaluations/artifacts/scn-003-document.json",
                "--retry-transient",
                "2",
                "--out",
                "evaluations/records/SUI-TEI-postgres-retry-2026-11-03.json",
            ],
        ),        "postgres_multidoc": run_step(
            "postgres_multidoc",
            [
                "integrations/pilot-sui-document/assembler/postgres_multi_save.py",
                "--sui-repo",
                args.sui_repo,
                "--artifact",
                "evaluations/artifacts/scn-003-document.json",
                "--out",
                "evaluations/records/SUI-TEI-postgres-multidoc-2026-11-03.json",
            ],
        ),
        "records": run_step(
            "records",
            [
                "integrations/tools/validate_records.py",
                "--sei-schema",
                args.sei_schema,
                "--mmi-schema",
                args.mmi_schema,
                "--eki-openapi",
                args.eki_openapi,
                "--sui-repo",
                args.sui_repo,
            ],
        ),
        "gate": run_step("gate", ["integrations/tools/gate_recheck.py"]),
        "sui_pg_tls": run_step("sui_pg_tls", ["integrations/pilot-sui-document/assembler/postgres_tls_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-postgres-tls-2026-11-03.json"]),
        "sui_ca_chain": run_step("sui_ca_chain", ["integrations/pilot-sui-document/assembler/ca_chain_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-ca-chain-2026-11-03.json"]),
        "sui_proxy": run_step("sui_proxy", ["integrations/pilot-sui-document/assembler/proxy_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-proxy-2026-11-03.json"]),
        "sui_multi_instance": run_step("sui_multi_instance", ["integrations/pilot-sui-document/assembler/postgres_multi_instance_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-multi-instance-2026-11-03.json"]),
        "sui_audit": run_step("sui_audit", ["integrations/pilot-sui-document/assembler/audit_export_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-audit-2026-11-03.json"]),
        "sui_admin": run_step("sui_admin", ["integrations/pilot-sui-document/assembler/admin_plane_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-admin-2026-11-03.json"]),
        "sui_provision": run_step("sui_provision", ["integrations/pilot-sui-document/assembler/provision_user_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-provision-2026-11-03.json"]),
        "sui_tei_reference": run_step("sui_tei_reference", ["integrations/pilot-sui-document/assembler/tei_reference_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-reference-2026-11-03.json"]),
        "sui_context": run_step("sui_context", ["integrations/pilot-sui-document/assembler/context_query_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-context-2026-11-03.json"]),
        "sui_context_bundle": run_step("sui_context_bundle", ["integrations/pilot-sui-document/assembler/context_bundle_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-context-bundle-2026-11-03.json"]),
        "sui_ce4": run_step("sui_ce4", ["integrations/pilot-sui-document/assembler/ce4_resolve_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-ce4-2026-11-03.json"]),
        "sui_registry": run_step("sui_registry", ["integrations/pilot-sui-document/assembler/model_registry_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-registry-2026-11-03.json"]),
        "sui_agent_guard": run_step("sui_agent_guard", ["integrations/pilot-sui-document/assembler/agent_credential_guard_check.py"]),
        "sui_agent_admin": run_step("sui_agent_admin", ["integrations/pilot-sui-document/assembler/agent_credential_admin_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-agent-credential-admin-2026-11-06.json"]),
        "sui_audit_pagination": run_step("sui_audit_pagination", ["integrations/pilot-sui-document/assembler/admin_audit_pagination_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-audit-pagination-2026-11-06.json"]),
        "sui_etag_stability": run_step("sui_etag_stability", ["integrations/pilot-sui-document/assembler/etag_stability_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-etag-stability-2026-11-06.json"]),
        "sui_archive_lifecycle": run_step("sui_archive_lifecycle", ["integrations/pilot-sui-document/assembler/archive_lifecycle_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-archive-lifecycle-2026-11-06.json"]),
        "sui_merge_decision_log": run_step("sui_merge_decision_log", ["integrations/pilot-sui-document/assembler/merge_decision_log_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-merge-decision-log-2026-11-06.json"]),
        "sui_ce4_audit_order": run_step("sui_ce4_audit_order", ["integrations/pilot-sui-document/assembler/ce4_audit_order_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-ce4-audit-order-2026-11-06.json"]),
        "sui_polygon_handoff": run_step("sui_polygon_handoff", ["integrations/pilot-sui-document/assembler/polygon_handoff_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-polygon-handoff-2026-11-06.json"]),
        "sui_similar_candidates": run_step("sui_similar_candidates", ["integrations/pilot-sui-document/assembler/similar_candidate_groups_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-similar-candidates-2026-11-06.json"]),
        "sui_export_dedup": run_step("sui_export_dedup", ["integrations/pilot-sui-document/assembler/export_audit_dedup_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-export-dedup-2026-11-06.json"]),
        "sui_native_action": run_step("sui_native_action", ["integrations/pilot-sui-document/assembler/native_action_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-native-action-2026-11-06.json"]),
        "sui_list_pagination": run_step("sui_list_pagination", ["integrations/pilot-sui-document/assembler/list_pagination_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-list-pagination-2026-11-06.json"]),
        "sui_agent_read_path": run_step("sui_agent_read_path", ["integrations/pilot-sui-document/assembler/agent_read_path_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-agent-read-path-2026-11-06.json"]),
        "sui_agent_key_wiring": run_step("sui_agent_key_wiring", ["integrations/pilot-sui-document/assembler/agent_key_wiring_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-agent-key-wiring-2026-11-06.json"]),
        "sui_saas_precondition": run_step("sui_saas_precondition", ["integrations/pilot-sui-document/assembler/saas_precondition_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-saas-precondition-2026-11-06.json"]),
        "sui_dedup_window": run_step("sui_dedup_window", ["integrations/pilot-sui-document/assembler/audit_dedup_window_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-dedup-window-2026-11-06.json"]),
        "sui_profile_policy": run_step("sui_profile_policy", ["integrations/pilot-sui-document/assembler/runtime_profile_policy_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-profile-policy-2026-11-06.json"]),
        "sui_probes": run_step("sui_probes", ["integrations/pilot-sui-document/assembler/probe_endpoints_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-probes-2026-11-06.json"]),
        "sui_auth_assurance": run_step("sui_auth_assurance", ["integrations/pilot-sui-document/assembler/auth_assurance_check.py", "--sui-repo", args.sui_repo, "--artifact", "evaluations/artifacts/scn-003-document.json", "--out", "evaluations/records/SUI-TEI-auth-assurance-2026-11-06.json"]),
    }
    steps["poc_eval_template"] = run_step("poc_eval_template", ["integrations/tools/poc_evaluation_template_check.py"])
    eki_env = {}
    if args.eki_control:
        eki_env["EKI_CONTROL"] = args.eki_control
    if args.eki_agent:
        eki_env["EKI_AGENT"] = args.eki_agent
    if args.eki_control:
        steps["eki_submit"] = run_step(
            "eki_submit",
            [
                "integrations/tools/eki_submit_projection.py",
                "--control-binary",
                args.eki_control,
                "--artifact",
                "evaluations/artifacts/eki-task-request-record.json",
                "--out",
                "evaluations/records/EKI-TEI-submit-2026-11-03.json",
            ],
        )
    eki_env = {}
    if args.eki_control:
        eki_env["EKI_CONTROL"] = args.eki_control
    if args.eki_agent:
        eki_env["EKI_AGENT"] = args.eki_agent
    if args.eki_control:
        steps["eki_projection"] = run_step(
            "eki_projection", ["integrations/tools/eki_projection_execution.py"], env=eki_env
        )
        steps["eki_manual"] = run_step("eki_manual", ["integrations/tools/eki_manual_execution.py"], env=eki_env)
        steps["eki_revoke"] = run_step("eki_revoke", ["integrations/tools/eki_worker_revoke.py"], env=eki_env)
        steps["eki_revoke_agent"] = run_step("eki_revoke_agent", ["integrations/tools/eki_revoke_agent.py"], env=eki_env)
    if args.skip_checker:
        steps.pop("checker", None)
    tei_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=args.tei_repo, capture_output=True, text=True).stdout.strip()
    passed = all(step["returncode"] == 0 for step in steps.values())
    receipt = {
        "schema": "tai.reference.tei-suite/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go on PATH, Python 3.12, and the SUI consumer",
        "command": "python integrations/tools/run_suite.py --tei-repo <TEI> --sui-repo <SUI>",
        "result": "PASS" if passed else "FAIL",
        "teiCommit": tei_commit,
        "steps": steps,
        "scope": "Runs the checker, artifact schema checks, SCN-003 link check, and the SUI pipeline (without save). It does not run Postgres, deployment, or external effects.",
    }
    out = ROOT / args.out
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run(
        [sys.executable, "integrations/tools/poc_evaluation_baseline.py"],
        cwd=ROOT,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    print(json.dumps({"result": receipt["result"], "steps": {k: v["returncode"] for k, v in steps.items()}}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
