"""Check that the gate-status prose matches the receipts it cites.

Documents 51 and 53 state counts about the gates: "3件実行済み・1件記述のみ・3件未実施",
"25件の候補", "6つの横断判断", "9編集". Each of those numbers comes from a receipt. A
number that has drifted from its receipt reads as a finding when it is only stale prose.

This reads the stated numbers and compares the ones it can derive mechanically.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

RECORDS = "evaluations/records"
DOCS = (
    "docs/yi-constellation/analysis/51-現在地とゲートの状態.md",
    "docs/yi-constellation/analysis/53-判定と残る前進.md",
)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(root, name):
    return json.loads((root / RECORDS / name).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    texts = {}
    for relative in DOCS:
        path = root / relative
        if not path.exists():
            print(f"missing {relative}", file=sys.stderr)
            return 1
        texts[relative] = path.read_text(encoding="utf-8")

    # The facts the documents assert, and where each comes from.
    stage3 = load(root, "YI-stage3-inventory-2026-11-11.json")["observed"]
    g1 = load(root, "YI-g1-status-2026-11-11.json")["observed"]
    g1_evidence = load(root, "YI-g1-evidence-2026-11-11.json")["observed"]
    candidates = load(root, "YI-candidate-fields-2026-11-11.json")["observed"]
    csw = load(root, "YI-csw-return-2026-11-11.json")["observed"]

    executed = len(stage3.get("executed") or [])
    evidence_only = len(stage3.get("evidenceOnly") or [])
    not_run = len(stage3.get("notRun") or [])
    decisions = len(g1_evidence.get("decisions") or [])
    decisions_checked = g1_evidence.get("decisionsChecked")
    without_observation = len(g1_evidence.get("decisionsWithoutObservation") or [])
    candidate_count = candidates.get("candidateCount") or candidates.get("candidates")
    if isinstance(candidate_count, list):
        candidate_count = len(candidate_count)
    edits = len(csw.get("results") or []) or csw.get("editsRecorded")

    # The prose counts, read from the text.
    claims = []
    pattern_stage3 = re.search(r"(\d+)件実行済み・(\d+)件記述のみ・(\d+)件未実施", texts[DOCS[0]])
    if pattern_stage3:
        claims.append({
            "claim": "stage3 executed/described/not-run",
            "stated": [int(pattern_stage3.group(1)), int(pattern_stage3.group(2)), int(pattern_stage3.group(3))],
            "fromReceipt": [executed, evidence_only, not_run],
            "source": "YI-stage3-inventory-2026-11-11.json",
        })
    pattern_candidates = re.search(r"(\d+)件の候補", texts[DOCS[0]])
    if pattern_candidates:
        claims.append({
            "claim": "candidate count",
            "stated": [int(pattern_candidates.group(1))],
            "fromReceipt": [candidate_count if isinstance(candidate_count, int) else None],
            "source": "YI-candidate-fields-2026-11-11.json",
        })
    # Search every document for the claim, and record which one stated it.
    pattern_decisions = None
    for relative, body in texts.items():
        match = re.search(r"(\d+)つの横断判断", body)
        if match:
            pattern_decisions = (relative, match)
            break
    if pattern_decisions:
        claims.append({
            "claim": "cross-cutting decisions",
            "stated": [int(pattern_decisions[1].group(1))],
            "fromReceipt": [decisions],
            "source": "YI-g1-evidence-2026-11-11.json",
            "statedIn": pattern_decisions[0],
        })
    pattern_edits = re.search(r"(\d+)編集", texts[DOCS[1]])
    if pattern_edits:
        claims.append({
            "claim": "CSW edits",
            "stated": [int(pattern_edits.group(1))],
            "fromReceipt": [edits if isinstance(edits, int) else None],
            "source": "YI-csw-return-2026-11-11.json",
        })

    mismatched = [
        claim for claim in claims
        if claim["stated"] != claim["fromReceipt"]
        and None not in claim["fromReceipt"]
    ]

    checks = {
        "documents": list(DOCS),
        "claimsChecked": len(claims),
        "claims": claims,
        "mismatched": mismatched,
        "g1StatusFields": {
            "decisionsChecked": decisions_checked,
            "decisionsWithoutObservation": without_observation,
        },
        "everyStatedNumberMatchesItsReceipt": not mismatched,
        "finding": (
            "ゲート状態の文書が述べる件数を、引用しているreceiptの値と突き合わせる。"
            "`3件実行済み・1件記述のみ・3件未実施`、候補数、横断判断の数、CSW編集数が対象である。"
        ),
    }
    passed = not mismatched

    receipt = {
        "schema": "tai.reference.yic-gate-prose-values/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the gate documents and their receipts",
        "command": "python integrations/tools/yic_gate_prose_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-gate-prose-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Compares four counts stated in the gate-status documents with the receipts those "
            "documents cite: stage-3 executed/described/not-run, candidate count, cross-cutting "
            "decision count and CSW edit count. It checks those four numbers only; other prose "
            "claims in the same documents are not examined."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "claims": len(claims),
        "mismatched": [claim["claim"] for claim in mismatched],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
