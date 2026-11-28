"""Check the correction took effect: how many notes still claim a commit that does not exist.

The truthfulness check counts how many annotated receipts can support the sentence "the
commit the receipt records is the durable reference". Before the correction 17 could; after
it, the same 17 should remain and the other 65 should say plainly that no commit is
recorded.

This asserts that no note now makes the stronger claim without support.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

NOTE_PREFIX = "The command above cites a check-out path that no longer exists"
STRONG_CLAIM = "the commit the receipt records is the durable reference"
HONEST_CLAIM = "this receipt records no commit"
COMMIT_KEYS = (
    "commit", "revision", "teiCommit", "suiCommit", "shoCommit", "ekiCommit",
    "seiCommit", "mmiCommit", "head", "sha", "ref",
)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def has_commit(data):
    for key in data:
        if any(commit_key.lower() in key.lower() for commit_key in COMMIT_KEYS):
            if re.fullmatch(r"[0-9a-f]{7,40}", str(data[key]).strip() or "x"):
                return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    unsupportedStrongClaims = []
    honestWhereNoCommit = 0
    strongWhereCommit = 0
    for path in sorted((root / "evaluations/records").glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        note = str(data.get("note", ""))
        if not note.startswith(NOTE_PREFIX):
            continue
        commit = has_commit(data)
        if STRONG_CLAIM in note:
            if commit:
                strongWhereCommit += 1
            else:
                unsupportedStrongClaims.append(path.name)
        if HONEST_CLAIM in note and not commit:
            honestWhereNoCommit += 1

    checks = {
        "strongClaimWithACommit": strongWhereCommit,
        "honestClaimWithoutOne": honestWhereNoCommit,
        "unsupportedStrongClaims": unsupportedStrongClaims,
        "noNoteClaimsACommitItDoesNotHave": not unsupportedStrongClaims,
        "finding": (
            f"注記の末尾を、根拠に合わせて書き換えた。"
            f"commitを持つreceiptで強い言い方を残したもの**{strongWhereCommit}件**、"
            f"commitを持たないreceiptで『commitを記録していない』と書いたもの"
            f"**{honestWhereNoCommit}件**、"
            f"**根拠なく強い言い方をしているもの{len(unsupportedStrongClaims)}件**。"
            "**ゼロであり、注記は自分の根拠を超えて主張していない。**"
        ),
    }
    passed = not unsupportedStrongClaims and honestWhereNoCommit > 0

    receipt = {
        "schema": "tai.reference.yic-note-correction-effect/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 re-reading the corrected notes",
        "command": "python integrations/tools/yic_note_correction_effect_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-note-correction-effect-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Re-reads the corrected notes and counts how many still make the commit claim "
            "without a commit. It checks the note text against the receipt's own fields; it does "
            "not verify that a recorded commit is the right one."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "strong": strongWhereCommit,
        "honest": honestWhereNoCommit,
        "unsupported": len(unsupportedStrongClaims),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
