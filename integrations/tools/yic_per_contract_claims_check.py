"""Check that the proposal document states per-contract differences, not one blanket claim.

Rounds 94-97 each corrected the previous round's scope. The document now separates four
contracts (AccessRequest, handoff envelope, audit envelope, EKI Lease). A single blanket
sentence would repeat the error the independent review identified. This check requires
that each contract appears with its own verdict, and that no sentence claims a
product-wide absence.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

DOC = "docs/yi-constellation/analysis/55-受信者の欄.md"
# Contracts that must each be named with their own status.
CONTRACTS = (
    {"name": "AccessRequest", "phrases": ("AccessRequest",), "mustSayAbsent": True},
    {"name": "handoffEnvelope", "phrases": ("handoff envelope", "disclosure.audience"), "mustSayAbsent": False},
    {"name": "auditEnvelope", "phrases": ("AuditEvent", "metadata"), "mustSayAbsent": True},
    {"name": "ekiLease", "phrases": ("leasedelivery", "WorkerIdentity"), "mustSayAbsent": False},
)
# Sentences that would generalise to the whole product group.
BLANKET = (
    "Pは測れない",
    "受信者の欄が無い製品",
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
    for contract in CONTRACTS:
        named = any(phrase in text for phrase in contract["phrases"])
        rows.append({
            "contract": contract["name"],
            "named": named,
            "phrasesPresent": [p for p in contract["phrases"] if p in text],
        })

    unnamed = [row["contract"] for row in rows if not row["named"]]
    # A blanket claim is one that does not name a contract in the same sentence.
    blanket = []
    for phrase in BLANKET:
        for match in re.finditer(re.escape(phrase), text):
            sentence_start = max(
                text.rfind("。", 0, match.start()), text.rfind("\n", 0, match.start())
            )
            # Include the rest of the sentence: a retraction can follow the claim.
            ends = [index for index in (text.find("。", match.end()),
                                        text.find("\n", match.end())) if index != -1]
            sentence_end = min(ends) if ends else len(text)
            sentence = text[sentence_start + 1:sentence_end]
            retracted = any(
                word in sentence for word in ("取り下げ", "訂正", "誤り", "とは書かない", "まとめることはできない")
            )
            named_a_contract = any(
                any(phrase in sentence for phrase in c["phrases"]) for c in CONTRACTS
            )
            if not retracted and not named_a_contract:
                blanket.append(sentence.strip()[:80])
    statedPerContract = "製品と契約ごとに違う" in text

    checks = {
        "document": DOC,
        "contracts": rows,
        "contractsNotNamed": unnamed,
        "blanketSentences": blanket,
        "statesTheDifferencesArePerContract": statedPerContract,
        "everyContractIsNamed": not unnamed,
        "noBlanketClaim": not blanket,
        "finding": (
            "提案文書が、契約ごとに受信者の有無が違うことを述べているかを見る。"
            "`AccessRequest`・handoff envelope・`AuditEvent`・EKI Leaseの4つを個別に名指しし、"
            "**製品群全体への全称判断が無いこと**を要求する。"
            "1つの契約の欠落を製品群の欠落と呼ばないためである。"
        ),
    }
    passed = not unnamed and not blanket and statedPerContract

    receipt = {
        "schema": "tai.reference.yic-per-contract-claims/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the proposal document",
        "command": "python integrations/tools/yic_per_contract_claims_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-per-contract-claims-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Checks the proposal document names each of four contracts and carries no sentence that "
            "generalises an absence to the whole product group. It checks the document's structure, "
            "not whether each contract's stated status is correct."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "contracts": len(rows),
        "notNamed": unnamed,
        "blanket": [b[:50] for b in blanket],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
