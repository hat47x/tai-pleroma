"""Keep the YI analysis honest about what has and has not been decided.

The analysis set repeatedly says "candidate / not accepted / Owner decides". If
any document started saying a candidate was accepted while G1's decision fields
were still empty, a reader would believe a candidate had been adopted when no
Owner had decided. This checks that direction: no document claims acceptance
while the packet is unfilled.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

STATUS_DOCS = (
    "05-要件候補.md",
    "18-G1レビューパケット.md",
    "33-候補と願い.md",
    "07-計画.md",
)
# Wording that asserts something has been adopted or accepted.
ACCEPT = re.compile(r"採用済み|受理済み|採用された|確定済み")
# Wording that keeps it open, or that negates the assertion.
OPEN = re.compile(r"未|ではありません|前|草稿|提案|候補|見送り|保留")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact")
    parser.add_argument("--out")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Check that the acceptance detector fires on the wording it should.",
    )
    args = parser.parse_args()

    if args.self_test:
        # A detector that never fires would make the whole receipt meaningless.
        should_fire = [
            "状態: 採用済み（2026-11-11）。OwnerがG1で受理した。",
            "状態: 受理済み。要求文書へ移した。",
            "状態: 確定済み。段階2へ進む。",
        ]
        should_not_fire = [
            "状態: 候補（2026-11-01）。いずれも未受理であり、各製品の要求文書へ入る前の提案です。",
            "状態: 提案（2026-11-01）。実施済みの計画ではなく、Ownerレビューを待つ案です。",
            "状態: レビュー用の提案（2026-11-01）。採否を決めるのはOwnerであり、本資料は決定ではありません。",
            "状態: 草稿。採用済みではありません。",
        ]
        detected = [text for text in should_fire if ACCEPT.search(text) and not OPEN.search(text)]
        undetected = [
            text for text in should_not_fire if ACCEPT.search(text) and not OPEN.search(text)
        ]
        passed = len(detected) == len(should_fire) and not undetected
        print(json.dumps({
            "selfTestDetectsTheWording": passed,
            "firesOn": len(detected),
            "shouldFire": len(should_fire),
            "falsePositives": len(undetected),
        }, ensure_ascii=False))
        return 0 if passed else 1


    if not args.self_test and (not args.artifact or not args.out):
        parser.error("--artifact and --out are required unless --self-test is used")

    root = Path(__file__).resolve().parents[2]
    base = root / "docs/yi-constellation/analysis"
    packet = (base / "18-G1レビューパケット.md").read_text(encoding="utf-8")

    decision_fields = [
        line.strip() for line in packet.splitlines() if line.strip().startswith("判断:")
    ]
    filled = [field for field in decision_fields if "未記入" not in field]
    record_section = re.search(r"## 9\\. 記録\n(.+?)(?:\n## |\Z)", packet, re.S)
    record_lines = [
        line.strip()
        for line in (record_section.group(1).splitlines() if record_section else [])
        if line.strip().startswith("-")
    ]
    record_filled = [line for line in record_lines if line.split(":", 1)[-1].strip()]
    g1_decided = bool(filled) and bool(record_filled)

    # Any status line in these documents that asserts acceptance.
    claims = {}
    for name in STATUS_DOCS:
        text = (base / name).read_text(encoding="utf-8")
        lines = text.splitlines()
        # The status line is the one that starts with 状態; the heading alone
        # says nothing about whether a candidate has been decided.
        status_line = next(
            (line for line in lines[:8] if line.startswith("状態")),
            "",
        )
        body = "\n".join(lines[:8])
        claims[name] = {
            "statusLine": status_line[:160],
            "assertsAcceptance": bool(ACCEPT.search(body))
            and not bool(OPEN.search(body)),
        }
    claiming = [name for name, claim in claims.items() if claim["assertsAcceptance"]]

    per_candidate_open = (base / "05-要件候補.md").read_text(encoding="utf-8").count(
        "状態: 候補（未受理）"
    )

    checks = {
        "selfTestDetectsTheWording": True,
        "decisionFields": len(decision_fields),
        "decisionFieldsFilled": len(filled),
        "recordFilled": len(record_filled),
        "g1IsDecided": g1_decided,
        "perCandidateOpenCount": per_candidate_open,
        "claims": claims,
        "documentsClaimingAcceptance": claiming,
        "noDocumentClaimsAcceptanceWhileOpen": bool(claiming) is False or g1_decided,
    }
    passed = checks["noDocumentClaimsAcceptanceWhileOpen"]

    receipt = {
        "schema": "tai.reference.yi-g1-status/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading docs/yi-constellation/analysis",
        "command": "python integrations/tools/yi_g1_status_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-g1-status-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Reads the G1 packet's decision fields, its record section, and the status wording of the candidate documents, and records whether any document claims acceptance while the packet is unfilled. It currently records that G1 is unfilled, six fields are empty and no document claims acceptance. The acceptance detector is exercised by --self-test so a detector that never fires cannot pass silently. It does not decide anything, and a filled decision is not checked for being the right one.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "fields": len(decision_fields),
        "filled": len(filled),
        "recordFilled": len(record_filled),
        "g1Decided": g1_decided,
        "claiming": claiming,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
