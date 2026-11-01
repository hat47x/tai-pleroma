#!/usr/bin/env python3
"""Check the TEI product capability chain used by TAI."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

RECORD = "evaluations/records/TEI-product-capabilities-2026-10-31.json"


def check(root: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        data = json.loads((root / RECORD).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {"passed": False, "errors": [str(error)], "publicationAllowed": False}
    capabilities = data.get("capabilities", {})
    required = {
        "product_contracts.eki_task_submit",
        "product_contracts.eki_attempt_execute",
        "product_contracts.eki_result_accept",
        "product_contracts.sui_document_put",
        "product_contracts.sei_decision_record",
        "product_contracts.mmi_observation_select",
    }
    if set(capabilities) != required:
        errors.append(f"capability set differs: {sorted(capabilities)}")
    chain = [
        ("product_contracts.eki_task_submit", "product_contracts.eki_attempt_execute"),
        ("product_contracts.eki_attempt_execute", "product_contracts.eki_result_accept"),
    ]
    for producer, consumer in chain:
        produced = capabilities.get(producer, {}).get("output")
        consumed = capabilities.get(consumer, {}).get("inputs", [{}])[0].get("type")
        if produced != consumed:
            errors.append(f"{producer} output {produced!r} does not feed {consumer} input {consumed!r}")
    for name in (
        "product_contracts.sui_document_put",
        "product_contracts.sei_decision_record",
        "product_contracts.mmi_observation_select",
    ):
        cap = capabilities.get(name, {})
        if cap.get("inputs", [{}])[0].get("type") != cap.get("output"):
            errors.append(f"{name} is not an identity capability")
    patterns = data.get("patterns", {})
    if set(patterns) != required:
        errors.append(f"pattern set differs: {sorted(patterns)}")
    for capability, pattern in patterns.items():
        expected = "product_contracts_flow." + capability.removeprefix("product_contracts.")
        if pattern != expected:
            errors.append(f"{capability} is not wired to {expected}: {pattern}")
    bindings = data.get("bindings", {})
    if set(bindings) != required:
        errors.append(f"binding set differs: {sorted(bindings)}")
    expected_bindings = {
        "product_contracts.eki_task_submit": "EKITaskSubmit",
        "product_contracts.eki_attempt_execute": "EKIAttemptExecute",
        "product_contracts.eki_result_accept": "EKIResultAccept",
        "product_contracts.sui_document_put": "SUIDocumentPut",
        "product_contracts.sei_decision_record": "SEIDecisionRecord",
        "product_contracts.mmi_observation_select": "MMIObservationSelect",
    }
    for capability, name in bindings.items():
        if expected_bindings.get(capability) != name:
            errors.append(f"{capability} binding differs: {name}")
    expected_flow = [
        "product_contracts.eki_task_submit",
        "product_contracts.eki_attempt_execute",
        "product_contracts.eki_result_accept",
    ]
    flow = data.get("flowOrder", [])
    if flow != expected_flow:
        errors.append(f"flow order differs: {flow}")
    for capability in flow:
        if capability not in patterns or capability not in bindings:
            errors.append(f"flow step has no pattern or binding: {capability}")
    if not data.get("worldFingerprint") or not data.get("sourceIndexFingerprint"):
        errors.append("TEI fingerprints are missing")
    if data.get("synthetic") is not True:
        errors.append("record is not marked synthetic")
    return {
        "schema": "tai.reference.tei-capability-chain/v0",
        "synthetic": True,
        "evidenceKind": "synthetic",
        "teiCommit": data.get("teiCommit"),
        "chain": ["eki_task_submit", "eki_attempt_execute", "eki_result_accept"],
        "flowOrder": flow,
        "publicationAllowed": False,
        "passed": not errors,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    receipt = check(pathlib.Path(args.root))
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
