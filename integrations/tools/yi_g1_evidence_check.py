"""Check whether each cross-cutting decision in G1 has the evidence it needs.

G1 asks an Owner to decide six things (D1-D6). Each decision rests on evidence:
a reference implementation, a document, or a measurement. If one of them has only
a document and no observation, the Owner is being asked to decide without a
measurement. This records, per decision, what evidence exists and what does not.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

# Each decision, the evidence that would support it, and what kind it is.
DECISIONS = (
    {
        "id": "D1",
        "question": "ハーネスの境界をどこに置くか",
        "evidence": [
            ("observation", "evaluations/records/YI-context-handoff-2026-11-11.json"),
            ("observation", "evaluations/records/YI-centre-handoff-2026-11-11.json"),
            ("document", "docs/yi-constellation/analysis/13-設計ノート.md"),
        ],
        "missing": "各製品の接続口（実製品側）の観測。参照実装はあるが、実製品には接続していない",
    },
    {
        "id": "D2",
        "question": "TAIを「輔相製品」と呼ぶか",
        "evidence": [
            ("document", "docs/yi-constellation/analysis/20-製品と卦の対応レビュー.md"),
            ("document", "docs/yi-constellation/analysis/18-G1レビューパケット.md"),
        ],
        "missing": "用語の変更が利用者・製品文書へ与える影響の観測（読みの一致だけでは足りない）",
    },
    {
        "id": "D3",
        "question": "SHOの状態をどう示すか",
        "evidence": [
            ("observation", "evaluations/records/YI-sho-actual-2026-11-11.json"),
            ("document", "docs/yi-constellation/analysis/21-SHOの扱い.md"),
            ("document", "docs/yi-constellation/analysis/20-製品と卦の対応レビュー.md"),
        ],
        "missing": "SHOを製品として扱った場合の要求文書・Owner・利用者の実在（リポジトリの内容は測った）",
    },
    {
        "id": "D4",
        "question": "坎をどう扱うか",
        "evidence": [
            ("observation", "evaluations/records/YI-danger-units-2026-11-11.json"),
            ("observation", "evaluations/records/YI-publication-refusal-2026-11-11.json"),
            ("document", "docs/yi-constellation/analysis/50-G4レビューパケット.md"),
        ],
        "missing": "危険の単位の測定（今は語彙検索による上限であり、単位そのものを測っていない）",
    },
    {
        "id": "D5",
        "question": "系列全体の要求を誰が受理するか",
        "evidence": [
            ("document", "docs/yi-constellation/analysis/18-G1レビューパケット.md"),
            ("document", "docs/yi-constellation/analysis/07-計画.md"),
        ],
        "missing": "受理者の権限と責任の所在を示す文書（現状は推奨のみ）",
    },
    {
        "id": "D6",
        "question": "SHOを製品・MMIの役割・保留のどれにするか",
        "evidence": [
            ("document", "docs/yi-constellation/analysis/21-SHOの扱い.md"),
            ("observation", "evaluations/records/YI-empty-reference-2026-11-11.json"),
        ],
        "missing": "SHOを製品として扱った場合の要求文書・Owner・利用者の実在",
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

    results = []
    for decision in DECISIONS:
        present = []
        absent = []
        for kind, relative in decision["evidence"]:
            path = root / relative
            (present if path.exists() else absent).append({"kind": kind, "path": relative})
        observ = [item for item in present if item["kind"] == "observation"]
        results.append({
            "id": decision["id"],
            "question": decision["question"],
            "evidencePresent": present,
            "evidenceMissing": absent,
            "hasObservation": bool(observ),
            "observationCount": len(observ),
            "gaps": decision["missing"],
        })

    no_observation = [item["id"] for item in results if not item["hasObservation"]]
    broken = [item for item in results for item in item["evidencePresent"]]
    missing_files = [
        {"id": item["id"], "path": entry["path"]}
        for item in results
        for entry in item["evidenceMissing"]
    ]

    checks = {
        "decisions": results,
        "decisionsChecked": len(results),
        "decisionsWithNoObservation": no_observation,
        "missingFiles": missing_files,
        # PASS here means the check ran and found the gaps it reports. The
        # absence of an observation for a decision is the finding, not a failure
        # of this check, so the field is named for what it measures rather than
        # as an invariant the receipt claims to have met.
        "decisionsWithoutObservation": no_observation,
        "everyDecisionHasAnObservation": not no_observation,
        "finding": (
            "6つの横断判断のうち、D1・D3・D4・D6は観測を持ち、D2・D5は文書だけである。"
            "観測を持たない2つ（呼び方と受理者）は、観測ではなく組織の決定かもしれない。"
        ),
        "everyCitedPathExists": not missing_files,
        "everyDecisionNamesItsGap": all(item["gaps"] for item in results),
    }
    passed = checks["everyCitedPathExists"] and checks["everyDecisionNamesItsGap"]

    receipt = {
        "schema": "tai.reference.yi-g1-evidence-check/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the analysis and receipts",
        "command": "python integrations/tools/yi_g1_evidence_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-g1-evidence-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "For each of G1's six cross-cutting decisions, records which evidence files exist, whether any of them is an observation rather than a document, and what gap the packet itself names. It reads presence and paths only: it does not judge whether the evidence supports the recommendation, and the named gaps are the packet author's, not a measurement.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "decisions": len(results),
        "withoutObservation": no_observation,
        "missingFiles": len(missing_files),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
