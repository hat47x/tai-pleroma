#!/usr/bin/env node
"use strict";
// Scores captured-record judgments against an evaluator-supplied expected file.
// Exit 0: all cases scored correctly; 1: a mismatch; 2: incomplete scoring.
const fs = require("node:fs");
const act = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const expFile = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
const exp = expFile.expected || expFile;
const methods = ["J0", "J1old", "J1p", "J2"];
const verdicts = new Set(["reuse", "reread", "reread-required", "stale", "unknown", "absent-now", "present"]);
const optimistic = new Set(["reuse", "absent-now"]);
const tot = {}, unscored = [];
if (!act.results || typeof act.results !== "object" || !exp || typeof exp !== "object") throw new Error("invalid scoring inputs");
if (Object.keys(act.results).length === 0) unscored.push("no actual cases");
for (const n of Object.keys(exp)) if (!Object.hasOwn(act.results, n)) unscored.push(`${n}: no actual case`);
for (const [n, byM] of Object.entries(act.results)) {
  if (!exp[n] || typeof exp[n] !== "object") { unscored.push(`${n}: no expected case`); continue; }
  for (const m of methods) {
    const byC = byM && byM[m];
    if (!byC || typeof byC !== "object") { unscored.push(`${n}/${m}: no actual method`); continue; }
    tot[m] ||= { correct: 0, wrong: 0, unsafeReuse: 0, overCautious: 0, other: 0 };
    for (const cid of Object.keys(exp[n])) {
      const e = exp[n][cid], g = byC[cid]?.verdict;
      if (!verdicts.has(e) || !verdicts.has(g)) { unscored.push(`${n}/${m}/${cid}: missing or invalid verdict`); continue; }
      if (g === e) { tot[m].correct++; continue; }
      tot[m].wrong++;
      if (optimistic.has(g) && !optimistic.has(e)) tot[m].unsafeReuse++;
      else if (!optimistic.has(g) && optimistic.has(e)) tot[m].overCautious++;
      else tot[m].other++;
      console.log(`${n} ${m} ${cid}: ${g} (expected ${e})`);
    }
    for (const cid of Object.keys(byC)) if (!Object.hasOwn(exp[n], cid)) unscored.push(`${n}/${m}/${cid}: no expected claim`);
  }
}
if (unscored.length) console.log("UNSCORED:", [...new Set(unscored)].join(", "));
console.log(JSON.stringify(tot, null, 1));
if (Object.values(tot).some(t => t.wrong)) process.exitCode = 1;
else if (unscored.length || !Object.values(tot).some(t => t.correct)) process.exitCode = 2;
