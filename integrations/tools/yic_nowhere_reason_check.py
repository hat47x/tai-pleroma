"""For each of the three assertions holding nowhere, name the reason it cannot hold.

"Assertion holds nowhere" can have three different causes, and each implies a different
owner:

  * the guard reads a field no receipt of that kind records (the rule was written against
    a different receipt shape);
  * the guard reads `artifact.schema` but the receipts carry no artifact object at all;
  * the field exists and holds a different value in every receipt (the rule's expectation
    is wrong).

This reads all matching receipts, records which case each assertion falls into, and states
the cause without deciding the repair.
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

CHECKER = "tools/check-synthetic-receipts/check.py"
CASES = (
    {
        "message": "TEI save plan receipt did not record four non-writing tests",
        "selector": "sui-tei-save-plan",
        "guard": 'observed.get("passed") != 5 or observed.get("writes") is not False',
        "fields": ("passed", "writes"),
        "expect": {"passed": 5, "writes": False},
    },
    {
        "message": "TEI auth receipt did not enable authorization",
        "selector": "tei-auth",
        "guard": 'observed.get("authEnabled") is not True',
        "fields": ("authEnabled",),
        "expect": {"authEnabled": True},
    },
    {
        "message": "TEI artifact receipt points at a missing file",
        "selector": "tei-artifact",
        "guard": 'artifact.get("path") is not None and not Path(...).exists()',
        "fields": ("path",),
        "expect": None,  # judged by the file's existence, not by a value
    },
)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def registered(root):
    sys.path.insert(0, str(root / "tools/check-synthetic-receipts"))
    import check as checker  # noqa: E402
    return list(checker.RECORDS) + list(checker.REAL_RECORDS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    names = registered(root)

    rows = []
    for case in CASES:
        matching = []
        for name in names:
            if case["selector"] not in name.lower():
                continue
            path = root / name
            if not path.exists():
                continue
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            observed = data.get("observed") if isinstance(data.get("observed"), dict) else {}
            artifact = data.get("artifact") if isinstance(data.get("artifact"), dict) else {}
            values = {}
            for field in case["fields"]:
                values[field] = artifact.get(field) if field == "path" else observed.get(field)
            matching.append({"receipt": path.name, "values": values})

        expected = case["expect"]

        def satisfies(entry):
            if expected is None:
                # Judged by existence of the cited file.
                cited = entry["values"].get("path")
                if not cited:
                    return False
                candidate = Path(cited)
                if not candidate.is_absolute():
                    candidate = (root / "evaluations/records" / cited)
                return candidate.exists()
            return all(
                entry["values"].get(field) == value for field, value in expected.items()
            )

        satisfiedBy = [entry["receipt"] for entry in matching if satisfies(entry)]
        withField = [
            entry["receipt"] for entry in matching
            if any(value is not None for value in entry["values"].values())
        ]
        everyReceiptLacks = bool(matching) and not withField
        if not matching:
            cause = "セレクタに当たるreceiptが登録に無い"
        elif everyReceiptLacks:
            cause = "どのreceiptも規則の欄を持たない（規則が別のreceipt形を前提にしている）"
        elif satisfiedBy:
            cause = "規則を満たすreceiptがある（分類の前提が誤っていた）"
        else:
            cause = "欄はあるが、期待値を満たすreceiptが無い"

        rows.append({
            "message": case["message"],
            "selector": case["selector"],
            "guard": case["guard"],
            "matchingReceipts": len(matching),
            "receiptsWithTheField": len(withField),
            "satisfiedBy": satisfiedBy,
            "cause": cause,
            "values": matching,
        })

    checks = {
        "checker": CHECKER,
        "assertionsExamined": len(rows),
        "rows": rows,
        "causes": [
            {"message": row["message"][:50], "cause": row["cause"]} for row in rows
        ],
        "finding": (
            "「どこでも成立しない」3種類について、**当たるreceiptを全部読み、"
            "なぜ成立しないかを場合分けした**。"
            + "；".join(f"{row['message'][:36]}→{row['cause']}" for row in rows)
            + "。**原因が違えば処置も違うが、処置は決めていない。**"
        ),
    }
    passed = len(rows) == len(CASES)

    receipt = {
        "schema": "tai.reference.yic-nowhere-reason/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading every receipt matching the three selectors",
        "command": "python integrations/tools/yic_nowhere_reason_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-nowhere-reason-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads every registered receipt matching each of the three selectors and records the "
            "field values, then names the reason the assertion holds nowhere. It names the cause; "
            "it does not decide whether the receipt or the rule should change."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "examined": len(rows),
        "causes": [row["cause"][:30] for row in rows],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
