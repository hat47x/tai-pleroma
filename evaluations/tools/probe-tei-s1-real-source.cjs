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
  try {return JSON.parse(call.stdout);}
  catch(e){throw new Error("non-JSON result [" + call.argv.slice(1).join(" ") + "]: " + e.message);}
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
  const validate=run(binary,["validate","-workspace",root,"-json"],tei);
  const val=jsonOf(validate);
  assert.equal(typeof val.ok,"boolean","validate status must be a boolean");
  assert.ok(Array.isArray(val.diagnostics),"validate diagnostics must be an array");
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
    inspectedJson:true,validationOk:val.ok,diagnostics:val.diagnostics.length,
    observations:[commands,catalog,inspect,validate].map(x=>({
      args:x.argv.slice(1),cwd:x.cwd,exit:x.exit,stdoutDigest:x.stdoutDigest,
      stderrPresent:x.stderr.length>0
    })),
    negative,
    notEstablished:["model actually read through external Harness","H2/H3 four independent sessions","complete Source/Provider closure","independent Business Oracle","Grant/OS/effective egress","Owner accepted meaning","real DB/Host Effect"]
  },null,2));
}
if(require.main===module){
  try {main();}
  catch(e){console.error("TAI S1 FAIL: "+e.message);process.exitCode=1;}
}
