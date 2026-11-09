#!/usr/bin/env node
"use strict";
// Public synthetic fixture and metamorphic checker, not a real YI Product/Harness test.
const fs = require("node:fs");
const path = require("node:path");

function impacted(graph, changed) {
  const known = new Set(graph.nodes);
  if (changed.some(id => !known.has(id))) throw new Error("unknown changed node");
  const reached = new Set(changed);
  let again = true;
  while (again) {
    again = false;
    for (const [from,to] of graph.edges) {
      if (!known.has(from) || !known.has(to)) throw new Error("invalid dependency edge");
      if (reached.has(from) && !reached.has(to)) { reached.add(to); again = true; }
    }
  }
  return [...reached].sort();
}
function handoff(s) {
  if (s.needsEffect && s.currentGrant !== true) return "effect-blocked";
  if (s.claimAck !== true) return "claim-unconfirmed";
  if (s.bodyPresent !== true) return "body-missing";
  if (s.bodyDigestMatches !== true) return "body-unverified";
  if (s.consumerRead !== true) return "consumer-not-observed";
  if (s.sourceEpochAligned !== true) return "joint-snapshot-unproved";
  if (s.scopeComplete !== true) return "scope-unproved";
  if (s.resultDisclosable !== true) return "result-withheld";
  if (s.ownerAccepted !== true) return "owner-unaccepted";
  return "qualified-fixture-only";
}
function sameSet(a,b) {
  return a.length === b.length && [...a].sort().every((v,i) => v === [...b].sort()[i]);
}
function check(fixture) {
  const seen = new Set(), results = [];
  for (const c of fixture.cases) {
    if (seen.has(c.id)) throw new Error("duplicate ID " + c.id);
    seen.add(c.id);
    if (c.mode === "impact") {
      const got = impacted(fixture.graph,c.changed);
      const expected = c.expectedAffected;
      const preserved = c.expectedPreserved;
      results.push({id:c.id,passed:sameSet(got,expected) && preserved.every(x => !got.includes(x)),actual:got});
    } else if (c.mode === "handoff") {
      const got = handoff(c.state);
      results.push({id:c.id,passed:got === c.expectedStatus,actual:got});
    } else throw new Error("unknown mode " + c.mode);
  }
  return {results,passed:results.filter(x=>x.passed).length,failed:results.filter(x=>!x.passed).length};
}
function copy(data) { return JSON.parse(JSON.stringify(data)); }
function mutations(original) {
  const trials=[];
  const a=copy(original);
  a.graph.edges=a.graph.edges.filter(e=>!(e[0]==="provider-binding"&&e[1]==="provider-read"));
  trials.push({name:"remove-relevant-dependency",detected:check(a).failed>0});
  const b=copy(original);
  b.cases.find(x=>x.id==="SK-C12").expectedStatus="claim-completed";
  trials.push({name:"fabricate-acceptance",detected:check(b).failed>0});
  const c=copy(original);
  c.cases.find(x=>x.id==="SK-C07").state.currentGrant=true;
  trials.push({name:"flip-grant-without-revising-expectation",detected:check(c).failed>0});
  const d=copy(original);
  d.graph.edges.push(["sho-index-title","tei-target"]);
  trials.push({name:"invent-extra-dependency",detected:check(d).failed>0});
  return trials;
}
function run() {
  const file=process.argv[2]||path.join(__dirname,"../fixtures/SK-C-continuation-requalification.synthetic.json");
  const fixture=JSON.parse(fs.readFileSync(file,"utf8"));
  const r=check(fixture);
  const m=mutations(fixture);
  const output={
    scope:"PUBLIC SYNTHETIC ONLY; actual Product, Host, EKI, TEI, SEI, SHO, TAI Skill, Oracle NOT RUN",
    fixture:fixture.schema,
    passed:r.passed,failed:r.failed,
    mutationChecks:m.map(x=>({name:x.name,detected:x.detected})),
    results:r.results
  };
  process.stdout.write(JSON.stringify(output,null,2)+"\n");
  if (r.failed || m.some(x=>!x.detected)) process.exitCode=1;
}
if(require.main===module)run();
module.exports={check,handoff,impacted,mutations};
