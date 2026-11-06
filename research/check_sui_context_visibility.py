#!/usr/bin/env python3
"""Bounded read-only observation of candidate IDs in a SUI Context bundle.

Input is a synthetic or explicitly permitted *saved* response, never a live
SUI request. Does not prove completeness, meaning, or disclosure authorization.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _ids(rows: Any, key: str, errors: list[str]) -> set[str]:
    if not isinstance(rows, list):
        errors.append(f"{key} must be an array")
        return set()
    values: list[str] = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            errors.append(f"{key}[{i}] requires a nonempty id")
        else:
            values.append(row["id"])
    if len(values) != len(set(values)):
        errors.append(f"{key} contains duplicate ids")
    return set(values)


def observe(record: Any) -> dict[str, Any]:
    errors: list[str] = []
    result: dict[str, Any] = {
        "passed": False,
        "errors": errors,
        "counts": {},
        "classes": {},
        "comparisonQualification": "NOT_QUALIFIED",
        "scope": ("read-only synthetic SUI Context observation; reference-only is "
                  "not selected, excluded reason is not per-candidate, "
                  "candidate absence and Owner decision are unproven"),
    }
    if not isinstance(record, dict) or record.get("synthetic") is not True:
        errors.append("only explicitly synthetic research input is accepted")
        return result

    query, bundle, direct = (record.get("query"), record.get("bundle"), record.get("directSnapshot"))
    if not isinstance(query, dict) or not isinstance(bundle, dict) or not isinstance(direct, dict):
        errors.append("query, bundle and directSnapshot must be objects")
        return result
    if query.get("safeModePolicy") != "strict" or query.get("reviewFilter") != "reviewedOnly":
        errors.append("pilot accepts only strict reviewedOnly query")
    if query.get("previewConfirmed") is not True:
        errors.append("preview was not confirmed")
    if bundle.get("schemaVersion") != "1.0.0":
        errors.append("not a ContextBundleResponse v1")
    if not isinstance(bundle.get("excludedReason"), list) or not all(
        isinstance(x, str) for x in bundle["excludedReason"]
    ):
        errors.append("excludedReason must be a string list")
    if not isinstance(bundle.get("truncationMeta"), dict):
        errors.append("truncationMeta must be an object")

    selected = _ids(bundle.get("selected"), "selected", errors)
    reviewed = bundle.get("selected", [])
    if isinstance(reviewed, list):
        for i, row in enumerate(reviewed):
            if isinstance(row, dict) and row.get("reviewed") is not True:
                errors.append(f"selected[{i}] violates strict reviewedOnly")
    flags = bundle.get("reviewFlags")
    if not isinstance(flags, dict) or type(flags.get("reviewed")) is not int or type(flags.get("unreviewed")) is not int:
        errors.append("reviewFlags must contain integer reviewed/unreviewed")
    elif flags["reviewed"] != len(selected) or flags["unreviewed"] != 0:
        errors.append("reviewFlags disagree with selected")
    refs: set[str] = set()
    evidence = bundle.get("evidence")
    if not isinstance(evidence, list):
        errors.append("evidence must be an array")
    else:
        for i, item in enumerate(evidence):
            if not isinstance(item, dict) or not isinstance(item.get("cardId"), str) or not item["cardId"]:
                errors.append(f"evidence[{i}] missing cardId")
            else:
                refs.add(item["cardId"])
    relations = bundle.get("relations")
    if not isinstance(relations, list):
        errors.append("relations must be an array")
    else:
        for i, item in enumerate(relations):
            if not isinstance(item, dict):
                errors.append(f"relations[{i}] not an object")
                continue
            for field in ("from", "to"):
                if not isinstance(item.get(field), str) or not item[field]:
                    errors.append(f"relations[{i}].{field} missing")
                else:
                    refs.add(item[field])

    if direct.get("scope") != "A2-minimal-v1-stub-only" or not isinstance(direct.get("sourceRevision"), str) or not direct["sourceRevision"]:
        errors.append("directSnapshot requires the fixed stub scope and sourceRevision")
    direct_ids = direct.get("candidateIds")
    if not isinstance(direct_ids, list) or any(
        not isinstance(x, str) or not x for x in direct_ids
    ) or len(direct_ids) != len(set(direct_ids)):
        errors.append("directSnapshot.candidateIds must be unique nonempty strings")
        direct_set: set[str] = set()
    else:
        direct_set = set(direct_ids)

    if errors:
        return result
    only_ref = refs - selected
    not_observed = direct_set - (selected | refs)
    extra_ref = (selected | refs) - direct_set
    result["passed"] = True
    result["counts"] = {
        "directObserved": len(direct_set),
        "selected": len(selected),
        "referencedOnly": len(only_ref),
        "notObservedInBundle": len(not_observed),
        "bundleOutsideDirectSnapshot": len(extra_ref),
    }
    result["classes"] = {
        "selected": sorted(selected),
        "referencedOnly": sorted(only_ref),
        "notObservedInBundle": sorted(not_observed),
        "bundleOutsideDirectSnapshot": sorted(extra_ref),
    }
    # SUI ContextBundleResponse does not carry a source snapshot identity
    # that ties it to directSnapshot, so matching scope is NOT established.
    result["comparisonQualification"] = "UNVERIFIED_SAME_SOURCE_REVISION"
    result["observedExclusionReasons"] = sorted(set(bundle["excludedReason"]))
    return result


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read(path: Path) -> dict[str, Any]:
    try:
        return observe(json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicate_keys))
    except (OSError, UnicodeError, ValueError) as exc:
        return {"passed": False, "errors": [f"invalid input: {exc}"], "counts": {},
                "comparisonQualification": "NOT_QUALIFIED"}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("input", nargs="?", default=str(Path(__file__).parent / "fixtures" / "sui-context-visibility.synthetic.json"))
    args = p.parse_args()
    observed = read(Path(args.input))
    # Never print per-candidate IDs by default; a real read-only response
    # may contain protected references even without card text.
    output = {k: v for k, v in observed.items() if k != "classes"}
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if observed["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
