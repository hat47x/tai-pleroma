"""Check that the deck proposals still match what the analysis now says.

Doc 17 proposes what to put into the summary deck once the analysis is accepted.
Its numbers and statuses were written before several measurements; if they have
drifted, an accepted proposal would put stale figures into a public deck. This
compares the figures doc 17 states against the receipts that measured them.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

# Figures doc 17 states, with the receipt that measured each and the field to read.
CLAIMS = (
    {
        "name": "candidateClassification",
        "document": "docs/yi-constellation/analysis/17-概要資料への反映案.md",
        "text": "新規7",
        "receipt": "evaluations/records/YI-citation-check-2026-11-11.json",
        "path": ("observed", "crossCheckClassification"),
        "key": "新規",
        "expected": 7,
    },
    {
        "name": "extensionCount",
        "document": "docs/yi-constellation/analysis/17-概要資料への反映案.md",
        "text": "拡張8",
        "receipt": "evaluations/records/YI-citation-check-2026-11-11.json",
        "path": ("observed", "crossCheckClassification"),
        "key": "拡張",
        "expected": 8,
    },
    {
        "name": "keptAsRequirements",
        "document": "docs/yi-constellation/analysis/17-概要資料への反映案.md",
        "text": "要求として残るのは15件",
        "receipt": "evaluations/records/YI-citation-check-2026-11-11.json",
        "path": ("observed", "keptInPacket"),
        "key": None,
        "expected": 15,
    },
    {
        "name": "movedToExisting",
        "document": "docs/yi-constellation/analysis/17-概要資料への反映案.md",
        "text": "既存の要求で足りる10件",
        "receipt": "evaluations/records/YI-citation-check-2026-11-11.json",
        "path": ("observed", "movedInPacket"),
        "key": None,
        "expected": 10,
    },
)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def get(data, path, key):
    value = data
    for step in path:
        value = value.get(step, {}) if isinstance(value, dict) else {}
    if key is not None:
        value = value.get(key) if isinstance(value, dict) else None
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]

    results = []
    for claim in CLAIMS:
        document = root / claim["document"]
        receipt = root / claim["receipt"]
        text_present = claim["text"] in document.read_text(encoding="utf-8")
        measured = (
            get(json.loads(receipt.read_text(encoding="utf-8")), claim["path"], claim["key"])
            if receipt.exists() else None
        )
        results.append({
            "name": claim["name"],
            "statedInDeckProposal": text_present,
            "expected": claim["expected"],
            "measured": measured,
            "agrees": measured == claim["expected"],
        })

    drifted = [item for item in results if not item["agrees"]]
    missing = [item for item in results if not item["statedInDeckProposal"]]

    checks = {
        "claims": results,
        "claimsChecked": len(results),
        "drifted": drifted,
        "missingFromProposal": missing,
        "everyClaimStillStated": not missing,
        "everyClaimAgreesWithReceipt": not drifted,
    }
    passed = not drifted and not missing

    receipt = {
        "schema": "tai.reference.yi-deck-proposal-figures/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the proposal and the receipts",
        "command": "python integrations/tools/yi_deck_proposal_figures_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-deck-figures-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Compares four figures stated in the deck proposal against the receipts that measured them, and records whether they still agree. It checks figures only: whether the deck should be updated at all is governed by the proposal's own rule that the analysis must be accepted first, and this does not decide that.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "drifted": [item["name"] for item in drifted],
        "missing": [item["name"] for item in missing],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
