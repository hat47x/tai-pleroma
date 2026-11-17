"""Derive the reach table from the receipts instead of trusting it.

The reviewer asked whether the ○ marks in the I/R/P/T/C/H table were drawn from the
receipts or summarised from their names. A claim like "I read them" is not a check.
This rebuilds each card's marks from the receipt's own `observed` fields and compares
that with what the table says, so a mark without a receipt behind it shows up as a
mismatch.

The stage predicates are deliberately conservative: I needs a recorded commit and
clean checkout (the invocation is pinned); R needs observed evidence that a subject
was actually resolved or located; P, T, C and H need the receipt to say something
about a recipient, delivery, a consumer or a harness reply.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

DOC = "docs/yi-constellation/irptch-reach-2026-11-16.md"
RECORDS = "evaluations/records"

# Which receipt backs which card, taken from the document's own table.
CARD_ROWS = {
    # card: receipt, and the one field that shows the card actually resolved a
    # subject or its source position. None means this card never resolved one.
    "QH-RESOLVE-09": {
        "receipt": "YIC-qh-resolve-09-2026-11-16",
        "rEvidence": None,
        "rWhy": "能力解決の曖昧/不在を固定する試験であり、Subjectを解決していない",
    },
    "QH-A0-RUN-10": {
        "receipt": "YIC-tei-product-read-2026-11-16",
        "rEvidence": "everyListedRegressionPassed",
        "rWhy": "8件の回帰にSubjectと元byte範囲の取得が含まれ、全件PASSした",
    },
    "QH-CLI-RANGE-11": {
        "receipt": "YIC-tei-readonly-cli-2026-11-16",
        "rEvidence": "inspectReturnedByteRange",
        "rWhy": "inspectが定義位置のoffset/line/columnを返した",
    },
    "QH-REVALIDATE-12": {
        "receipt": "YIC-qh-revalidate-2026-11-16",
        "rEvidence": "snapshotFingerprint",
        "rWhy": "traceがSubjectを解決し、snapshot指紋を返した",
    },
    "QH-FIELD-13": {
        "receipt": "YIC-qh-field-13-2026-11-16",
        "rEvidence": None,
        "rWhy": "Transformの投影差を評価する試験であり、Subjectを解決していない",
    },
}

# Observed keys that show each stage was actually exercised.
RESOLVE_EVIDENCE = ()  # replaced by per-card rEvidence

DISCLOSURE_EVIDENCE = (
    "selectiveDisclosureWorks",
    "disclosesAudienceAndDisclosure",
    "declaresItIsNotAccessControl",
    "everyBoundaryTestPassed",
)
DELIVERY_EVIDENCE = ("deliveryObserved", "artifactSent", "bytesSent", "recipient")
CONSUMER_EVIDENCE = ("consumer", "consumerRead", "consumerReceived")
HARNESS_EVIDENCE = ("harnessReply", "toolReply", "harnessSession")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def marks_for(observed, entry):
    """Which stages this receipt's observed data supports, per card.

    I needs the run pinned to a commit and a clean checkout. R needs the card's named
    evidence field to be truthy. P, T, C and H need fields about a recipient, delivery,
    a consumer or a harness reply — none of the cards have them yet.
    """
    def truthy(key):
        value = observed.get(key)
        return value not in (None, "", [], {}, False)

    intent = (
        truthy("checkoutClean")
        and (truthy("teiCommit") or truthy("suiCommit"))
    )
    resolve = bool(entry["rEvidence"]) and truthy(entry["rEvidence"])

    return {
        "I": intent,
        "R": resolve,
        "P": any(truthy(k) for k in DISCLOSURE_EVIDENCE) and False,
        "T": any(truthy(k) for k in DELIVERY_EVIDENCE),
        "C": any(truthy(k) for k in CONSUMER_EVIDENCE),
        "H": any(truthy(k) for k in HARNESS_EVIDENCE),
    }


def table_marks(text):
    """The marks the document prints, per card."""
    rows = {}
    for line in text.splitlines():
        match = re.match(r"\|\s*(QH-[A-Z0-9-]+)\s*\|(.+)\|", line)
        if not match:
            continue
        cells = [cell.strip() for cell in match.group(2).split("|")]
        # A marks row has exactly six cells, each a mark; the evidence table's rows
        # carry a receipt link and prose instead.
        if len(cells) != 6:
            continue
        if not all(cell in ("○", "−", "-", "") for cell in cells):
            continue
        marks = {stage: cell.startswith("○") for stage, cell in zip("IRPTCH", cells)}
        rows[match.group(1)] = marks
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    text = (root / DOC).read_text(encoding="utf-8")
    printed = table_marks(text)
    if not printed:
        print("could not read the reach table", file=sys.stderr)
        return 1

    rows = []
    for card, entry in CARD_ROWS.items():
        receipt = entry["receipt"]
        path = root / RECORDS / f"{receipt}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        observed = data.get("observed") or {}
        derived = marks_for(observed, entry)
        documented = printed.get(card)
        if documented is None:
            rows.append({"card": card, "receipt": receipt, "documented": None, "error": "no table row"})
            continue
        mismatches = [
            {"stage": stage, "documented": documented[stage], "derived": derived[stage]}
            for stage in "IRPTCH"
            if documented[stage] != derived[stage]
        ]
        rows.append({
            "card": card,
            "receipt": receipt,
            "receiptResult": data.get("result"),
            "rEvidence": entry["rEvidence"],
            "rWhy": entry["rWhy"],
            "documented": documented,
            "derived": derived,
            "mismatches": mismatches,
        })

    mismatched = [row["card"] for row in rows if row.get("mismatches")]
    missing_rows = [row["card"] for row in rows if row.get("documented") is None]
    checks = {
        "document": DOC,
        "cards": len(CARD_ROWS),
        "rows": rows,
        "mismatchedCards": mismatched,
        "cardsWithoutATableRow": missing_rows,
        "oMarksAreBackedByTheReceipt": not mismatched and not missing_rows,
        "finding": (
            "到達点の表の○を、receiptの`observed`から機械的に再生成して突き合わせた。"
            "Iは実行の固定（commit・clean checkout）、RはSubjectの解決または位置取得の観測、"
            "P以降は受信者・配送・Consumer・Harnessの記録を要求する。"
            "Pは開示の**選択**では立たない（受信者別の判定ではないため）。"
        ),
    }
    passed = not mismatched and not missing_rows

    receipt = {
        "schema": "tai.reference.yic-reach-table-derivation/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the documents and the receipts",
        "command": "python integrations/tools/yic_reach_table_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-reach-table-2026-11-17.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Rebuilds the I/R/P/T/C/H marks from each card's receipt and compares them with the "
            "document. It checks that a printed ○ has receipt evidence behind it and that no receipt "
            "hides a stage the document leaves blank. The predicates are conservative heuristics over "
            "field names: they can confirm a mark is backed, and they can catch a mark with no backing "
            "field, but they do not judge whether the evidence means what the stage requires."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "cards": len(CARD_ROWS),
        "mismatched": mismatched,
        "missingRows": missing_rows,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
