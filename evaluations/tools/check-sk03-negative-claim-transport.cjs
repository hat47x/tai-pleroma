#!/usr/bin/env node
"use strict";
/*
 * SK-03 test-only transport/claim-loss experiment. Uses a real local Node child
 * process as a synthetic producer; it is NOT a TEI or AI Harness conformance run.
 * Source/Query/Host evidence semantics remain owned by the relevant Product.
 * Usage: node check-sk03-negative-claim-transport.cjs --self-test
 */
const assert = require("node:assert/strict");
const {spawnSync} = require("node:child_process");
// SK03_DUPLICATE_JSON_HARDENING_20261104: share the existing test-only JSON duplicate-member guard.
const {parseTrialJSON} = require("./check-sk02-pair-eligibility.cjs");

function producer(kind) {
  const meta = {
    scope: "authorized-population:orders", predicate: "status=open",
    sourceEpoch: "rev-1", sourceIndex: "index-1", cohort: "cohort-1",
    visibility: "authorized-population", coverage: "complete",
    nonOutputDependencies: ["membership-as-of"],
    warnings: [], unknown: []
  };
  if (kind === "partial") meta.coverage = "partial";
  if (kind === "hidden") meta.visibility = "subset-with-unknown-hidden-rows";
  if (kind === "warning") meta.warnings.push("source-relocation-needs-review");
  if (kind === "one") process.stdout.write(JSON.stringify({rows:[{id:"order-1"}],meta}));
  else if (kind === "broken") {process.stderr.write("simulated provider error\n");process.exitCode = 2;}
  else if (kind === "malformed") process.stdout.write('{"rows":[');
  else if (kind === "duplicate-coverage") {
    const raw=JSON.stringify({rows:[],meta});
    process.stdout.write(raw.replace('"coverage":"complete"',
      '"coverage":"partial","coverage":"complete"'));
  }
  else if (kind === "escaped-duplicate-coverage") {
    const raw=JSON.stringify({rows:[],meta});
    process.stdout.write(raw.replace('"coverage":"complete"',
      '"coverage":"partial","cover\\u0061ge":"complete"'));
  }
  else if (kind === "duplicate-rows") {
    const raw=JSON.stringify({rows:[],meta});
    process.stdout.write(raw.replace('"rows":[]',
      '"rows":[{"id":"a"}],"rows":[]'));
  }
  else process.stdout.write(JSON.stringify({rows:[],meta}));
}

function observe(kind) {
  const run = spawnSync(process.execPath,[__filename,"--producer",kind],
    {encoding:"utf8",shell:false,timeout:4000,maxBuffer:1024*1024});
  return {exit:run.status, signal:run.signal, error:run.error ? String(run.error) : null,
    stdout:run.stdout||"", stderr:run.stderr||""};
}

const keys = ["scope","predicate","sourceEpoch","sourceIndex","cohort",
  "visibility","coverage","nonOutputDependencies","warnings","unknown"];
function clone(v){return JSON.parse(JSON.stringify(v));}
function decode(run) {
  if (run.error || run.signal || run.exit !== 0) return {error:"producer-failed"};
  try {
    const value=parseTrialJSON(run.stdout);
    if (!value || !Array.isArray(value.rows) || !value.meta || typeof value.meta!=="object")
      return {error:"producer-unparseable"};
    return {value};
  } catch {return {error:"producer-unparseable"};}
}
function evaluate(run, projection, claim) {
  const actual=decode(run);
  if (actual.error) return actual.error;
  const {rows,meta}=actual.value;
  if (!projection || !Array.isArray(projection.rows) || !projection.meta)
    return "insufficient-evidence";
  if (JSON.stringify(rows)!==JSON.stringify(projection.rows)) return "evidence-mismatch";
  for (const key of keys) {
    if (!(key in projection.meta) || !(key in meta)) return "insufficient-evidence";
    if (JSON.stringify(projection.meta[key])!==JSON.stringify(meta[key]))
      return "evidence-mismatch";
  }
  if (claim.scope!==meta.scope || claim.predicate!==meta.predicate ||
      claim.sourceEpoch!==meta.sourceEpoch || claim.sourceIndex!==meta.sourceIndex)
    return "stale-or-different-binding";
  if (rows.length!==0) return "claim-contradicted";
  if (meta.coverage!=="complete" || meta.visibility!=="authorized-population" ||
      !meta.cohort || !Array.isArray(meta.nonOutputDependencies) ||
      meta.nonOutputDependencies.length===0 ||
      !Array.isArray(meta.unknown) || meta.unknown.length) return "insufficient-evidence";
  if (claim.quantification!=="within-authorized-population") return "insufficient-evidence";
  return "evidence-preserved-for-scoring";
}
function selfTest() {
  const valid=observe("complete");
  const projected=clone(decode(valid).value);
  const claim={scope:"authorized-population:orders",predicate:"status=open",
    sourceEpoch:"rev-1",sourceIndex:"index-1",
    quantification:"within-authorized-population"};
  const cases=[
    ["NC01 complete scoped empty",valid,clone(projected),clone(claim),"evidence-preserved-for-scoring"],
    ["NC02 empty partial",observe("partial"),null,clone(claim),"insufficient-evidence"],
    ["NC03 empty unknown hidden",observe("hidden"),null,clone(claim),"insufficient-evidence"],
    ["NC04 missing coverage in adapter",valid,((v)=>{delete v.meta.coverage;return v;})(clone(projected)),clone(claim),"insufficient-evidence"],
    ["NC05 missing negative dependencies",valid,((v)=>{delete v.meta.nonOutputDependencies;return v;})(clone(projected)),clone(claim),"insufficient-evidence"],
    ["NC06 adapter upgrades partial to complete",observe("partial"),((v)=>{v.meta.coverage="complete";return v;})(clone(projected)),clone(claim),"evidence-mismatch"],
    ["NC07 silent predicate replacement",valid,((v)=>{v.meta.predicate="status=closed";return v;})(clone(projected)),clone(claim),"evidence-mismatch"],
    ["NC08 warning erased by adapter",observe("warning"),clone(projected),clone(claim),"evidence-mismatch"],
    ["NC09 actual row contradicted",observe("one"),null,clone(claim),"claim-contradicted"],
    ["NC10 provider failure",observe("broken"),clone(projected),clone(claim),"producer-failed"],
    ["NC11 broken response",observe("malformed"),clone(projected),clone(claim),"producer-unparseable"],
    ["NC12 global absence from scoped view",valid,clone(projected),{...claim,quantification:"all-tenants"},"insufficient-evidence"],
    ["NC13 stale Source epoch",valid,clone(projected),{...claim,sourceEpoch:"rev-2"},"stale-or-different-binding"],
    ["NC14 same World value, SourceIndex moved",valid,clone(projected),{...claim,sourceIndex:"index-2"},"stale-or-different-binding"],
    ["NC15 Tool truncates output",{...valid,stdout:valid.stdout.slice(0,20)},clone(projected),clone(claim),"producer-unparseable"],
    ["NC16 no read cohort in source witness",valid,((v)=>{delete v.meta.cohort;return v;})(clone(projected)),clone(claim),"insufficient-evidence"],
    ["NC17 duplicate coverage overrides partial",observe("duplicate-coverage"),clone(projected),clone(claim),"producer-unparseable"],
    ["NC18 unicode escaped duplicate coverage",observe("escaped-duplicate-coverage"),clone(projected),clone(claim),"producer-unparseable"],
    ["NC19 duplicate root rows overrides witness",observe("duplicate-rows"),clone(projected),clone(claim),"producer-unparseable"],
  ];
  const results=[];
  for (const [name,run,p,requested,expected] of cases){
    const actualProjection=p??(decode(run).value ? clone(decode(run).value) : null);
    const received=evaluate(run,actualProjection,requested);
    assert.equal(received,expected,name);results.push({id:name.slice(0,4),result:received});
  }
  return {scope:"local Node child process with synthetic JSON only; no real TEI/Harness/Provider/Host/OS isolation/independent Product Oracle",
    node:process.version, uniqueProducerProfiles:[...new Set(["complete","partial","hidden","one","warning","broken","malformed"])].length,
    passed:results.length, total:cases.length,results};
}
if (require.main===module){
  if(process.argv[2]==="--producer") producer(process.argv[3]);
  else if(process.argv[2]==="--self-test") console.log(JSON.stringify(selfTest(),null,2));
  else {console.error("usage: node check-sk03-negative-claim-transport.cjs --self-test");process.exitCode=2;}
}
module.exports={evaluate,observe,decode,selfTest};
