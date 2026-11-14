"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const probe = path.join(__dirname, "probe-tei-sei-requalification.cjs");
const scorer = path.join(__dirname, "score-requalification-probe.cjs");
function temp(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "tai-requal-test-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  return root;
}
function runProbe(source, work, out, dump) {
  const args = [probe, "--tei-bin", process.execPath, "--sei-bin", process.execPath,
    "--workspace", source, "--work", work, "--out", out];
  if (dump) args.push("--dump-observations", dump);
  return spawnSync(process.execPath, args, { encoding: "utf8" });
}
function score(root, actual, expected) {
  const a = path.join(root, "actual.json"), e = path.join(root, "expected.json");
  fs.writeFileSync(a, JSON.stringify({ results: actual }));
  fs.writeFileSync(e, JSON.stringify({ expected }));
  return spawnSync(process.execPath, [scorer, a, e], { encoding: "utf8" });
}
const verdict = () => ({ M: "reuse", L: "stale", K: "unknown", calls: 1, ms: 2 });
const actual = () => ({ A1: { J0: verdict(), J1: verdict(), J2: verdict() } });
const expected = () => ({ A1: { M: "reuse", L: "stale", K: "unknown" } });

test("matching claims score successfully; mismatches fail", t => {
  const root = temp(t);
  assert.equal(score(root, actual(), expected()).status, 0);
  const changed = actual(); changed.A1.J1.M = "stale";
  assert.equal(score(root, changed, expected()).status, 1);
});

test("missing claims, cases, and cost observations stay unscored", t => {
  const root = temp(t);
  const missingClaim = expected(); delete missingClaim.A1.L;
  let r = score(root, actual(), missingClaim);
  assert.equal(r.status, 2); assert.match(r.stdout, /UNSCORED/);
  r = score(root, {}, expected()); assert.equal(r.status, 2);
  const missingCost = actual(); delete missingCost.A1.J2.ms;
  r = score(root, missingCost, expected()); assert.equal(r.status, 2);
});

test("probe refuses an existing output without touching it or work files", t => {
  const root = temp(t), source = path.join(root, "source"), work = path.join(root, "work"), out = path.join(root, "output.json");
  fs.mkdirSync(source); fs.mkdirSync(work); fs.writeFileSync(out, "keep output");
  const r = runProbe(source, work, out);
  assert.notEqual(r.status, 0); assert.equal(fs.readFileSync(out, "utf8"), "keep output");
  assert.deepEqual(fs.readdirSync(work), []);
});

test("probe keeps caller-owned variants and store when an input is incomplete", t => {
  const root = temp(t), source = path.join(root, "source"), work = path.join(root, "work");
  fs.mkdirSync(source); fs.mkdirSync(work);
  for (const name of ["variants", "sei-store"]) {
    fs.mkdirSync(path.join(work, name)); fs.writeFileSync(path.join(work, name, "sentinel"), name);
  }
  const r = runProbe(source, work, path.join(root, "new-output.json"));
  assert.notEqual(r.status, 0);
  for (const name of ["variants", "sei-store"]) assert.equal(fs.readFileSync(path.join(work, name, "sentinel"), "utf8"), name);
  assert.ok(fs.readdirSync(work).some(name => name.startsWith("tei-sei-probe-")));
});

test("probe refuses work directory inside the source workspace", t => {
  const root = temp(t), source = path.join(root, "source"), work = path.join(source, "work");
  fs.mkdirSync(work, { recursive: true });
  const r = runProbe(source, work, path.join(root, "new-output.json"));
  assert.notEqual(r.status, 0); assert.match(r.stderr, /outside --workspace/);
  assert.deepEqual(fs.readdirSync(work), []);
});
