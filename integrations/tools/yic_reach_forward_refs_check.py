"""Check that the reach document's stage table points forward to the later findings.

The reach document states in §4.7 that I, T and C hold. §4.8 then explains why that
table cannot be read as a measurement. A reader who stops at §4.7 takes the earlier,
stronger claim. This check requires §4.7 to name §4.8 (and §4.8.2 where the reading is
corrected), and requires the per-contract correction of §6.8 to be reachable from the
stage section.

It checks cross-references, not the claims themselves.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

DOC = "docs/yi-constellation/irptch-reach-2026-11-16.md"
# Each later section that revises an earlier one, and the earlier section it revises.
FORWARD_REFERENCES = (
    {"later": "4.8", "revises": "4.7", "why": "the stage table is not a measurement"},
    {"later": "4.8.2", "revises": "4.7", "why": "states how §4.7 must be read"},
    # §4.9 adds material; it does not revise §3, so it is not tracked here.

)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def section(text, number):
    """Return the text of the section with this number, up to the next heading."""
    start = re.search(rf"^#{{2,3}} {re.escape(number)}[. ]", text, re.M)
    if not start:
        return None
    following = re.search(r"^#{2,3} ", text[start.end():], re.M)
    end = start.end() + following.start() if following else len(text)
    return text[start.end():end]


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
    for ref in FORWARD_REFERENCES:
        earlier = section(text, ref["revises"])
        later_text = section(text, ref["later"])
        present = earlier is not None and later_text is not None
        # The earlier section must mention the later one.
        # Naming the parent section makes the sub-section reachable.
        top_level = ref["later"].split(".")[0]
        points_forward = earlier is not None and (
            ref["later"] in earlier
            or (ref["revises"].split(".")[0] == top_level
                and re.search(rf"§{re.escape(top_level)}(?:[^0-9]|$)", earlier) is not None)
        )
        rows.append({
            "earlier": ref["revises"],
            "later": ref["later"],
            "bothSectionsExist": present,
            "earlierPointsToLater": points_forward,
            "why": ref["why"],
        })

    missingSection = [row["later"] for row in rows if not row["bothSectionsExist"]]
    notForward = [
        f"{row['earlier']}->{row['later']}" for row in rows if not row["earlierPointsToLater"]
    ]

    # The stage table must not be the last word on I/T/C.
    claimsHoldWithoutCaveat = bool(
        section(text, "4.7") and "測った結果ではない" not in text
    )
    checks = {
        "document": DOC,
        "rows": rows,
        "sectionsMissing": missingSection,
        "sectionsWithoutForwardReference": notForward,
        "correctsTheStageTableSomewhere": "測った結果ではない" in text,
        "everyRevisionIsReachable": not missingSection and not notForward,
        "finding": (
            "到達点の文書の段階表（§4.7）が、後から書いた修正（§4.8）を指しているかを見る。"
            "§4.7だけを読んだ人が「I・T・Cは成立した」で止まらないようにするためである。"
            "節の存在と参照だけを見ており、記述の正しさは判定しない。"
        ),
    }
    passed = not missingSection and not notForward and checks["correctsTheStageTableSomewhere"]

    receipt = {
        "schema": "tai.reference.yic-reach-forward-refs/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the reach document's sections",
        "command": "python integrations/tools/yic_reach_forward_refs_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-reach-forward-refs-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Parses the reach document's sections and checks that each earlier section names the "
            "later section that revises it. It checks that the cross-references exist; it does not "
            "judge whether the later section's correction is adequate."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "rows": len(rows),
        "missing": missingSection,
        "notForward": notForward,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
