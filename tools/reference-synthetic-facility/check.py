#!/usr/bin/env python3
"""Detect the intended evidence defects in the synthetic SCN-001 facility corpus.

This checks synthetic documents only. It never marks the review status as a
real-object review and never enables publication.
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any


CHECKS = (
    ("O-02", "entrance-notice.md", "施設全体の利用は予約不要", "総則の予約不要"),
    ("O-03", "meeting-room-guidance.md", "事前予約制", "会議室の予約制"),
    ("O-06", "distribution-2026-10.md", "事前予約制", "10月版の予約制"),
    ("O-07", "distribution-2026-11.md", "予約不要", "11月版の予約不要"),
    ("O-08", "original-policy-note.md", "原本を取得できなかった", "原本未取得"),
)


def check(root: pathlib.Path) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema": "tai.reference.synthetic-facility/v0",
        "synthetic": True,
        "evidenceKind": "synthetic",
        "publicationAllowed": False,
        "findings": [],
        "passed": False,
        "notes": [
            "製造工程の課題検出用に創作した文書だけを対象にする。",
            "実在の施設・規程・権限を確認した証拠ではない。",
        ],
    }
    texts: dict[str, str] = {}
    missing: list[str] = []
    for _, filename, _, _ in CHECKS:
        path = root / filename
        if not path.is_file():
            missing.append(filename)
            continue
        texts[filename] = path.read_text(encoding="utf-8")
    if missing:
        receipt["reason"] = "missing synthetic documents: " + ", ".join(missing)
        return receipt
    for observation, filename, marker, label in CHECKS:
        found = marker in texts[filename]
        receipt["findings"].append(
            {"observation": observation, "document": filename, "marker": label, "found": found}
        )
        if not found:
            receipt["reason"] = f"{observation} marker is missing: {label}"
            return receipt
    entrance = texts["entrance-notice.md"]
    if "別途" not in entrance or "会議室" not in entrance:
        receipt["reason"] = "entrance notice does not preserve the meeting-room exception"
        return receipt
    v11 = texts["distribution-2026-11.md"]
    if "会議室" in v11 or "事前予約" in v11:
        receipt["reason"] = "November distribution still contains the meeting-room reservation"
        return receipt
    receipt["detectedDefects"] = [
        "総則の予約不要と会議室の予約制が併存する",
        "10月版と11月版で会議室の条件が変わる",
        "11月版から会議室の記載が消える",
        "予約規程の原本を取得できていない",
    ]
    receipt["passed"] = True
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="scenarios/SCN-001-synthetic-facility")
    parser.add_argument("--out")
    args = parser.parse_args()
    receipt = check(pathlib.Path(args.root))
    encoded = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        pathlib.Path(args.out).write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if receipt.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
