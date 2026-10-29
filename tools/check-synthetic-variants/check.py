#!/usr/bin/env python3
"""Check that synthetic SCN-001 variants run through MMI and TEI."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

VARIANTS = {
    "variant-b": {
        "mmi": "evaluations/records/SCN-001-variant-b-mmi-2026-10-29.json",
        "tei": "evaluations/records/SCN-001-variant-b-tei-2026-10-29.json",
        "ids": ["O-02", "O-03", "O-10", "O-11", "O-14"],
    },
    "variant-c": {
        "mmi": "evaluations/records/SCN-001-variant-c-mmi-2026-10-29.json",
        "tei": "evaluations/records/SCN-001-variant-c-tei-2026-10-29.json",
        "ids": ["O-02", "O-03", "O-20", "O-21", "O-23"],
    },
}


def load(root: pathlib.Path, relative: str) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def check(root: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    results: dict[str, Any] = {}
    for name, expected in VARIANTS.items():
        try:
            mmi = load(root, expected["mmi"])
            tei = load(root, expected["tei"])
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{name}: {error}")
            continue
        if mmi.get("synthetic") is not True or mmi.get("selectedRows") != 5 or mmi.get("passed") is not True:
            errors.append(f"{name}: MMI did not return a passed 5-row synthetic result")
        if mmi.get("observedIds") != expected["ids"]:
            errors.append(f"{name}: MMI observed IDs differ: {mmi.get('observedIds')}")
        if tei.get("synthetic") is not True or tei.get("validation") != "ok" or tei.get("passed") is not True:
            errors.append(f"{name}: TEI validation did not pass")
        results[name] = {"mmi": mmi.get("passed"), "tei": tei.get("passed")}

    return {
        "schema": "tai.reference.scn001-variant-matrix/v0",
        "synthetic": True,
        "evidenceKind": "synthetic",
        "variants": list(VARIANTS),
        "results": results,
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
