#!/usr/bin/env python3
"""Submit one synthetic EKI Task and cancel it.

This exercises Task admission and cancellation, not execution. No Worker is
started, so the Task never produces a result.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from typing import Any


SCHEMA = "tai.reference.eki-task-cancel/v0"


def _request(
    method: str, url: str, token: str, body: bytes | None = None, key: str = ""
) -> tuple[int, dict[str, Any]]:
    headers = {"Authorization": f"Bearer {token}"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if key:
        headers["Idempotency-Key"] = key
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        return error.code, {"raw": raw}


def cancel(base_url: str, token: str, fixture: dict[str, Any], key: str) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "synthetic": True,
        "evidenceKind": "synthetic",
        "baseUrl": base_url,
        "readOnly": False,
        "taskSubmitted": False,
        "cancelled": False,
        "taskExecuted": False,
        "workerResult": False,
        "resultAvailable": False,
        "authorityVerified": False,
        "passed": False,
        "notes": [
            "EKI Control APIへ合成Taskを1件送信し、cancelを要求してcancelledを読む。",
            "Workerは起動しておらず、Taskの実行・結果は未検証。",
        ],
    }
    base = base_url.rstrip("/")
    status, accepted = _request(
        "POST",
        base + "/v1/tasks",
        token,
        json.dumps(fixture, ensure_ascii=False).encode("utf-8"),
        key,
    )
    receipt["submitStatus"] = status
    if status != 202 or not accepted.get("task_id"):
        receipt["reason"] = f"task submission failed: {status} {accepted}"
        return receipt
    task_id = accepted["task_id"]
    receipt["taskSubmitted"] = True
    receipt["taskId"] = task_id
    status, cancelled = _request(
        "POST",
        base + "/v1/tasks/" + task_id + "/cancel",
        token,
        b"",
        key + "-cancel",
    )
    receipt["cancelStatus"] = status
    if status != 202:
        receipt["reason"] = f"task cancellation failed: {status} {cancelled}"
        return receipt
    status, task = _request("GET", base + "/v1/tasks/" + task_id, token)
    receipt["statusReadStatus"] = status
    if status != 200:
        receipt["reason"] = f"task status read failed: {status} {task}"
        return receipt
    receipt["taskStatus"] = task.get("status")
    receipt["terminalCode"] = task.get("terminal_code")
    if receipt["taskStatus"] != "cancelled" or receipt["terminalCode"] != "CANCELLED":
        receipt["reason"] = "task did not reach cancelled/CANCELLED"
        return receipt
    receipt["cancelled"] = True
    status, result = _request("GET", base + "/v1/tasks/" + task_id + "/result", token)
    receipt["resultStatus"] = status
    if status == 200:
        receipt["reason"] = f"unexpected result was returned: {result}"
        return receipt
    if status != 501:
        receipt["reason"] = f"unexpected result endpoint status: {status}"
        return receipt
    receipt["resultAvailable"] = False
    receipt["passed"] = True
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:18082")
    parser.add_argument("--token", default=os.environ.get("EKI_TOKEN", ""))
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--idempotency-key", default="tai-scn001-cancel-0001")
    parser.add_argument("--out")
    args = parser.parse_args()
    if not args.token:
        parser.error("--token or EKI_TOKEN is required")
    with open(args.fixture, encoding="utf-8") as handle:
        fixture = json.load(handle)
    receipt = cancel(args.base_url, args.token, fixture, args.idempotency_key)
    encoded = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    print(encoded, end="")
    return 0 if receipt.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
