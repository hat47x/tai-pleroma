/**
 * G6: `references[].digest` を SEI の Exact Binding 形式と照合する（Test-only）。
 *
 * 位置づけ:
 * - これは **照合** であり、意味受理でも真正性証明でもない。
 * - 診断名は TEI E9 の既存語彙（`reference-linked-unverified` など）を再利用する。
 *   `verified` へ自動昇格させない。
 * - 新しい共通Oracle・Claim Storeは作らない。SEI契約の schema と、票のreferences
 *   の形だけを突き合わせる。
 *
 * 使い方:
 *   node evaluations/tools/check-handoff-sei-binding.cjs --ticket <abs-ticket.json> \
 *     --schema <abs path to sei semantic-reference.schema.json> --self-test
 *
 * `--self-test` は、実票を必要としない負例を含む自己試験を走らせる。
 */

'use strict';

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const DIAGNOSTICS = {
  linked: 'reference-linked-unverified',
  missing: 'reference-missing',
  stale: 'reference-stale',
  mismatch: 'reference-target-mismatch',
  incomplete: 'reference-incomplete',
  ambiguous: 'reference-ambiguous',
  unsupported: 'reference-profile-unsupported',
};

const PROFILE_ID = 'sei.jcs+sha256/v1alpha1';

/** Exact Binding の `content_digest` は `sha256:<64hex>` の形を取る。 */
const DIGEST_PATTERN = /^sha256:[0-9a-f]{64}$/;

/**
 * 票の `references[]` を SEI Exact Binding と照合する。
 *
 * - `digest` が無い（null）参照は `reference-incomplete`。推測で埋めない。
 * - `digest` の形が違う参照は `reference-target-mismatch`。
 * - `representation_profile` を票が宣言していないため、Profile の一致は
 *   **確認できない**。したがって成功しても `reference-linked-unverified` に
 *   留め、`verified` にしない。
 * - 同じ `locator` に複数の参照がある場合は `reference-ambiguous`（一意に選ばない）。
 */
function reconcile(references, expectedProfileId = PROFILE_ID) {
  if (!Array.isArray(references)) {
    return { subjects: [], note: 'references is not an array' };
  }
  const byLocator = new Map();
  for (const reference of references) {
    const locator = typeof reference?.locator === 'string' ? reference.locator : '';
    if (!byLocator.has(locator)) byLocator.set(locator, []);
    byLocator.get(locator).push(reference);
  }
  const subjects = [];
  for (const [locator, group] of [...byLocator.entries()].sort((a, b) => (a[0] < b[0] ? -1 : 1))) {
    if (group.length > 1) {
      subjects.push({ locator, state: DIAGNOSTICS.ambiguous, exactCount: group.length });
      continue;
    }
    const reference = group[0];
    const digest = reference.digest;
    if (digest === null || digest === undefined) {
      subjects.push({ locator, state: DIAGNOSTICS.incomplete, reason: 'digest is absent' });
      continue;
    }
    if (typeof digest !== 'string' || !DIGEST_PATTERN.test(digest)) {
      subjects.push({ locator, state: DIAGNOSTICS.mismatch, reason: 'digest is not sha256:<64 lowercase hex>' });
      continue;
    }
    // 票は representation_profile を運ばない。宣言が無い状態で Profile 一致を
    // 主張できないため、照合は「参照がリンクしたが未検証」で止める。
    subjects.push({
      locator,
      state: DIAGNOSTICS.linked,
      profile: {
        declaredByTicket: null,
        expected: expectedProfileId,
        matched: false,
      },
      reason: 'the ticket carries no representation_profile, so profile agreement cannot be verified',
    });
  }
  return {
    subjects,
    note: 'a linked reference is NOT a conformance assertion, a meaning acceptance, or a current-source proof',
  };
}

/** Exact Binding の形そのものが valid かを確認する（SEI schemaの必須欄に合わせる）。 */
function exactBindingShape(digest, profileId = PROFILE_ID) {
  if (typeof digest !== 'string' || !DIGEST_PATTERN.test(digest)) return null;
  return {
    logical_ref: { kind: 'handoff-reference', id: 'unspecified' },
    content_digest: digest,
    representation_profile: { profile_id: profileId, version: 'v1alpha1' },
  };
}

function main(argv) {
  const options = { ticket: null, schema: null, selfTest: false };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--ticket') options.ticket = argv[++index];
    else if (arg === '--schema') options.schema = argv[++index];
    else if (arg === '--self-test') options.selfTest = true;
    else return fail(`unknown option ${arg}`);
  }
  if (options.schema !== null) {
    if (!path.isAbsolute(options.schema)) return fail('--schema must be an absolute path');
    const schema = JSON.parse(fs.readFileSync(options.schema, 'utf8'));
    const required = schema?.$defs?.exactBinding?.required;
    const expected = ['logical_ref', 'content_digest', 'representation_profile'];
    if (!Array.isArray(required) || required.length !== expected.length ||
        !expected.every((field) => required.includes(field))) {
      return fail('the SEI exact_binding required fields are not the expected ones');
    }
  }
  if (options.ticket !== null) {
    if (!path.isAbsolute(options.ticket)) return fail('--ticket must be an absolute path');
    const ticket = JSON.parse(fs.readFileSync(options.ticket, 'utf8').replace(/^\uFEFF/, ''));
    // Fail closed, not open. An input that is not a v1 handoff ticket, or that
    // has no `references` array, must NOT produce a "reconciled with nothing"
    // exit 0 -- that would read as "I checked and found nothing" when in fact
    // nothing was checkable.
    if (ticket === null || typeof ticket !== 'object' || Array.isArray(ticket)) {
      return fail('the input is not a JSON object');
    }
    if (ticket.schema !== 'yi.handoff.context/v1') {
      return fail(`the input schema is ${JSON.stringify(ticket.schema)}, not yi.handoff.context/v1`);
    }
    if (!Array.isArray(ticket.references)) {
      return fail('the ticket has no references array; there is nothing to reconcile');
    }
    const report = reconcile(ticket.references);
    process.stdout.write(JSON.stringify({
      schema: 'yi.handoff.sei-binding-review/v1',
      ticket: options.ticket,
      ticketSha256: 'sha256:' + crypto.createHash('sha256')
        .update(fs.readFileSync(options.ticket)).digest('hex'),
      ...report,
    }, null, 2) + '\n');
  }
  if (options.selfTest) {
    const cases = selfTest();
    process.stdout.write(JSON.stringify({ schema: 'yi.handoff.sei-binding-self-test/v1', cases }, null, 2) + '\n');
    if (!cases.every((entry) => entry.ok)) return fail('self-test failed');
  }
  return 0;
}

function selfTest() {
  const cases = [];
  const check = (id, references, expectedState) => {
    const report = reconcile(references);
    const states = report.subjects.map((subject) => subject.state);
    cases.push({ id, ok: states.length === 1 && states[0] === expectedState, expected: expectedState, actual: states });
  };
  const goodDigest = 'sha256:' + 'a'.repeat(64);
  const ref = (overrides = {}) => ({
    kind: 'tei-readonly-observation',
    locator: 'tei:tei.cli.model/v0:application:order_entry',
    digest: goodDigest,
    note: 'n',
    ...overrides,
  });

  // G6-N1: 空配列を「グローバル不存在」と結論づけない。ここでは母集団が無いこと
  // 自体を「照合対象が無い」と記録し、不存在の証明にはしない。
  // NOTE: this case is about the RECONCILER, not about the CLI. A ticket with no
  // `references` array is rejected by main() before reconcile() is reached, so
  // it can never be read as "checked and found nothing".
  const empty = reconcile([]);
  cases.push({
    id: 'G6-N1-empty-is-not-absent',
    ok: empty.subjects.length === 0 && empty.note.includes('NOT'),
    expected: 'no subjects, no absence claim',
    actual: empty.subjects.length,
  });
  // G6-N2: 部分取得を全件として扱わない。digest欠落は incomplete。
  check('G6-N2-missing-digest-is-incomplete', [ref({ digest: null })], DIAGNOSTICS.incomplete);

  // G6-N3: 形の違うdigestはtarget-mismatch（staleと混同しない）。
  check('G6-N3-bad-digest-is-mismatch', [ref({ digest: 'sha256:ABC' })], DIAGNOSTICS.mismatch);

  // G6-N4: 同じlocatorに複数参照はambiguous（一意に選ばない）。
  check('G6-N4-duplicate-locator-is-ambiguous', [ref(), ref({ digest: 'sha256:' + 'b'.repeat(64) })],
    DIAGNOSTICS.ambiguous);

  // 成功しても linked-unverified に留まる。verifiedへ昇格させない。
  check('G6-linked-never-verified', [ref()], DIAGNOSTICS.linked);
  const linked = reconcile([ref()]);
  cases.push({
    id: 'G6-linked-carries-profile-gap',
    ok: linked.subjects[0].profile.matched === false &&
      linked.subjects[0].profile.declaredByTicket === null,
    expected: 'profile matched=false',
    actual: linked.subjects[0].profile,
  });

  // Exact Binding の形はSEI schemaの必須欄に一致する。
  const binding = exactBindingShape(goodDigest);
  cases.push({
    id: 'G6-exact-binding-shape',
    ok: binding !== null && Object.keys(binding).sort().join(',') ===
      ['content_digest', 'logical_ref', 'representation_profile'].sort().join(','),
    expected: 'logical_ref,content_digest,representation_profile',
    actual: binding === null ? null : Object.keys(binding).sort(),
  });
  cases.push({
    id: 'G6-exact-binding-rejects-bad-digest',
    ok: exactBindingShape('not-a-digest') === null,
    expected: null,
    actual: exactBindingShape('not-a-digest'),
  });
  return cases;
}

function fail(message) {
  process.stderr.write(JSON.stringify({ error: 'sei-binding-review-failed', message }) + '\n');
  return 2;
}

process.exitCode = main(process.argv.slice(2));
