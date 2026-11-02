#!/usr/bin/env python3
"""Read-only reachability probe for the SUI API.

This does not read or write SUI documents. It only checks /healthz and the
public OpenAPI document, which are sufficient to prove that the API process is
reachable without claiming SCN-001 data integration.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

import suipin


SCHEMA = "tai.reference.sui-api-probe/v0"


def _get_json(base_url: str, path: str, timeout: float, opener: Any = None) -> Any:
    opening = opener.open if opener is not None else urllib.request.urlopen
    with opening(base_url.rstrip("/") + path, timeout=timeout) as response:
        if response.status != 200:
            raise ValueError(f"{path} returned HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


def _document_digest(document: dict[str, Any]) -> str:
    canonical = json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def probe(
    base_url: str,
    timeout: float = 10.0,
    doc_id: str | None = None,
    binding: suipin.Binding | None = None,
) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "baseUrl": base_url,
        "readOnly": True,
        "realProductConnected": False,
        "synthetic": True,
        "evidenceKind": "synthetic",
        "passed": False,
        "notes": [
            "SUI APIの到達性と公開OpenAPIだけを確認する。",
            "SUI Documentの内容・テナント・認可・SCN-001データは検証しない。",
        ],
    }
    guard = suipin.Guard(binding)
    pinned = guard.binding.pinned
    if not guard.before(receipt, base_url, doc_id):
        return receipt
    # /version is read first and only recorded unless an expectation was given: a
    # failure here never fails a default run. A pinned run stops before /healthz.
    if not guard.read_identity(receipt, base_url, timeout):
        return receipt
    _read(receipt, guard, base_url, timeout, doc_id, pinned)
    guard.finish(receipt, base_url, timeout)
    return receipt


def _read(
    receipt: dict[str, Any], guard: suipin.Guard, base_url: str, timeout: float, doc_id: str | None, pinned: bool
) -> None:
    opener = guard.opener()
    errors: tuple[type[BaseException], ...] = (urllib.error.URLError, ValueError, json.JSONDecodeError)
    if pinned:
        errors = errors + (OSError, http.client.HTTPException)
    try:
        health = _get_json(base_url, "/healthz", timeout, opener)
        if health.get("status") != "ok":
            receipt["reason"] = "healthz did not report ok"
            return
        openapi = _get_json(base_url, "/openapi.json", timeout, opener)
        documents = _get_json(base_url, "/docs", timeout, opener)
    except errors as error:
        receipt["reason"] = suipin.error_text(error, pinned)
        return
    guard.note_openapi(receipt, openapi)
    receipt["health"] = health
    if not isinstance(documents, list):
        receipt["reason"] = "docs did not return a list"
        return
    receipt["documentCount"] = len(documents)
    receipt["documentIds"] = [
        item.get("id") for item in documents if isinstance(item, dict) and item.get("id")
    ]
    if doc_id is not None:
        try:
            document = _get_json(
                base_url, "/docs/" + urllib.parse.quote(doc_id, safe=""), timeout, opener
            )
        except errors as error:
            receipt["reason"] = suipin.error_text(error, pinned)
            return
        if document.get("version") != 1 or not isinstance(document.get("cards"), list):
            receipt["reason"] = "document is not DocumentV1"
            return
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
        edges = document.get("edges", [])
        receipt["documentEdgeCount"] = len(edges)
        receipt["documentEdges"] = [
            {
                "id": edge.get("id"),
                "fromId": edge.get("fromId"),
                "toId": edge.get("toId"),
                "type": edge.get("type"),
            }
            for edge in edges
            if isinstance(edge, dict)
        ]
    paths = openapi.get("paths")
    if not isinstance(paths, dict) or not paths:
        receipt["reason"] = "openapi paths are missing"
        return
    receipt["openapiVersion"] = openapi.get("openapi", "")
    receipt["pathCount"] = len(paths)
    receipt["paths"] = sorted(paths.keys())
    receipt["realProductConnected"] = True
    receipt["passed"] = True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--doc-id")
    parser.add_argument("--out")
    suipin.add_arguments(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    binding = suipin.Binding.from_args(args)
    if binding.expect_digest and not args.doc_id:
        parser.error("--expect-document-digest needs --doc-id")
    try:
        receipt = probe(args.base_url, args.timeout, args.doc_id, binding)
    except (urllib.error.URLError, ValueError, json.JSONDecodeError) as error:
        receipt = {
            "schema": SCHEMA,
            "baseUrl": args.base_url,
            "readOnly": True,
            "realProductConnected": False,
            "passed": False,
            "reason": suipin.error_text(error, binding.pinned),
        }
    encoded = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    print(encoded, end="")
    return 0 if receipt.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
