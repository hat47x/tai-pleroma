#!/usr/bin/env node
"use strict";
/*
 * TAI S1: invoke one REAL, fixed TEI Go CLI against a public TEI checkout.
 * Not an AI Harness test, Source closure proof, Owner acceptance, or safety audit.
 * Run: node evaluations/tools/probe-tei-s1-real-source.cjs <tei-binary> <tei-checkout>
 */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const crypto = require("node:crypto");
const {spawnSync} = require("node:child_process");
// Reuse SK-02 test-only JSON duplicate-member rejection at the evidence boundary.
const {parseTrialJSON} = require("./check-sk02-pair-eligibility.cjs");

const digest = bytes => "sha256:" + crypto.createHash("sha256").update(bytes).digest("hex");
const SUBJECT = {kind:"semantic-data", id:"sales.order"};
const SOURCE = "semantic/sales/order.tei";
function run(file, args, cwd) {
  const p = spawnSync(file, args, {
    cwd, encoding:"utf8", maxBuffer:8*1024*1024,
    timeout:120000, shell:false, env:process.env
  });
  if(p.error) throw p.error;
  if(p.status !== 0) throw new Error("CLI failure [" + args.join(" ") + "]: exit=" + p.status + " stderr=" + p.stderr.slice(0,900) + " stdout=" + p.stdout.slice(0,900));
  return {argv:[file,...args],cwd,exit:p.status,stdout:p.stdout,stderr:p.stderr,stdoutDigest:digest(Buffer.from(p.stdout))};
}
function jsonOf(call) {
  try {return parseTrialJSON(call.stdout);}
  catch(e){throw new Error("non-JSON result [" + call.argv.slice(1).join(" ") + "]: " + e.message);}
}
// Bind an independently-read byte fingerprint to the actual TEI Index
// artifact and subject's definition reference. Both must come from Inspect,
// not just from a separately selected file or a catalog name.
function qualifySubjectSource(result, expectedPath, expectedFingerprint) {
  assert.deepEqual(result?.subject, SUBJECT, "Inspect resolved a different canonical subject");
  assert.equal(result?.sourceStatus, "indexed", "subject needs an indexed source witness");
  const artifacts = result?.sources?.artifacts;
  const refs = result?.sources?.references;
  assert.ok(Array.isArray(artifacts) && Array.isArray(refs), "Inspect source witness missing");
  const selected = artifacts.filter(x => x?.path === expectedPath);
  assert.equal(selected.length, 1, "expected exactly one Source Index artifact for requested file");
  assert.equal(selected[0].fingerprint, expectedFingerprint,
    "the bytes indexed by Product CLI differ from the independent source read");
  const definitions = refs.filter(x => x?.artifactPath === expectedPath &&
    x?.subject?.kind === SUBJECT.kind && x?.subject?.id === SUBJECT.id &&
    x?.role === "definition");
  assert.ok(definitions.length > 0, "no canonical definition reference to expected file");
  return {artifactPath:expectedPath,artifactFingerprint:selected[0].fingerprint,
    definitionReferences:definitions.length, sourceStatus:result.sourceStatus};
}

// The evidence ledger is a reviewed, pinned public S1 baseline, not a signed
// attestation. Comparing a fresh real CLI receipt detects drift of claimed
// observed bytes, bindings, and diagnostics without pretending to validate
// external Harness behavior or Owner Meaning.
function verifyLedger(ledger, receipt) {
  let compared=0;
  const eq = (key, actual, expected) => {
    assert.deepStrictEqual(actual, expected, "ledger mismatch: " + key);
    compared++;
  };
  eq("receipt schema",receipt.schema,"tai.s1.real-tei-public-read/v0");
  eq("TEI repository",ledger.source.repo,"hat47x/tei-platform");
  eq("pinned commit",receipt.teiCommit,ledger.source.commit);
  eq("source path",receipt.source,ledger.source.path);
  eq("source bytes",receipt.sourceDigest,"sha256:"+ledger.source.sha256);
  eq("compiled binary bytes",receipt.binaryDigest,"sha256:"+ledger.build.binary_sha256);
  eq("subject",receipt.subject,ledger.source.subject);
  eq("catalog matches",receipt.catalogMatches,ledger.actualRead.catalogMatches);
  eq("catalog source status",receipt.catalogSourceStatus,ledger.actualRead.catalogSourceStatus);
  eq("inspect success",receipt.inspectedJson,ledger.actualRead.inspectOk);
  eq("validate success",receipt.validationOk,ledger.actualRead.validateOk);
  eq("diagnostic count",receipt.diagnostics,ledger.actualRead.diagnosticsCount);
  eq("empty root has no user Subject",receipt.negative.userSubjectLoaded,false);
  eq("empty root validate",receipt.negative.validationOk,ledger.negativeControl.validateOk);
  eq("empty root standard entries",receipt.negative.stdEntries,ledger.negativeControl.observedStdEntries);
  const witness=ledger.indexedSourceBinding.productInspect;
  eq("Source Index subject",receipt.subject,witness.subject);
  eq("Source Index file",receipt.sourceWitness.artifactPath,witness.artifactPath);
  eq("Source Index file bytes",receipt.sourceWitness.artifactFingerprint,witness.artifactFingerprint);
  eq("Source Index definition references",receipt.sourceWitness.definitionReferences,witness.definitionReferences);
  eq("Source Index status",receipt.sourceWitness.sourceStatus,witness.sourceStatus);
  eq("World fingerprint",receipt.worldFingerprint,witness.worldFingerprint);
  eq("Source Index fingerprint",receipt.sourceIndexFingerprint,witness.sourceIndexFingerprint);
  eq("four actual selected command calls",receipt.observations.length,4);
  for(const [i,key] of ["commands","catalog","inspect","validate"].entries()){
    eq("stdout digest of "+key,receipt.observations[i].stdoutDigest,
      "sha256:"+ledger.actualRead.stdoutSha256[key]);
    eq("CLI exit of "+key,receipt.observations[i].exit,0);
  }
  assert.ok(receipt.notEstablished.includes("H2/H3 four independent sessions"));
  return {scope:"pinned public TEI Product S1 ledger-to-fresh-CLI-receipt",
    compared,verdict:"matching-bounded-S1-evidence",
    notQualified:["external Harness/Skill","Business Oracle","Owner Meaning","actual Host/Provider effects"]};
}

function selfTest() {
  const fp = digest(Buffer.from("fixture"));
  const good = () => ({subject:{...SUBJECT},sourceStatus:"indexed",sources:{
    artifacts:[{path:SOURCE,format:"tei",fingerprint:fp}],
    references:[{artifactPath:SOURCE,subject:{...SUBJECT},role:"definition"}]
  }});
  const tests = [
    ["S1-W01 actual artifact and definition match", () => qualifySubjectSource(good(),SOURCE,fp)],
    ["S1-W02 relocated artifact cannot masquerade", () => {const x=good();x.sources.artifacts[0].path="semantic/other/order.tei";qualifySubjectSource(x,SOURCE,fp);},true],
    ["S1-W03 stale Source bytes cannot qualify", () => qualifySubjectSource(good(),SOURCE,digest(Buffer.from("changed"))),true],
    ["S1-W04 reference to a different file is not provenance", () => {const x=good();x.sources.references[0].artifactPath="semantic/other/order.tei";qualifySubjectSource(x,SOURCE,fp);},true],
    ["S1-W05 missing canonical definition cannot qualify", () => {const x=good();x.sources.references[0].role="derived";qualifySubjectSource(x,SOURCE,fp);},true],
    ["S1-W06 same Source path but different Subject cannot qualify", () => {const x=good();x.subject.id="sales.order_line";qualifySubjectSource(x,SOURCE,fp);},true],
    ["S1-W07 unindexed subject cannot qualify", () => {const x=good();x.sourceStatus="not-indexed";qualifySubjectSource(x,SOURCE,fp);},true],
    ["S1-W08 duplicate artifact paths cannot qualify", () => {const x=good();x.sources.artifacts.push({...x.sources.artifacts[0]});qualifySubjectSource(x,SOURCE,fp);},true]
  ];
  tests.push(
    ["S1-W09 duplicate Source digest in receipt text is rejected",
      () => assert.throws(() => parseTrialJSON('{"sourceDigest":"a","sourceDigest":"b"}'),
        e => e.code === "DUPLICATE_TRIAL_JSON_MEMBER")],
    ["S1-W10 escaped-key duplicate is rejected",
      () => assert.throws(() => parseTrialJSON(String.raw`{"sourceDigest":"a","sourceDiges\u0074":"b"}`),
        e => e.code === "DUPLICATE_TRIAL_JSON_MEMBER")],
    ["S1-W11 nested Ledger object duplicate is rejected",
      () => assert.throws(() => parseTrialJSON('{"source":{"commit":"a","commit":"b"}}'),
        e => e.code === "DUPLICATE_TRIAL_JSON_MEMBER")],
    ["S1-W12 identical field names in different JSON objects are allowed",
      () => assert.equal(parseTrialJSON('{"source":{"commit":"a"},"build":{"commit":"b"}}').source.commit,"a")],
    ["S1-W13 malformed evidence JSON is rejected",
      () => assert.throws(() => parseTrialJSON('{"source":,}'),
        e => e.code === "INVALID_TRIAL_JSON")]
  );
  for (const [name, task, shouldFail] of tests) {
    if (shouldFail) assert.throws(task,undefined,name);
    else task();
  }
  console.log(JSON.stringify({scope:"synthetic Index binding assertions, not TEI/Harness",
    passed:tests.length,total:tests.length,cases:tests.map(([name])=>name.split(" ")[0])},null,2));
}

function main() {
  const binary = path.resolve(process.argv[2] || "");
  const tei = path.resolve(process.argv[3] || "");
  assert.ok(fs.statSync(binary).isFile(),"exact binary required");
  assert.ok(fs.statSync(path.join(tei,"go.mod")).isFile(),"actual TEI checkout required");
  const root = path.join(tei, "reference/workspace");
  const declared = fs.readFileSync(path.join(root,SOURCE));
  assert.match(declared.toString("utf8"),/\bdata Order\s*\{/,"independently expected named declaration missing");
  assert.match(declared.toString("utf8"),/attribute total type std\.money/,"independently expected field missing");
  const commands = run(binary,["commands"],tei);
  const discovered = jsonOf(commands);
  assert.equal(discovered.scope,"selected-read-only-commands");
  for (const name of ["model catalog","inspect","validate"])
    assert.ok(discovered.commands?.some(x=>x.name===name && x.effect==="read-only"),"required command is not advertised read-only: "+name);
  const catalog=run(binary,["model","catalog","-workspace",root],tei);
  const cat=jsonOf(catalog);
  assert.equal(cat.ok,true,"model catalog CLI envelope must report ok");
  assert.equal(cat.schemaVersion,"tei.cli.model/v0");
  const matches=(cat.result?.entries||[]).filter(x=>x?.subject?.kind===SUBJECT.kind && x.subject.id===SUBJECT.id);
  assert.equal(matches.length,1,"expected non-std sales.order semantic-data must be loaded exactly once");
  assert.notEqual(matches[0].sourceStatus,"not-indexed","required user-defined Subject must not be std-only/not-indexed");
  const inspect=run(binary,["inspect","-workspace",root,"-subject-kind",SUBJECT.kind,"-subject-id",SUBJECT.id],tei);
  const inspection=jsonOf(inspect);
  assert.equal(inspection.ok,true,"inspect CLI envelope must report ok");
  assert.equal(inspection.schemaVersion,"tei.cli.inspect/v0");
  const sourceWitness=qualifySubjectSource(inspection.result,SOURCE,digest(declared));
  assert.equal(cat.result.worldFingerprint,inspection.result.worldFingerprint,
    "Catalog and Inspect refer to different World fingerprints");
  assert.equal(cat.result.sourceIndexFingerprint,inspection.result.sourceIndexFingerprint,
    "Catalog and Inspect refer to different Source Index fingerprints");
  const validate=run(binary,["validate","-workspace",root,"-json"],tei);
  const val=jsonOf(validate);
  assert.equal(typeof val.ok,"boolean","validate status must be a boolean");
  assert.ok(Array.isArray(val.diagnostics),"validate diagnostics must be an array");
  assert.equal(val.worldFingerprint,inspection.result.worldFingerprint,
    "Validate and Inspect refer to different World fingerprints");
  assert.equal(val.sourceIndexFingerprint,inspection.result.sourceIndexFingerprint,
    "Validate and Inspect refer to different Source Index fingerprints");
  const git=run("git",["rev-parse","HEAD"],tei);
  const binaryDigest=digest(fs.readFileSync(binary));
  // Independent negative control: an empty workspace can validate, but must
  // never establish that the requested user-defined sales.order was loaded.
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),"tai-tei-s1-empty-"));
  let negative;
  try {
    fs.writeFileSync(path.join(temp,"tei.workspace.yaml"),"workspace: tai_empty\nformatVersion: 1\nsources:\n  - semantic\n");
    const negCat=jsonOf(run(binary,["model","catalog","-workspace",temp],tei));
    assert.equal((negCat.result?.entries||[]).filter(x=>x?.subject?.kind===SUBJECT.kind && x.subject.id===SUBJECT.id).length,0,
      "empty workspace must not claim selected user Subject");
    const negValidate=jsonOf(run(binary,["validate","-workspace",temp,"-json"],tei));
    negative={userSubjectLoaded:false,validationOk:negValidate.ok,
      stdEntries:(negCat.result?.entries||[]).filter(x=>x.subject?.id?.startsWith("std.")).length,
      interpretation:"validate.ok and nonempty std catalog cannot prove requested user source was read"};
  } finally { fs.rmSync(temp,{recursive:true,force:true}); }
  console.log(JSON.stringify({
    schema:"tai.s1.real-tei-public-read/v0",
    evidence:"real TEI CLI executed from pinned checkout; no AI Harness",
    teiCommit:git.stdout.trim(),binaryDigest,source:SOURCE,sourceDigest:digest(declared),
    subject:SUBJECT,catalogMatches:matches.length,catalogSourceStatus:matches[0].sourceStatus || "unreported",
    inspectedJson:true,sourceWitness,worldFingerprint:val.worldFingerprint,
    sourceIndexFingerprint:val.sourceIndexFingerprint,validationOk:val.ok,diagnostics:val.diagnostics.length,
    observations:[commands,catalog,inspect,validate].map(x=>({
      args:x.argv.slice(1),cwd:x.cwd,exit:x.exit,stdoutDigest:x.stdoutDigest,
      stderrPresent:x.stderr.length>0
    })),
    negative,
    notEstablished:["model actually read through external Harness","H2/H3 four independent sessions","complete Source/Provider closure","independent Business Oracle","Grant/OS/effective egress","Owner accepted meaning","real DB/Host Effect"]
  },null,2));
}
if(require.main===module){
  try {
    if (process.argv[2] === "--self-test") selfTest();
    else if (process.argv[2] === "--verify-ledger") {
      if(process.argv.length !== 5) throw new Error("usage: --verify-ledger ledger.json receipt.json");
      const ledger=parseTrialJSON(fs.readFileSync(process.argv[3],"utf8"));
      const receipt=parseTrialJSON(fs.readFileSync(process.argv[4],"utf8"));
      console.log(JSON.stringify(verifyLedger(ledger,receipt),null,2));
    } else main();
  } catch(e){console.error("TAI S1 FAIL: "+e.message);process.exitCode=1;}
}
module.exports={qualifySubjectSource,verifyLedger,selfTest};
