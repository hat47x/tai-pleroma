#!/usr/bin/env node
"use strict";
// Scores probe-tei-sei-requalification.cjs output against an expected file supplied by an evaluator.
// The expected file is NOT stored in this repository. A case or method with no expected entry is reported
// as "unscored", never counted as correct. Safety counters are reported separately and never netted
// against cost: unsafeReuse (stale/unknown judged reuse), unknownMissed, overStale (reuse judged stale).
// usage: node score-requalification-probe.cjs <probe-result.json> <expected.json>
// Exit 0 means all supplied cases were scored correctly; 1 means at least one
// mismatch; 2 means one or more cases, claims or cost observations are unscored.
const fs = require("node:fs");
const act = JSON.parse(fs.readFileSync(process.argv[2], "utf8")).results;
const expFile = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
const exp = expFile.expected || expFile;
const tot = {}; const unscored = [];
for (const j of ["J0", "J1", "J2"]) tot[j] = { correct: 0, wrong: 0, unsafeReuse: 0, unknownMissed: 0, overStale: 0, unknownKept: 0, calls: 0, ms: 0 };
const rows = [];
const verdicts = new Set(["reuse", "stale", "unknown"]);
if (Object.keys(act).length === 0) unscored.push("no actual results");
for (const name of Object.keys(exp)) {
  if (!Object.prototype.hasOwnProperty.call(act, name)) unscored.push(`${name}: no actual entry`);
}
for (const name of Object.keys(act)) {
  if (typeof act[name] === "string") { unscored.push(`${name}: ${act[name]}`); continue; }
  if (!exp[name]) { unscored.push(`${name}: no expected entry`); continue; }
  const row = [name.padEnd(3)];
  for (const j of ["J0", "J1", "J2"]) {
    const a = act[name][j]; let cell = "";
    if (!a || typeof a !== "object") { unscored.push(`${name}/${j}: no actual verdict`); continue; }
    for (const c of ["M", "L", "K"]) {
      const e = exp[name][c], g = a[c];
      if (!verdicts.has(e) || !verdicts.has(g)) {
        unscored.push(`${name}/${j}/${c}: missing or invalid verdict`);
        continue;
      }
      if (e === g) { tot[j].correct++; cell += `${c}=${g} `; if (g === "unknown") tot[j].unknownKept++; }
      else {
        tot[j].wrong++; cell += `${c}=${g}(expected ${e}) `;
        if (g === "reuse" && e === "stale") tot[j].unsafeReuse++;
        else if (g === "reuse" && e === "unknown") tot[j].unknownMissed++;
        else tot[j].overStale++;
      }
    }
    if (!Number.isFinite(a.calls) || a.calls < 0 || !Number.isFinite(a.ms) || a.ms < 0) {
      unscored.push(`${name}/${j}: missing or invalid cost observation`);
    } else {
      tot[j].calls += a.calls; tot[j].ms += a.ms;
    }
    row.push(`${j}[${a.calls} calls, ${a.note}] ${cell}`);
  }
  rows.push(row.join(" | "));
}
console.log(rows.join("\n"));
if (unscored.length) console.log("UNSCORED:", unscored.join("; "));
console.log(JSON.stringify(tot, null, 1));
if (Object.values(tot).some(t => t.wrong)) process.exitCode = 1;
else if (unscored.length) process.exitCode = 2;
