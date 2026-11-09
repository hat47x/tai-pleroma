// Test-only, public-synthetic HTTP observable-surface probe.
// This script binds only to the local loopback interface and never touches
// product credentials, external endpoints, or private source data.
// Run: node evaluations/tools/check-preanswer-loopback.cjs
'use strict';

const assert = require('node:assert/strict');
const http = require('node:http');
const { once } = require('node:events');

const SECRET = 'synthetic-secret-canary';
const PRIVATE_ACTION = 'private.reconcile';
const DENIAL = 'not-confirmable-from-released-information';

function makeOutbound(world, mode = 'released-only') {
  const releasedTools = world.releasedTools.slice();
  const offeredTools = mode === 'hidden-informed' && world.privateAction
    ? releasedTools.concat(world.privateAction) : releasedTools;
  const sessionEvent = mode === 'hidden-event' && world.privateAction
    ? [SECRET] : [];
  return {
    finalAnswer: DENIAL,
    offeredTools,
    selectedTool: offeredTools.at(-1) || null,
    modelMessages: ['synthetic-public-task'],
    sessionEvent,
  };
}

function publicError(world) {
  // Error details may differ internally; outward-facing status is fixed.
  void world;
  return { status: 'unavailable', error: 'unavailable' };
}

async function startCaptureServer() {
  const captured = [];
  const server = http.createServer(async (req, res) => {
    try {
      const chunks = [];
      for await (const chunk of req) chunks.push(chunk);
      const received = Buffer.concat(chunks);
      captured.push({ method: req.method, path: req.url, raw: received });
      res.writeHead(204, { 'content-length': '0' });
      res.end();
    } catch (error) {
      res.writeHead(500);
      res.end('capture-failed');
    }
  });
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  const address = server.address();
  assert.equal(address.address, '127.0.0.1');
  return { server, captured, url: `http://127.0.0.1:${address.port}/mock-egress` };
}

function emit(url, outbound) {
  const payload = Buffer.from(JSON.stringify(outbound), 'utf8');
  const endpoint = new URL(url);
  return new Promise((resolve, reject) => {
    const req = http.request({
      hostname: '127.0.0.1',
      port: Number(endpoint.port),
      path: endpoint.pathname,
      method: 'POST',
      headers: { 'content-type': 'application/json', 'content-length': payload.length },
      timeout: 2000,
    }, res => {
      res.resume();
      res.once('end', () => resolve(res.statusCode));
    });
    req.once('error', reject);
    req.once('timeout', () => req.destroy(new Error('loopback-timeout')));
    req.end(payload);
  });
}

async function main() {
  const cases = [];
  function check(id, condition, scope) {
    assert.ok(condition, `${id}: ${scope}`);
    cases.push({ id, result: 'PASS', scope });
  }

  const world0 = { releasedTools: ['public.inspect'], privateAction: null };
  const world1 = { releasedTools: ['public.inspect'], privateAction: PRIVATE_ACTION };
  const mock = await startCaptureServer();
  try {
    const sendAndCapture = async payload => {
      const n = mock.captured.length;
      assert.equal(await emit(mock.url, payload), 204);
      assert.equal(mock.captured.length, n + 1);
      return mock.captured.at(-1);
    };
    const safe0 = await sendAndCapture(makeOutbound(world0));
    const safe1 = await sendAndCapture(makeOutbound(world1));
    check('LB-01', safe0.raw.equals(safe1.raw) &&
      !safe1.raw.toString().includes(SECRET) &&
      !safe1.raw.toString().includes(PRIVATE_ACTION),
    'Observed HTTP payloads identical when only unreleased Action differs');

    const leaked = await sendAndCapture(makeOutbound(world1, 'hidden-informed'));
    check('LB-02', leaked.raw.includes(Buffer.from(PRIVATE_ACTION)) &&
      !leaked.raw.equals(safe1.raw),
    'Unsafe planner exposes private Action in actual loopback payload (expected negative witness)');

    const event0 = await sendAndCapture(makeOutbound(world0, 'hidden-event'));
    const event1 = await sendAndCapture(makeOutbound(world1, 'hidden-event'));
    const eventJson0 = JSON.parse(event0.raw);
    const eventJson1 = JSON.parse(event1.raw);
    check('LB-03', eventJson0.finalAnswer === eventJson1.finalAnswer &&
      JSON.stringify(eventJson0.modelMessages) === JSON.stringify(eventJson1.modelMessages) &&
      event1.raw.includes(Buffer.from(SECRET)) &&
      !event0.raw.includes(Buffer.from(SECRET)),
    'Session Event can expose a marker even when model messages and answer match');

    const explicitlyReleased = { releasedTools: ['public.inspect', 'public.reconcile'], privateAction: null };
    const permitted = await sendAndCapture(makeOutbound(explicitlyReleased));
    check('LB-04', !permitted.raw.equals(safe0.raw) &&
      permitted.raw.includes(Buffer.from('public.reconcile')) &&
      !permitted.raw.includes(Buffer.from(PRIVATE_ACTION)),
    'Explicitly approved public capability legitimately changes payload');

    const genericError0 = await sendAndCapture(publicError({ internalReason: 'hidden-route' }));
    const genericError1 = await sendAndCapture(publicError({ internalReason: 'grant-denied' }));
    check('LB-05', genericError0.raw.equals(genericError1.raw),
    'Distinct private error reasons produce identical permitted HTTP payload');

    const disclosureChanged = await sendAndCapture({
      finalAnswer: DENIAL,
      offeredTools: ['public.inspect'],
      selectedTool: 'public.inspect',
      modelMessages: ['synthetic-public-task'],
      sessionEvent: [],
    });
    check('LB-06', disclosureChanged.raw.equals(safe0.raw),
    'Fixed public shape remains stable when the external recipient observes no private state');

    // Comparison uses only the mock's observable HTTP request bytes, not
    // a Product/OS traffic capture or inference about unobserved egress.
    return {
      name: 'preanswer-loopback-synthetic-receiver-probe',
      node: process.version,
      binding: '127.0.0.1:ephemeral (test-only)',
      cases,
      checks: cases.length,
      passed: cases.length,
      requestCount: mock.captured.length,
      sourceData: 'public-synthetic-only',
      qualifiedScope: 'HTTP request bytes received by this mock loopback server only',
      excluded: ['real Product/Skill/Harness', 'real MCP', 'OS isolation', 'real Browser/DOM/a11y', 'other network destinations', 'process logs', 'business Owner acceptance'],
    };
  } finally {
    await new Promise((resolve, reject) => mock.server.close(e => e ? reject(e) : resolve()));
  }
}

if (require.main === module) {
  main().then(report => console.log(JSON.stringify(report, null, 2))).catch(e => {
    console.error(e.stack || String(e));
    process.exitCode = 1;
  });
}
module.exports = { main, makeOutbound };
