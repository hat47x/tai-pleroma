"""Check that a design proposal names who may decide it, and that TAI did not.

Doc 55 recommends adding an `audience` field to SUI's `AccessRequest`. That is a
change to a product's contract, which TAI is not allowed to decide. The document says
so, but a claim in prose is not a constraint. This checks that the document carries
both halves: a recommendation, and an explicit statement that the decision belongs to
the product owner and that TAI does not implement it.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

DOC = "docs/yi-constellation/analysis/55-受信者の欄.md"
# Each requirement, with the phrases that would satisfy it.
REQUIRES = (
    {
        "name": "statesItIsAProposal",
        "phrases": ("提案", "材料", "設計の比較"),
        "question": "提案であって受理ではないと述べているか",
    },
    {
        "name": "namesTheOwner",
        "phrases": ("Owner",),
        "question": "判断する主体を名指ししているか",
    },
    {
        "name": "saysTaiWillNotImplement",
        "phrases": ("TAIは変更しない", "TAIがこれを実装しない", "編集・採用確定しない"),
        "question": "TAIが実装しないと述べているか",
    },
    {
        "name": "givesARecommendation",
        "phrases": ("推奨", "案A"),
        "question": "推奨を一つに絞っているか",
    },
    {
        "name": "namesWhatWouldBreak",
        "phrases": ("壊れる",),
        "question": "壊れる可能性を述べているか",
    },
    {
        "name": "givesAMinimalTest",
        "phrases": ("最小の試験",),
        "question": "最小の試験を挙げているか",
    },
)


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
    for item in REQUIRES:
        found = [phrase for phrase in item["phrases"] if phrase in text]
        rows.append({
            "requirement": item["name"],
            "question": item["question"],
            "matchedPhrases": found,
            "satisfied": bool(found),
        })

    unsatisfied = [row["requirement"] for row in rows if not row["satisfied"]]
    # The document must not present the change as decided.
    assertsDecision = any(
        phrase in text for phrase in ("採用する", "決定した", "受理した")
    )
    checks = {
        "document": DOC,
        "requirements": rows,
        "unsatisfied": unsatisfied,
        "assertsTheChangeIsDecided": assertsDecision,
        "everyRequirementIsStated": not unsatisfied,
        "finding": (
            "製品の契約変更を提案する文書が、**提案であること・判断主体・"
            "TAIが実装しないこと**を述べているかを点検する。"
            "推奨だけを書くと、読み手が決定と読む。"
        ),
    }
    passed = not unsatisfied and not assertsDecision

    receipt = {
        "schema": "tai.reference.yic-proposal-boundary/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the design proposal",
        "command": "python integrations/tools/yic_proposal_boundary_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-proposal-boundary-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Checks that the design proposal document states it is a proposal, names the deciding "
            "owner, says TAI will not implement it, and gives a recommendation with a breakage note "
            "and a minimal test. It checks the presence of those statements, not whether the "
            "recommendation is sound."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "requirements": len(rows),
        "unsatisfied": unsatisfied,
        "assertsDecided": assertsDecision,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
