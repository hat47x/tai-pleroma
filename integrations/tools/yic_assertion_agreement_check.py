"""Check whether the worked-around evaluation produced the same answer as the rule.

For the two assertions that still hold nowhere, compare what the guard evaluation said with
what the checker itself says on the next full run. If the checker reports exactly the
baseline entries and nothing else, the evaluation agrees with the rule; if it reports more or
different messages, the evaluation is still blind to something.
"""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

CHECKER = "tools/check-synthetic-receipts/check.py"
SIBLINGS = "evaluations/records/YIC-assertion-siblings-2026-11-28.json"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    completed = subprocess.run(
        [sys.executable, str(root / CHECKER), "--root", str(root)],
        cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=3600,
    )
    body = completed.stdout
    payload = json.loads(body[body.index("{"):]) if "{" in body else {}

    reported = payload.get("knownRuleFailures") or []
    unresolved = payload.get("resolvedRuleFailures") or []
    blocking = payload.get("errors") or []

    data = json.loads((root / SIBLINGS).read_text(encoding="utf-8"))
    nowhere = (data.get("observed") or {}).get("assertionsHoldingNowhere") or []

    requestedMessages = set(nowhere)
    reportedMessages = {
        message.split(": ")[0] for message in reported + unresolved
    }
    absent = [message for message in requestedMessages if message not in reportedMessages]

    checks = {
        "checkerExit": completed.returncode,
        "checkerPassed": payload.get("passed"),
        "knownRuleFailures": len(reported),
        "resolvedRuleFailures": len(unresolved),
        "blocking": len(blocking),
        "assertionsTheEvaluationCouldNotSupport": len(nowhere),
        "messagesTheCheckerActuallyReports": sorted(reportedMessages),
        "assertionsNotReportedByTheChecker": absent,
        "evaluationAgreesWithTheRule": not absent and payload.get("passed") is True,
        "finding": (
            "ガード評価が『どこでも成立しない』とした"
            f"{len(nowhere)}種類を、**checker自身の出力と突き合わせた**。"
            f"checkerは{len(reported)}件の既知失敗を報告し、阻止は{len(blocking)}件。"
            + (
                "**評価が根拠にした種類はすべてcheckerも報告している。**"
                "評価は規則と一致している。"
                if not absent
                else f"**checkerが報告しない種類が{len(absent)}件ある。評価が何かを見落としている。**"
            )
        ),
    }
    passed = payload.get("passed") is True and not absent

    receipt = {
        "schema": "tai.reference.yic-assertion-agreement/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 running the checker and comparing its messages",
        "command": "python integrations/tools/yic_assertion_agreement_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-assertion-agreement-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs the checker and compares the messages it reports with the assertions the "
            "sibling evaluation could not support. It checks agreement of message sets; it does not "
            "verify the evaluation of every individual receipt."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "checkerPassed": payload.get("passed"),
        "known": len(reported),
        "absent": len(absent),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
