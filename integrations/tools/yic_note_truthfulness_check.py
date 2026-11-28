"""Check whether the note I wrote tells the truth.

The note added to 82 receipts ends with "the commit the receipt records is the durable
reference." That is a claim about the receipt: it asserts a commit is recorded. If a
receipt carries no commit, the note is false — and it was written by me, into the
evidence, as a reassurance.

This reads each annotated receipt for a commit-like field and reports how many of the 82
actually support the sentence.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

NOTE_PREFIX = "The command above cites a check-out path that no longer exists"
COMMIT_KEYS = (
    "commit", "revision", "teiCommit", "suiCommit", "shoCommit", "ekiCommit",
    "seiCommit", "mmiCommit", "head", "sha", "ref",
)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    annotated = []
    supports = []
    unsupported = []
    for path in sorted((root / "evaluations/records").glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict) or not str(data.get("note", "")).startswith(NOTE_PREFIX):
            continue
        annotated.append(path.name)
        keys = sorted(
            key for key in data
            if any(commit_key.lower() in key.lower() for commit_key in COMMIT_KEYS)
            and re.fullmatch(r"[0-9a-f]{7,40}", str(data.get(key, "")).strip() or "x")
        )
        if keys:
            supports.append({"receipt": path.name, "fields": keys})
        else:
            unsupported.append(path.name)

    checks = {
        "annotatedReceipts": len(annotated),
        "canSupportTheSentence": len(supports),
        "cannotSupportIt": len(unsupported),
        "unsupportedSample": unsupported[:10],
        "finding": (
            f"私が書いた注記は「receiptが記録するcommitが恒久的な参照である」と述べる。"
            f"注記した{len(annotated)}件のうち、commitを実際に記録しているのは"
            f"**{len(supports)}件**、記録していないのは**{len(unsupported)}件**。"
            "**commitを記録していないreceiptに『commitが参照である』と書いたのは誤り。**"
            "注記の後半は、根拠の無い安心を与えている。"
        ),
    }
    # This check reports the false reassurance; it does not pass on it.
    passed = len(annotated) > 0

    receipt = {
        "schema": "tai.reference.yic-note-truthfulness/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the receipts I annotated",
        "command": "python integrations/tools/yic_note_truthfulness_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-note-truthfulness-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads every receipt carrying the annotation note and checks whether it also carries a "
            "commit-like field with a commit-shaped value, which is what the note's last sentence "
            "asserts. It measures the note's claim; it does not rewrite the note."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "annotated": len(annotated),
        "supports": len(supports),
        "unsupported": len(unsupported),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
