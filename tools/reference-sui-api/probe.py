#!/usr/bin/env python3
"""Read-only reachability probe for the SUI API.

This does not read or write SUI documents. It only checks /healthz and the
public OpenAPI document, which are sufficient to prove that the API process is
reachable without claiming SCN-001 data integration.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


SCHEMA = "tai.reference.sui-api-probe/v0"


def _get_json(base_url: str, path: str, timeout: float) -> Any:
    with urllib.request.urlopen(base_url.rstrip("/") + path, timeout=timeout) as response:
        if response.status != 200:
            raise ValueError(f"{path} returned HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


def _document_digest(document: dict[str, Any]) -> str:
    canonical = json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def probe(base_url: str, timeout: float = 10.0, doc_id: str | None = None) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "baseUrl": base_url,
        "readOnly": True,
        "realProductConnected": False,
        "passed": False,
        "notes": [
            "SUI APIの到達性と公開OpenAPIだけを確認する。",
            "SUI Documentの内容・テナント・認可・SCN-001データは検証しない。",
        ],
    }
    try:
        health = _get_json(base_url, "/healthz", timeout)
        if health.get("status") != "ok":
            receipt["reason"] = "healthz did not report ok"
            return receipt
        openapi = _get_json(base_url, "/openapi.json", timeout)
        documents = _get_json(base_url, "/docs", timeout)
    except (urllib.error.URLError, ValueError, json.JSONDecodeError) as error:
        receipt["reason"] = str(error)
        return receipt
    receipt["health"] = health
    if not isinstance(documents, list):
        receipt["reason"] = "docs did not return a list"
        return receipt
    receipt["documentCount"] = len(documents)
    receipt["documentIds"] = [
        item.get("id") for item in documents if isinstance(item, dict) and item.get("id")
    ]
    if doc_id is not None:
        try:
            document = _get_json(
                base_url, "/docs/" + urllib.parse.quote(doc_id, safe=""), timeout
            )
        except (urllib.error.URLError, ValueError, json.JSONDecodeError) as error:
            receipt["reason"] = str(error)
            return receipt
        if document.get("version") != 1 or not isinstance(document.get("cards"), list):
            receipt["reason"] = "document is not DocumentV1"
            return receipt
        receipt["documentRead"] = True
        receipt["documentId"] = doc_id
        receipt["documentTitle"] = document.get("title")
        receipt["documentCardCount"] = len(document["cards"])
        receipt["documentDigest"] = _document_digest(document)
        receipt["documentCards"] = [
            {
                "id": card.get("id"),
                "claimType": card.get("claimType"),
                "textDigest": "sha256:"
                + hashlib.sha256(str(card.get("text", "")).encode("utf-8")).hexdigest(),
            }
            for card in document["cards"]
            if isinstance(card, dict)
        ]
        islands = document.get("islands", [])
        receipt["documentIslandCount"] = len(islands)
        receipt["documentIslands"] = [
            {"id": island.get("id"), "cardIds": island.get("cardIds", [])}
            for island in islands
            if isinstance(island, dict)
        ]
        receipt["documentEdgeCount"] = len(document.get("edges", []))
    paths = openapi.get("paths")
    if not isinstance(paths, dict) or not paths:
        receipt["reason"] = "openapi paths are missing"
        return receipt
    receipt["openapiVersion"] = openapi.get("openapi", "")
    receipt["pathCount"] = len(paths)
    receipt["paths"] = sorted(paths.keys())
    receipt["realProductConnected"] = True
    receipt["passed"] = True
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--doc-id")
    parser.add_argument("--out")
    args = parser.parse_args()
    try:
        receipt = probe(args.base_url, args.timeout, args.doc_id)
    except (urllib.error.URLError, ValueError, json.JSONDecodeError) as error:
        receipt = {
            "schema": SCHEMA,
            "baseUrl": args.base_url,
            "readOnly": True,
            "realProductConnected": False,
            "passed": False,
            "reason": str(error),
        }
    encoded = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    print(encoded, end="")
    return 0 if receipt.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
