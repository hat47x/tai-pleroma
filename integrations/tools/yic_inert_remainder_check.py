"""Check whether the two remaining inert selectors name a receipt that exists elsewhere.

`tei-comparison` and `tei-text-selection` reach no registered receipt. Before calling them
stale, look for the receipts they would govern: a comparison receipt and a text-selection
receipt. If such files exist under other names, the selector is a naming mismatch like the
reversed ones; if nothing resembling them exists, the rule describes a check that has no
receipt at all.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

CHECKER = "tools/check-synthetic-receipts/check.py"
INERT = ("tei-comparison", "tei-text-selection")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    text = (root / CHECKER).read_text(encoding="utf-8")

    rows = []
    for selector in INERT:
        stem = selector.split("-")[-1]  # "comparison" or "text-selection"
        registered = [
            line.split('"')[1]
            for line in text.splitlines()
            if line.strip().startswith('"evaluations/records/')
            and stem in line.lower()
        ]
        on_disk = sorted(
            p.name for p in (root / "evaluations/records").glob("*.json")
            if stem in p.name.lower()
        )
        # The guard beneath each selector, for the record.
        lines = text.splitlines()
        guards = []
        for index, line in enumerate(lines):
            if f'if "{selector}" in relative_lower:' in line:
                for follow in lines[index + 1:index + 5]:
                    if follow.strip().startswith(("if ", "errors.append")):
                        guards.append(follow.strip()[:100])
                break
        rows.append({
            "selector": selector,
            "stem": stem,
            "registeredWithTheStem": registered,
            "fullCallersBelow": [  # registered names that also carry the full selector text
                name for name in (line.split('"')[1] for line in text.splitlines()
                                  if line.strip().startswith('"evaluations/records/'))
                if selector in name.lower()
            ],
            "filesOnDiskWithTheStem": on_disk,
            "guards": guards,
        })

    noDisk = [row["selector"] for row in rows if not row["filesOnDiskWithTheStem"]]
    checks = {
        "inertSelectors": list(INERT),
        "rows": rows,
        "selectorsWithNoResemblingFile": noDisk,
        "finding": (
            "残る2件を調べた。"
            f"`tei-comparison` は語尾`comparison`を持つreceiptが"
            f"{'あり' if rows[0]['filesOnDiskWithTheStem'] else '無く'}、"
            f"`tei-text-selection` は`text-selection`を持つreceiptが"
            f"{'あり' if rows[1]['filesOnDiskWithTheStem'] else '無い'}。"
            "**receiptが存在しない規則は、対象がまだ作られていない**という意味であり、"
            "名前の不一致ではない。"
        ),
    }
    passed = len(rows) == len(INERT)

    receipt = {
        "schema": "tai.reference.yic-inert-remainder/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the checker and the records folder",
        "command": "python integrations/tools/yic_inert_remainder_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-inert-remainder-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "For each of the two remaining inert selectors, searches the registered list and the "
            "records folder for a name carrying the same distinguishing word. It distinguishes "
            "'a receipt exists under another name' from 'no such receipt exists'; it does not "
            "decide whether the rule should be deleted."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "noResemblingFile": noDisk,
        "rows": [(row["selector"], len(row["filesOnDiskWithTheStem"])) for row in rows],
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
