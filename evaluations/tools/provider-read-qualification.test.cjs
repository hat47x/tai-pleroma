"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const judge = path.join(__dirname, "judge-provider-read-requalification.cjs");
const scorer = path.join(__dirname, "score-provider-read-requalification.cjs");
function temporary(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tai-provider-test-"));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return dir;
}
function put(dir, name, value) { fs.writeFileSync(path.join(dir, name), JSON.stringify(value)); }
function fixture() {
  const witness = { systemIdentifier: "cluster", database: "db", databaseOid: "1", user: "reader", bypassRlsOrSuper: false, rlsOnTable: true };
  const read = { read: { status: "OPEN", operator: "eq", offset: 0 }, instanceId: "instance", rowCount: 0, rows: [] };
  return { sessionBinding: "single-read-only-transaction/v1", witnessBefore: witness, witnessAfter: { ...witness }, reads: [read] };
}
function setup(t) {
  const dir = temporary(t), h = fixture(), c = fixture();
  const inspectQ = { ok: true, result: { worldFingerprint: "world", canonical: { id: "query" } } };
  const inspectP = { ok: true, result: { worldFingerprint: "world", canonical: { id: "pattern" } } };
  for (const name of ["base", "case"]) { put(dir, `${name}.inspect-query.json`, inspectQ); put(dir, `${name}.inspect-pattern.json`, inspectP); }
  put(dir, "base.reads.json", h); put(dir, "case.reads.json", c);
  put(dir, "claims.json", [{ id: "R", read: "OPEN|eq|0", kind: "R" }, { id: "Z", read: "OPEN|eq|0", kind: "Z" }]);
  return { dir, h, c, inspectQ, inspectP };
}
function evaluate(dir, output = "result.json") {
  const out = path.join(dir, output);
  const r = spawnSync(process.execPath, [judge, "--dir", dir, "--history", "base", "--claims", path.join(dir, "claims.json"), "--out", out], { encoding: "utf8" });
  return { r, out, data: r.status === 0 ? JSON.parse(fs.readFileSync(out, "utf8")) : null };
}

test("bound observations permit reread but zero rows never prove full visibility", t => {
  const { dir } = setup(t), { r, data } = evaluate(dir);
  assert.equal(r.status, 0, r.stderr);
  assert.equal(data.results.case.J1p.R.verdict, "reread");
  assert.equal(data.results.case.J1p.Z.verdict, "unknown");
  assert.match(data.methodQualifications.J0, /negative control/);
});

test("missing transaction binding or provider fields remain unknown", t => {
  const { dir, c } = setup(t); delete c.sessionBinding; put(dir, "case.reads.json", c);
  let x = evaluate(dir, "unbound.json"); assert.equal(x.r.status, 0, x.r.stderr); assert.equal(x.data.results.case.J1p.R.verdict, "unknown");
  c.sessionBinding = "single-read-only-transaction/v1"; delete c.witnessBefore.databaseOid; delete c.witnessAfter.databaseOid;
  put(dir, "case.reads.json", c); x = evaluate(dir, "missing-witness.json");
  assert.equal(x.r.status, 0, x.r.stderr); assert.equal(x.data.results.case.J1p.R.verdict, "unknown");
});

test("missing counts and duplicate read keys do not prove absence", t => {
  const { dir, c } = setup(t); delete c.reads[0].rowCount; put(dir, "case.reads.json", c);
  let x = evaluate(dir, "missing-count.json"); assert.equal(x.r.status, 0, x.r.stderr); assert.equal(x.data.results.case.J1p.Z.verdict, "unknown");
  c.reads[0].rowCount = 0; c.reads.push({ ...c.reads[0] }); put(dir, "case.reads.json", c);
  x = evaluate(dir, "duplicate.json"); assert.equal(x.r.status, 0, x.r.stderr); assert.equal(x.data.results.case.J1p.R.verdict, "unknown");
});

test("incomplete or cross-world inspect evidence is unknown", t => {
  const { dir, inspectQ, inspectP } = setup(t); delete inspectQ.result.canonical; put(dir, "case.inspect-query.json", inspectQ);
  let x = evaluate(dir, "missing-canonical.json"); assert.equal(x.r.status, 0, x.r.stderr); assert.equal(x.data.results.case.J1p.D.verdict, "unknown");
  inspectQ.result.canonical = { id: "query" }; put(dir, "case.inspect-query.json", inspectQ);
  inspectP.result.worldFingerprint = "other-world"; put(dir, "case.inspect-pattern.json", inspectP);
  x = evaluate(dir, "cross-world.json"); assert.equal(x.r.status, 0, x.r.stderr); assert.equal(x.data.results.case.J1p.D.verdict, "unknown");
});

test("judge never overwrites an existing output", t => {
  const { dir } = setup(t); const out = path.join(dir, "existing.json"); fs.writeFileSync(out, "keep");
  const x = evaluate(dir, "existing.json"); assert.notEqual(x.r.status, 0); assert.equal(fs.readFileSync(out, "utf8"), "keep");
});

test("claim IDs cannot overwrite object prototypes or each other", t => {
  const { dir } = setup(t);
  put(dir, "claims.json", [{ id: "__proto__", read: "OPEN|eq|0", kind: "R" }]);
  const x = evaluate(dir, "prototype.json");
  assert.equal(x.r.status, 0, x.r.stderr);
  assert.equal(x.data.results.case.J1p.__proto__.verdict, "reread");
  put(dir, "claims.json", [{ id: "same", read: "OPEN|eq|0", kind: "R" }, { id: "same", read: "OPEN|eq|0", kind: "Z" }]);
  assert.notEqual(evaluate(dir, "duplicate-claims.json").r.status, 0);
});

test("scorer distinguishes correct, wrong and incomplete claims", t => {
  const dir = temporary(t), methods = ["J0", "J1old", "J1p", "J2"];
  const results = { case: Object.fromEntries(methods.map(m => [m, { R: { verdict: "reread" } }])) };
  put(dir, "actual.json", { results }); put(dir, "expected.json", { case: { R: "reread" } });
  const run = () => spawnSync(process.execPath, [scorer, path.join(dir, "actual.json"), path.join(dir, "expected.json")], { encoding: "utf8" });
  assert.equal(run().status, 0);
  results.case.J1p.R.verdict = "reuse"; put(dir, "actual.json", { results }); assert.equal(run().status, 1);
  delete results.case.J1p; put(dir, "actual.json", { results }); const incomplete = run(); assert.equal(incomplete.status, 2); assert.match(incomplete.stdout, /UNSCORED/);
});
