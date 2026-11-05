#!/usr/bin/env python3
"""Check a bounded, synthetic CSW/YI candidate-selection trace.

This is a research-only structural check, not a cross-product contract,
human review, completeness proof, or authorization gate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA = "tai.research.yi-selection-surface/synthetic-v0"
STAGES = ("generated", "captured", "searched", "presented", "evaluated", "recommended")


def unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def check(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return {"passed": False, "errors": ["root is not an object"]}
    if data.get("schema") != SCHEMA or data.get("synthetic") is not True:
        errors.append("unexpected schema or non-synthetic input")
    run = data.get("run")
    if not isinstance(run, dict) or run.get("candidateUniverse") != "observed_in_this_run_only":
        errors.append("run scope must explicitly limit the candidate universe")
    if not isinstance(run, dict) or run.get("externalCoverage") != "unknown":
        errors.append("external universe cannot be claimed complete")

    records = data.get("candidates")
    ids: set[str] = set()
    if not isinstance(records, list) or not records:
        errors.append("candidates must be a nonempty list")
    else:
        for record in records:
            if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"]:
                errors.append("candidate lacks a valid ID")
                continue
            candidate = record["id"]
            if candidate in ids:
                errors.append(f"duplicate candidate ID: {candidate}")
            ids.add(candidate)
            if not isinstance(record.get("basis"), str) or not record["basis"].startswith("synthetic:"):
                errors.append(f"candidate has no synthetic basis: {candidate}")

    snapshots = data.get("stages")
    observed: dict[str, set[str]] = {}
    closed: dict[str, bool] = {}
    if not isinstance(snapshots, list) or len(snapshots) != len(STAGES):
        errors.append("stages must contain one ordered entry per stage")
    else:
        for index, item in enumerate(snapshots):
            stage = STAGES[index]
            if not isinstance(item, dict) or item.get("name") != stage:
                errors.append(f"stage at index {index} is not {stage}")
                continue
            raw = item.get("observedIds")
            if not isinstance(raw, list) or any(not isinstance(x, str) or not x for x in raw):
                errors.append(f"invalid observedIds for {stage}")
                continue
            if len(raw) != len(set(raw)):
                errors.append(f"duplicate observedIds for {stage}")
            current = set(raw)
            if not current <= ids:
                errors.append(f"unknown candidates in {stage}: {sorted(current - ids)}")
            if index == 0 and current != ids:
                errors.append("candidate register must match this run's observed generation set")
            if index > 0 and STAGES[index - 1] in observed:
                missing = current - observed[STAGES[index - 1]]
                if missing:
                    errors.append(f"reappearance without trace at {stage}: {sorted(missing)}")
            observed[stage] = current
            if type(item.get("closedForRun")) is not bool:
                errors.append(f"closedForRun must be boolean for {stage}")
            else:
                closed[stage] = item["closedForRun"]

    claims = data.get("claims")
    if not isinstance(claims, list):
        errors.append("claims must be an array")
    else:
        for i, claim in enumerate(claims):
            if not isinstance(claim, dict):
                errors.append(f"claim {i} is not an object")
                continue
            cid, stage, kind = claim.get("candidate"), claim.get("stage"), claim.get("kind")
            if cid not in ids or stage not in STAGES or claim.get("scope") != "this_run":
                errors.append(f"claim {i} has unknown candidate/stage or unbounded scope")
                continue
            if stage not in observed:
                errors.append(f"claim {i} references a malformed stage")
                continue
            if kind == "observed_in_bounded_stage":
                if cid not in observed[stage]:
                    errors.append(f"claim {i} asserts an unobserved candidate as present")
            elif kind == "absent_in_bounded_stage":
                position = STAGES.index(stage)
                if position == 0 or not closed.get(stage, False):
                    errors.append(f"claim {i} cannot infer absence without a closed noninitial stage")
                elif cid in observed[stage]:
                    errors.append(f"claim {i} contradicts the observed stage")
                elif STAGES[position - 1] not in observed or cid not in observed[STAGES[position - 1]]:
                    errors.append(f"claim {i} cannot attribute drop to this stage")
            else:
                errors.append(f"claim {i} has unlicensed kind (no global absence or rejection)")
    if data.get("ownerAccepted") is not False or data.get("realWorldEvaluation") != "not_run":
        errors.append("test fixture must not imply Owner acceptance or real-world evaluation")
    return {"passed": not errors, "errors": errors,
            "observedCounts": {name: len(observed.get(name, [])) for name in STAGES},
            "scope": "bounded synthetic trace; no global absence, correctness, or authorization"}


def check_file(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)
    except (OSError, UnicodeError, ValueError) as exc:
        return {"passed": False, "errors": [f"invalid fixture: {exc}"]}
    return check(data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", nargs="?", default=str(Path(__file__).with_name("fixtures") / "yi-selection-surface-synthetic.json"))
    args = parser.parse_args()
    result = check_file(Path(args.fixture))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
