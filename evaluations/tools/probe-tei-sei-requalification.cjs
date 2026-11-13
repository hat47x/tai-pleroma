#!/usr/bin/env node
"use strict";
// Read-only probe: does a past TEI observation held by SEI still qualify for current use?
// Calls ONLY actual product CLIs (tei: source-index/inspect/trace/validate/world; sei: init/add/resume).
// It copies a TEI workspace into a throwaway directory for each variant. It never writes to a product repo.
// It does not own a dependency graph, a meaning, or an expected result. Expected results are read only by
// score-requalification-probe.cjs from a path the evaluator supplies (not stored in this repository).
//
// usage: node probe-tei-sei-requalification.cjs --tei-bin A --sei-bin B --workspace DIR --work DIR --out FILE
//        [--tei-old-bin C] [--tei-source-revision SHA] [--dump-observations FILE]
const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

function arg(name, required) {
  const i = process.argv.indexOf("--" + name);
  if (i < 0) { if (required) throw new Error("missing --" + name); return null; }
  return process.argv[i + 1];
}
const TEI = arg("tei-bin", true), SEI = arg("sei-bin", true), SRC_WS = arg("workspace", true);
const WORK = arg("work", true), OUT = arg("out", true), TEI_OLD = arg("tei-old-bin");
const TEI_REV = arg("tei-source-revision") || "unspecified";
const TEI_OLD_REV = arg("tei-old-source-revision") || "unspecified-old";
const DUMP = arg("dump-observations");
const KIND = "semantic-validation";
const REQUIRED = ["sales.order_line.quantity_positive", "sales.order.lines.line_number_unique", "sales.order_line.line_number_positive"];
const EXTRA_REQUIRED = "sales.order.total_positive"; // Synthetic Consumer requirement (R1); never observed
const MAX_DEPTH = 8;

// ---------------------------------------------------------------- variants (throwaway copies)
const V = path.join(WORK, "variants");
function copyTree(from, to) { fs.cpSync(from, to, { recursive: true }); }
function edit(root, rel, fn) {
  const f = path.join(root, rel); const before = fs.readFileSync(f, "utf8"); const after = fn(before);
  if (after === before) throw new Error(`variant edit changed nothing: ${rel}`);
  fs.writeFileSync(f, after);
}
const VAL = "semantic/sales/validation.tei", ORD = "semantic/sales/order.tei";
const VARIANTS = {
  A1: r => edit(r, VAL, s => s.replace("namespace sales\n\n", "namespace sales\n\n\n")),
  A5: r => edit(r, VAL, s => s + "\n"),
  A2: r => edit(r, "databases/sales-core/README.md", s => s + "\n"),
  A3: r => edit(r, "semantic/customer/customer.tei", s => s + "\n"),
  B1: r => edit(r, VAL, s => s.replace(/(validation sales\.order_line\.line_number_positive positive \{\n\s+attribute sales\.order_line\.)line_number/, "$1quantity")),
  B2: r => edit(r, VAL, s => s.replace(/validation sales\.order_line\.quantity_positive positive \{\n[^}]*\}\n\n/, "")),
  B3: r => edit(r, VAL, s => s.replace("validation sales.order_line.line_number_positive", "validation sales.order_line.line_no_positive")),
  B4: r => edit(r, VAL, s => s.replace("line_number_positive positive {", "line_number_positive non-negative {")),
  B5: r => edit(r, "environments/development/environment.tei", s => s.replace("provider postgres", "provider oracle")),
  B6: r => edit(r, ORD, s => s.replace("attribute lineNumber type std.integer", "attribute lineNumber type std.decimal")),
  N1: r => fs.writeFileSync(path.join(r, "semantic/sales/extra.tei"),
    "namespace sales\n\nvalidation sales.order_line.quantity_positive_again positive {\n    attribute sales.order_line.quantity\n}\n"),
  // Added after the first TASK 3 run (Fable section 7 items 1-3):
  C1: r => edit(r, "tei.workspace.yaml", s => s + "\n# comment only\n"),                 // manifest bytes change, no model change
  C2: r => edit(r, "databases/sales-core/query-realizations/order-line-find-by-order.sql", s => s + "\n"), // provider raw bytes only
};
const CASES = Object.keys(VARIANTS).concat(["R1", "T1"]); // R1: Consumer requirement change; T1: older TEI binary

// ---------------------------------------------------------------- process helpers
let calls = 0;
function run(bin, args) {
  calls++;
  const r = spawnSync(bin, args, { encoding: "utf8", maxBuffer: 128 << 20 });
  let json = null; try { json = JSON.parse(r.stdout); } catch (e) {}
  return { exit: r.status, json, stdout: r.stdout, stderr: r.stderr };
}
const ok = r => r.exit === 0 && r.json && r.json.ok === true && r.json.result;
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const sortById = list => [...list].sort((a, b) => (a.kind + a.id).localeCompare(b.kind + b.id));

class Reader { // binds a TEI binary and a workspace
  constructor(bin, ws, rev) { this.bin = bin; this.ws = ws; this.rev = rev; }
  inspect(kind, id) { return run(this.bin, ["inspect", "-workspace", this.ws, "-subject-kind", kind, "-subject-id", id]); }
  trace(kind, id) { return run(this.bin, ["trace", "-workspace", this.ws, "-scope", "workspace", "-subject-kind", kind, "-subject-id", id, "-direction", "outgoing", "-mode", "full"]); }
  index() { return run(this.bin, ["source-index", "-workspace", this.ws]); }
  validate() { return run(this.bin, ["validate", "-workspace", this.ws]); }
}
const manifestOf = res => (res.workspace && res.workspace.manifest ? res.workspace.manifest.sha256 : undefined);
const locOf = res => ({ artifacts: res.sources ? res.sources.artifacts : null, references: res.sources ? res.sources.references : null }); // builtin types have no source

// Observation of one subject: the product's own replies, followed outgoing edges to a fixed point.
// Anything that cannot be followed (read failure, unresolved edge, depth limit) is recorded, never skipped.
function observe(rd, kind, id) {
  const seen = new Map(); const queue = [{ kind, id, depth: 0 }]; const problems = [];
  let top = null;
  while (queue.length) {
    const cur = queue.shift(); const key = cur.kind + ":" + cur.id;
    if (seen.has(key)) continue;
    if (cur.depth > MAX_DEPTH) { problems.push(`${key}: depth limit`); continue; }
    const i = rd.inspect(cur.kind, cur.id);
    if (!ok(i)) { seen.set(key, { ok: false, exit: i.exit }); problems.push(`${key}: inspect exit=${i.exit}`); continue; }
    const t = rd.trace(cur.kind, cur.id);
    if (!ok(t)) { seen.set(key, { ok: false, exit: t.exit }); problems.push(`${key}: trace exit=${t.exit}`); continue; }
    const tr = t.json.result.trace;
    const edges = sortById((tr.rows || []).map(r => ({ kind: r.edge.to.subject.kind, id: r.edge.to.subject.id, relation: r.edge.relation, status: r.status })));
    if (tr.unresolved !== 0) problems.push(`${key}: unresolved=${tr.unresolved}`);
    const node = { ok: true, canonical: i.json.result.canonical, edges, unresolved: tr.unresolved, projectionUnresolved: t.json.result.projectionUnresolved || [], loc: locOf(i.json.result) };
    seen.set(key, node);
    if (!top) top = { world: i.json.result.worldFingerprint, sourceIndex: i.json.result.sourceIndexFingerprint, manifest: i.json.result.workspace && i.json.result.workspace.manifest && i.json.result.workspace.manifest.sha256 };
    for (const e of edges) queue.push({ kind: e.kind, id: e.id, depth: cur.depth + 1 });
  }
  return { top, nodes: Object.fromEntries(seen), problems };
}
function cohort(rd) {
  const r = rd.index();
  if (!ok(r)) return { ok: false };
  return { ok: true, ids: [...new Set(r.json.result.references.filter(x => x.subject.kind === KIND).map(x => x.subject.id))].sort() };
}

// ---------------------------------------------------------------- historical evidence (actual reads, base world, new TEI binary)
function captureHistory(rd) {
  const H = { subjects: {}, cohort: cohort(rd).ids };
  for (const id of REQUIRED) H.subjects[id] = observe(rd, KIND, id);
  H.rev = rd.rev; const t = H.subjects[REQUIRED[0]].top; H.world = t.world; H.sourceIndex = t.sourceIndex; H.manifest = t.manifest;
  return H;
}

// ---------------------------------------------------------------- Consumer: SEI holds the recommendation and basis pointers
function seiStore(H) {
  const store = path.join(WORK, "sei-store"); fs.rmSync(store, { recursive: true, force: true });
  run(SEI, ["init", "--data-root", store]);
  const basis = [];
  for (const id of REQUIRED) basis.push("--basis", `tei-${KIND}:${id}`);
  basis.push("--basis", `tei-world:${H.world}`, "--basis", `tei-source-revision:${TEI_REV}`);
  const a = run(SEI, ["add", "recommendation", "--data-root", store, "--id", "t3-required-rule-index",
    "--statement", "Inspect the complete index-mode source index for three fixed validations; a single subject is insufficient.",
    "--source", "probe-evaluator", ...basis]);
  if (a.exit !== 0) throw new Error("SEI add failed: " + a.stderr);
  return store;
}
function consumerRead(store) {
  calls++;
  const r = spawnSync(SEI, ["resume", "--data-root", store, "--json"], { encoding: "utf8" });
  const j = JSON.parse(r.stdout);
  const rec = j.recommendations_not_yet_relied_on.find(x => x.id === "t3-required-rule-index");
  const refs = rec.basis_references || [];
  return { digest: j.snapshot_digest, required: refs.filter(x => x.kind === "tei-" + KIND).map(x => x.id), world: (refs.find(x => x.kind === "tei-world") || {}).id };
}

// ---------------------------------------------------------------- claim judgments (M: meaning of required members, L: locators, K: set/negation)
function judgeM(H, rd, required) {
  let stale = false, unknown = false; const why = [];
  // trace/inspect content is defined by the Tool build. Comparing replies across builds proves nothing either way.
  if (rd.rev !== H.rev) return { verdict: "unknown", why: [`tool source revision changed (${H.rev} -> ${rd.rev}); replies are not comparable`] };
  for (const id of required) {
    const h = H.subjects[id];
    if (!h) { stale = true; why.push(`${id}: required now, never observed`); continue; }
    const now = observe(rd, KIND, id);
    const top = now.nodes[KIND + ":" + id];
    if (!top || !top.ok) {
      const c = cohort(rd);
      if (!c.ok) { unknown = true; why.push(`${id}: unreadable and index unreadable`); }
      else if (!c.ids.includes(id)) { stale = true; why.push(`${id}: absent from current index`); }
      else { unknown = true; why.push(`${id}: unreadable although listed`); }
      continue;
    }
    for (const [key, hn] of Object.entries(h.nodes)) {
      const nn = now.nodes[key];
      if (!hn.ok) continue;
      if (!nn) { stale = true; why.push(`${key}: no longer reachable`); continue; }
      if (!nn.ok) { unknown = true; why.push(`${key}: unreadable now`); continue; }
      if (!same(nn.canonical, hn.canonical)) { stale = true; why.push(`${key}: canonical differs`); }
      if (!same(nn.edges, hn.edges)) { stale = true; why.push(`${key}: edges differ`); }
    }
    for (const key of Object.keys(now.nodes)) if (!(key in h.nodes)) { stale = true; why.push(`${key}: new dependency`); }
    if (now.problems.length) { unknown = true; why.push(...now.problems.map(p => "open: " + p)); }
  }
  return { verdict: stale ? "stale" : unknown ? "unknown" : "reuse", why };
}
function judgeK(H, rd) {
  const c = cohort(rd);
  if (!c.ok) return { verdict: "unknown", why: ["index read failed"] };
  return same(c.ids, H.cohort) ? { verdict: "reuse", why: [] } : { verdict: "stale", why: ["validation id set differs"] };
}
const memberLoc = (H, id) => H.subjects[id].nodes[KIND + ":" + id].loc;
function judgeL(H, rd, required) {
  for (const id of required) {
    if (!H.subjects[id]) return { verdict: "stale", why: [`${id}: locator never observed`] };
    const i = rd.inspect(KIND, id);
    if (!ok(i)) { const c = cohort(rd); return c.ok ? { verdict: "stale", why: [`${id}: not locatable`] } : { verdict: "unknown", why: ["read failed"] }; }
    if (!same(locOf(i.json.result), memberLoc(H, id))) return { verdict: "stale", why: [`${id}: locator or artifact fingerprint differs`] };
  }
  return { verdict: "reuse", why: [] };
}

// Owner decision E2 (proxy, 2026-11-11, TEI #2586): a world that TEI's own `validate` rejects does not qualify
// a "reuse" of meaning (M) or of the validation id set (K). A refutation (stale) still wins; locators (L) are
// compared literally and are not affected. The cost is over-caution when the failure is unrelated to the Claim.
function validWorld(j, v) {
  if (j.verdict !== "reuse" || v.exit === 0) return j;
  return { verdict: "unknown", why: [`product validate exit=${v.exit}: current world is not accepted by the product`] };
}
// ---------------------------------------------------------------- the three methods
function J0(H, rd, store, extra) {
  const c = consumerRead(store); const required = c.required.concat(extra);
  const v = rd.validate();
  return { M: validWorld(judgeM(H, rd, required), v), L: judgeL(H, rd, required), K: validWorld(judgeK(H, rd), v), note: `validate exit=${v.exit}` };
}
function J1(H, rd, store, extra) {
  const c = consumerRead(store); const required = c.required.concat(extra);
  const out = {};
  const probe = rd.inspect(KIND, c.required[0]);
  const sameWorld = ok(probe) && probe.json.result.worldFingerprint === c.world && manifestOf(probe.json.result) === H.manifest; // missing field => identity unproven => deep path
  const uncovered = required.filter(id => !H.subjects[id]);
  if (sameWorld && uncovered.length === 0) { out.M = { verdict: "reuse", why: ["same product world fingerprint and manifest"] }; out.K = { verdict: "reuse", why: ["same world"] }; }
  else if (sameWorld) { out.M = { verdict: "stale", why: uncovered.map(id => `${id}: required now, never observed`) }; out.K = { verdict: "reuse", why: ["same world"] }; }
  else { const v = rd.validate(); out.M = validWorld(judgeM(H, rd, required), v); out.K = validWorld(judgeK(H, rd), v); }
  if (uncovered.length === 0 && ok(probe) && probe.json.result.sourceIndexFingerprint === H.sourceIndex) out.L = { verdict: "reuse", why: ["same source index fingerprint"] };
  else out.L = judgeL(H, rd, required);
  out.note = sameWorld ? "short path" : "deep path";
  return out;
}
function J2(H, rd, store) {
  const c = consumerRead(store); const w = [`SEI resume returned the same record, digest ${c.digest.slice(0, 19)}`];
  return { M: { verdict: "reuse", why: w }, L: { verdict: "reuse", why: w }, K: { verdict: "reuse", why: w }, note: "no TEI read" };
}

function dumpObs(rd) { // raw product replies for every required member; no verdict and no description of the change
  const nodes = {}, problems = []; let top = null;
  for (const id of REQUIRED) { const o = observe(rd, KIND, id); Object.assign(nodes, o.nodes); problems.push(...o.problems); top = top || o.top; }
  const c = cohort(rd); const v = rd.validate();
  return { world: top && top.world, manifest: top && top.manifest, sourceIndex: top && top.sourceIndex, nodes, problems, validationIds: c.ids, validateExit: v.exit, validateErrors: v.stdout.split("\n").filter(x => /\terror\t/.test(x)) };
}
// ---------------------------------------------------------------- main
fs.rmSync(V, { recursive: true, force: true }); fs.mkdirSync(V, { recursive: true });
const BASE = path.join(V, "base"); copyTree(SRC_WS, BASE);
for (const [name, mk] of Object.entries(VARIANTS)) { const d = path.join(V, name); copyTree(SRC_WS, d); mk(d); }
const baseRd = new Reader(TEI, BASE, TEI_REV);
const H = captureHistory(baseRd);
const store = seiStore(H);
const results = {}; const dump = {};
for (const name of CASES) {
  const ws = name === "R1" || name === "T1" ? BASE : path.join(V, name);
  const bin = name === "T1" ? TEI_OLD : TEI;
  if (name === "T1" && !TEI_OLD) { results[name] = "NOT RUN (no --tei-old-bin)"; continue; }
  const rd = new Reader(bin, ws, name === "T1" ? TEI_OLD_REV : TEI_REV); const extra = name === "R1" ? [EXTRA_REQUIRED] : [];
  results[name] = {};
  for (const [j, f] of [["J0", J0], ["J1", J1], ["J2", J2]]) {
    calls = 0; const t0 = Date.now(); const r = f(H, rd, store, extra);
    results[name][j] = { M: r.M.verdict, L: r.L.verdict, K: r.K.verdict, calls, ms: Date.now() - t0, note: r.note, why: { M: r.M.why, L: r.L.why, K: r.K.why } };
  }
  if (DUMP) { // raw product replies only, no variant description and no verdict: input for an independent expected author
    dump[name] = dumpObs(rd);
  }
}
fs.writeFileSync(OUT, JSON.stringify({ scope: "ACTUAL TEI+SEI CLI on throwaway workspace copies; Consumer requirement R1 is Synthetic", teiBin: TEI, seiBin: SEI, teiSourceRevision: TEI_REV, history: { world: H.world, manifest: H.manifest, cohort: H.cohort }, results }, null, 1));
if (DUMP) {
  dump.base = dumpObs(baseRd);
  fs.writeFileSync(DUMP, JSON.stringify(dump, null, 1));
}
console.log("written", OUT);
