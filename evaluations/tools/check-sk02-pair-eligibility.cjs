#!/usr/bin/env node
"use strict";
/*
 * SK-02 test-only comparability checker. Synthetic records cannot attest
 * actual harness/tool/skill observations or evaluate business correctness.
 * Usage: node check_sk02_pair_eligibility.cjs --self-test
 *        node check_sk02_pair_eligibility.cjs path/to/trial-group.json
 */
const assert = require("node:assert/strict");
const fs = require("node:fs");

const SAME = ["task_id", "repo_head", "binary_digest", "workspace_tree_digest",
  "world_fingerprint", "source_index_fingerprint", "prompt_digest",
  "harness_build", "model_profile", "tool_profile_digest", "principal",
  "grant_profile_digest", "disclosure_profile_digest", "oracle_version"];
const DIGEST = /^sha256:[a-f0-9]{64}$/;
const HEAD = /^[a-f0-9]{40}$/;

function evaluate(group) {
  const invalid = [], unknown = [];
  const rows = group?.trials;
  if (!Array.isArray(rows) || rows.length !== 4) {
    return { verdict: "ineligible", invalid: ["four-independent-trials-required"], unknown: [],
      answerCorrectness:"not-evaluated", skillBenefit:"not-evaluated",
      note:"test-only metadata classification, not proof of actual observations" };
  }
  const arms = ["H2", "H3", "H3", "H2"];
  if (rows.some((r, i) => r?.arm !== arms[i])) invalid.push("counterbalanced-arm-order-mismatch");
  const sessions = rows.map(r => r?.session_id);
  if (sessions.some(s => typeof s !== "string" || !s.trim())) unknown.push("session-identity-unobserved");
  else if (new Set(sessions).size !== 4) invalid.push("session-reused");
  for (const key of SAME) {
    const values = rows.map(r => r?.[key]);
    if (values.some(v => typeof v !== "string" || !v)) unknown.push("missing-" + key);
    else if (new Set(values).size !== 1) invalid.push("pair-differs-" + key);
  }
  if (rows.every(r => typeof r?.repo_head === "string") &&
      rows.some(r => !HEAD.test(r.repo_head))) invalid.push("invalid-repository-revision");
  for (const key of ["binary_digest", "workspace_tree_digest", "prompt_digest",
                     "tool_profile_digest", "grant_profile_digest", "disclosure_profile_digest"]) {
    if (rows.every(r => typeof r?.[key] === "string") &&
        rows.some(r => !DIGEST.test(r[key]))) invalid.push("invalid-digest-" + key);
  }
  const h3 = rows.filter(r => r?.arm === "H3");
  if (h3.length === 2 && h3.every(r => typeof r.skill_activation === "string" && ["forced","auto"].includes(r.skill_activation))
      && h3[0].skill_activation !== h3[1].skill_activation) invalid.push("H3-activation-mode-mismatch");
  if (h3.length === 2 && h3.every(r => DIGEST.test(r.skill_package_digest || ""))
      && h3[0].skill_package_digest !== h3[1].skill_package_digest) invalid.push("H3-package-version-mismatch");
  for (const [i, row] of rows.entries()) {
    const id = "trial" + (i + 1);
    if (row.independent_session_observed === false || row.oracle_exposed === true ||
        row.unauthorized_write_observed === true || row.unauthorized_egress_observed === true) {
      invalid.push(id + "-experimental-boundary-violated");
    }
    if (row.independent_session_observed !== true) unknown.push(id + "-session-independence-unverified");
    if (row.oracle_exposed == null) unknown.push(id + "-oracle-exposure-unverified");
    if (row.tool_invocation_observed !== true || row.actual_cli_output_observed !== true)
      unknown.push(id + "-actual-tool-evidence-unobserved");
    if (row.grant_observed_at_invocation !== true || row.egress_scope_observed !== true)
      unknown.push(id + "-current-authority-or-egress-unobserved");
    if (row.arm === "H2") {
      if (row.skill_activation != null && row.skill_activation !== "none") invalid.push(id + "-H2-activation-not-none");
      if (row.skill_exposed === true || row.skill_loaded === true) invalid.push(id + "-H2-contaminated-by-skill");
      if (row.skill_exposed !== false || row.skill_loaded !== false)
        unknown.push(id + "-H2-skill-absence-unobserved");
    }
    if (row.arm === "H3") {
      if (!["forced","auto"].includes(row.skill_activation)) unknown.push(id + "-H3-activation-mode-unobserved");
      if (row.skill_loaded === false || row.skill_exposed === false)
        invalid.push(id + "-H3-skill-not-delivered");
      if (row.skill_loaded !== true || row.skill_exposed !== true ||
          !DIGEST.test(row.skill_package_digest || ""))
        unknown.push(id + "-H3-real-skill-load-unverified");
    }
  }
  // The output deliberately makes no assertion that the trial answers were correct.
  const verdict = invalid.length ? "ineligible" : unknown.length ? "insufficient-evidence" : "eligible-to-score";
  return {verdict, invalid:[...new Set(invalid)].sort(), unknown:[...new Set(unknown)].sort(),
    answerCorrectness:"not-evaluated", skillBenefit:"not-evaluated",
    note:"test-only metadata classification, not proof of actual observations"};
}
function seed() {
  const hash = x => "sha256:" + x.repeat(64);
  const common = {task_id:"public-reference-fixture-01",repo_head:"a".repeat(40),
    binary_digest:hash("1"), workspace_tree_digest:hash("2"),
    world_fingerprint:"public-world-A",source_index_fingerprint:"public-source-index-A",
    prompt_digest:hash("3"),harness_build:"mock-harness-v0",model_profile:"mock-model-fixed",
    tool_profile_digest:hash("4"),principal:"public-evaluator",
    grant_profile_digest:hash("5"),disclosure_profile_digest:hash("6"),
    oracle_version:"private-oracle-reference-v1"};
  return {trials:["H2","H3","H3","H2"].map((arm, i) => ({...common,arm,
    session_id:"independent-mock-session-" + i,independent_session_observed:true,
    oracle_exposed:false,unauthorized_write_observed:false,
    unauthorized_egress_observed:false,tool_invocation_observed:true,
    actual_cli_output_observed:true,grant_observed_at_invocation:true,
    egress_scope_observed:true,skill_exposed:arm === "H3",skill_loaded:arm === "H3",
    skill_activation:arm === "H3" ? "forced" : "none",
    ...(arm==="H3" ? {skill_package_digest:hash("7")} : {})}))};
}
function syntheticSelfTest() {
  const tests = [
    ["E01 eligible four-session counterbalanced public baseline", x=>x, "eligible-to-score"],
    ["E02 one-sided Source Index mutation", x=>{x.trials[1].source_index_fingerprint="other";return x;},"ineligible"],
    ["E03 model mismatch", x=>{x.trials[3].model_profile="another";return x;},"ineligible"],
    ["E04 one-sided authority mismatch", x=>{x.trials[2].grant_profile_digest="sha256:"+"9".repeat(64);return x;},"ineligible"],
    ["E05 reused session", x=>{x.trials[3].session_id=x.trials[0].session_id;return x;},"ineligible"],
    ["E06 H2 receives Skill", x=>{x.trials[0].skill_exposed=true;return x;},"ineligible"],
    ["E07 H3 never loaded Skill", x=>{x.trials[1].skill_loaded=false;return x;},"ineligible"],
    ["E08 H3 load not observable", x=>{delete x.trials[1].skill_loaded;return x;},"insufficient-evidence"],
    ["E09 model assertion without Tool trace", x=>{x.trials[2].tool_invocation_observed=false;return x;},"insufficient-evidence"],
    ["E10 missing actual egress scope", x=>{delete x.trials[0].egress_scope_observed;return x;},"insufficient-evidence"],
    ["E11 Oracle disclosed", x=>{x.trials[3].oracle_exposed=true;return x;},"ineligible"],
    ["E12 unauthorized local write", x=>{x.trials[1].unauthorized_write_observed=true;return x;},"ineligible"],
    ["E13 prompt differs", x=>{x.trials[0].prompt_digest="sha256:"+"8".repeat(64);return x;},"ineligible"],
    ["E14 no current-grant witness", x=>{delete x.trials[0].grant_observed_at_invocation;return x;},"insufficient-evidence"],
    ["E15 invalid repo HEAD", x=>{for(const r of x.trials)r.repo_head="not-a-real-commit";return x;},"ineligible"],
    ["E16 three trials only", x=>{x.trials.pop();return x;},"ineligible"],
    ["E17 one-sided World fingerprint mutation", x=>{x.trials[2].world_fingerprint="other-world";return x;},"ineligible"],
    ["E18 independent session not observed", x=>{delete x.trials[1].independent_session_observed;return x;},"insufficient-evidence"],
    ["E19 forced and auto skill activation mixed", x=>{x.trials[2].skill_activation="auto";return x;},"ineligible"],
    ["E20 H3 skill package changed", x=>{x.trials[2].skill_package_digest="sha256:"+"c".repeat(64);return x;},"ineligible"],
  ];
  const results=[];
  for(const [title,change,expected] of tests){
    const outcome=evaluate(change(seed()));
    assert.equal(outcome.verdict,expected,title);
    assert.equal(outcome.answerCorrectness,"not-evaluated");
    assert.equal(outcome.skillBenefit,"not-evaluated");
    results.push({case:title.split(" ")[0],verdict:outcome.verdict});
  }
  return {scope:"public synthetic comparator only; NO harness trial, Product Skill install, real TEI CLI, external egress or independent Oracle executed",
          passed:results.length,total:tests.length,results};
}
if (require.main===module) {
  if (process.argv[2]==="--self-test") console.log(JSON.stringify(syntheticSelfTest(),null,2));
  else if (process.argv[2]) {
    const obj=JSON.parse(fs.readFileSync(process.argv[2],"utf8"));
    console.log(JSON.stringify(evaluate(obj),null,2));
    if(evaluate(obj).verdict!=="eligible-to-score")process.exitCode=1;
  } else {console.error("usage: node check_sk02_pair_eligibility.cjs --self-test | path/to/trial-group.json");process.exitCode=2;}
}
module.exports={evaluate,syntheticSelfTest};
