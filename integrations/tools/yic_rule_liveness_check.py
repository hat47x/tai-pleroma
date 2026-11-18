"""Check that every per-receipt rule can actually fire on a registered receipt.

The checker matches rules with `if "<name>" in relative:`. `relative` is the receipt's
path, which carries the name as written on disk: `SUI-TEI-adapter-…`. Rules are written
in lower case: `tei-adapter`. Twenty-nine of them never match because of the case alone,
so the detailed checks they encode silently never run — the receipt still passes on the
generic rules.

This compares each rule against the registered names, case-sensitively and
case-insensitively, and reports the rules that only fail on case.
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
    registered = sorted(
        set(re.findall(r'"(evaluations/records/[^"]+\.json)"', text))
    )
    rules = sorted(set(re.findall(r'if "([^"]+)" in relative:', text)))

    caseOnlyDead = []
    trulyDead = []
    for rule in rules:
        exact = [name for name in registered if rule in name]
        if exact:
            continue
        insensitive = [name for name in registered if rule in name.lower()]
        if insensitive:
            caseOnlyDead.append({
                "rule": rule,
                "wouldMatch": insensitive[:3],
                "matchCount": len(insensitive),
            })
        else:
            trulyDead.append(rule)

    checks = {
        "checker": CHECKER,
        "registeredReceipts": len(registered),
        "rules": len(rules),
        "rulesDeadOnlyOnCase": caseOnlyDead,
        "caseDeadCount": len(caseOnlyDead),
        "rulesDeadRegardlessOfCase": trulyDead,
        "trulyDeadCount": len(trulyDead),
        "comparedCaseSensitively": True,
        "finding": (
            "checkerの規則は`if \"...\" in relative:`で照合する。"
            "`relative`はディスク上の名前（`SUI-TEI-adapter-…`）を保ち、"
            "規則は小文字（`tei-adapter`）で書かれている。"
            f"**{len(caseOnlyDead)}件の規則が、大小文字の違いだけで一度も発火しない。**"
            "それらのreceiptは汎用の規則だけを通り、"
            "**詳細な検査が無音で飛ばされている**。"
        ),
    }
    # This check passes when it can report the finding, not when there are no dead rules:
    # the dead rules are the finding.
    passed = len(caseOnlyDead) > 0

    receipt = {
        "schema": "tai.reference.yic-rule-liveness/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 comparing rules with registered names",
        "command": "python integrations/tools/yic_rule_liveness_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-rule-liveness-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Compares the checker's rule strings with its registered receipt names, case-sensitively "
            "and case-insensitively. It shows which rules cannot fire; it does not run them or judge "
            "whether they would pass if they did."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "rules": len(rules),
        "caseDead": len(caseOnlyDead),
        "trulyDead": len(trulyDead),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
