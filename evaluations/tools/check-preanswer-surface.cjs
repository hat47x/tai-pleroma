// Public synthetic witness for YI Constellation pre-answer observable surfaces.
// No production Product/Host/Policy/Renderer/MCP code is executed.
// Run: node evaluations/tools/check-preanswer-surface.cjs
"use strict";

function same(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}
function assert(condition, message) {
  if (!condition) throw new Error(message);
}
function planningTrace(world, mode) {
  const visible = world.releasedTools.slice();
  const proposed = mode === "hidden-informed" && world.privateTool
    ? visible.concat(world.privateTool) : visible;
  return { answer: "not-confirmable-from-released-information",
    offeredTools: proposed, toolRequest: proposed.length ? proposed[proposed.length - 1] : null };
}
function statusProjection(internal) {
  return internal.revealDetails ? internal.reason : "unavailable";
}
function presentation(markdownVersion, rendererProfile) {
  const sourceLinks = ["https://example.org/md"];
  const rendererLinks = rendererProfile === "allow-raw-html"
    ? sourceLinks.concat("https://example.org/html") : sourceLinks.slice();
  return { markdownVersion, sourceLinks, rendererLinks, rendererProfile };
}
function canReportDelivered(delivery) {
  return delivery.ack && delivery.bodyReceived &&
    delivery.bodyDigestVerified && delivery.readerConsumed;
}
function canInvoke(action) {
  return action.resolved && action.currentGrant &&
    action.expectedStateMatches && action.currentSourceVersion;
}
function runSelfcheck() {
  const cases = [];
  function test(id, predicate) {
    assert(predicate(), id + " unexpected result");
    cases.push(id);
  }
  const a = { releasedTools: ["public.inspect"], privateTool: null };
  const b = { releasedTools: ["public.inspect"], privateTool: "private.reconcile" };

  test("AS-01", () => {
    const x = planningTrace(a, "hidden-informed");
    const y = planningTrace(b, "hidden-informed");
    return x.answer === y.answer && !same(x.offeredTools, y.offeredTools);
  });
  test("AS-02", () =>
    same(planningTrace(a, "released-only"), planningTrace(b, "released-only")));
  test("AS-03", () => {
    const released = { releasedTools: ["public.inspect", "public.reconcile"], privateTool: null };
    return !same(planningTrace(a, "released-only"), planningTrace(released, "released-only"));
  });
  test("AS-04", () =>
    statusProjection({ reason: "hidden-route-ambiguous", revealDetails: false }) ===
    statusProjection({ reason: "grant-denied", revealDetails: false }));
  test("AS-05", () => {
    const x = presentation("source-r1", "escape-raw-html");
    const y = presentation("source-r1", "allow-raw-html");
    return same(x.sourceLinks, y.sourceLinks) &&
      !same(x.rendererLinks, y.rendererLinks);
  });
  test("AS-06", () => {
    const presented = presentation("source-r1", "allow-raw-html");
    const transport = { requestSent: false };
    return presented.rendererLinks.length === 2 && !transport.requestSent;
  });
  test("AS-07", () => {
    const x = { modelMessages: ["same-answer"], sessionEvent: [] };
    const y = { modelMessages: ["same-answer"], sessionEvent: ["synthetic-private-marker"] };
    return same(x.modelMessages, y.modelMessages) && !same(x.sessionEvent, y.sessionEvent);
  });
  test("AS-08", () => {
    const x = { finalAnswer: "unavailable", accessibilityTree: ["public"] };
    const y = { finalAnswer: "unavailable", accessibilityTree: ["public", "synthetic-private-marker"] };
    return x.finalAnswer === y.finalAnswer &&
      !same(x.accessibilityTree, y.accessibilityTree);
  });
  test("AS-09", () => {
    const offered = { resolved: true, currentGrant: true,
      expectedStateMatches: true, currentSourceVersion: true };
    return canInvoke(offered) && !canInvoke({ ...offered, currentGrant: false });
  });
  test("AS-10", () => {
    const ackOnly = { ack: true, bodyReceived: false,
      bodyDigestVerified: false, readerConsumed: false };
    const received = { ack: true, bodyReceived: true,
      bodyDigestVerified: true, readerConsumed: true };
    return !canReportDelivered(ackOnly) && canReportDelivered(received);
  });
  test("AS-11", () => {
    const source = { statement: "op: delete", role: "test" };
    const quote = { source, authorizedRoleBinding: false };
    const definition = { source, authorizedRoleBinding: true };
    return same(quote.source, definition.source) &&
      quote.authorizedRoleBinding !== definition.authorizedRoleBinding;
  });
  test("AS-12", () => {
    const prior = { offered: true, accessEpoch: "r1", currentEpoch: "r2" };
    return prior.offered && prior.accessEpoch !== prior.currentEpoch;
  });
  return { name: "preanswer-active-surface-synthetic-reference",
    checks: cases.length, passed: cases.length, cases,
    scope: "synthetic differentiation only; Product/OS/Host/Network NOT RUN" };
}
if (typeof module !== "undefined") {
  module.exports = { runSelfcheck };
  if (typeof require === "function" && require.main === module) {
    console.log(JSON.stringify(runSelfcheck(), null, 2));
  }
}
