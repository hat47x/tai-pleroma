"""Check that every candidate states what Acceptance would need to weigh.

Doc 05 lists 25 candidates, and the G1 packet asks an Owner to accept or decline
each. A candidate that lacks its non-goal or its test proposal cannot be judged:
"it sounds worthwhile" is not a decision basis. This reads each candidate's
section and records which of its required fields are present.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

# The fields each candidate section carries, per doc 05's own shape.
FIELDS = {
    "requirement": "要求",
    "reason": "理由",
    "conditions": "成立条件",
    "nonGoals": "非目標",
    "testProposal": "検証の",
    "owner": "担当",
}
SECTION = re.compile(r"^### (RQ-YI-0\d\d) (.+)$", re.M)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    source = root / "docs/yi-constellation/analysis/05-要件候補.md"
    text = source.read_text(encoding="utf-8")

    matches = list(SECTION.finditer(text))
    candidates = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.start():end]
        present = {key: (label in body) for key, label in FIELDS.items()}
        candidates.append({
            "id": match.group(1),
            "name": match.group(2).strip(),
            "fields": present,
            "complete": all(present.values()),
        })

    incomplete = [item for item in candidates if not item["complete"]]
    missingByField = {
        key: [item["id"] for item in candidates if not item["fields"][key]]
        for key in FIELDS
    }

    checks = {
        "source": "docs/yi-constellation/analysis/05-要件候補.md",
        "candidates": len(candidates),
        "complete": len(candidates) - len(incomplete),
        "incomplete": [item["id"] for item in incomplete],
        "missingByField": {key: value for key, value in missingByField.items() if value},
        "everyCandidateStatesItsFields": not incomplete,
    }
    passed = not incomplete and len(candidates) == 25

    receipt = {
        "schema": "tai.reference.yi-candidate-fields/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading doc 05",
        "command": "python integrations/tools/yi_candidate_fields_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-candidate-fields-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Reads each candidate section in doc 05 and records whether it states a requirement, a reason, conditions, non-goals, a test proposal and an owner. It matches labels, not meaning: a section that carries the label but states something unusable passes here, and it does not judge whether a candidate is worth accepting.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidates": len(candidates),
        "incomplete": checks["incomplete"],
        "missing": checks["missingByField"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
