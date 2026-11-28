# integrations/tools

TEI投影パイロットを検証するための小さなツール群。製品のコードは各リポジトリにあり、ここは接続と検証だけを置く。

## 前提

- Goが`PATH`にあり、`GOCACHE`/`GOMODCACHE`/`TMP`が書き込み可能
- Python 3.12に`jsonschema`
- MMIのconsumerを動かすときだけNode 24と`tsx`\n- SaaS契約テストは`SUI_ADMIN_API_KEY`を必要とする。SEIの段は`--sei-repo`（または`SEI_REPO`）、MMIの段は`--mmi-repo`（または`MMI_REPO`）を使う。`--sei-repo`が無いと既定のチェックアウトを見るSUIのpytestは`SUI_*`環境変数を外して実行する
- EKIへ投入するときだけ、ビルド済みの`eki-control`
- 各製品リポジトリのパス（TEI・SUI・SEI・MMI・EKI）

## 一括検証

```text
python integrations/tools/run_suite.py \
  --tei-repo <TEI> --sui-repo <SUI> \
  --sei-schema <SEI>/contracts/schemas/v1alpha1/decision-memory.schema.json \
  --mmi-schema <MMI>/02_Architecture/format-profile-v1.schema.json \
  --eki-openapi <EKI>/spec/external/openapi.json \
  --eki-control <eki-control binary>
```

107段（checker・artifact・digest・MMIのassert/consumer/inspect/inventory/delivery・SEIのgate変種・TEI artifact複数配信・公開gateの再確認・SUI製品面8段・SaaS外部HTTP3種・ログイン開始・コールバック・token検証・SUIのSaaS/文書/認証連携/セッションテスト・SEIのCLI/gate/MCP・シナリオ・pipeline・compose・TLS・Postgres・migration・ETag・同時更新・継続競合・再試行・複数文書・レコード・EKI投入）を実行し、`evaluations/records/TEI-suite-2026-11-03.json`へ記録する。

- receipt自身をcheckerが読むため、FAILのreceiptが残っていると次の実行もFAILになる。その場合は`--skip-checker`で実行し、後からcheckerを単独で回す
- `--eki-control`・`--eki-agent`を省くとEKI投入の段は実行しない

## 個別ツール

| ツール | 用途 |
| --- | --- |
| `run_selection.py` | 1契約の生成・fixture選抜 |
| `validate_artifacts.py` | 4製品artifactのスキーマ検証 |
| `verify_artifact_digests.py` | artifactのcontractDigestを契約ファイルから再計算 |
| `check_scenario_artifacts.py` | SCN-003の識別子確認 |
| `compose_scn_003.py` | 判断・仕事・形式をSUI文書へ合成 |
| `check_determinism.py` | 単一record artifactの再生成同一性 |
| `validate_records.py` | 4製品artifactを正規レコードへ変換して検証 |
| `eki_submit_projection.py` | 投影TaskRequestを実eki-controlへ投入 |

## 注意

- Windowsでは`TMP`/`TEMP`を書き込み可能な場所へ向ける
- Goの出力はUTF-8で読む
- 選抜のreceipt名に`TEI-pilot`を含めると既存の検証規則に当たる
- 外部作用は行わない。EKI投入はTaskの受理までで、Workerは起動しない

<!-- tool-index:begin -->

以下は各ツールのdocstringの冒頭から生成した。**手で保たない。**
生成対象: `integrations/tools` の `*.py`（191件）。

### YIC（分析・点検）（96件）

| ツール | 目的（docstringの冒頭） |
| --- | --- |
| `yic_analysis_gates.py` | Run the analysis-level YI checks in one pass. |
| `yic_annotation_digest_impact.py` | Check whether the annotation left any recorded digest pointing at changed bytes. |
| `yic_annotation_readiness_check.py` | Correct the annotation-readiness detector: the checker has no global field allow-list. |
| `yic_audience_consumer_probe.py` | Run SHO's consumer against a ticket whose audience names a third party. |
| `yic_audience_declaration_check.py` | Check what the handoff envelope's `audience` field actually does. |
| `yic_audience_declaration_probe.py` | Check what the cross-product handoff does with `disclosure.audience`. |
| `yic_audience_execution_probe.py` | Run the envelope validator with a shape the product's own test uses. |
| `yic_audience_instrument_probe.py` | Check whether SUI's access decision varies with the audience, not just the tenant. |
| `yic_audit_recipient_probe.py` | Measure what the audit layer records about who received what. |
| `yic_authority_limits_check.py` | Check that receipts quoting a Product's own authority limits keep them verbatim. |
| `yic_baseline_classify.py` | Classify the known rule failures: is the rule current, or is the receipt historical? |
| `yic_baseline_classify_effect.py` | Derive the expected fields from the checker's own rule body, not from a guess. |
| `yic_citation_date_check.py` | Check whether the citations that no longer resolve are all historical. |
| `yic_citation_form_check.py` | Extend the citation check: does the current writing habit still cite a worktree path? |
| `yic_cited_path_check.py` | Check whether receipts cite a checkout path that still exists. |
| `yic_claim_ceiling_check.py` | Separate claims this runner measures from claims it merely declares. |
| `yic_codex_adapter_probe.py` | Check what the codex-exec adapter's tests establish, and whether it can ever run here. |
| `yic_commit_field_check.py` | Check the proposal the document now makes: receipts should cite a commit, not a path. |
| `yic_count_agreement_check.py` | Check that a checker's expected count is derived, not hard-coded. |
| `yic_count_claim_span_check.py` | Find every receipt-count claim in the docs, not only the one a checker reads. |
| `yic_dead_rule_fields_check.py` | Check whether the 22 rules that never fire are stale, or reject receipts correctly. |
| `yic_dead_rule_impact_probe.py` | Replace the dead-rule experiment with the question that remains after the fix. |
| `yic_deck_counts_check.py` | Check the deck slide counts that the indexes state against the actual files. |
| `yic_doc55_renumber.py` | Renumber doc 55's §6.8 so the letter suffixes become numbers. |
| `yic_doc_links_check.py` | Check every relative Markdown link in docs/ resolves to a file that exists. |
| `yic_docs_index.py` | Generate an index of docs/ from each document's own title and status line. |
| `yic_docs_index_freshness.py` | Verify the generated docs index lists every top-level document. |
| `yic_document_gates.py` | Run the document-level YI checks in one pass. |
| `yic_eki_private_input.py` | Check that EKI refuses a public disclosure profile when private input is required. |
| `yic_eki_recipient_check.py` | Check whether EKI verifies that a Lease goes to the intended recipient. |
| `yic_exhaustion_claim_check.py` | Check whether doc 53's "nothing further can be done" claim is still true. |
| `yic_folder_index.py` | Generate a directory index for any top-level folder, from each document's heading. |
| `yic_folder_index_check.py` | Check every top-level folder whose documents should be indexed. |
| `yic_g1_packet_readiness.py` | Check that the G1 packet is ready for a decision, not that it has been decided. |
| `yic_gate_citation_check.py` | Check that a gate document's citations match what each receipt actually claims. |
| `yic_gate_prose_check.py` | Check that the gate-status prose matches the receipts it cites. |
| `yic_gate_reproducibility.py` | Check that running the gates twice in a row produces the same receipts. |
| `yic_growth_watch_probe.py` | Prove the growth watch fires: add one mismatched name and see the check fail. |
| `yic_h_conditions_parser_check.py` | Check whether the harness adapter can observe H's two conditions. |
| `yic_handoff_conditions_check.py` | Check that the handoff-condition document keeps the distinction it was written to make. |
| `yic_handoff_stage_mapping.py` | Run SHO's cross-product handoff with and without a TEI checkout, and map the result onto I/R/P/T/C/H. |
| `yic_harness_evidence_check.py` | Check that the harness-adapter's evidence files are honest about what they ran. |
| `yic_inert_remainder_check.py` | Check whether the two remaining inert selectors name a receipt that exists elsewhere. |
| `yic_inert_selector_check.py` | Check that the seven selectors that reach nothing are dead, or missing a receipt. |
| `yic_note_correction.py` | Correct the note I wrote: 65 of the 82 receipts record no commit. |
| `yic_note_correction_effect_check.py` | Check the correction took effect: how many notes still claim a commit that does not exist. |
| `yic_note_truthfulness_check.py` | Check whether the note I wrote tells the truth. |
| `yic_notrun_refresh_check.py` | Check that the inventory's not-run list is still the current not-run list. |
| `yic_numbering_after_repair.py` | Install a section-numbering check that covers every YI document, not just two. |
| `yic_numbering_span_check.py` | Look for the same numbering disorder in every YI document, not only doc 53. |
| `yic_path_annotation.py` | Add a machine-readable note to receipts whose cited checkout path no longer exists. |
| `yic_pdp_payload_probe.py` | Measure what the external PDP request body actually carries. |
| `yic_per_contract_claims_check.py` | Check that the proposal document states per-contract differences, not one blanket claim. |
| `yic_preflight_disclosure_boundary.py` | Check what the nearest thing to a P step can and cannot decide. |
| `yic_proposal_boundary_check.py` | Check that a design proposal names who may decide it, and that TAI did not. |
| `yic_qh_field_13_probe.py` | Confirm that a whole Record keeps its fields while an explicit projection drops the rest. |
| `yic_qh_resolve_09_probe.py` | Confirm that "ambiguous" and "absent" are not distinguished, as QH-RESOLVE-09 claims. |
| `yic_qh_revalidate_probe.py` | Measure the current-fingerprint guard the read-only CLI now carries. |
| `yic_reach_forward_refs_check.py` | Check that the reach document's stage table points forward to the later findings. |
| `yic_reach_table_check.py` | Derive the reach table from the receipts instead of trusting it. |
| `yic_readme_coverage_check.py` | Check that the README index lists every YI document and links it correctly. |
| `yic_receipt_gates.py` | Run the gates a new receipt must survive, in one command. |
| `yic_receipt_name_date_check.py` | Check whether a receipt's file-name date matches the `date` field inside it. |
| `yic_receipt_review_probe.py` | Ask whether the Producer's receipt review looks at the audience at all. |
| `yic_recipient_search_probe.py` | Check the independent review's objection: is the "no recipient field" claim supported? |
| `yic_registration_parity_check.py` | Check that every receipt the checker registers also has a rule, and vice versa. |
| `yic_rename_cost_check.py` | Measure what a `date`-wins policy would cost before renaming anything. |
| `yic_reversed_selector_probe.py` | Measure the reordered selectors correctly: five of them point at real receipts. |
| `yic_rule_liveness_check.py` | Point the liveness reading at the selector that now exists, and at both loops. |
| `yic_runbook_expectation_check.py` | Check that the runbook's expected-output block matches what the gates report. |
| `yic_scope_coverage_check.py` | Check that the scope-halves rule covers every YI receipt, not only the yi- prefixed ones. |
| `yic_section_order_check.py` | Check that a document's numbered sections appear in order. |
| `yic_section_sequence_check.py` | Extend the section-order check to the whole YI document set. |
| `yic_share_guard_probe.py` | Check what SUI does when the action is `share`: the closest thing it has to disclosure. |
| `yic_skip_disclosure_check.py` | Check that receipts reporting test runs do not hide a skip behind a pass. |
| `yic_status_line_check.py` | Check that every YI document states what it is, in a predictable place. |
| `yic_step_review.py` | Ask Step 3.7 (architect role) whether the YI work has an honest stopping point. |
| `yic_subsection_numbering_check.py` | Check that a document's numbered subsections ascend without gaps or stray suffixes. |
| `yic_subsection_renumber.py` | Renumber doc 53's §6.1 so the order matches the reading order. |
| `yic_sui_r2_gate_hosts.py` | Compare one SUI gate test suite on Windows and on linux, and record why. |
| `yic_sui_source_policy_boundary.py` | Measure the strongest P-shaped decision found so far: a per-resource-kind override. |
| `yic_sui_tenant_boundary.py` | Measure the one product decision that refuses before asking anyone else. |
| `yic_suite_invocation_check.py` | Record the flags a suite run actually used, and refuse a receipt that loses them. |
| `yic_suite_step_accounting.py` | Check that the suite's registered steps, its run_step calls and its record agree. |
| `yic_tei_host_skip_probe.py` | Record which TEI regressions cannot run on this host, and why. |
| `yic_tei_knowledge_disclosure.py` | Measure whether TEI can answer "may this be disclosed" as a Product decision. |
| `yic_tei_linux_regression.py` | Run the linux-pinned TEI regressions on an actual linux host via WSL. |
| `yic_tei_product_read_regressions.py` | Run the TEI product-read regressions the YIC execution ticket listed as NOT RUN. |
| `yic_tei_readonly_cli_baseline.py` | Run the TEI read-only CLI baseline the YIC ticket lists as an unexecuted example. |
| `yic_tei_rooted_source.py` | Run the rooted-source boundary tests on both hosts and record the difference. |
| `yic_tei_selfbuild_observations.py` | Run the linux-pinned self-build observation tests on an actual linux host. |
| `yic_tool_index.py` | Generate a tool index from each tool's own docstring, and check it stays complete. |
| `yic_tool_index_freshness.py` | Check that the generated block in the README matches the tools on disk. |
| `yic_tool_routing_check.py` | Record which YI tools need a product checkout, so a reader knows what a suite run covers. |
| `yic_universal_claim_check.py` | Check that a "every X is true" receipt also says how many X it examined. |
| `yic_verdict_computation_check.py` | Check that every YI receipt writer computes its verdict rather than asserting one. |

### YI（初期の点検）（31件）

| ツール | 目的（docstringの冒頭） |
| --- | --- |
| `yi_acceptance_authority_check.py` | Check whether the acceptance authority G1's D5 asks about actually exists. |
| `yi_artifact_digest_check.py` | Check that each YI receipt's recorded artifact digest still matches the file. |
| `yi_candidate_fields_check.py` | Check that every candidate states what Acceptance would need to weigh. |
| `yi_centre_handoff_probe.py` | Probe the centre handoff (RQ-YI-020) with the records that already exist. |
| `yi_centre_key_options.py` | Compare where a reference to an artifact could be added for the centre handoff. |
| `yi_citation_check.py` | Check that requirement IDs cited by the YI analysis exist in each product. |
| `yi_context_handoff_probe.py` | Measure which units the context handoff actually carries (RQ-YI-024). |
| `yi_cross_receipt_check.py` | Check that receipts which report the same fact report the same number. |
| `yi_csw_return_check.py` | Check that what the YI analysis says it returned to CSW is still there. |
| `yi_danger_units_check.py` | Inventory the smallest danger units from the receipts that already exist. |
| `yi_deck_proposal_figures_check.py` | Check that the deck proposals still match what the analysis now says. |
| `yi_doc_integrity_check.py` | Check the YI Constellation document set for index and link integrity. |
| `yi_eki_measurement_probe.py` | Try the first experiment of the EKI phase expansion: measure value, not just safety. |
| `yi_empty_reference_probe.py` | Try the first experiment of the SHO phase expansion: detect an empty reference. |
| `yi_fold_with_dissent_probe.py` | Try the first experiment of the SUI phase expansion: fold a field, keep the dissent. |
| `yi_g1_evidence_check.py` | Check whether each cross-cutting decision in G1 has the evidence it needs. |
| `yi_g1_status_check.py` | Keep the YI analysis honest about what has and has not been decided. |
| `yi_g2_landing_check.py` | Work out where each adopted candidate would land in a product's requirement document. |
| `yi_landing_paths_check.py` | Check that the plan's landing paths exist and do not contradict themselves. |
| `yi_naming_blast_radius.py` | Measure how far the "統合製品" wording reaches, which G1's D2 rests on. |
| `yi_overreach_probe.py` | Try the first experiment of the TEI phase expansion: refuse an over-reach at design time. |
| `yi_pass_consistency_check.py` | Check that a PASS receipt's own observations do not contradict its verdict. |
| `yi_publication_refusal_probe.py` | Observe a publication refusal instead of only declaring it held. |
| `yi_receipt_auditability_check.py` | Check that every YI receipt can still be re-read by someone who was not there. |
| `yi_receipt_quality.py` | Run the receipt-quality checks in one pass, and refuse to report PASS if any is missing. |
| `yi_scope_halves_check.py` | Check that each YI receipt's scope separates what it measured from what it did not. |
| `yi_sho_actual_check.py` | Establish what sho-composer actually contains, which G1's D3/D6 rest on. |
| `yi_stage3_inventory.py` | Inventory what stage 3 of the YI plan has actually run, and what has not. |
| `yi_staleness_probe.py` | Measure what happens to an artifact's provenance when its source is revised. |
| `yi_state_classification.py` | Classify SCN-001's negative cases into the six states of the TAI expansion. |
| `yi_unreferenced_probe.py` | Try the first experiment of the SEI phase expansion: show an unreferenced record. |

### その他（64件）

| ツール | 目的（docstringの冒頭） |
| --- | --- |
| `check_determinism.py` | Rebuild each single-record projection artifact twice and compare digests. |
| `check_scenario_artifacts.py` | Check that the SCN-003 artifacts carry the documented identifiers. |
| `compose_scn_003.py` | Compose a SUI document artifact with the SEI decision as an extra card. |
| `conclusion_integrity_check.py` | Check that the conclusion's evidence links are live and actually PASS. |
| `doc_consistency_check.py` | Check that the documented suite size and receipt counts match the records. |
| `eki_manual_execution.py` | Drive EKI manually: own control config, own trust anchor, own Agent, one Task. |
| `eki_multi_worker.py` | Drive EKI manually: own control config, own trust anchor, own Agent, one Task. |
| `eki_projection_execution.py` | Run TAI's projected TaskRequest through EKI's own HTTP-submit execution harness. |
| `eki_record_from_projection.py` | Turn the EKI projection artifact into an eki.task-request/v1 record. |
| `eki_revoke_agent.py` | Drive EKI manually: own control config, own trust anchor, own Agent, one Task. |
| `eki_submit_projection.py` | Submit the projected TaskRequest to a real eki-control and record the answer. |
| `eki_worker_revoke.py` | Revoke an enrolled Worker and check the Control Plane refuses it afterwards. |
| `fixture_field_coverage_check.py` | Check that every contract field is exercised by at least one fixture case. |
| `gate_recheck.py` | _docstring not parseable_ |
| `mmi_consumer_tests.py` | _docstring not parseable_ |
| `mmi_delivery_audit_check.py` | _docstring not parseable_ |
| `mmi_inspect_check.py` | _docstring not parseable_ |
| `mmi_inventory_check.py` | _docstring not parseable_ |
| `mmi_profile_assert.py` | Check that the projected MMI format profile is accepted by MMI's own validator. |
| `mmi_record_from_projection.py` | Try to turn the MMI projection artifact into a full format-profile record. |
| `normalize_go_line_endings.py` | Normalise Go files committed with CRLF to LF. |
| `poc_evaluation_baseline.py` | Record the current suite timings as a baseline observation for later comparison. |
| `poc_evaluation_template_check.py` | Validate the PoC evaluation template against its schema and its own limits. |
| `probe_saas_profile.py` | Probe the SUI SaaS multi-tenant profile without changing it. |
| `receipt_consistency_check.py` | Check that a PASS receipt does not also report a failed success flag. |
| `receipt_scope_check.py` | Check that every receipt says what it does not prove. |
| `repair_receipt_metadata.py` | Record the pre-convention receipts and add the safe metadata they can carry. |
| `result_exit_parity_check.py` | Audit scripts for a receipt verdict that can disagree with their exit code. |
| `run_selection.py` | Build and select a reference generator for one contract, then record it. |
| `run_suite.py` | Run the TAI-side verification steps in one command and record the result. |
| `saas_startup_probe.py` | Start SUI under the SaaS profile with a migrated Postgres and record the refusal. |
| `scope_equivalence_probe.py` | Which TEI read-only responses change when only content outside the asked scope changes? |
| `sei_cli_record.py` | Record the projected SEI decision through SEI's own CLI and verify the bundle. |
| `sei_doctor_check.py` | Check SEI's `doctor` self-diagnosis: what it reports before and after a store exists. |
| `sei_gate_check.py` | Run SEI's policy gate against the projected decision, for allow and deny cases. |
| `sei_gate_variants.py` | _docstring not parseable_ |
| `sei_mcp_check_decision.py` | Call SEI's MCP check_decision for an allow and a deny case. |
| `sei_mcp_probe.py` | Probe SEI's MCP stdio server with the JSON-RPC calls an AI tool would send. |
| `sei_record_from_projection.py` | Turn the SEI projection artifact into a decision-memory record and validate it. |
| `sei_resume_check.py` | Check SEI's resume snapshot binding and the safe-text escaping of stored values. |
| `skill_selection_check.py` | Check Skill text against a real TEI CLI, and score capability selections. |
| `sui_auth_flow_tests.py` | Run SUI's SaaS auth test subset and record the result. |
| `sui_docs_tests.py` | Run SUI's SaaS auth test subset and record the result. |
| `sui_saas_adapter_contract.py` | Drive SUI's external SaaS adapters against a local stub and check their contracts. |
| `sui_saas_callback_contract.py` | Check SUI's OAuth callback error contract without an identity provider. |
| `sui_saas_identity_contract.py` | Check SUI's broker-token identity verification with a local JWKS stub. |
| `sui_saas_login_contract.py` | Check the authorize-step contract of SUI's OAuth login against the local modules. |
| `sui_saas_oauth_contract.py` | Drive SUI's OAuth broker client against a local stub and record the contract. |
| `sui_saas_tests.py` | Run SUI's SaaS auth test subset and record the result. |
| `sui_session_tests.py` | Run SUI's SaaS auth test subset and record the result. |
| `tei_contract_decode_probe.py` | Compare how TEI's two entry points decode the same contract. |
| `tei_decimal_fidelity_probe.py` | Measure whether the record template preserves decimal digits. |
| `tei_independent_oracle_check.py` | Validate every projected record against SUI's own model, not against the contract. |
| `tei_many_primitive_probe.py` | Probe how TEI handles a `many` record field whose primitive is numeric. |
| `tei_meaning_change_experiment.py` | Measure one meaning change from contract edit to regenerated, conforming output. |
| `tei_meaning_change_required.py` | Second meaning-change run: add a required field instead of an optional one. |
| `tei_meaning_change_requiredness.py` | Third meaning change: make an existing optional field required. |
| `tei_nesting_probe.py` | Probe whether TEI's generator-contract accepts a nested record field. |
| `tei_optional_flag_probe.py` | Check whether the contract's `optional` flag changes the generated candidate. |
| `tei_projection_strategy_probe.py` | Check whether a projection contract can use a long-running generator strategy. |
| `tei_target_profile_compare.py` | Run the same pilot contract and fixtures on two Target Profiles and compare. |
| `validate_artifacts.py` | Validate every pilot projection artifact against its JSON Schema. |
| `validate_records.py` | Convert every pilot artifact into its product record and check the results. |
| `verify_artifact_digests.py` | Verify that every pilot artifact's contractDigest matches its contract file. |
<!-- tool-index:end -->
