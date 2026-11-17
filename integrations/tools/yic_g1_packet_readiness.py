"""Check that the G1 packet is ready for a decision, not that it has been decided.

G1 asks the Owner to classify 25 candidates and settle six cross-cutting questions.
The packet is TAI's input to that decision. "Ready" means each row has an empty
judgement cell (TAI has not decided for the Owner) and each candidate carries the
fields a decision needs. It does not mean the decision exists.

This reads the packet's two tables and reports, per candidate, whether the judgement
cell is empty and the recommendation present, and per decision whether a question and
options are stated.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

PACKET = "docs/yi-constellation/analysis/18-G1レビューパケット.md"
# Section 2 keeps 15 candidates; section 3 lists the 10 that moved to other requirements.
KEPT_HEADING = "## 2. 要求として残る15件"
MOVED_HEADING = "## 3. 移した10件の確認"
KEPT_ROW = re.compile(
    r"^\|\s*(?P<id>[0-9]{3})\s*\|\s*(?P<name>[^|]+)\|(?P<rest>.+)\|\s*$", re.M
)
MOVED_ROW = re.compile(
    r"^\|\s*(?P<id>[0-9]{3})\s+(?P<name>[^|]+)\|(?P<rest>.+)\|\s*$", re.M
)
DECISION_HEADING = re.compile(r"^###\s+(D[1-6])\s+(.+)$", re.M)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cells(rest):
    return [cell.strip() for cell in rest.split("|")]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    path = root / PACKET
    if not path.exists():
        print(f"missing {PACKET}", file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")

    # Split the document so each table is read with its own shape.
    kept_start = text.index(KEPT_HEADING)
    moved_start = text.index(MOVED_HEADING)
    decisions_start = text.index("## 4. ")
    kept_text = text[kept_start:moved_start]
    moved_text = text[moved_start:decisions_start]

    candidates = []
    for match in KEPT_ROW.finditer(kept_text):
        parts = cells(match.group("rest"))
        if len(parts) < 5:
            continue
        # name, class, owner, evidence, recommendation, judgement
        judgement = parts[-1]
        candidates.append({
            "id": match.group("id"),
            "name": match.group("name").strip(),
            "classification": parts[0],
            "owner": parts[1],
            "evidence": parts[2],
            "recommendation": parts[3],
            "judgement": judgement,
            "judgementIsEmpty": judgement == "",
            "hasRecommendation": bool(parts[3]),
            "hasEvidence": bool(parts[2]),
            "hasOwner": bool(parts[1]),
        })

    moved = []
    for match in MOVED_ROW.finditer(moved_text):
        parts = cells(match.group("rest"))
        if len(parts) < 2:
            continue
        moved.append({
            "id": match.group("id"),
            "name": match.group("name").strip(),
            "movedTo": parts[0],
            "todo": parts[1],
            "hasDestination": bool(parts[0]),
            "hasTodo": bool(parts[1]),
        })

    decisions = []
    for match in DECISION_HEADING.finditer(text):
        start = match.end()
        # The block runs to the next heading at the same or higher level.
        following = re.search(r"^###\s+D[0-9]|^##\s", text[start:], re.M)
        block = text[start:start + following.start()] if following else text[start:]
        has_question = "?" in block or "か" in block.split("\n")[0]
        options = len(re.findall(r"^- ", block, re.M))
        decisions.append({
            "id": match.group(1),
            "title": match.group(2).strip(),
            "statesAQuestion": has_question,
            "optionLines": options,
        })

    filled = [c["id"] for c in candidates if not c["judgementIsEmpty"]]
    movedMissing = [
        row["id"] for row in moved
        if not (row["hasDestination"] and row["hasTodo"])
    ]
    incomplete = [
        c["id"] for c in candidates
        if not (c["hasRecommendation"] and c["hasEvidence"] and c["hasOwner"])
    ]
    ready = (
        not filled
        and not incomplete
        and not movedMissing
        and len(decisions) == 6
        and len(candidates) + len(moved) == 25
    )
    checks = {
        "packet": PACKET,
        "keptCandidates": len(candidates),
        "movedCandidates": len(moved),
        "candidates": len(candidates) + len(moved),
        "movedRows": moved,
        "movedRowsMissingAField": movedMissing,
        "decisions": len(decisions),
        "judgementCellsEmpty": len([c for c in candidates if c["judgementIsEmpty"]]),
        "filledJudgementCells": filled,
        "candidatesMissingADecisionField": incomplete,
        "decisionRows": decisions,
        "everyJudgementCellIsEmpty": not filled,
        "everyCandidateCarriesItsFields": not incomplete,
        "sixDecisionsPresent": len(decisions) == 6,
        "readyForADecision": ready,
        "finding": (
            "G1パケットが判断可能な状態かを点検する。判断はOwnerのものであるため、"
            "**判断欄が空であること**を合格条件にする。各候補に担当・証拠・推奨が揃い、"
            "D1〜D6の6問が存在することを確かめる。"
        ),
    }
    passed = checks["readyForADecision"]

    receipt = {
        "schema": "tai.reference.yic-g1-packet-readiness/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the G1 packet",
        "command": "python integrations/tools/yic_g1_packet_readiness.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-g1-packet-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads the G1 packet and checks that 25 candidates each carry a class, owner, evidence "
            "and recommendation with an empty judgement cell, and that six cross-cutting questions "
            "are present. It checks readiness for a decision, never the decision: an empty cell means "
            "TAI did not decide, not that the candidate is right, and the reading makes no judgement "
            "about whether the evidence is adequate."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidates": len(candidates),
        "decisions": len(decisions),
        "filledCells": filled,
        "incomplete": incomplete,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
