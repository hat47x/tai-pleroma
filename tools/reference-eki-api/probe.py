#!/usr/bin/env python3
"""Read-only EKI Control API authentication probe.

GET /v1/tasks is not a supported method, so a valid Client credential returns
405 after authentication. A missing or invalid credential returns 401. The
probe never submits a Task and never changes EKI state.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from typing import Any

import ekipin


SCHEMA = "tai.reference.eki-api-probe/v0"


def _status(base_url: str, token: str, timeout: float) -> int:
    request = urllib.request.Request(
        base_url.rstrip("/") + "/v1/tasks",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code


def probe(base_url: str, token: str, timeout: float = 10.0, binding: ekipin.Binding | None = None) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "baseUrl": base_url,
        "readOnly": True,
        "authenticated": False,
        "taskDelegated": False,
        "authorityVerified": False,
        "passed": False,
        "notes": [
            "EKI Control APIのGET /v1/tasksに対する認証結果だけを確認する。",
            "Taskの送信・委任・Worker・結果検証・Authorityは未検証。",
        ],
    }
    guard = ekipin.Guard(binding)
    if not guard.before(receipt, base_url):
        return receipt
    return guard.after(_probe(receipt, base_url, token, timeout))


def _probe(receipt: dict[str, Any], base_url: str, token: str, timeout: float) -> dict[str, Any]:
    try:
        status = _status(base_url, token, timeout)
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        receipt["reason"] = str(error)
        return receipt
    receipt["tasksStatus"] = status
    if status == 401:
        receipt["reason"] = "credential was not accepted"
        return receipt
    if status != 405:
        receipt["reason"] = f"unexpected GET /v1/tasks status: {status}"
        return receipt
    receipt["authenticated"] = True
    receipt["passed"] = True
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:18080")
    parser.add_argument("--token", default=os.environ.get("EKI_TOKEN", ""))
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--out")
    ekipin.add_arguments(parser)
    args = parser.parse_args()
    if not args.token:
        parser.error("--token or EKI_TOKEN is required")
    receipt = probe(args.base_url, args.token, args.timeout, ekipin.Binding.from_args(args))
    encoded = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    print(encoded, end="")
    return 0 if receipt.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
