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
const crypto = require("node:crypto");

const SAME = ["task_id", "repo_head", "binary_digest", "workspace_tree_digest",
  "world_fingerprint", "source_index_fingerprint", "prompt_digest",
  "harness_build", "model_profile", "tool_profile_digest", "principal",
  "grant_profile_digest", "disclosure_profile_digest", "oracle_version", "cli_cwd"];
const DIGEST = /^sha256:[a-f0-9]{64}$/;
const HEAD = /^[a-f0-9]{40}$/;
// The pre-registered Task is deliberately bound for this FIRST SK-02 Product pilot.
// A different Task belongs in a new trial group and a separately reviewed pin.
const PRE_REGISTERED_PARTICIPANT_TASK = "sha256:38a0b238018e050f2116f10f1ca2cb3a54319c2743e2fb9bbe128d4be96a84cf";


// A trial-group file is untrusted input, including when AI generated it.
// JSON.parse alone accepts repeated object keys and silently keeps the last.
// Scan valid JSON strings and object scopes to reject that ambiguity before
// interpreting any observed_* claim. Test-only; not a Product JSON parser.
function parseTrialJSON(raw) {
  let result;
  try { result = JSON.parse(raw); }
  catch {
    const error = new Error("invalid trial JSON syntax");
    error.code = "INVALID_TRIAL_JSON";
    throw error;
  }
  const scopes = [];
  for (let i = 0; i < raw.length;) {
    const c = raw[i];
    if (c === '"') {
      const start = i++;
      while (i < raw.length) {
        if (raw[i] === "\\") { i += 2; continue; }
        if (raw[i] === '"') { i++; break; }
        i++;
      }
      const value = JSON.parse(raw.slice(start, i));
      let next = i;
      while (next < raw.length && /\s/u.test(raw[next])) next++;
      const scope = scopes[scopes.length - 1];
      if (scope?.kind === "object" && raw[next] === ":") {
        if (scope.keys.has(value)) {
          const error = new Error("duplicate JSON member at byte/char position " + start);
          error.code = "DUPLICATE_TRIAL_JSON_MEMBER";
          throw error;
        }
        scope.keys.add(value);
      }
      continue;
    }
    if (c === "{") scopes.push({kind:"object",keys:new Set()});
    else if (c === "[") scopes.push({kind:"array"});
    else if (c === "}" || c === "]") scopes.pop();
    i++;
  }
  return result;
}


/**
 * SK-02 covers a restricted TEI read-only CLI task.
 * This checks stated argv family, NOT actual process observation, Product effects,
 * Host authorization, OS containment, or all of TEI's available commands.
 */
function readOnlyCommandFamily(argv) {
  if (!Array.isArray(argv) || argv.length < 2 ||
      argv.some(t => typeof t !== "string" || t.length === 0)) return "unobserved";
  if (!/(?:^|[\\/])tei(?:\.exe)?$/iu.test(argv[0])) return "outside-tool-profile";
  if (argv.slice(1).some(t => /^(?:--?out)(?:=|$)/u.test(t))) return "write-option-not-allowed";
  if (argv[1] === "version" || argv[1] === "commands" ||
      argv[1] === "inspect" || argv[1] === "trace" || argv[1] === "validate") return "allowed-family";
  if (argv[1] === "model" && argv[2] === "catalog") return "allowed-family";
  // operations/artifacts exist in TEI but are outside this initial selected scope.
  return "outside-initial-readonly-profile";
}

/**
 * SK-02's first task uses one workspace. The selected CLI catalog is NOT a
 * guarantee that two recorded invocations selected the same source root.
 * This is an argv-shape and literal binding check, not a filesystem/Loader proof.
 */
function recordedWorkspace(argv) {
  const scoped = argv?.[1] === "inspect" || argv?.[1] === "trace" ||
    argv?.[1] === "validate" || (argv?.[1] === "model" && argv?.[2] === "catalog");
  if (!scoped) return {status:"not-needed"};
  const args = argv.slice(argv[1] === "model" ? 3 : 2);
  const workspaces = [];
  for (let i = 0; i < args.length; i++) {
    const t = args[i];
    if (t === "-world" || t === "--world" ||
        t.startsWith("-world=") || t.startsWith("--world="))
      return {status:"world-outside-initial-profile"};
    if (t === "-workspace" || t === "--workspace") {
      workspaces.push(args[i + 1]);
      i++;
    } else if (t.startsWith("-workspace=") || t.startsWith("--workspace=")) {
      workspaces.push(t.slice(t.indexOf("=") + 1));
    }
  }
  if (workspaces.length > 1) return {status:"ambiguous-workspace-argv"};
  if (!workspaces.length || typeof workspaces[0] !== "string" ||
      !workspaces[0].trim() || workspaces[0].startsWith("-"))
    return {status:"workspace-argv-unobserved"};
  return {status:"bound",value:workspaces[0]};
}

function evaluate(group, options = {}) {
  const invalid = [], unknown = [];
  const rows = group?.trials;
  if (!Array.isArray(rows) || rows.length !== 4) {
    return { verdict: "ineligible", invalid: ["four-independent-trials-required"], unknown: [],
      answerCorrectness:"not-evaluated", skillBenefit:"not-evaluated",
      note:"test-only metadata classification, not proof of actual observations" };
  }
  // The same wrong prompt can be used in every arm, making SAME pass.
  // Only a separately supplied, raw-byte Task pin can establish the intended
  // participant prompt. This is not evidence that the Harness received it.
  if (Object.prototype.hasOwnProperty.call(options,"expectedPromptDigest")) {
    if (options.expectedPromptDigest === null) {
      unknown.push("participant-task-raw-not-bound");
    } else if (!DIGEST.test(options.expectedPromptDigest)) {
      invalid.push("invalid-expected-participant-task-digest");
    } else if (options.expectedPromptDigest !== PRE_REGISTERED_PARTICIPANT_TASK) {
      invalid.push("participant-task-not-preregistered");
    } else if (rows.some(r => r?.prompt_digest !== options.expectedPromptDigest)) {
      invalid.push("participant-task-digest-mismatch");
    }
  }
  // Malformed JSON trial rows must receive a verdict, not crash the checker.
  if (rows.some(r => r === null || typeof r !== "object" || Array.isArray(r))) {
    return {verdict:"ineligible", invalid:["invalid-trial-record"], unknown:[],
      answerCorrectness:"not-evaluated", skillBenefit:"not-evaluated",
      note:"test-only metadata classification, not proof of actual observations"};
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
  const readWorkspaceBindings = [];
  for (const [i, row] of rows.entries()) {
    const id = "trial" + (i + 1);
    if (row.independent_session_observed === false || row.oracle_exposed === true ||
        row.unauthorized_write_observed === true || row.unauthorized_egress_observed === true) {
      invalid.push(id + "-experimental-boundary-violated");
    }
    if (row.independent_session_observed !== true) unknown.push(id + "-session-independence-unverified");
    // JSON strings "false"/"true", 0, objects, etc. are NOT boolean observations.
    // In particular, "false" must not silently count as "no unauthorized effect".
    if (typeof row.oracle_exposed !== "boolean") unknown.push(id + "-oracle-exposure-unverified");
    if (typeof row.unauthorized_write_observed !== "boolean") unknown.push(id + "-write-observer-missing");
    if (typeof row.unauthorized_egress_observed !== "boolean") unknown.push(id + "-egress-observer-missing");
    if (!Array.isArray(row.cli_invocations) || row.cli_invocations.length === 0) {
      unknown.push(id + "-actual-cli-invocations-unobserved");
    } else {
      const withinTrial = new Set();
      for (const argv of row.cli_invocations) {
        const family = readOnlyCommandFamily(argv);
        if (family === "unobserved") {unknown.push(id + "-cli-argv-unobserved");continue;}
        if (family !== "allowed-family") {
          invalid.push(id + "-cli-" + family);continue;
        }
        const binding = recordedWorkspace(argv);
        if (binding.status === "bound") withinTrial.add(binding.value);
        else if (binding.status === "world-outside-initial-profile" ||
                 binding.status === "ambiguous-workspace-argv")
          invalid.push(id + "-" + binding.status);
        else if (binding.status === "workspace-argv-unobserved")
          unknown.push(id + "-workspace-argv-unobserved");
      }
      if (withinTrial.size > 1) invalid.push(id + "-mixed-actual-workspaces");
      if (withinTrial.size === 0) unknown.push(id + "-workspace-read-unobserved");
      else if (withinTrial.size === 1) readWorkspaceBindings.push([...withinTrial][0]);
    }
    if (row.tool_invocation_observed !== true || row.actual_cli_output_observed !== true)
      unknown.push(id + "-actual-tool-evidence-unobserved");
    if (row.grant_observed_at_invocation !== true || row.egress_scope_observed !== true)
      unknown.push(id + "-current-authority-or-egress-unobserved");
    if (row.arm === "H2") {
      if (row.skill_activation == null) unknown.push(id + "-H2-activation-unverified");
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
  // A shared workspace digest in a JSON ticket cannot substitute for the argv
  // that the real CLI was asked to read. Literal equality is a necessary but
  // not sufficient condition: cli_cwd, symlinks and actual loaded bytes still
  // require a separate real process/Source observer.
  if (new Set(readWorkspaceBindings).size > 1)
    invalid.push("pair-differs-actual-workspace-argv");
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
    tool_profile_digest:hash("4"),principal:"public-evaluator",cli_cwd:"/fixture/tei",
    grant_profile_digest:hash("5"),disclosure_profile_digest:hash("6"),
    oracle_version:"private-oracle-reference-v1"};
  return {trials:["H2","H3","H3","H2"].map((arm, i) => ({...common,arm,
    session_id:"independent-mock-session-" + i,independent_session_observed:true,
    oracle_exposed:false,unauthorized_write_observed:false,
    unauthorized_egress_observed:false,tool_invocation_observed:true,
    actual_cli_output_observed:true,grant_observed_at_invocation:true,
    cli_invocations:[["/tmp/tei","commands"],
      ["/tmp/tei","model","catalog","-workspace","reference/workspace"],
      ["/tmp/tei","validate","-workspace","reference/workspace","-json"]],
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
    ["E21 missing write observation", x=>{delete x.trials[0].unauthorized_write_observed;return x;},"insufficient-evidence"],
    ["E22 missing egress observation", x=>{delete x.trials[1].unauthorized_egress_observed;return x;},"insufficient-evidence"],
    ["E23 missing CLI argv", x=>{delete x.trials[2].cli_invocations;return x;},"insufficient-evidence"],
    ["E24 artifacts output writes locally", x=>{x.trials[1].cli_invocations.push(["tei","artifacts","-out","build"]);return x;},"ineligible"],
    ["E25 operations exists but not in selected discovery", x=>{x.trials[0].cli_invocations.push(["tei","operations"]);return x;},"ineligible"],
    ["E26 artifacts stdout still outside initial profile", x=>{x.trials[3].cli_invocations.push(["tei","artifacts"]);return x;},"ineligible"],
    ["E27 Windows TEI executable path accepted", x=>{x.trials[1].cli_invocations.push(["C:\\bin\\tei.exe","inspect","-workspace","reference/workspace"]);return x;},"eligible-to-score"],
    ["E28 different allowed read-only commands", x=>{x.trials[2].cli_invocations.push(["tei","trace","-workspace","reference/workspace"]);return x;},"eligible-to-score"],
    ["E29 missing H2 activation witness", x=>{delete x.trials[0].skill_activation;return x;},"insufficient-evidence"],
    ["E30 non TEI command outside profile", x=>{x.trials[2].cli_invocations.push(["curl","https://example.invalid"]);return x;},"ineligible"],
    ["E31 out flag on otherwise allowed command", x=>{x.trials[1].cli_invocations.push(["tei","validate","--out=/tmp/result"]);return x;},"ineligible"],
    ["E32 malformed actual CLI invocation", x=>{x.trials[3].cli_invocations.push(null);return x;},"insufficient-evidence"],
    ["E33 string false oracle exposure not a boolean witness", x=>{x.trials[0].oracle_exposed="false";return x;},"insufficient-evidence"],
    ["E34 string false write observation not a boolean witness", x=>{x.trials[1].unauthorized_write_observed="false";return x;},"insufficient-evidence"],
    ["E35 numeric zero egress observation not a boolean witness", x=>{x.trials[2].unauthorized_egress_observed=0;return x;},"insufficient-evidence"],
    ["E36 null trial is rejected without crashing", x=>{x.trials[1]=null;return x;},"ineligible"],
    ["E37 array trial is rejected without crashing", x=>{x.trials[3]=[];return x;},"ineligible"],
    ["E38 string true oracle exposure is not silent PASS", x=>{x.trials[2].oracle_exposed="true";return x;},"insufficient-evidence"],
    ["E39 real boolean false remains declared comparable", x=>{x.trials[2].oracle_exposed=false;return x;},"eligible-to-score"],
    ["E40 real boolean true unauthorized egress invalidates", x=>{x.trials[3].unauthorized_egress_observed=true;return x;},"ineligible"],
    ["E41 mixed string false observations all insufficient", x=>{x.trials[0].oracle_exposed="false";x.trials[0].unauthorized_write_observed="false";x.trials[0].unauthorized_egress_observed="false";return x;},"insufficient-evidence"],
    ["E49 missing cli cwd witness", x=>{delete x.trials[0].cli_cwd;return x;},"insufficient-evidence"],
    ["E50 different cli cwd across arms", x=>{x.trials[2].cli_cwd="/fixture/other";return x;},"ineligible"],
    ["E51 different workspace argv despite matching declared digests", x=>{x.trials[1].cli_invocations[1][4]="other/workspace";return x;},"ineligible"],
    ["E52 one read with missing workspace flag", x=>{x.trials[0].cli_invocations[2]=["tei","validate","-json"];return x;},"insufficient-evidence"],
    ["E53 duplicate workspace flags on one invocation", x=>{x.trials[1].cli_invocations[2].push("-workspace","reference/workspace");return x;},"ineligible"],
    ["E54 two valid workspace flags to different roots within trial", x=>{x.trials[0].cli_invocations.push(["tei","inspect","-workspace","other/workspace"]);return x;},"ineligible"],
    ["E55 world file outside initial workspace profile", x=>{x.trials[1].cli_invocations[2]=["tei","validate","-world","other.json"];return x;},"ineligible"],
    ["E56 workspace equals syntax accepted", x=>{x.trials[0].cli_invocations[2]=["tei","validate","-workspace=reference/workspace","-json"];return x;},"eligible-to-score"],
    ["E57 commands without an actual scoped read are insufficient", x=>{x.trials[0].cli_invocations=[["tei","commands"]];return x;},"insufficient-evidence"],
    ["E58 workspace flag with option instead of path", x=>{x.trials[1].cli_invocations[2]=["tei","validate","-workspace","-json"];return x;},"insufficient-evidence"],
    ["E59 double dash workspace syntax accepted", x=>{x.trials[2].cli_invocations[2]=["tei","validate","--workspace","reference/workspace","-json"];return x;},"eligible-to-score"],
    ["E60 different workspace across one arm despite same workspace hash", x=>{x.trials[3].cli_invocations=x.trials[3].cli_invocations.map(a=>a.map(t=>t==="reference/workspace"?"alternative/workspace":t));return x;},"ineligible"],
  ];
  const results=[];
  for(const [title,change,expected] of tests){
    const outcome=evaluate(change(seed()));
    assert.equal(outcome.verdict,expected,title);
    assert.equal(outcome.answerCorrectness,"not-evaluated");
    assert.equal(outcome.skillBenefit,"not-evaluated");
    results.push({case:title.split(" ")[0],verdict:outcome.verdict});
  }
  // These test the actual JSON text ingestion, which evaluate(object) cannot see.
  // A duplicate field can override an observed violation before evaluate() runs.
  const jsonSeed = JSON.stringify(seed());
  const rawTests = [
    ["E42 root trials duplicated", '{"trials":[],"trials":' + JSON.stringify(seed().trials) + '}', "DUPLICATE_TRIAL_JSON_MEMBER"],
    ["E43 egress observation overwritten", jsonSeed.replace('"unauthorized_egress_observed":false', '"unauthorized_egress_observed":true,"unauthorized_egress_observed":false'), "DUPLICATE_TRIAL_JSON_MEMBER"],
    ["E44 unicode escaped duplicate key", jsonSeed.replace('"oracle_exposed":false', '"oracle_exposed":false,"oracle_expos\\u0065d":true'), "DUPLICATE_TRIAL_JSON_MEMBER"],
    ["E45 unknown nested object also rejects duplicates", jsonSeed.replace(/}$/, ',"extra":{"a":1,"a":2}}'), "DUPLICATE_TRIAL_JSON_MEMBER"],
    ["E46 same field in separate trial objects remains valid", jsonSeed, "valid"],
    ["E47 malformed JSON rejected", '{"trials":,}', "INVALID_TRIAL_JSON"],
    ["E48 Skill load overridden to false", jsonSeed.replace('"skill_loaded":true', '"skill_loaded":false,"skill_loaded":true'), "DUPLICATE_TRIAL_JSON_MEMBER"],
  ];
  for (const [title, raw, expected] of rawTests) {
    if (expected === "valid") {
      assert.equal(evaluate(parseTrialJSON(raw)).verdict, "eligible-to-score", title);
    } else {
      assert.throws(() => parseTrialJSON(raw), e => e.code === expected, title);
    }
    results.push({case:title.split(" ")[0],verdict:expected});
  }
  return {scope:"public synthetic comparator only; NO harness trial, Product Skill install, real TEI CLI, external egress or independent Oracle executed",
          passed:results.length,total:results.length,results};
}
if (require.main===module) {
  if (process.argv[2]==="--self-test") console.log(JSON.stringify(syntheticSelfTest(),null,2));
  else if (process.argv[2]) {
    try {
      if(process.argv.length !== 3 && !(process.argv.length===5 && process.argv[3]==="--task-file"))
        throw Object.assign(new Error("usage: checker trial.json --task-file participant-task.txt"),{code:"INVALID_CLI_ARGUMENTS"});
      const obj=parseTrialJSON(fs.readFileSync(process.argv[2],"utf8"));
      const taskPath=process.argv[3]==="--task-file" ? process.argv[4] : null;
      const expectedPromptDigest=taskPath
        ? "sha256:"+crypto.createHash("sha256").update(fs.readFileSync(taskPath)).digest("hex")
        : null;
      const outcome=evaluate(obj,{expectedPromptDigest});
      console.log(JSON.stringify(outcome,null,2));
      if(outcome.verdict!=="eligible-to-score")process.exitCode=1;
    } catch (e) {
      console.log(JSON.stringify({verdict:"ineligible",
        invalid:[e.code || "INVALID_TRIAL_FILE"], unknown:[],
        answerCorrectness:"not-evaluated",skillBenefit:"not-evaluated",
        note:"trial file rejected before scoring; no Product/Harness observations verified"},null,2));
      process.exitCode=1;
    }
  } else {console.error("usage: node check_sk02_pair_eligibility.cjs --self-test | path/to/trial-group.json");process.exitCode=2;}
}
module.exports={evaluate,recordedWorkspace,parseTrialJSON,syntheticSelfTest,syntheticSeed:seed};
