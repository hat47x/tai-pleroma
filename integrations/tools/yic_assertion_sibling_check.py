"""Evaluate each assertion's guard as a predicate against sibling receipts.

Three attempts at this failed the same way: parsing the comparison operators out of the
condition by hand and then guessing which direction means success. The guard in the checker
is written as *the failure predicate* — `if observed.get("x") != 409 or ...: errors.append(...)`
— so a receipt satisfies the assertion exactly when the guard evaluates to False.

Rather than invert operators by hand, evaluate the guard itself against the receipt. The
condition text comes from the checker's own source, so evaluating it is reading the rule as
the rule means it.
"""

import argparse
import ast
import hashlib
import json
import re
import time
from pathlib import Path

LOCATE = "evaluations/records/YIC-assertion-locate-2026-11-28.json"
CHECKER = "tools/check-synthetic-receipts/check.py"
BASELINE_NAME = "KNOWN_RULE_FAILURE_BASELINE"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def baseline_by_message(root):
    """Which receipts are in the baseline for which message."""
    tree = ast.parse((root / CHECKER).read_text(encoding="utf-8"))
    mapping = {}
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and node.targets
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == BASELINE_NAME
        ):
            stack = [node.value]
            while stack:
                current = stack.pop()
                if isinstance(current, ast.BinOp) and isinstance(current.op, ast.Add):
                    stack.extend([current.left, current.right])
                elif isinstance(current, (ast.Tuple, ast.List)):
                    for element in current.elts:
                        if isinstance(element, ast.Tuple) and len(element.elts) == 2:
                            values = [
                                item.value for item in element.elts
                                if isinstance(item, ast.Constant) and isinstance(item.value, str)
                            ]
                            if len(values) == 2:
                                mapping.setdefault(values[0], set()).add(Path(values[1]).name)
    return mapping


def guard_evaluates_to_failure(condition, receipt, root):
    """True / False for whether this receipt trips the guard, or None if it cannot be read."""
    expression = condition.strip()
    if expression.startswith("if "):
        expression = expression[3:]
    while expression.endswith(":"):
        expression = expression[:-1].rstrip()
    if not expression:
        return None

    observed = receipt.get("observed")
    if not isinstance(observed, dict):
        observed = {}
    artifact = receipt.get("artifact")
    if not isinstance(artifact, dict):
        artifact = {}
    # `root` and the standard modules are part of the checker's own namespace; supplying
    # them lets guards that inspect the filesystem be evaluated instead of skipped.
    namespace = {
        "__builtins__": {},
        "observed": observed,
        "data": receipt,
        "artifact": artifact,
        "root": root,
        "Path": Path,
        "hashlib": hashlib,
        "len": len,
        "str": str,
        "bool": bool,
        "int": int,
    }
    # Some guards sit in an `else:` branch and use a name bound a few lines earlier in the
    # checker's own block (`artifact_path = root / artifact["path"]`). Bind the names those
    # branches need so the guard can be evaluated rather than skipped.
    if "artifact_path" in expression:
        try:
            namespace["artifact_path"] = root / artifact["path"]
        except Exception:
            return None
    try:
        return bool(eval(expression, namespace, {}))  # noqa: S307 - the checker's own text
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    located = json.loads((root / LOCATE).read_text(encoding="utf-8"))
    rows_in = (located.get("observed") or {}).get("rows") or []
    excluded_by_message = baseline_by_message(root)

    rows = []
    for entry in rows_in:
        condition = entry.get("condition") or ""
        excluded = excluded_by_message.get(entry.get("message"), set())
        siblings = []
        unevaluable = []
        excludedCount = 0
        for name in entry.get("siblings") or []:
            if Path(name).name in excluded:
                excludedCount += 1
                continue
            path = root / "evaluations/records" / name
            if not path.exists():
                continue
            receipt = json.loads(path.read_text(encoding="utf-8-sig"))
            verdict = guard_evaluates_to_failure(condition, receipt, root)
            if verdict is None:
                unevaluable.append(name)
                continue
            siblings.append({
                "receipt": name,
                "guardTrips": verdict,
                # The assertion holds for a receipt exactly when the guard does not trip.
                "satisfiesAssertion": verdict is False,
            })
        # "Holds nowhere" and "could not be judged" are different findings, and a count of
        # zero siblings must not be read as either without saying which.
        if siblings:
            state = "evaluated"
        elif unevaluable:
            state = "unevaluable"
        elif excludedCount:
            state = "allSiblingsAreThemselvesFailing"
        else:
            state = "noSiblingsAtAll"
        rows.append({
            "message": entry.get("message"),
            "selector": entry.get("selector"),
            "condition": condition,
            "state": state,
            "excludedAsFailingThisAssertion": excludedCount,
            "unevaluable": unevaluable,
            "siblings": siblings,
        })

    per_assertion = {}
    for row in rows:
        key = row["message"]
        supporting = [item["receipt"] for item in row["siblings"] if item["satisfiesAssertion"]]
        record = per_assertion.setdefault(
            key, {"selector": row["selector"], "satisfiedBy": [], "states": []}
        )
        record["satisfiedBy"].extend(supporting)
        record["states"].append(row["state"])

    holds = {key: bool(value["satisfiedBy"]) for key, value in per_assertion.items()}
    # Separate "no receipt satisfies it" from "there was no receipt to judge".
    nowhere = [
        key for key, value in holds.items()
        if not value and "unevaluable" not in per_assertion[key]["states"]
    ]
    unevaluated = [
        key for key, value in holds.items()
        if not value and "unevaluable" in per_assertion[key]["states"]
    ]
    all_siblings = [item for row in rows for item in row["siblings"]]
    satisfying = [item for item in all_siblings if item["satisfiesAssertion"]]

    checks = {
        "locateReceipt": LOCATE,
        "distinctAssertions": len(per_assertion),
        "assertionsHoldingSomewhere": len([key for key, value in holds.items() if value]),
        "assertionsHoldingNowhere": nowhere,
        "assertionsNotJudgeable": unevaluated,
        "perAssertion": [
            {
                "message": key,
                "holdsSomewhere": holds[key],
                "states": value["states"],
                "siblingCount": len([
                    item for row in rows if row["message"] == key for item in row["siblings"]
                ]),
                "satisfiedBy": sorted(set(value["satisfiedBy"]))[:3],
            }
            for key, value in per_assertion.items()
        ],
        "siblingsEvaluated": len(all_siblings),
        "siblingsSatisfying": len(satisfying),
        "rows": rows,
        "finding": (
            f"各assertionの**ガード条件そのものを評価**して、兄弟receiptが規則を満たすかを見た。"
            f"規則は『失敗する条件』として書かれているので、"
            f"**ガードが偽になるreceiptが規則を満たす**。"
            f"基準の背後にある{len(per_assertion)}種類のうち、"
            f"**どこかで成立するもの{len([key for key, value in holds.items() if value])}件**、"
            f"**判定できる兄弟が無いもの{len(unevaluated)}件**、"
            f"**兄弟はいるが満たさないもの{len(nowhere)}件**。"
            "**『どこでも成立しない』と『判定する相手が無い』は別である。**"
            "**演算子を手で反転させようとして3回誤った。条件を評価すれば反転は要らない。**"
        ),
    }
    passed = bool(all_siblings)

    receipt = {
        "schema": "tai.reference.yic-assertion-sibling-check/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 evaluating each checker guard against sibling receipts",
        "command": "python integrations/tools/yic_assertion_sibling_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-assertion-siblings-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Evaluates each assertion's guard condition against sibling receipts, treating a guard "
            "that does not trip as satisfaction, and reports separately the assertions no sibling "
            "satisfies and the ones no sibling could be judged for. It evaluates only the siblings "
            "named by the location receipt; it does not sweep every registered receipt, and a guard "
            "closing over helpers rather than the receipt's own fields cannot be evaluated."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "assertions": len(per_assertion),
        "holdsSomewhere": len([key for key, value in holds.items() if value]),
        "holdsNowhere": len([key for key, value in holds.items() if not value]),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
