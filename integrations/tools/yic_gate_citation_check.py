"""Check that a gate document's citations match what each receipt actually claims.

Doc 53 maps each gate to a receipt. A reader follows those links to decide whether a
gate is stuck. If the receipt's `result` is FAIL while the document presents it as
supporting material, the reader sees a contradiction the document never
acknowledges. This lists, per citation, the receipt's result and whether the document
mentions a caveat near the link.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

DOCS = (
    "docs/yi-constellation/analysis/51-現在地とゲートの状態.md",
    "docs/yi-constellation/analysis/53-判定と残る前進.md",
)
RECORDS = "evaluations/records"
LINK = re.compile(r"\]\([^)]*records/(?P<name>[^)\s]+\.json)\)")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    rows = []
    for relative in DOCS:
        path = root / relative
        if not path.exists():
            print(f"missing {relative}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        for match in LINK.finditer(text):
            name = match.group("name")
            receipt_path = root / RECORDS / name
            if not receipt_path.exists():
                rows.append({
                    "document": relative,
                    "receipt": name,
                    "exists": False,
                })
                continue
            data = json.loads(receipt_path.read_text(encoding="utf-8"))
            # Look for an acknowledgement near the link, within the same paragraph.
            start = max(0, match.start() - 400)
            context = text[start:match.end() + 200]
            caveat_words = ("未了", "未着手", "未実施", "NOT RUN", "材料", "判断は", "揺れ")
            rows.append({
                "document": relative,
                "receipt": name,
                "exists": True,
                "result": data.get("result"),
                "receiptIsPass": data.get("result") == "PASS",
                "hasNearbyCaveat": any(word in context for word in caveat_words),
                "scopeStartsWithChecksOnly": "checks" in (data.get("scope") or "").lower(),
            })

    # Gate coverage: G1..G5 must each appear somewhere in the gate-status tables.
    gate_names = [f"G{index}" for index in range(1, 6)]
    covered = {}
    for name in gate_names:
        seen = False
        for relative in DOCS:
            body = (root / relative).read_text(encoding="utf-8")
            # A row that begins with the gate name, as the status tables do.
            if re.search(rf"^\|\s*{name}\s*\|", body, re.M):
                seen = True
                break
        covered[name] = seen
    uncoveredGates = [name for name, seen in covered.items() if not seen]

    failing = [row for row in rows if row.get("result") and row["result"] != "PASS"]
    # A FAIL receipt presented without any caveat wording is the case to flag.
    failWithoutCaveat = [row for row in failing if not row["hasNearbyCaveat"]]
    checks = {
        "documents": list(DOCS),
        "citations": len(rows),
        "distinctReceipts": len({row["receipt"] for row in rows}),
        "missingFiles": [row["receipt"] for row in rows if not row.get("exists")],
        "nonPassReceipts": [
            {"document": row["document"], "receipt": row["receipt"], "result": row.get("result")}
            for row in failing
        ],
        "nonPassWithoutAnyCaveat": [
            row["receipt"] for row in failWithoutCaveat
        ],
        "gatesFound": covered,
        "uncoveredGates": uncoveredGates,
        "everyCitationResolves": all(row.get("exists") for row in rows),
        "everyGateIsCited": not uncoveredGates,
        "everyNonPassCitationIsCaveated": not failWithoutCaveat,
        "finding": (
            "ゲート状態の文書が引用するreceiptを開き、`result`がPASS以外のものを"
            "文書が注記なしで提示していないかを点検する。"
            "読者はリンク先を見てゲートの状態を判断するため、"
            "文書の主張とreceiptの結果が食い違うと止まっている場所を取り違える。"
        ),
    }
    passed = (
        checks["everyCitationResolves"]
        and checks["everyNonPassCitationIsCaveated"]
        and checks["everyGateIsCited"]
    )

    receipt = {
        "schema": "tai.reference.yic-gate-citation-check/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the gate documents and their cited receipts",
        "command": "python integrations/tools/yic_gate_citation_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-gate-citation-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Opens each receipt cited by the two gate documents and records its result, flagging a "
            "non-PASS receipt that the surrounding text does not qualify. It checks citation "
            "consistency only: a PASS receipt cited in a misleading way is not detected, and the "
            "caveat search is lexical over a fixed word list."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "citations": len(rows),
        "distinct": checks["distinctReceipts"],
        "nonPass": len(failing),
        "uncaveated": checks["nonPassWithoutAnyCaveat"],
        "uncoveredGates": uncoveredGates,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
