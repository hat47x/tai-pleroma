"""Check that receipts which report the same fact report the same number.

Several YI receipts measure overlapping facts: how many candidates there are,
how many are kept, how many cross-cutting decisions G1 has. If one receipt was
regenerated after a later change and another was not, a reader gets two answers
for one question. This compares the overlapping facts across receipts.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

RECORDS = Path("evaluations/records")

# Facts reported by more than one receipt, with how to read each one.
FACTS = {
    "candidateCount": (
        ("YI-doc-integrity-2026-11-11.json", ("candidatesInList",)),
        ("YI-doc-integrity-2026-11-11.json", ("candidatesInPacket",)),
    ),
    "crossCuttingDecisionCount": (
        ("YI-g1-status-2026-11-11.json", ("decisionFields",)),
        ("YI-g1-evidence-2026-11-11.json", ("decisionsChecked",)),
    ),
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(root, name, path):
    file = root / RECORDS / name
    if not file.exists():
        return None
    data = json.loads(file.read_text(encoding="utf-8"))
    value = data.get("observed", {})
    for step in path:
        if not isinstance(value, dict) or step not in value:
            return None
        value = value[step]
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]

    rows = []
    mismatches = []
    for fact, sources in FACTS.items():
        values = []
        for name, path in sources:
            values.append({"receipt": name, "path": path[0], "value": read(root, name, path)})
        distinct = {item["value"] for item in values if item["value"] is not None}
        agree = len(distinct) <= 1
        rows.append({"fact": fact, "values": values, "agrees": agree})
        if not agree:
            mismatches.append({"fact": fact, "values": values})

    # The kept + moved pair must equal the candidate total.
    kept = read(root, "YI-citation-check-2026-11-11.json", ("keptInPacket",))
    moved = read(root, "YI-citation-check-2026-11-11.json", ("movedInPacket",))
    total = read(root, "YI-doc-integrity-2026-11-11.json", ("candidatesInList",))
    partitionHolds = (
        kept is not None and moved is not None and total is not None
        and kept + moved == total
    )

    checks = {
        "facts": rows,
        "mismatches": mismatches,
        "kept": kept,
        "moved": moved,
        "total": total,
        "keptPlusMovedEqualsTotal": partitionHolds,
        "everyOverlappingFactAgrees": not mismatches,
    }
    passed = not mismatches and partitionHolds

    receipt = {
        "schema": "tai.reference.yi-cross-receipt/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading evaluations/records",
        "command": "python integrations/tools/yi_cross_receipt_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-cross-receipt-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Compares the facts that more than one YI receipt reports, and checks that kept plus moved equals the candidate total. It compares numbers only, so two receipts can agree on a number while disagreeing about what it counts; it does not detect a stale list whose length happens to match, such as decisionsWithNoObservation.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "mismatches": [item["fact"] for item in mismatches],
        "partition": partitionHolds,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
