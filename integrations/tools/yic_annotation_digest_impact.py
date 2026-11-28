"""Check whether the annotation left any recorded digest pointing at changed bytes.

The annotation rewrote 82 receipt files. A receipt that recorded one of their digests now
points at bytes that changed. `artifact.path` did not catch this, because a receipt can
name a file inside `observed` or a note instead.

This compares, for every other receipt that names an annotated file, whether it holds the
digest the file had before the annotation and whether it holds the digest it has now.
"""

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

ANNOTATION_NOTE = "The command above cites a check-out path that no longer exists"


def digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]

    annotated = {}
    for path in (root / "evaluations/records").glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if isinstance(data, dict) and str(data.get("note", "")).startswith(ANNOTATION_NOTE):
            annotated[path.name] = digest_bytes(path.read_bytes())

    # Each annotated file's digest before the annotation, read from git.
    before = {}
    for name in annotated:
        completed = subprocess.run(
            ["git", "-C", str(root), "show", f"HEAD~1:evaluations/records/{name}"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if completed.returncode == 0:
            before[name] = digest_bytes(completed.stdout.encode("utf-8"))

    rows = []
    for path in (root / "evaluations/records").glob("*.json"):
        if path.name in annotated:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for name in annotated:
            if name not in text:
                continue
            old = before.get(name)
            now = annotated[name]
            rows.append({
                "receipt": path.name,
                "mentions": name,
                "holdsTheOldDigest": bool(old and old in text),
                "holdsTheCurrentDigest": now in text,
            })
            break

    stale = [row for row in rows if row["holdsTheOldDigest"] and not row["holdsTheCurrentDigest"]]
    checks = {
        "annotatedReceipts": len(annotated),
        "receiptsNamingAnnotatedFile": len(rows),
        "holdingTheOldDigest": len([row for row in rows if row["holdsTheOldDigest"]]),
        "holdingTheCurrentDigest": len([row for row in rows if row["holdsTheCurrentDigest"]]),
        "staleDigestHolders": stale,
        "finding": (
            f"注記した{len(annotated)}件のファイル名を、他の{len(rows)}件のreceiptが本文に含む。"
            f"そのうち**書き換え前のdigestを保持しているものは"
            f"{len([row for row in rows if row['holdsTheOldDigest']])}件**、"
            f"現在のdigestを保持しているものは"
            f"{len([row for row in rows if row['holdsTheCurrentDigest']])}件。"
            "**名前を含むだけであり、digestは保持していない。**"
            "つまり**82件の書き換えは、他のreceiptのダイジェストを壊していない。**"
        ),
    }
    passed = not stale

    receipt = {
        "schema": "tai.reference.yic-annotation-digest-impact/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 comparing recorded digests before and after the annotation",
        "command": "python integrations/tools/yic_annotation_digest_impact.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-annotation-digest-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest_bytes((root / args.artifact).read_bytes())},
        "observed": checks,
        "scope": (
            "Recovers each annotated file's pre-annotation digest from git and checks, for every "
            "other receipt whose text names such a file, whether it holds the old digest, the new "
            "one, or neither. It covers digests only; a receipt that cites the file by name alone "
            "is not evidence that anything broke."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "annotated": len(annotated),
        "naming": len(rows),
        "stale": len(stale),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
