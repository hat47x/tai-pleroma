#!/usr/bin/env python3
"""Render a synthetic research stimulus, or check a *public* fixture.

No TEI/EKI/MFT command is executed here. Public Gold is NOT an independent holdout.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STIMULI = ROOT / "fixtures" / "RQ7_BOUNDED_COMPLETENESS_PILOT.synthetic.json"
GOLD = ROOT / "fixtures" / "RQ7_BOUNDED_COMPLETENESS_GOLD.public.json"
ARMS = ("V0", "V1", "V2", "V3")
VERDICTS = {"supported", "refuted", "undetermined"}
TICK = chr(96)


def load() -> tuple[dict, dict]:
    return (
        json.loads(STIMULI.read_text(encoding="utf-8")),
        json.loads(GOLD.read_text(encoding="utf-8")),
    )


def validate(stimuli: dict, gold: dict) -> dict:
    errors: list[str] = []
    if stimuli.get("schema") != "tai.research.rq7-stimuli/v0" or not stimuli.get("synthetic"):
        errors.append("invalid synthetic stimulus schema")
    if gold.get("schema") != "tai.research.rq7-public-gold/v0" or not gold.get("synthetic"):
        errors.append("invalid public gold schema")
    if stimuli.get("holdout") is not False or gold.get("holdout") is not False:
        errors.append("public pilot must not be labelled as a holdout")
    if stimuli.get("experiment_run_status") != "NOT_RUN" or gold.get("run_status") != "NOT_RUN":
        errors.append("prepilot experiment status must be NOT_RUN")

    cases = stimuli.get("cases", [])
    answers = gold.get("cases", [])
    ids = [case.get("id") for case in cases]
    keys = [item.get("id") for item in answers]
    if len(ids) != len(set(ids)) or len(keys) != len(set(keys)) or set(ids) != set(keys):
        errors.append("case IDs missing, duplicated or mismatched")
    for case in cases:
        cid = case.get("id", "?")
        nodes = case.get("declared", {}).get("nodes", [])
        node_ids = [node.get("id") for node in nodes]
        if not node_ids or len(node_ids) != len(set(node_ids)):
            errors.append(f"{cid}: duplicate or empty graph nodes")
        if any(not isinstance(n, str) or re.fullmatch(r"[a-z][a-z0-9_]*", n) is None for n in node_ids):
            errors.append(f"{cid}: unsafe node ID")
        for edge in case.get("declared", {}).get("edges", []):
            if not isinstance(edge, list) or len(edge) != 2 or any(n not in node_ids for n in edge):
                errors.append(f"{cid}: dangling or malformed edge")
        req = case.get("resolved", {}).get("required", [])
        skips = case.get("resolved", {}).get("valid_skips", [])
        if (set(req) | set(skips)) - set(node_ids) or set(req) & set(skips):
            errors.append(f"{cid}: invalid required or skipped steps")
        if case.get("observed", {}).get("observer_coverage") not in ("partial", "closed-for-specified-steps"):
            errors.append(f"{cid}: unsupported observer coverage")
        if case.get("disclosure") != "public-synthetic":
            errors.append(f"{cid}: non-public or unknown disclosure")
        if "gold" in case or "expected" in case:
            errors.append(f"{cid}: Gold leaked into subject stimulus")
    for entry in answers:
        expected = entry.get("expected", {})
        if set(expected) != set(ARMS) or any(value not in VERDICTS for value in expected.values()):
            errors.append(f"{entry.get('id')}: invalid verdict set")
        if expected.get("V0") != expected.get("V1") or expected.get("V2") != expected.get("V3"):
            errors.append(f"{entry.get('id')}: unequal Gold under equivalent-information arms")
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "status": "PUBLIC_SYNTHETIC_FIXTURE_CHECK_ONLY",
        "experiment_run_status": "NOT_RUN",
        "cases": len(cases),
        "gold_entries": len(answers),
        "arms": list(ARMS),
        "independent_holdout": False,
    }


def declared_text(case: dict) -> str:
    lines = ["### Declared graph — text"]
    lines += [f"- Node {TICK}{n['id']}{TICK}: {n['label']}" for n in case["declared"]["nodes"]]
    lines += [f"- Edge: {TICK}{a}{TICK} → {TICK}{b}{TICK}" for a, b in case["declared"]["edges"]]
    return "\n".join(lines)


def declared_graph(case: dict) -> str:
    lines = ["### Declared graph — diagram", TICK * 3 + "mermaid", "flowchart LR"]
    for node in case["declared"]["nodes"]:
        label = node["label"].replace('"', "'").replace("<", "‹").replace(">", "›")
        lines.append(f'  {node["id"]}["{label}"]')
    for a, b in case["declared"]["edges"]:
        lines.append(f"  {a} --> {b}")
    lines.append(TICK * 3)
    return "\n".join(lines)


def evidence(case: dict) -> str:
    resolved, observed, consumer = case["resolved"], case["observed"], case["consumer"]
    rows = [
        "### Additional stipulated evidence (public synthetic input)",
        f"- Required steps: {', '.join(resolved['required']) or '(none)'}",
        f"- Legitimate skips: {', '.join(resolved['valid_skips']) or '(none)'}",
        f"- Expected input revision: {resolved['expected_input_revision']}",
        f"- Observed input revision: {observed['actual_input_revision']}",
        f"- Expected artifact generation: {resolved['expected_generation']}",
        f"- Observed artifact generation: {observed['artifact_generation']}",
        f"- Observer coverage: {observed['observer_coverage']} (stipulated; not independently verified)",
        f"- Observed event steps: {', '.join(e['step'] for e in observed['events']) or '(none recorded)'}",
        f"- Transfer ACK: {consumer.get('ack', '(not recorded)')}",
        f"- Consumer read generation: {consumer.get('read_generation', '(not recorded)')}",
        "- Consumer member reads: " + (
            ", ".join(f"{r['member']}@{r['generation']}" for r in consumer.get("reads", []))
            or "(not observed)"
        ),
    ]
    return "\n".join(rows)


def render(case: dict, arm: str) -> str:
    if arm not in ARMS:
        raise ValueError("unknown arm")
    sections = [
        f"## RQ7 {case['id']} — {arm}",
        f"**Domain**: {case['domain']} | **Scope**: {case['scope']} | **Graph revision**: {case['revision']}",
        "**Status**: PUBLIC SYNTHETIC STIMULUS — NOT actual Product execution; NOT an independent holdout.",
        f"**Question**: {case['claim']}",
        declared_graph(case) if arm in ("V1", "V3") else declared_text(case),
    ]
    if arm in ("V2", "V3"):
        sections.append(evidence(case))
    sections.append("**Answer**: supported / refuted / undetermined. Give the exact evidence boundary and the next check needed.")
    return "\n\n".join(sections) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check the public fixtures only")
    parser.add_argument("--case", help="case ID to render")
    parser.add_argument("--arm", choices=ARMS, help="presentation and evidence arm")
    args = parser.parse_args()
    if not args.check and (not args.case or not args.arm):
        parser.error("specify --check or both --case and --arm")
    stimuli, gold = load()
    result = validate(stimuli, gold)
    if args.check:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    matches = [case for case in stimuli["cases"] if case["id"] == args.case]
    if len(matches) != 1:
        parser.error("unknown case")
    print(render(matches[0], args.arm), end="")


if __name__ == "__main__":
    main()
