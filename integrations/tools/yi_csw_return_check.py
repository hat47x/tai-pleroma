"""Check that what the YI analysis says it returned to CSW is still there.

Doc 12 records nine edits to CSW's text. If a later CSW change removed one, the
record would claim a return that no longer exists. This resolves each recorded
edit against CSW's current files and reports which sections are present.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

CSW = Path("D:/GIT/hat47x/cultural-substrate-weaving")
REFS = CSW / "skills/cultural-substrate-weaving/references"
SKILL = CSW / "skills/cultural-substrate-weaving/SKILL.md"

# Each edit doc 12 records, with the file and the heading or phrase that proves it.
EDITS = (
    {
        "n": 1,
        "file": REFS / "writing-techniques.md",
        "proves": "## 易 — 六爻の変爻を、局面の転換として読む",
        "what": "変爻を局面の転換として読む節",
    },
    {
        "n": 2,
        "file": REFS / "framework-selection.md",
        "proves": "変爻",
        "what": "易の行への追記",
    },
    {
        "n": 3,
        "file": SKILL,
        "proves": "変爻",
        "what": "技法の一覧への追加",
    },
    {
        "n": 4,
        "file": REFS / "writing-techniques.md",
        "proves": "## 価値の交差：製品やサービスの価値を、第二の体系で読み直す",
        "what": "価値の交差の節",
    },
    {
        "n": 5,
        "file": REFS / "writing-techniques.md",
        "proves": "## 価値の生剋：五つの働きで、価値の巡りと毒を読む",
        "what": "価値の生剋の節",
    },
    {
        "n": 6,
        "file": REFS / "writing-techniques.md",
        "proves": "## 経験の味わい：状況、表れ、移ろいから、製品の経験を読む",
        "what": "経験の味わいの節",
    },
    {
        "n": 7,
        "file": REFS / "writing-techniques.md",
        "proves": "## 場と身体の価値：五大で、製品の場所を読む",
        "what": "場と身体の価値の節",
    },
    {
        "n": 8,
        "file": REFS / "writing-techniques.md",
        "proves": "## 読みを、一日の物語へ織る",
        "what": "一日の物語へ織る節",
    },
    {
        "n": 9,
        "file": REFS / "writing-techniques.md",
        "proves": "一枚紙",
        "what": "一枚紙の形",
    },
)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    results = []
    for edit in EDITS:
        path = edit["file"]
        present = path.exists() and edit["proves"] in path.read_text(encoding="utf-8")
        results.append({
            "edit": edit["n"],
            "what": edit["what"],
            "file": str(path.relative_to(CSW)),
            "stillPresent": present,
        })

    missing = [item for item in results if not item["stillPresent"]]
    checks = {
        "editsRecorded": len(results),
        "results": results,
        "missing": missing,
        "everyReturnedEditIsStillPresent": not missing,
    }
    passed = not missing

    receipt = {
        "schema": "tai.reference.yi-csw-return-check/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the CSW checkout",
        "command": "python integrations/tools/yi_csw_return_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-csw-return-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Reads the nine edits doc 12 records and checks that each heading or phrase is still present in CSW's current files. It checks presence only: it does not read the prose, does not check whether the technique is any good, and does not run CSW's own review.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "edits": len(results),
        "missing": [item["edit"] for item in missing],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
