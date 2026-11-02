#!/usr/bin/env python3
"""PUT one synthetic DocumentV1 and read it back."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from typing import Any


def request(method: str, url: str, body: bytes | None = None) -> tuple[int, Any]:
    req = urllib.request.Request(url, data=body, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, {"raw": error.read().decode("utf-8", errors="replace")}


def put_document(base_url: str, fixture: dict[str, Any], expected: tuple[int, int, int] = (5, 3, 1)) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema": "tai.reference.sui-document-put/v0",
        "synthetic": True,
        "evidenceKind": "synthetic",
        "docId": fixture.get("id"),
        "passed": False,
    }
    base = base_url.rstrip("/")
    status, saved = request("PUT", f"{base}/docs/{fixture['id']}", json.dumps(fixture, ensure_ascii=False).encode("utf-8"))
    receipt["putStatus"] = status
    if status not in (200, 201):
        receipt["reason"] = f"PUT failed: {status} {saved}"
        return receipt
    status, document = request("GET", f"{base}/docs/{fixture['id']}")
    receipt["readStatus"] = status
    if status != 200:
        receipt["reason"] = f"GET failed: {status} {document}"
        return receipt
    receipt["cardCount"] = len(document.get("cards", []))
    receipt["islandCount"] = len(document.get("islands", []))
    receipt["edgeCount"] = len(document.get("edges", []))
    receipt["edgeType"] = document.get("edges", [{}])[0].get("type") if document.get("edges") else None
    receipt["expected"] = {"cards": expected[0], "islands": expected[1], "edges": expected[2]}
    receipt["passed"] = (
        receipt["cardCount"] == expected[0]
        and receipt["islandCount"] == expected[1]
        and receipt["edgeCount"] == expected[2]
    )
    if not receipt["passed"]:
        receipt["reason"] = f"DocumentV1 shape is not {expected[0]} cards / {expected[1]} islands / {expected[2]} edges"
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--cards", type=int, default=5)
    parser.add_argument("--islands", type=int, default=3)
    parser.add_argument("--edges", type=int, default=1)
    parser.add_argument("--out")
    args = parser.parse_args()
    fixture = json.loads(open(args.fixture, encoding="utf-8").read())
    receipt = put_document(args.base_url, fixture, (args.cards, args.islands, args.edges))
    encoded = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        open(args.out, "w", encoding="utf-8", newline="\n").write(encoded)
    print(encoded, end="")
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
