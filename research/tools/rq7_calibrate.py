#!/usr/bin/env python3
"""Calibrate PUBLIC synthetic RQ7 Gold with deterministic, non-agent baselines.

This tool deliberately reads public Gold. Never use it with blinded participants,
private holdouts, or as proof of TEI Product, human, or AI performance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import rq7_pilot

VERDICTS = ("supported", "refuted", "undetermined")
ARMS = rq7_pilot.ARMS


def declared_query_verdict(case: dict) -> str:
    """Answer ONLY explicitly typed declaration queries; otherwise abstain.

    The selector is research metadata, not provided to the study participant.
    This is a privileged calibration bound, NOT a fair human/AI comparator.
    """
    selector = case.get("question_selector")
    if selector is None:
        return "undetermined"
    if set(selector) != {"kind", "source", "target"}:
        raise ValueError("unsupported query selector fields")
    source, target, kind = (
        selector["source"],
        selector["target"],
        selector["kind"],
    )
    nodes = {node["id"] for node in case["declared"]["nodes"]}
    if source not in nodes or target not in nodes:
        raise ValueError("query endpoint is outside declared nodes")
    edges = {tuple(pair) for pair in case["declared"]["edges"]}
    if kind == "direct-edge":
        return "supported" if (source, target) in edges else "refuted"
    if kind != "directed-path":
        raise ValueError("unsupported query predicate")
    seen = {source}
    todo = [source]
    while todo:
        current = todo.pop(0)
        if current == target:
            return "supported"
        for a, b in edges:
            if a == current and b not in seen:
                seen.add(b)
                todo.append(b)
    return "refuted"


def score(gold: list[str], answers: list[str]) -> dict:
    if not gold or len(gold) != len(answers):
        raise ValueError("empty or misaligned responses")
    if any(v not in VERDICTS for v in gold + answers):
        raise ValueError("invalid verdict")
    confusion = {
        actual: {predicted: 0 for predicted in VERDICTS}
        for actual in VERDICTS
    }
    for actual, predicted in zip(gold, answers):
        confusion[actual][predicted] += 1
    n = len(gold)
    correct = sum(a == b for a, b in zip(gold, answers))
    false_certainty = sum(a == "undetermined" and b != a for a, b in zip(gold, answers))
    unnecessary_abstention = sum(a != "undetermined" and b == "undetermined" for a, b in zip(gold, answers))
    wrong_direction = sum(a != "undetermined" and b != "undetermined" and a != b for a, b in zip(gold, answers))
    return {
        "correct": correct,
        "total": n,
        "accuracy": round(correct / n, 6),
        "false_certainty": false_certainty,
        "unnecessary_abstention": unnecessary_abstention,
        "wrong_direction": wrong_direction,
        "confusion": confusion,
    }


def _frequency(vals: list[str]) -> dict:
    counts = Counter(vals)
    return {key: counts[key] for key in VERDICTS}


def calibrate(dataset: str) -> dict:
    stimuli, gold_document = rq7_pilot.load(dataset)
    rq7_pilot.validate(stimuli, gold_document)
    if stimuli.get("holdout") is not False or gold_document.get("holdout") is not False:
        raise ValueError("never calibrate a holdout")
    if stimuli.get("experiment_run_status") != "NOT_RUN":
        raise ValueError("calibration fixture must have NOT_RUN study status")
    gold_by_id = {entry["id"]: entry for entry in gold_document["cases"]}
    cases = stimuli["cases"]
    if len(gold_by_id) != len(cases):
        raise ValueError("Gold IDs are not one-to-one")

    group_names = list(dict.fromkeys(c.get("study_case_stage", "unclassified") for c in cases))
    rules = ("always-supported", "always-refuted", "always-undetermined", "typed-selector-else-undetermined")
    arm_metrics = {}
    for arm in ARMS:
        actual = [gold_by_id[c["id"]]["expected"][arm] for c in cases]
        predicted = {
            "always-supported": ["supported"] * len(cases),
            "always-refuted": ["refuted"] * len(cases),
            "always-undetermined": ["undetermined"] * len(cases),
            "typed-selector-else-undetermined": [declared_query_verdict(c) for c in cases],
        }
        results = {}
        for rule in rules:
            totals = score(actual, predicted[rule])
            by_group = {}
            for group in group_names:
                indices = [i for i, case in enumerate(cases) if case.get("study_case_stage", "unclassified") == group]
                by_group[group] = {
                    "gold_distribution": _frequency([actual[i] for i in indices]),
                    "score": score([actual[i] for i in indices], [predicted[rule][i] for i in indices]),
                }
            results[rule] = {"overall": totals, "by_study_case_stage": by_group}
        arm_metrics[arm] = {
            "gold_distribution": _frequency(actual),
            "baselines": results,
        }

    source, gold_path = rq7_pilot.PUBLIC_DATASETS[dataset]
    return {
        "status": "PUBLIC_SYNTHETIC_GOLD_CALIBRATION_ONLY",
        "study_experiment_status": "NOT_RUN",
        "human_or_ai_responses": "NONE",
        "product_execution": "NOT_RUN",
        "dataset": dataset,
        "holdout": False,
        "privileged_baseline_notice": (
            "typed-selector-else-undetermined accesses typed metadata hidden from "
            "participant renderings. It is a calibration bound, NOT a fair AI/human model."
        ),
        "source_sha256": hashlib.sha256(Path(source).read_bytes()).hexdigest(),
        "gold_sha256": hashlib.sha256(Path(gold_path).read_bytes()).hexdigest(),
        "cases": len(cases),
        "arms": arm_metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=tuple(rq7_pilot.PUBLIC_DATASETS), default="v1")
    args = parser.parse_args()
    print(json.dumps(calibrate(args.dataset), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
