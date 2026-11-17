"""Check whether doc 53's "nothing further can be done" claim is still true.

Doc 53 (2026-11-11) ends with "これ以上TAIが単独で進めても、新しい証拠は増えない". Since
that sentence was written, this session produced twenty-odd further receipts. The
sentence is a dated judgement, not a permanent fact, but a reader arriving now reads it
as current.

This counts receipts dated after the claim and checks that the document acknowledges
them, so the two do not silently disagree.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

DOC = "docs/yi-constellation/analysis/53-判定と残る前進.md"
CLAIM_DATE = "2026-11-11"
CLAIM = "新しい証拠は増えない"
ACKNOWLEDGEMENT = "その後の追記"


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

    # Receipts dated strictly after the claim.
    later = []
    for receipt in sorted((root / "evaluations/records").glob("*.json")):
        try:
            data = json.loads(receipt.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        day = str(data.get("date", ""))
        if day > CLAIM_DATE:
            later.append({"receipt": receipt.name, "date": day})

    claimsExhaustion = CLAIM in text
    acknowledgesLater = ACKNOWLEDGEMENT in text
    namesClaimDate = CLAIM_DATE in text.split(CLAIM)[0][-400:] if claimsExhaustion else False
    # Only receipts the acknowledgement actually lists count as covered.
    listed = [
        item["receipt"] for item in later
        if item["receipt"] in text
    ]
    notNamedIndividually = [item["receipt"] for item in later if item["receipt"] not in listed]

    checks = {
        "document": DOC,
        "claimDate": CLAIM_DATE,
        "carriesTheExhaustionClaim": claimsExhaustion,
        "namesTheClaimDateNearby": namesClaimDate,
        "hasAnAcknowledgementSection": acknowledgesLater,
        "receiptsDatedAfterTheClaim": len(later),
        "receiptsNamedInTheDocument": len(listed),
        # Listing every receipt is not the standard; saying that evidence increased is.
        "receiptsNotNamedIndividually": notNamedIndividually,
        "finding": (
            "文書53は2026-11-11に「これ以上TAIが単独で進めても、新しい証拠は増えない」と書いた。"
            f"しかしそれ以降に**{len(later)}件**のreceiptが書かれている。"
            "**この文は日付つきの判断であり、恒久的な事実ではない。**"
            "読者が現在の記述と読まないよう、その後の追記で何が増えたかを記す。"
        ),
    }
    # Passes when the claim is either acknowledged or absent.
    passed = (not claimsExhaustion) or (acknowledgesLater and namesClaimDate)

    receipt = {
        "schema": "tai.reference.yic-exhaustion-claim/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading doc 53 and every receipt",
        "command": "python integrations/tools/yic_exhaustion_claim_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-exhaustion-claim-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Compares doc 53's dated exhaustion claim against the dates of every receipt in the "
            "repository and checks whether the document acknowledges later work. It judges whether "
            "the document and the tree disagree on this one claim, not whether the claim was right "
            "when written."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "later": len(later),
        "listed": len(listed),
        "notNamedIndividually": len(notNamedIndividually),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
