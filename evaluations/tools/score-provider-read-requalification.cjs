#!/usr/bin/env node
"use strict";
// Scores judge-provider-read-requalification.cjs output against an evaluator-supplied expected file
// (not stored in this repository). Cases or claims without an expected entry are reported as unscored.
// Safety counters are never netted against cost.
//   unsafeReuse   : method said reuse / absent-now where expected says stale / present / unknown / reread-required
//   overStale     : method said stale or unknown where expected says reuse / reread / absent-now
// usage: node score-provider-read-requalification.cjs <judge-result.json> <expected.json>
const fs = require("node:fs");
const act = JSON.parse(fs.readFileSync(process.argv[2], "utf8")), expFile = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
const exp = expFile.expected || expFile;
const tot = {}; const unscored = [];
const OPT = new Set(["reuse", "absent-now"]); // verdicts that let the Consumer keep using the old Claim as is
for (const [n, byM] of Object.entries(act.results)) {
  if (!exp[n]) { unscored.push(n); continue; }
  for (const [m, byC] of Object.entries(byM)) {
    tot[m] = tot[m] || { correct: 0, wrong: 0, unsafeReuse: 0, overCautious: 0, other: 0 };
    for (const [cid, v] of Object.entries(byC)) {
      const e = exp[n][cid]; if (e === undefined) { unscored.push(`${n}/${cid}`); continue; }
      if (v.verdict === e) { tot[m].correct++; continue; }
      tot[m].wrong++;
      if (OPT.has(v.verdict) && !OPT.has(e)) tot[m].unsafeReuse++;
      else if (!OPT.has(v.verdict) && OPT.has(e)) tot[m].overCautious++;
      else tot[m].other++;
      console.log(`${n} ${m} ${cid}: ${v.verdict} (expected ${e})`);
    }
  }
}
if (unscored.length) console.log("UNSCORED:", [...new Set(unscored)].join(", "));
console.log(JSON.stringify(tot, null, 1));
