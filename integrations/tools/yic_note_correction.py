"""Correct the note I wrote: 65 of the 82 receipts record no commit.

The note's last sentence asserted "the commit the receipt records is the durable
reference". For 65 receipts there is no commit, so that sentence gives reassurance the
evidence does not support. Replace the sentence per receipt: keep it where a commit
exists, and say plainly that no commit is recorded where none is.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

NOTE_PREFIX = "The command above cites a check-out path that no longer exists"
OLD_TAIL = "the commit the receipt records is the durable reference."
NEW_WITH_COMMIT = "the commit the receipt records is the durable reference."
NEW_WITHOUT_COMMIT = (
    "this receipt records no commit, so it carries no durable reference of its own."
)
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
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    kept = []
    corrected = []
    alreadyCorrect = []
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
        if not note.endswith(OLD_TAIL):
            alreadyCorrect.append(path.name)
            continue
        if has_commit(data):
            kept.append(path.name)
            continue
        data["note"] = note[: -len(OLD_TAIL)] + NEW_WITHOUT_COMMIT
        if args.apply:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        corrected.append(path.name)

    checks = {
        "keptBecauseACommitExists": len(kept),
        "correctedBecauseNoCommit": len(corrected),
        "alreadyCorrect": len(alreadyCorrect),
        "applied": bool(args.apply),
        "finding": (
            "私が書いた注記の末尾は「receiptが記録するcommitが恒久的な参照である」と述べていた。"
            f"commitを記録している{len(kept)}件では正しいが、"
            f"記録していない{len(corrected)}件では**根拠の無い安心**を与えていた。"
            "commitが無いreceiptには「このreceiptはcommitを記録していない」と書き換えた。"
            "**根拠の無い一文を、証拠の中に残さない。**"
        ),
    }
    passed = len(kept) + len(corrected) > 0

    receipt = {
        "schema": "tai.reference.yic-note-correction/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 correcting the note I wrote into 82 receipts",
        "command": "python integrations/tools/yic_note_correction.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-note-correction-2026-11-28.json --apply",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Rewrites the closing sentence of the annotation note only, in receipts that record no "
            "commit. It changes no measured value; it does not add a commit, and where a commit "
            "exists the original sentence is kept unchanged."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "kept": len(kept),
        "corrected": len(corrected),
        "already": len(alreadyCorrect),
        "applied": bool(args.apply),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
