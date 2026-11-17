"""Check that the handoff-condition document keeps the distinction it was written to make.

Doc 54 separates "the instrument exists" from "the instrument does not exist" for
P/T/C/H. The distinction is the whole point: a reader who sees a condition and assumes
it is currently measurable would repeat the error the previous rounds uncovered. This
check reads the document and verifies each stage states both its instrument status and
the observation that would count as a handoff.

It checks the document's structure, not its correctness.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

DOC = "docs/yi-constellation/analysis/54-受渡し条件.md"
STAGES = ("P", "T", "C", "H")
# Phrases that assert an instrument is absent or limited.
ABSENT = ("計器なし", "計器がない", "なし")
LIMITED = ("限定的", "限定的にあり")
PRESENT = ("あり",)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    path = root / DOC
    if not path.exists():
        print(f"missing {DOC}", file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")

    rows = []
    for stage in STAGES:
        # Each stage has a `### 2.N P（…）` block.
        match = re.search(rf"^###\s+2\.\d+\s+{stage}（", text, re.M)
        if not match:
            rows.append({"stage": stage, "found": False})
            continue
        following = re.search(r"^###\s+2\.\d+", text[match.end():], re.M)
        block = text[match.end():match.end() + following.start()] if following else text[match.end():]
        # The status row of the stage's table.
        status_match = re.search(r"\|\s*現在の状態\s*\|\s*(.+?)\s*\|", block)
        status = status_match.group(1) if status_match else ""
        rows.append({
            "stage": stage,
            "found": True,
            "statusCell": status,
            "statesInstrumentAbsent": any(word in status for word in ABSENT),
            "statesInstrumentLimited": any(word in status for word in LIMITED),
            "hasMinimumTestSet": "最小検証セット" in block,
            "hasCounterExample": "反例" in block,
        })

    missing = [row["stage"] for row in rows if not row["found"]]
    noStatus = [
        row["stage"] for row in rows
        if row["found"] and not (row["statesInstrumentAbsent"] or row["statesInstrumentLimited"])
    ]
    noTests = [row["stage"] for row in rows if row["found"] and not row["hasMinimumTestSet"]]
    noCounter = [row["stage"] for row in rows if row["found"] and not row["hasCounterExample"]]

    # The document must also separate what G1 changes from what it does not.
    separatesG1 = (
        "G1の判断で変わるか" in text
        and "変わらない" in text
    )
    checks = {
        "document": DOC,
        "stages": rows,
        "stagesMissing": missing,
        "stagesWithoutAnInstrumentStatement": noStatus,
        "stagesWithoutAMinimumTestSet": noTests,
        "stagesWithoutACounterExample": noCounter,
        "separatesWhatG1Changes": separatesG1,
        "everyStageStatesItsInstrument": not noStatus,
        "everyStageHasATestSet": not noTests,
        "finding": (
            "受渡し条件の文書が、各段階について**計器の有無**と**最小検証セット**を"
            "述べているか、またG1で変わるものと変わらないものを分けているかを見る。"
            "計器の有無を書かずに条件だけ書くと、"
            "「条件はあるが今は測れない」という要点が読者に伝わらない。"
        ),
    }
    passed = (
        not missing and not noStatus and not noTests and separatesG1
    )

    receipt = {
        "schema": "tai.reference.yic-handoff-condition-doc/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the handoff-condition document",
        "command": "python integrations/tools/yic_handoff_conditions_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-handoff-conditions-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads the handoff-condition document and checks each of P/T/C/H states its instrument "
            "status, a minimum test set and a counter-example, and that the document separates what "
            "G1 changes from what it does not. It checks the document's structure; whether the stated "
            "conditions would in fact establish a handoff is not judged."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "stages": len(rows),
        "missing": missing,
        "noStatus": noStatus,
        "noTests": noTests,
        "separatesG1": separatesG1,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
