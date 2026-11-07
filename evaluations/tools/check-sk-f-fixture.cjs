// Synthetic SK-F fixture self-check only; no real product or network access.
const fs = require("fs");
const fixture = JSON.parse(fs.readFileSync(process.argv[2] || "evaluations/fixtures/SK-F-access-rule-disclosure.synthetic.json", "utf8"));
function classify(x) {
 if (x.kind === "footprint") return !x.requested ? "declared_only" : x.witness.level !== "provider" ? "physical_access_unknown" : x.witness.accesses.some(v => !x.declared.includes(v)) ? "observed_overfetch" : "provider_witness_within_declaration";
 if (x.kind === "output_comparison") return JSON.stringify(x.worlds[0].projection) === JSON.stringify(x.worlds[1].projection) && JSON.stringify(x.worlds[0].reads) !== JSON.stringify(x.worlds[1].reads) ? "same_output_different_reads" : "other";
 if (x.kind === "rule") return x.rule_dependencies.every(v => x.observed_dependencies.includes(v)) ? (x.consumer_may_view_result ? "disclosable_rule_result" : "result_withheld") : "rule_unresolved";
 if (x.kind === "completeness") return x.requested === "all" && !x.observed_complete ? "completeness_unproved" : "other";
 if (x.kind === "snapshot") return x.observations.every(v => v.source === x.observations[0].source && v.epoch === x.observations[0].epoch) ? "same_snapshot" : "mixed_snapshot";
 if (x.kind === "planner") return x.public_actions.includes(x.chosen_action) ? "public_only_route" : x.private_actions.includes(x.chosen_action) ? "private_route_leaked" : "unsupported_route";
 if (x.kind === "egress") return x.external_send_attempted && !x.external_send_allowed ? "egress_forbidden" : "other";
 if (x.kind === "action") return x.rule_preview_ok && !x.current_grant_observed && !x.commit_receipt_observed ? "preview_only" : "other";
 throw new Error("unsupported kind");
}
const output = fixture.cases.map(x => ({id:x.id,actual:classify(x),passed:classify(x)===x.expected}));
console.log(JSON.stringify({scope:"public fixture only",passed:output.filter(x=>x.passed).length,failed:output.filter(x=>!x.passed).length,output},null,2));
if (output.some(x => !x.passed)) process.exitCode = 1;
