#!/usr/bin/env node
"use strict";
// Judges whether a past real-Provider-Read Claim can still be used, from CAPTURED product output only.
// It never connects to a database or runs a product. Input per case (files produced by an evaluator harness
// that called the product's own Resolver/Executor and TEI `inspect`):
//   <case>.reads.json            {witnessBefore, witnessAfter, reads:[{read:{status,operator,offset}, error?, rows, rowCount, instanceId}]}
//                                witness = what the Provider reported on the SAME connection the Executor used
//   <case>.inspect-query.json    TEI `inspect -subject-kind query ...` reply
//   <case>.inspect-pattern.json  TEI `inspect -subject-kind application-pattern ...` reply
// The Consumer's requirement is a claims file: [{"id","read":"STATUS|OP|OFFSET","kind":"R"|"Z"}]
//   R = the Consumer reuses the rows of that Read.   Z = the Consumer reuses "nothing matched" (absence).
// It owns no graph, no store and no meaning; it compares what the Product and Provider said then and now.
//
// Methods (verdict vocabulary):
//   D (definition):  reuse | stale | unknown
//   R (rows):        reuse | reread | stale | unknown     J1p never returns reuse for R: no data-state witness exists.
//   Z (absence):     absent-now | present | unknown
// usage: node judge-provider-read-requalification.cjs --dir DIR --history CASE --claims FILE --out FILE
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
function arg(n) { const i = process.argv.indexOf("--" + n); if (i < 0) throw new Error("missing --" + n); return process.argv[i + 1]; }
const DIR = arg("dir"), HIST = arg("history"), CLAIMS = JSON.parse(fs.readFileSync(arg("claims"), "utf8")), OUT = arg("out");
const rd = f => { try { return JSON.parse(fs.readFileSync(path.join(DIR, f), "utf8")); } catch (e) { return null; } };
const sha = o => crypto.createHash("sha256").update(JSON.stringify(o)).digest("hex").slice(0, 8);
const key = r => `${r.status}|${r.operator}|${r.offset}`;

function load(name) {
  const rf = rd(name + ".reads.json"), q = rd(name + ".inspect-query.json"), p = rd(name + ".inspect-pattern.json");
  const reads = {}; for (const x of (rf && rf.reads) || []) reads[key(x.read)] = x;
  return {
    name, reads, wBefore: rf && rf.witnessBefore, wAfter: rf && rf.witnessAfter,
    world: q && q.ok ? q.result.worldFingerprint : null,
    qCanon: q && q.ok ? sha(q.result.canonical) : null, pCanon: p && p.ok ? sha(p.result.canonical) : null,
  };
}
const identity = w => w && !w.error ? [w.systemIdentifier, w.databaseOid, w.user, w.bypassRlsOrSuper, w.rlsOnTable].join("/") : null;
const H = load(HIST);

function judgeD(c) {
  if (!c.world || !c.qCanon || !c.pCanon) return { verdict: "unknown", why: ["product inspect failed"] };
  const diff = []; if (c.world !== H.world) diff.push("world"); if (c.qCanon !== H.qCanon) diff.push("query"); if (c.pCanon !== H.pCanon) diff.push("pattern");
  return diff.length ? { verdict: "stale", why: [`changed: ${diff.join(",")}`] } : { verdict: "reuse", why: [] };
}
// provider identity: same Provider/DB/session class as when the Claim was observed, and stable across this attempt
function providerSame(c) {
  const a = identity(c.wBefore), b = identity(c.wAfter), h = identity(H.wBefore);
  if (!a || !b || !h) return { ok: null, why: ["provider witness unavailable"] };
  if (a !== b) return { ok: false, why: ["provider witness changed during the attempt"] };
  if (a !== h) return { ok: false, why: ["provider identity differs from the observation"] };
  return { ok: true, why: [] };
}
function visibleAll(c) { const w = c.wBefore; return !!w && !w.error && (w.bypassRlsOrSuper === true || w.rlsOnTable === false); }

function J1p(c, claim) {
  if (claim.kind === "D") return judgeD(c);
  const r = c.reads[claim.read];
  if (!r || r.error) return { verdict: "unknown", why: [r ? "read failed: " + r.error.slice(0, 80) : "no read"] };
  const ps = providerSame(c);
  if (ps.ok === null) return { verdict: "unknown", why: ps.why };
  if (claim.kind === "R") return ps.ok ? { verdict: "reread", why: ["fresh rows attributable to the same provider identity"] } : { verdict: "stale", why: ps.why };
  // Z: absence needs a visibility witness at the time of THIS read
  if (r.rowCount > 0) return { verdict: "present", why: ["rows returned"] };
  if (!ps.ok) return { verdict: "unknown", why: ps.why };
  return visibleAll(c) ? { verdict: "absent-now", why: ["session sees every row"] } : { verdict: "unknown", why: ["zero rows under a restricted session (RLS applies): absence not established"] };
}
function J0(c, claim) { // everything re-read; no provider witness consulted
  if (claim.kind === "D") return judgeD(c);
  const r = c.reads[claim.read];
  if (!r || r.error) return { verdict: "unknown", why: ["read failed"] };
  return claim.kind === "R" ? { verdict: "reread", why: [] } : r.rowCount > 0 ? { verdict: "present", why: [] } : { verdict: "absent-now", why: ["zero rows"] };
}
function J1old(c, claim) { // TASK 3 short path: product world identity only
  const d = judgeD(c);
  if (claim.kind === "D") return d;
  return d.verdict === "reuse" ? (claim.kind === "R" ? { verdict: "reuse", why: ["world unchanged"] } : { verdict: (H.reads[claim.read] && H.reads[claim.read].rowCount === 0) ? "absent-now" : "present", why: ["world unchanged"] }) : J0(c, claim);
}
function J2(c, claim) { // old success reused as is
  if (claim.kind === "D") return { verdict: "reuse", why: [] };
  const h = H.reads[claim.read];
  return claim.kind === "R" ? { verdict: "reuse", why: [] } : { verdict: h && h.rowCount === 0 ? "absent-now" : "present", why: [] };
}
const METHODS = { J0, J1old, J1p, J2 };
const cases = fs.readdirSync(DIR).filter(f => f.endsWith(".reads.json")).map(f => f.replace(".reads.json", "")).filter(n => n !== HIST);
const claims = [{ id: "D", kind: "D" }].concat(CLAIMS);
const results = {};
for (const n of cases) {
  const c = load(n); results[n] = {};
  for (const [m, f] of Object.entries(METHODS)) {
    results[n][m] = {};
    for (const cl of claims) { const v = f(c, cl); results[n][m][cl.id] = { verdict: v.verdict, why: v.why }; }
  }
}
fs.writeFileSync(OUT, JSON.stringify({ scope: "judgement over CAPTURED real PostgreSQL reads and TEI replies; no Provider or Product was contacted", history: HIST, claims, results }, null, 1));
console.log("written", OUT, "cases", cases.length, "claims", claims.length);
