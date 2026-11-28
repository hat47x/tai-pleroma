"""Derive the expected fields from the checker's own rule body, not from a guess.

The first version carried a hand-written mapping from message phrase to field name, and the
names were wrong: the assembler rule tests `assemblerPassed`/`assemblerTests`/`cardCases`/
`cardQualified`, not `passed`/`cardRecordBound`. It read the sibling, found no such field, and
reported the classification as unsupported — when the sibling in fact satisfies the rule.

Reading the rule's own body removes the guess: parse `observed.get("X") != Y` out of the
rule and check those exact fields in the sibling.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

CHECKER = "tools/check-synthetic-receipts/check.py"
CLASSIFY = "evaluations/records/YIC-baseline-classify-2026-11-28.json"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rule_bodies(root):
    """Per selector, the comparison expressions in its block."""
    text = (root / CHECKER).read_text(encoding="utf-8")
    lines = text.splitlines()
    bodies = {}
    for index, line in enumerate(lines):
        match = re.match(r'\s*if "(\S+)" in relative_lower:', line)
        if not match:
            continue
        selector = match.group(1)
        block = []
        for follow in lines[index + 1:index + 12]:
            if re.match(r'\s*if "\S+" in relative_lower:', follow):
                break
            block.append(follow)
        bodies.setdefault(selector, []).extend(block)
    return bodies


def expectations(block):
    """(field, expected literal) pairs from a rule block."""
    pairs = []
    joined = " ".join(line.strip() for line in block)
    for match in re.finditer(
        r'observed\.get\("(\w+)"\)\s*(?:!=|==)\s*(?:"([^"]*)"|(\d+|True|False))', joined
    ):
        field = match.group(1)
        literal = match.group(2) if match.group(2) is not None else match.group(3)
        if literal in ("True", "False"):
            value = literal == "True"
        elif literal.isdigit():
            value = int(literal)
        else:
            value = literal
        pairs.append((field, value))
    return pairs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    data = json.loads((root / CLASSIFY).read_text(encoding="utf-8"))
    historical = (data.get("observed") or {}).get("historicalSample") or []
    bodies = rule_bodies(root)

    rows = []
    for entry in historical:
        selector = entry.get("selector")
        wanted = expectations(bodies.get(selector, []))
        checks = []
        for name in entry.get("siblings") or []:
            path = root / "evaluations/records" / name
            if not path.exists():
                continue
            receipt = json.loads(path.read_text(encoding="utf-8-sig"))
            observed = receipt.get("observed")
            if not isinstance(observed, dict):
                observed = receipt
            satisfied = [
                field for field, value in wanted
                if observed.get(field) == value
            ]
            checks.append({
                "receipt": name,
                "fieldsRequired": len(wanted),
                "fieldsSatisfied": len(satisfied),
                "satisfiesAll": len(wanted) > 0 and len(satisfied) == len(wanted),
            })
        rows.append({"selector": selector, "checks": checks})

    allSiblings = [check for row in rows for check in row["checks"]]
    unsupporting = [check for check in allSiblings if not check["satisfiesAll"]]
    checks = {
        "classificationReceipt": CLASSIFY,
        "historicalEntriesSampled": len(historical),
        "selectorsResolved": len([row for row in rows if row["checks"]]),
        "siblingsChecked": len(allSiblings),
        "siblingsThatSatisfyTheRule": len(allSiblings) - len(unsupporting),
        "siblingsThatDoNot": unsupporting,
        "finding": (
            f"「規則が他所で成立している」と分類した{len(historical)}件について、"
            "**checkerの規則本文から期待値を読み出し**、兄弟receiptが実際にそれを満たすかを確かめた。"
            f"検査した兄弟{len(allSiblings)}件のうち**{len(allSiblings) - len(unsupporting)}件が規則を満たす**。"
            "**最初の版は手書きの欄名表を使い、欄名を間違えて『満たさない』と誤判定した。**"
            "**規則本文から読めば、推測は要らない。**"
        ),
    }
    passed = bool(allSiblings) and not unsupporting

    receipt = {
        "schema": "tai.reference.yic-baseline-classification-effect/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 deriving the rule's expectations from its own body",
        "command": "python integrations/tools/yic_baseline_classify_effect.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-baseline-classify-effect-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Parses the comparison expressions out of each rule block and checks whether the "
            "sibling receipts hold those exact values. It validates the classification's evidence "
            "for the sampled entries; it does not check every baseline entry."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "siblings": len(allSiblings),
        "satisfying": len(allSiblings) - len(unsupporting),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
