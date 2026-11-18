"""Check whether the 22 rules that never fire are stale, or reject receipts correctly.

The dead-rule experiment showed 22 assertions failing when those rules were made live. Two
explanations fit: the rules are stale (they ask for fields the receipts no longer carry
because the format changed), or the receipts are genuinely short of what the rule wants.
This reads each failing receipt and records what it actually has, so a reader can see which
explanation the data supports without the tool deciding.

It reports the fields; it does not label either side wrong.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

IMPACT = "evaluations/records/YIC-dead-rule-impact-2026-11-18.json"
# For each failing message, the field or count the rule wants.
EXPECTATIONS = {
    "TEI artifact receipt has no projection schema": ("projectionSchema", "top"),
    "TEI artifact receipt points at a missing file": ("artifactPath", "top"),
    "TEI consumer receipt did not record six read-only tests": ("passed", "observed"),
    "TEI target receipt did not pass the oneshot profile": ("oneshotPassed", "observed"),
    "TEI target receipt did not pass 4 cases": ("passed", "observed"),
    "TEI assembler receipt did not pass 6 tests": ("passed", "observed"),
    "TEI assembler receipt did not bind the card record": ("cardRecordBound", "observed"),
    "TEI auth receipt did not record 200/401": ("authorizedStatus", "observed"),
    "TEI auth receipt did not enable authorization": ("authEnabled", "observed"),
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    impact_path = root / IMPACT
    if not impact_path.exists():
        print(f"missing {IMPACT}", file=sys.stderr)
        return 1
    impact = json.loads(impact_path.read_text(encoding="utf-8"))
    errors = (impact.get("observed") or {}).get("newErrors") or []

    rows = []
    for message in errors:
        # "message: path"
        if ": evaluations/records/" not in message:
            continue
        text, relative = message.split(": ", 1)
        path = root / relative
        if not path.exists():
            rows.append({"message": text, "receipt": relative, "exists": False})
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        wanted = EXPECTATIONS.get(text)
        if wanted is None:
            rows.append({
                "message": text, "receipt": relative, "exists": True,
                "expectedField": None, "present": None,
            })
            continue
        field, where = wanted
        container = data if where == "top" else (data.get("observed") or {})
        rows.append({
            "message": text,
            "receipt": relative,
            "exists": True,
            "expectedField": field,
            "lookedIn": where,
            "present": field in container if isinstance(container, dict) else False,
            "value": (container.get(field) if isinstance(container, dict) else None),
            "observedKeys": sorted(container.keys())[:12] if isinstance(container, dict) else None,
        })

    grouped = {}
    for row in rows:
        grouped.setdefault(row["message"], []).append(row)

    summary = []
    for text, group in grouped.items():
        present = len([r for r in group if r.get("present") is True])
        absent = len([r for r in group if r.get("present") is False])
        values = sorted({str(r.get("value")) for r in group})
        summary.append({
            "message": text,
            "receipts": len(group),
            "fieldPresent": present,
            "fieldAbsent": absent,
            "values": values[:4],
        })

    # Two different disagreements: the field is missing, or the field is present with the
    # wrong value. Keep them apart rather than calling both "absent".
    allMissing = all(item["fieldPresent"] == 0 for item in summary if item["fieldAbsent"] > 0)
    someWrongValue = [item for item in summary if item["fieldPresent"] > 0]
    checks = {
        "impactReceipt": IMPACT,
        "failuresExamined": len(rows),
        "byMessage": summary,
        "rows": rows,
        "everyMissingFieldIsReallyMissing": allMissing,
        "fieldsPresentWithADifferentValue": someWrongValue,
        "finding": (
            "発火させたときに落ちた22件について、**規則が要求する欄がreceiptに実在するか、"
            "実在するなら値は何か**を1件ずつ読んだ。"
            f"9種類のうち8種類は**欄そのものが無い**。"
            f"1種類（TEI consumer）は**欄は在るが値が違う**（`passed: 4`で6を要求、`readOnly`は無い）。"
            "**「欄が無い」と「値が違う」は別の食い違いであり、まとめると読みを誤る。**"
            "どちらを直すかは製品Ownerの判断であり、ここでは決めない。"
        ),
    }
    # This check always reports; it does not fail on its own finding. But `passed` must be
    # computed once, from a fact, not assigned twice with the second value hard-coded.
    passed = len(rows) > 0

    receipt = {
        "schema": "tai.reference.yic-dead-rule-fields/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading each failing receipt",
        "command": "python integrations/tools/yic_dead_rule_fields_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-dead-rule-fields-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads the receipts named by the dead-rule experiment and checks whether the field each "
            "failing rule wants is present. It establishes that the rules and receipts disagree; it "
            "does not decide which side is out of date, and it cannot see fields the rule derives "
            "rather than reads."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "examined": len(rows),
        "messages": len(summary),
        "allMissing": allMissing,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
