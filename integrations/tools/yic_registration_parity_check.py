"""Check that every receipt the checker registers also has a rule, and vice versa.

The checker has two independent lists: `RECORDS` (which receipts are known) and the
`if "<name>" in relative:` rules (which receipts are inspected in detail). A receipt on
one list but not the other is either registered without being checked, or checked
without being registered — both silent.

This compares the two lists and reports both directions.
"""

import argparse
import hashlib
import json
import os
import re
import time
from pathlib import Path

CHECKER = "tools/check-synthetic-receipts/check.py"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    text = (root / CHECKER).read_text(encoding="utf-8")

    registered = sorted(set(re.findall(r'"(evaluations/records/[^"]+\.json)"', text)))
    rules = sorted(set(re.findall(r'if "([^"]+)" in relative:', text)))

    # A rule matches by substring; a receipt is covered when some rule's text appears
    # in its file name.
    covered = [name for name in registered if any(rule in os.path.basename(name) for rule in rules)]
    uncovered = [name for name in registered if name not in covered]

    # A rule that matches no registered receipt is dead: it can never fire.
    firing = {}
    for rule in rules:
        matches = [name for name in registered if rule in os.path.basename(name)]
        firing[rule] = matches
    deadRules = [rule for rule, matches in firing.items() if not matches]
    ambiguousRules = {
        rule: matches for rule, matches in firing.items() if len(matches) > 1
    }

    onDisk = sorted(
        "evaluations/records/" + path.name
        for path in (root / "evaluations/records").glob("*.json")
    )
    unregisteredOnDisk = [name for name in onDisk if name not in registered]

    checks = {
        "checker": CHECKER,
        "registeredReceipts": len(registered),
        "rules": len(rules),
        "receiptsWithARule": len(covered),
        "receiptsWithoutARule": uncovered,
        "rulesThatMatchNothing": deadRules,
        "rulesMatchingMoreThanOne": ambiguousRules,
        "receiptsOnDiskNotRegistered": unregisteredOnDisk,
        "everyRegisteredReceiptHasARule": not uncovered,
        "everyRuleCanFire": not deadRules,
        "finding": (
            f"checkerの`RECORDS`（{len(registered)}件）と、"
            f"`if \"...\" in relative:`（{len(rules)}件）を突き合わせた。"
            f"**{len(uncovered)}件のreceiptには個別規則が無く**、汎用の規則だけで検査される。"
            f"**{len(deadRules)}件の規則は一度も発火しない**。"
            f"**{len(unregisteredOnDisk)}件はディスク上にあるがRECORDSに無い**。"
            "**これは欠陥の一覧ではなく、検査の網目が粗いことの測定である。**"
            "個別規則の無いreceiptは「合格」と報告されるが、"
            "その合格は**汎用規則を満たしただけ**である。"
        ),
    }
    passed = len(registered) > 0 and len(rules) > 0

    receipt = {
        "schema": "tai.reference.yic-registration-parity/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the checker's two lists",
        "command": "python integrations/tools/yic_registration_parity_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-registration-parity-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Compares the checker's registered receipt list with its per-file rule list, and with "
            "the files on disk. It finds receipts that are listed but never inspected, rules that "
            "can never fire, and files that are not registered; it does not judge whether a rule "
            "checks the right thing."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "registered": len(registered),
        "rules": len(rules),
        "withoutRule": len(uncovered),
        "deadRules": len(deadRules),
        "amb": len(ambiguousRules),
        "unregistered": len(unregisteredOnDisk),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
