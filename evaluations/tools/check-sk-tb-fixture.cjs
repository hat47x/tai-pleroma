#!/usr/bin/env node
'use strict';
// Public, unsealed reference decision-table selfcheck only; NOT an EKI or Harness test.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');
const fixturePath = path.resolve(__dirname, '../fixtures/SK-TB-current-trust.synthetic.json');
const f = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));
const sha = bytes => createHash('sha256').update(bytes).digest();
function classify(c) {
  if (c.kind === 'trust') {
    if (c.installed === 'never') {
      return c.compatApproved && c.legacyCAAndRegistryValid
        ? 'legacy-path-eligible' : 'not-qualified';
    }
    if (c.installed !== 'ever' || c.latest !== 'ok') {
      return 'reject-unverified-current-trust';
    }
    if (c.currentIssuerAllowed !== true) return 'reject-current-issuer';
    return c.legacyCAAndRegistryValid
      ? 'proceed-to-other-host-checks' : 'reject-legacy-ca-registry';
  }
  if (c.kind === 'handoff') {
    return (c.latest !== 'ok' || c.grantAtResume !== 'valid')
      ? 'reauthorize-before-effect' : 'continue-only-after-current-checks';
  }
  if (c.kind === 'disclosure') {
    return c.publicProjectionS0 === c.publicProjectionS1
      ? 'indistinguishable-to-public-consumer' : 'public-observations-differ';
  }
  if (c.kind === 'digest') {
    assert.equal(c.sampleBytesAreActualDER, false);
    const first = sha(Buffer.from(c.sampleBytesHex, 'hex'));
    const double = sha(first);
    assert.equal(first.toString('hex'), c.oracleSingle);
    assert.equal(double.toString('hex'), c.doubleSha);
    assert.notEqual(c.oracleSingle, c.doubleSha);
    return 'single-sha-only';
  }
  throw new Error('Unknown public fixture case type: ' + c.kind);
}
assert.equal(f.classification, 'public-synthetic-unsealed');
assert.equal(f.cases.length, 9);
assert.equal(new Set(f.cases.map(c => c.id)).size, 9);
const seen = [];
for (const c of f.cases) {
  const actual = classify(c);
  assert.equal(actual, c.expected, c.id);
  seen.push(c.id);
}
console.log(JSON.stringify({ status: 'PASS', scope: 'public synthetic decision-table only', count: seen.length, cases: seen }, null, 2));
