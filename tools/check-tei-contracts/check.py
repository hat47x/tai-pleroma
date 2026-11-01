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
    implementations = data.get("bindingImplementations", {})
    if set(implementations) != required:
        errors.append(f"binding implementation set differs: {sorted(implementations)}")
    for capability, names in implementations.items():
        if not names:
            errors.append(f"{capability} has no binding implementation")
    submit_implementations = implementations.get("product_contracts.eki_task_submit", [])
    if "EKITaskSubmitHTTP" not in submit_implementations:
        errors.append("eki_task_submit has no HTTP binding implementation")
    http_binding = data.get("httpBinding", {})
    expected_http_binding = {
        "method": "POST",
        "path": "/v1/tasks",
        "idempotencyHeader": "Idempotency-Key",
        "successStatus": 202,
        "errorFormat": "application/problem+json",
    }
    for key, value in expected_http_binding.items():
        if http_binding.get(key) != value:
            errors.append(f"http binding {key} differs: {http_binding.get(key)}")
    live_call = data.get("liveCall", {})
    live = http_binding.get("liveCallExecuted")
    if live is True:
        if live_call.get("result") != "PASS":
            errors.append("live call is claimed without a PASS result")
        if not live_call.get("ekiControlCommit"):
            errors.append("live call is claimed without an eki-control commit")
        if live_call.get("taskIdPrefix") != "tsk_":
            errors.append("live call is claimed without a task id prefix")
        if live_call.get("resultStatus") != 202:
            errors.append("live call is claimed without status 202")
    elif live is not False:
        errors.append("httpBinding.liveCallExecuted must be true or false")
    expected_flow = [
        "product_contracts.eki_task_submit",
        "product_contracts.eki_attempt_execute",
        "product_contracts.eki_result_accept",
    ]
    flow = data.get("flowOrder", [])
    if flow != expected_flow:
        errors.append(f"flow order differs: {flow}")
    order_evidence = data.get("orderEvidence", {})
    if order_evidence.get("mechanism") != "composition.ActivationOrder":
        errors.append(f"order evidence mechanism differs: {order_evidence.get('mechanism')}")
    if order_evidence.get("result") != "PASS":
        errors.append("order evidence is not PASS")
    if order_evidence.get("order") != [c.split(".")[-1] for c in expected_flow]:
        errors.append(f"order evidence differs: {order_evidence.get('order')}")
    for capability in flow:
        if capability not in patterns or capability not in bindings:
            errors.append(f"flow step has no pattern or binding: {capability}")
    expected_effects = {
        "product_contracts.eki_task_submit": "create product_contracts.attempt",
        "product_contracts.eki_attempt_execute": "create product_contracts.result_claim",
        "product_contracts.eki_result_accept": "create product_contracts.accepted_result",
        "product_contracts.sui_document_put": "update product_contracts.document",
        "product_contracts.sei_decision_record": "create product_contracts.decision",
        "product_contracts.mmi_observation_select": "none",
    }
    effects = data.get("effects", {})
    if set(effects) != required:
        errors.append(f"effect set differs: {sorted(effects)}")
    for capability, effect in effects.items():
        if expected_effects.get(capability) != effect:
            errors.append(f"{capability} effect differs: {effect}")
        if effect != "none" and not effect.startswith(("create ", "update ")):
            errors.append(f"{capability} effect is not create/update/none: {effect}")
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
        "orderEvidence": order_evidence,
        "effects": effects,
        "bindingImplementations": implementations,
        "httpBinding": http_binding,
        "liveCall": live_call,
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
