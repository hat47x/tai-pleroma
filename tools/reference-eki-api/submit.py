#!/usr/bin/env python3
"""Submit one synthetic EKI Task and read its public status.

This exercises Task admission only. No Worker is started, so the Task remains
queued; this is not a completed delegation or an authority decision.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from typing import Any


SCHEMA = "tai.reference.eki-task-submit/v0"


def _request(
    method: str, url: str, token: str, body: bytes | None = None, idempotency_key: str = ""
) -> tuple[int, dict[str, Any]]:
    headers = {"Authorization": f"Bearer {token}"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        return error.code, {"raw": raw}


def submit(base_url: str, token: str, fixture: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "baseUrl": base_url,
        "readOnly": False,
        "taskSubmitted": False,
        "idempotent": False,
        "taskExecuted": False,
        "workerResult": False,
        "authorityVerified": False,
        "passed": False,
        "notes": [
            "EKI Control APIへ合成Taskを1件だけ送信し、queued状態を読む。",
            "Workerは起動しておらず、Taskの実行・結果・委任の完了は未検証。",
        ],
    }
    status, accepted = _request(
        "POST",
        base_url.rstrip("/") + "/v1/tasks",
        token,
        json.dumps(fixture, ensure_ascii=False).encode("utf-8"),
        idempotency_key,
    )
    receipt["submitStatus"] = status
    if status != 202 or not accepted.get("task_id"):
        receipt["reason"] = f"task submission failed: {status} {accepted}"
        return receipt
    task_id = accepted["task_id"]
    receipt["taskSubmitted"] = True
    receipt["taskId"] = task_id
    receipt["submitResponseStatus"] = accepted.get("status")
    status, repeated = _request(
        "POST",
        base_url.rstrip("/") + "/v1/tasks",
        token,
        json.dumps(fixture, ensure_ascii=False).encode("utf-8"),
        idempotency_key,
    )
    receipt["repeatStatus"] = status
    if status != 202 or repeated.get("task_id") != task_id:
        receipt["reason"] = "idempotent retry produced a different task"
        return receipt
    receipt["idempotent"] = True
    status, task = _request("GET", base_url.rstrip("/") + "/v1/tasks/" + task_id, token)
    receipt["statusReadStatus"] = status
    if status != 200:
        receipt["reason"] = f"task status read failed: {status} {task}"
        return receipt
    receipt["taskStatus"] = task.get("status")
    if receipt["taskStatus"] != "queued":
        receipt["reason"] = "task did not remain queued without a Worker"
        return receipt
    receipt["passed"] = True
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:18081")
    parser.add_argument("--token", default=os.environ.get("EKI_TOKEN", ""))
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--idempotency-key", default="tai-scn001-0001")
    parser.add_argument("--out")
    args = parser.parse_args()
    if not args.token:
        parser.error("--token or EKI_TOKEN is required")
    with open(args.fixture, encoding="utf-8") as handle:
        fixture = json.load(handle)
    receipt = submit(args.base_url, args.token, fixture, args.idempotency_key)
    encoded = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    print(encoded, end="")
    return 0 if receipt.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
