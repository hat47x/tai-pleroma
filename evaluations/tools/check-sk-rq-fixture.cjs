#!/usr/bin/env node
'use strict';
// Public fixture selfcheck only. Not a Product Skill, Owner oracle, or runtime safety enforcement.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
function classify(check,changed) {
  const guards={
    "disclosure-change":"recheck-disclosure",
    "trust-unverified-effect":"suspend-effect",
    "joint-epoch-mismatch":"joint-unknown",
    "mixed-publication":"recheck-publication",
    "body-delivery-observed":"recheck-delivery",
    "purpose-changed":"requalify-purpose"
  };
  if(check.guard){
    if(!(check.guard in guards))throw Error("unexpected guard "+check.guard);
    return guards[check.guard];
  }
  if(!Array.isArray(check.dependencies)||!Array.isArray(changed))throw Error("missing dependencies");
  if(check.dependencies.some(x=>changed.includes(x)))return "requalify-dependency";
  return check.dependenciesComplete===true?"retain-bounded-evidence":"unknown-impact";
}
const f=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../fixtures/SK-RQ-selective-requalification.synthetic.json'),'utf8'));
assert.equal(f.classification,'public-synthetic-unsealed-reference');
assert.equal(f.cases.length,12);
assert.equal(new Set(f.cases.map(c=>c.id)).size,12);
let checked=0;
for(const c of f.cases){
 for(const check of c.checks){
  assert.equal(classify(check,c.changed),check.expected,c.id+':'+check.claim);
  checked++;
 }
}
assert.equal(checked,14);
console.log(JSON.stringify({status:'PASS',scope:'public reference fixture only',cases:f.cases.length,checks:checked,notProductTest:true},null,2));
