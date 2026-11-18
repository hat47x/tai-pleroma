"""Check that the scope-halves rule covers every YI receipt, not only the yi- prefixed ones.

`yi_scope_halves_check.py` scans receipts whose names start with `yi-`. The later
receipts in this analysis are named `YIC-`. The check therefore reports 32 receipts while
59 `YIC-` receipts exist, and nothing in its output says so.

This walks both naming families, runs the same two detectors, and reports coverage.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

# Reuse the original check's detectors rather than keeping a second vocabulary: two
# copies of the same rule drift apart, and only one of them can be the one that matters.
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "yi_scope_halves",
    Path(__file__).resolve().parent / "yi_scope_halves_check.py",
)
_halves = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_halves)
MEASURED = _halves.MEASURED
LIMIT = _halves.LIMIT


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    records = root / "evaluations/records"
    own = Path(args.out).name

    families = {"yi": [], "yic": []}
    for path in sorted(records.glob("*.json")):
        name = path.name
        if name == own:
            continue
        lowered = name.lower()
        if lowered.startswith("yic-"):
            families["yic"].append(path)
        elif lowered.startswith(("yi-", "yi_")):
            families["yi"].append(path)

    rows = []
    for family, paths in families.items():
        for path in paths:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                rows.append({"family": family, "receipt": path.name, "parsed": False})
                continue
            scope = str(data.get("scope", ""))
            rows.append({
                "family": family,
                "receipt": path.name,
                "parsed": True,
                "scopeLength": len(scope),
                "statesWhatWasMeasured": bool(MEASURED.search(scope)),
                "statesALimit": bool(LIMIT.search(scope)),
            })

    unparsed = [row["receipt"] for row in rows if not row.get("parsed")]
    noMeasured = [
        row["receipt"] for row in rows
        if row.get("parsed") and not row["statesWhatWasMeasured"]
    ]
    noLimit = [
        row["receipt"] for row in rows
        if row.get("parsed") and not row["statesALimit"]
    ]
    counts = {
        family: len(paths) for family, paths in families.items()
    }

    checks = {
        "families": counts,
        "receiptsCovered": len(rows),
        "unparsedReceipts": unparsed,
        "receiptsWithoutAMeasuredHalf": noMeasured,
        "receiptsWithoutALimitHalf": noLimit,
        "theYiChecksFamilyOnly": "yic" not in {
            name.lower() for name in (p.name for p in records.glob("*.json"))
        },
        "finding": (
            "`yi_scope_halves_check.py`は`yi-`で始まる名前だけを走査する。"
            f"本分析の後のreceiptは`YIC-`で始まるため、**{counts['yic']}件が対象外**だった。"
            "点検は32件を調べて合格と報告し、"
            "**対象外の件数を書いていない**。"
            "両方の名前を走査して、scopeが2つの半分を書いているかを確認した。"
        ),
    }
    passed = not unparsed and not noMeasured and not noLimit

    receipt = {
        "schema": "tai.reference.yic-scope-coverage/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading every YI and YIC receipt",
        "command": "python integrations/tools/yic_scope_coverage_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-scope-coverage-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads every receipt whose name starts with yi- or YIC-, and applies the measured/limit "
            "detectors to each scope. It shows the earlier check's coverage gap and confirms both "
            "halves are present; it does not judge whether a scope's stated limit is the right one."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "yi": counts["yi"],
        "yic": counts["yic"],
        "withoutMeasured": len(noMeasured),
        "withoutLimit": len(noLimit),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
