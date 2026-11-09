#!/usr/bin/env node
"use strict";
// PUBLIC SYNTHETIC ONLY. Claim-relative evidence and handoff qualification;
// not TEI, SHO, EKI, TAI, DB, OS, or a general dependency validator.
const assert = require("node:assert/strict");

const base = Object.freeze({
  dependencies: ["field:amount", "predicate:hidden_flag", "rule:credit_limit",
    "provider:route", "artifact:required_members", "role:operator"],
  dependencyCoverageVerified: true,
  changed: [],
  requiredCohort: true, cohortProven: true,
  requiredReadWitness: true, readWitnessProven: true,
  requiredArtifact: true, requiredMembersKnown: true, artifactMemberBytesVerified: true,
  requiredAttemptBody: true, claimAck: true, bodyReceivedForSameAttempt: true,
  requiredEgress: false, currentEgressAllowed: true,
  requiredEffect: false, currentEffectGrant: true,
  ownerMeaningAccepted: true,
  outputDigest: "unchanged-fixture-output"
});

function qualification(input) {
  const s = { ...base, ...input };
  const impact = s.dependencyCoverageVerified !== true ? "unknown-dependencies"
    : s.changed.some(k => s.dependencies.includes(k)) ? "requalify-dependency"
    : "reusable-dependency-evidence";
  const blockers = [];
  if (s.requiredCohort && s.cohortProven !== true) blockers.push("cohort-unproved");
  if (s.requiredReadWitness && s.readWitnessProven !== true) blockers.push("read-witness-unproved");
  if (s.requiredArtifact && s.requiredMembersKnown !== true) blockers.push("required-members-unknown");
  if (s.requiredArtifact && s.artifactMemberBytesVerified !== true) blockers.push("artifact-bytes-unverified");
  if (s.requiredAttemptBody && (s.claimAck !== true || s.bodyReceivedForSameAttempt !== true)) blockers.push("attempt-body-unreceived");
  if (s.requiredEgress && s.currentEgressAllowed !== true) blockers.push("egress-not-authorized");
  if (s.requiredEffect && s.currentEffectGrant !== true) blockers.push("effect-not-authorized");
  if (s.ownerMeaningAccepted !== true) blockers.push("meaning-not-accepted");
  return { impact, blockers, currentlyReusable: impact === "reusable-dependency-evidence" && blockers.length === 0 };
}

const cases = [
  ["QH-01 baseline scoped reuse", {}, "reusable-dependency-evidence", []],
  ["QH-02 unrelated SHO title", {changed:["sho:title"]}, "reusable-dependency-evidence", []],
  ["QH-03 hidden WHERE unchanged output", {changed:["predicate:hidden_flag"]}, "requalify-dependency", []],
  ["QH-04 credit limit hidden Rule", {changed:["rule:credit_limit"]}, "requalify-dependency", []],
  ["QH-05 provider route changes", {changed:["provider:route"]}, "requalify-dependency", []],
  ["QH-06 Consumer required members change", {changed:["artifact:required_members"]}, "requalify-dependency", []],
  ["QH-07 Role/Operator revision", {changed:["role:operator"]}, "requalify-dependency", []],
  ["QH-08 unknown dependency coverage", {changed:["unresolved:predicate"],dependencyCoverageVerified:false}, "unknown-dependencies", []],
  ["QH-09 same snapshot label no cohort proof", {cohortProven:false}, "reusable-dependency-evidence", ["cohort-unproved"]],
  ["QH-10 same result unknown Read Trace", {readWitnessProven:false}, "reusable-dependency-evidence", ["read-witness-unproved"]],
  ["QH-11 Manifest complete unknown required set", {requiredMembersKnown:false}, "reusable-dependency-evidence", ["required-members-unknown"]],
  ["QH-12 artifact bytes changed after Manifest", {artifactMemberBytesVerified:false}, "reusable-dependency-evidence", ["artifact-bytes-unverified"]],
  ["QH-13 Claim ACK without same Attempt Body", {bodyReceivedForSameAttempt:false}, "reusable-dependency-evidence", ["attempt-body-unreceived"]],
  ["QH-14 egress permission revoked", {requiredEgress:true,currentEgressAllowed:false}, "reusable-dependency-evidence", ["egress-not-authorized"]],
  ["QH-15 effect Grant revoked", {requiredEffect:true,currentEffectGrant:false}, "reusable-dependency-evidence", ["effect-not-authorized"]],
  ["QH-16 Owner meaning not accepted", {ownerMeaningAccepted:false}, "reusable-dependency-evidence", ["meaning-not-accepted"]],
  ["QH-17 multiple independent missing proofs", {requiredMembersKnown:false,cohortProven:false,requiredEgress:true,currentEgressAllowed:false}, "reusable-dependency-evidence", ["cohort-unproved", "required-members-unknown", "egress-not-authorized"]],
  ["QH-18 unresolved change plus unavailable Body", {dependencyCoverageVerified:false,bodyReceivedForSameAttempt:false}, "unknown-dependencies", ["attempt-body-unreceived"]]
];

function run() {
  let passed = 0, naiveFalseReuse = 0;
  const results = [];
  for (const [id, changes, impact, blockers] of cases) {
    const actual = qualification(changes);
    assert.equal(actual.impact, impact, id);
    assert.deepEqual(actual.blockers, blockers, id);
    assert.equal(actual.currentlyReusable, impact === "reusable-dependency-evidence" && blockers.length === 0, id);
    // J2 intentionally reuses whenever the displayed output bytes are unchanged.
    if (!actual.currentlyReusable) naiveFalseReuse++;
    results.push({id, impact:actual.impact, blockers:actual.blockers, eligible:actual.currentlyReusable});
    passed++;
  }
  // Mutation pressure: dropping a hidden predicate from the supposedly closed graph
  // changes the answer. A real product MUST independently establish dependency coverage.
  const hidden = qualification({changed:["predicate:hidden_flag"]});
  const dropped = qualification({changed:["predicate:hidden_flag"], dependencies: base.dependencies.filter(x=>x!=="predicate:hidden_flag")});
  assert.equal(hidden.impact,"requalify-dependency");
  assert.equal(dropped.impact,"reusable-dependency-evidence");
  return {scope:"synthetic public reference / no product or security proof", passed, total:cases.length,
    mutationWarning:"dropping an unobserved dependency gives false reuse even when the fixture says coverage verified",
    naiveJ2FalseReuse:naiveFalseReuse, results};
}
if (require.main === module) process.stdout.write(JSON.stringify(run(), null, 2)+"\n");
module.exports={qualification,run};
