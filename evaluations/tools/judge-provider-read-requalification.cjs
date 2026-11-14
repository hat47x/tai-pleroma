#!/usr/bin/env node
"use strict";
// Judges whether a past real-Provider-Read Claim can still be used, from CAPTURED product output only.
// It never connects to a database or runs a product. Input per case (files produced by an evaluator harness
// that called the product's own Resolver/Executor and TEI `inspect`):
//   <case>.reads.json            {witnessBefore, witnessAfter, reads:[{read:{status,operator,offset}, error?, rows, rowCount, instanceId}]}
//                                witness = what the Provider reported before and after; connection binding is unproven
//   <case>.inspect-query.json    TEI `inspect -subject-kind query ...` reply
//   <case>.inspect-pattern.json  TEI `inspect -subject-kind application-pattern ...` reply
// The Consumer's requirement is a claims file: [{"id","read":"STATUS|OP|OFFSET","kind":"R"|"Z"}]
//   R = the Consumer reuses the rows of that Read.   Z = the Consumer reuses "nothing matched" (absence).
// It owns no graph, no store and no meaning; it compares what the Product and Provider said then and now.
//
// Methods (verdict vocabulary):
//   D (definition):  reuse | stale | unknown
//   R (rows):        reuse | reread | stale | unknown     J1p never returns reuse for R: no data-state witness exists.
//   Z (absence):     present | unknown for J1p; zero rows do not prove full visibility.
// usage: node judge-provider-read-requalification.cjs --dir DIR --history CASE --claims FILE --out FILE
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
function arg(n) { const i = process.argv.indexOf("--" + n); if (i < 0) throw new Error("missing --" + n); return process.argv[i + 1]; }
const DIR = arg("dir"), HIST = arg("history"), CLAIMS = JSON.parse(fs.readFileSync(arg("claims"), "utf8")), OUT = arg("out");
const rd = f => { try { return JSON.parse(fs.readFileSync(path.join(DIR, f), "utf8")); } catch (e) { return null; } };
const sha = o => o && typeof o === "object" ? crypto.createHash("sha256").update(JSON.stringify(o)).digest("hex") : null;
const key = r => `${r.status}|${r.operator}|${r.offset}`;

function load(name) {
  const rf = rd(name + ".reads.json"), q = rd(name + ".inspect-query.json"), p = rd(name + ".inspect-pattern.json");
  const reads = Object.create(null);
  for (const x of Array.isArray(rf?.reads) ? rf.reads : []) {
    const r = x?.read;
    if (!r || typeof r.status !== "string" || typeof r.operator !== "string" ||
        r.status.includes("|") || r.operator.includes("|") || !Number.isSafeInteger(r.offset)) continue;
    const k = key(r);
    reads[k] = Object.prototype.hasOwnProperty.call(reads, k) ? { error: "duplicate read key" } : x;
  }
  return {
    name, reads, wBefore: rf?.witnessBefore, wAfter: rf?.witnessAfter, sessionBinding: rf?.sessionBinding,
    world: q?.ok ? q.result?.worldFingerprint : null,
    pWorld: p?.ok ? p.result?.worldFingerprint : null,
    qCanon: q?.ok ? sha(q.result?.canonical) : null, pCanon: p?.ok ? sha(p.result?.canonical) : null,
  };
}
const identity = w => {
  if (!w || w.error || ![w.systemIdentifier, w.database, w.databaseOid, w.user].every(v => typeof v === "string" && v.trim()) ||
      !/^\d+$/.test(w.databaseOid) || w.databaseOid === "0" ||
      typeof w.bypassRlsOrSuper !== "boolean" || typeof w.rlsOnTable !== "boolean") return null;
  return JSON.stringify([w.systemIdentifier, w.database, w.databaseOid, w.user, w.bypassRlsOrSuper, w.rlsOnTable]);
};
const validRead = r => r && !r.error && typeof r.instanceId === "string" && r.instanceId.trim() &&
  Number.isSafeInteger(r.rowCount) && r.rowCount >= 0 && Array.isArray(r.rows) && r.rows.length === r.rowCount;
const H = load(HIST);

function judgeD(c) {
  if (!c.world || !c.pWorld || c.world !== c.pWorld || !c.qCanon || !c.pCanon || !H.world || !H.pWorld || H.world !== H.pWorld || !H.qCanon || !H.pCanon) return { verdict: "unknown", why: ["product or historical inspect is incomplete or inconsistent"] };
  const diff = []; if (c.world !== H.world) diff.push("world"); if (c.qCanon !== H.qCanon) diff.push("query"); if (c.pCanon !== H.pCanon) diff.push("pattern");
  return diff.length ? { verdict: "stale", why: [`changed: ${diff.join(",")}`] } : { verdict: "reuse", why: [] };
}
// provider identity: same Provider/DB/session class as when the Claim was observed, and stable across this attempt
function providerSame(c) {
  if (c.sessionBinding !== "single-read-only-transaction/v1" || H.sessionBinding !== "single-read-only-transaction/v1") {
    return { ok: null, why: ["read and provider witnesses lack a single-transaction binding"] };
  }
  const a = identity(c.wBefore), b = identity(c.wAfter), h = identity(H.wBefore), hAfter = identity(H.wAfter);
  if (!a || !b || !h || !hAfter || h !== hAfter) return { ok: null, why: ["provider witness unavailable or historical witness changed"] };
  if (a !== b) return { ok: false, why: ["provider witness changed during the attempt"] };
  if (a !== h) return { ok: false, why: ["provider identity differs from the observation"] };
  return { ok: true, why: [] };
}
// A MaxOpenConns(1) pool alone cannot bind reads and witnesses to a session.
// The capture must declare the single read-only transaction used for both.
function J1p(c, claim) {
  if (claim.kind === "D") return judgeD(c);
  const r = c.reads[claim.read];
  if (!validRead(r)) return { verdict: "unknown", why: ["read is missing, ambiguous, or incomplete"] };
  const ps = providerSame(c);
  if (ps.ok === null) return { verdict: "unknown", why: ps.why };
  if (!ps.ok) return { verdict: claim.kind === "R" ? "stale" : "unknown", why: ps.why };
  if (claim.kind === "R") return { verdict: "reread", why: ["read and provider witnesses share the declared read-only transaction"] };
  if (r.rowCount > 0) return { verdict: "present", why: ["rows returned in the declared read-only transaction"] };
  return { verdict: "unknown", why: ["zero rows do not establish complete source visibility"] };
}
function J0(c, claim) { // everything re-read; no provider witness consulted
  if (claim.kind === "D") return judgeD(c);
  const r = c.reads[claim.read];
  if (!validRead(r)) return { verdict: "unknown", why: ["read failed or is incomplete"] };
  return claim.kind === "R" ? { verdict: "reread", why: [] } : r.rowCount > 0 ? { verdict: "present", why: [] } : { verdict: "absent-now", why: ["zero rows"] };
}
function J1old(c, claim) { // TASK 3 short path: product world identity only
  const d = judgeD(c);
  if (claim.kind === "D") return d;
  if (d.verdict !== "reuse") return J0(c, claim);
  if (!validRead(H.reads[claim.read])) return { verdict: "unknown", why: ["historical read incomplete"] };
  return claim.kind === "R" ? { verdict: "reuse", why: ["world unchanged"] } : { verdict: H.reads[claim.read].rowCount === 0 ? "absent-now" : "present", why: ["world unchanged"] };
}
function J2(c, claim) { // old success reused as is
  if (claim.kind === "D") return { verdict: "reuse", why: [] };
  const h = H.reads[claim.read];
  if (!validRead(h)) return { verdict: "unknown", why: ["historical read incomplete"] };
  return claim.kind === "R" ? { verdict: "reuse", why: [] } : { verdict: h.rowCount === 0 ? "absent-now" : "present", why: [] };
}
const METHODS = { J0, J1old, J1p, J2 };
const cases = fs.readdirSync(DIR).filter(f => f.endsWith(".reads.json")).map(f => f.replace(".reads.json", "")).filter(n => n !== HIST);
if (!Array.isArray(CLAIMS) || CLAIMS.some(c => !c || typeof c.id !== "string" || !c.id || typeof c.read !== "string" || !["R", "Z"].includes(c.kind)) ||
    new Set(CLAIMS.map(c => c.id)).size !== CLAIMS.length || CLAIMS.some(c => c.id === "D")) throw new Error("invalid or duplicate claims");
const claims = [{ id: "D", kind: "D" }].concat(CLAIMS);
const results = Object.create(null);
for (const n of cases) {
  const c = load(n); results[n] = Object.create(null);
  for (const [m, f] of Object.entries(METHODS)) {
    results[n][m] = Object.create(null);
    for (const cl of claims) { const v = f(c, cl); results[n][m][cl.id] = { verdict: v.verdict, why: v.why }; }
  }
}
fs.writeFileSync(OUT, JSON.stringify({ scope: "judgement over captured records; no Provider or Product was contacted",
  methodQualifications: { J0: "negative control: no visibility witness", J1old: "negative control: world identity only", J1p: "checks declared transaction binding; zero rows do not prove full visibility", J2: "negative control: old result reused" },
  history: HIST, claims, results }, null, 1), { flag: "wx" });
console.log("written", OUT, "cases", cases.length, "claims", claims.length);
