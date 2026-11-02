#!/usr/bin/env node
"use strict";

// This is a public, deliberately limited fixture self-check.
// It neither calls TEI nor executes Product/Harness Skills.
// Expected outcomes in the fixture are intentionally visible.

const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");

function classify(c, context) {
  const base = { effect_confirmed: false };
  if (c.visibility === "hidden") return { status: "withheld_discovery", ...base };
  if (c.epoch !== context.epoch) return { status: "stale_context", ...base };

  switch (c.operation) {
    case "read":
      if (c.subject_kind === "entity" && context.cohorts.D1.known.includes(c.subject)) {
        return { status: "read_offer_only", subject: c.subject, ...base };
      }
      return { status: "unresolved_subject", ...base };
    case "edit":
      if (c.subject_kind === "aggregate" && c.known_inverse_targets.length === 0) {
        return { status: "ambiguous_inverse", ...base };
      }
      if (c.subject_kind === "entity" && context.cohorts.D1.known.includes(c.subject)) {
        return { status: "intent_candidate_authority_unverified", ...base };
      }
      return { status: "requires_specialist_contract", ...base };
    case "bulk_delete":
      if (c.requires_complete && !context.cohorts[c.subject]?.complete) {
        return { status: "requires_complete_scope", ...base };
      }
      return { status: "intent_candidate_authority_unverified", ...base };
    case "unlink":
      return c.subject_kind === "edge"
        ? { status: "edge_intent_candidate", ...base }
        : { status: "subject_kind_mismatch", ...base };
    case "count_entities":
      return {
        status: "read_result_only",
        entity_count: new Set(context.join.entity_ids).size,
        ...base
      };
    case "discover":
      return { status: "discovery_candidate_only", ...base };
    case "confirm_effect":
      return c.provider_ack && !c.effect_observed
        ? { status: "receipt_only", ...base }
        : { status: "not_established", ...base };
    default:
      return { status: "unsupported_operation", ...base };
  }
}

function run(inputPath) {
  const bytes = fs.readFileSync(inputPath);
  const fixture = JSON.parse(bytes.toString("utf8"));
  if (!Array.isArray(fixture.cases) || fixture.cases.length === 0) throw new Error("no cases");
  const ids = new Set(), observations = [];

  for (const c of fixture.cases) {
    if (ids.has(c.id)) throw new Error("duplicate case id: " + c.id);
    ids.add(c.id);
    const actual = classify(c, fixture.context);
    const passed = JSON.stringify(actual) === JSON.stringify(c.expected);
    observations.push({ id: c.id, passed, actual, expected: c.expected });
  }

  const summary = {
    fixture_id: fixture.fixture_id,
    fixture_sha256: crypto.createHash("sha256").update(bytes).digest("hex"),
    kind: "public-fixture-classification-selfcheck-only",
    cases: observations.length,
    passed: observations.filter(x => x.passed).length,
    failed: observations.filter(x => !x.passed).length,
    not_run: [
      "Actual Skill selection or loading",
      "TEI semantic action applicability/Product CLI",
      "Human or Owner business acceptance",
      "OS/Host authorization and isolation",
      "Provider effects and independent observations",
      "Sealed holdout comparison and multiple Harnesses"
    ],
    observations
  };
  process.stdout.write(JSON.stringify(summary, null, 2) + "\n");
  if (summary.failed) process.exitCode = 1;
}

if (require.main === module) {
  const input = process.argv[2]
    ? path.resolve(process.argv[2])
    : path.resolve(__dirname, "../fixtures/SK-M-semantic-action.synthetic.json");
  run(input);
}

module.exports = { classify, run };
