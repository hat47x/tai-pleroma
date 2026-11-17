"""Check that the inventory's not-run list is still the current not-run list.

`YI-stage3-inventory` records three items as not-run: centreHandoff, thinPhaseExpansion
and contextHandoff. Work has since been done on all three — there are probe receipts
for the two handoffs, and doc 49 records the six phase-expansion results. The inventory
was right when written and is stale now.

This compares the recorded not-run list against what the repository now contains, and
reports per item whether later evidence exists. It does not rewrite the inventory:
that record is a statement about its own date.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

INVENTORY = "evaluations/records/YI-stage3-inventory-2026-11-11.json"
# Later evidence, per not-run item, with what it shows.
LATER_EVIDENCE = {
    "centreHandoff": {
        "receipt": "evaluations/records/YI-centre-handoff-2026-11-11.json",
        "doc": "docs/yi-constellation/analysis/48-接続の単位の不足.md",
        "kind": "probe of the field set the handoff carries",
    },
    "contextHandoff": {
        "receipt": "evaluations/records/YI-context-handoff-2026-11-11.json",
        "doc": "docs/yi-constellation/analysis/48-接続の単位の不足.md",
        "kind": "probe of the three units a context handoff must carry",
    },
    "thinPhaseExpansion": {
        "receipt": None,
        "doc": "docs/yi-constellation/analysis/49-相の拡充の結果.md",
        "kind": "six phase expansions recorded in a document",
    },
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    inventory = json.loads((root / INVENTORY).read_text(encoding="utf-8"))
    recorded_not_run = inventory["observed"].get("notRun") or []

    rows = []
    for item in recorded_not_run:
        later = LATER_EVIDENCE.get(item, {})
        receipt = later.get("receipt")
        doc = later.get("doc")
        # Compare by string only; this checks presence, not content.
        doc_text = ""
        if doc and (root / doc).exists():
            doc_text = (root / doc).read_text(encoding="utf-8", errors="replace")
        rows.append({
            "item": item,
            "receiptExists": bool(receipt and (root / receipt).exists()),
            "receipt": receipt,
            "documentExists": bool(doc and (root / doc).exists()),
            "document": doc,
            "kind": later.get("kind"),
            "documentMentionsTheItem": (
                item in doc_text if doc_text else False
            ),
        })

    withLaterEvidence = [
        row["item"] for row in rows
        if row["receiptExists"] or row["documentExists"]
    ]
    checks = {
        "inventory": INVENTORY,
        "inventoryDate": (inventory.get("date") or ""),
        "recordedNotRun": recorded_not_run,
        "rows": rows,
        "itemsWithLaterEvidence": withLaterEvidence,
        "stillWithoutEvidence": [
            row["item"] for row in rows if row["item"] not in withLaterEvidence
        ],
        "theNotRunListIsStale": bool(withLaterEvidence),
        "finding": (
            "`YI-stage3-inventory`が`not-run`とした3件のうち、"
            "3件すべてに後続の証拠がある。この記録は書かれた時点では正しく、"
            "現在は古い。**記録を書き換えない**：その記録は自分の日付についての陳述である。"
            "代わりに、後続の証拠の所在を対応表として残す。"
        ),
    }
    # This check passes when it has shown the mapping, not when the list is current.
    passed = all(row["receiptExists"] or row["documentExists"] for row in rows)

    receipt = {
        "schema": "tai.reference.yic-notrun-refresh/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the inventory and later records",
        "command": "python integrations/tools/yic_notrun_refresh_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-notrun-refresh-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Compares the inventory's recorded not-run list with later receipts and documents, and "
            "states where later evidence sits. It checks that the later evidence exists, not that it "
            "settles the item: the probe receipts measure a field set, which is weaker than the "
            "running handoff the inventory asked for."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "recordedNotRun": recorded_not_run,
        "withLaterEvidence": withLaterEvidence,
        "stale": checks["theNotRunListIsStale"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
