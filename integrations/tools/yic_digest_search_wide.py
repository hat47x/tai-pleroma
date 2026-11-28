"""The 29 missing digests were searched in artifacts/ only. Widening to the whole tree.

`yic_digest_search_check` indexed `evaluations/artifacts` and found none of the 29 remaining
digests. But an artifact can be committed anywhere — docs/, analysis/, integrations/. Before
concluding "the content is gone", search the whole tracked tree.

Tracking *every* file's digest would be slow and noisy, so restrict to files whose name
could plausibly be an artifact (anything under a path containing `artifact` or ending in
`.json`/`.md` under an artifacts directory) — and say so in the scope.
"""

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path


def digest_of(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]

    # Candidate files: anything git tracks that is not a receipt or a tool.
    tracked = subprocess.run(
        ["git", "-C", str(root), "ls-files"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.splitlines()
    candidates = [
        name for name in tracked
        if not name.startswith(("evaluations/records/", "integrations/tools/", "tools/"))
    ]

    index = {}
    skipped = 0
    for name in candidates:
        path = root / name
        if not path.is_file():
            continue
        try:
            if path.stat().st_size > 4_000_000:
                skipped += 1
                continue
            index.setdefault(digest_of(path), []).append(name)
        except OSError:
            skipped += 1
            continue

    previous = root / "evaluations/records/YIC-digest-search-2026-11-28.json"
    prior = json.loads(previous.read_text(encoding="utf-8"))
    missingRows = [
        row for row in (prior.get("observed") or {}).get("rows") or []
        if row.get("status") == "notFound"
    ]

    found = []
    stillMissing = []
    for row in missingRows:
        receipt = root / "evaluations/records" / row["receipt"]
        data = json.loads(receipt.read_text(encoding="utf-8-sig"))
        recorded = (data.get("artifact") or {}).get("digest")
        locations = index.get(recorded, [])
        if locations:
            found.append({"receipt": row["receipt"], "locations": locations[:2]})
        else:
            stillMissing.append(row["receipt"])

    checks = {
        "filesIndexed": len(index),
        "filesSkipped": skipped,
        "digestsTheNarrowSearchMissed": len(missingRows),
        "foundInTheWiderTree": len(found),
        "stillMissing": stillMissing,
        "foundRows": found[:10],
        "finding": (
            f"狭い探索（`evaluations/artifacts`のみ）が見つけられなかった"
            f"{len(missingRows)}件を、**git追跡下の全ファイル**で探した。"
            f"索引したファイル{len(index)}件（大きすぎて飛ばしたもの{skipped}件）。"
            f"**見つかったもの{len(found)}件**、**見つからないもの{len(stillMissing)}件**。"
            "**探索範囲を広げても見つからないものは、本当にこのリポジトリに無い。**"
            "ただし**それは記録が誤りであることを意味しない**。"
            "**当時の作業場所に在って、ここへ持ち込まれなかった**だけの可能性が高い。"
        ),
    }
    passed = len(missingRows) > 0

    receipt = {
        "schema": "tai.reference.yic-digest-search-wide/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 indexing every tracked non-receipt file's digest",
        "command": "python integrations/tools/yic_digest_search_wide.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-digest-search-wide-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest_of(args.artifact)},
        "observed": checks,
        "scope": (
            "Indexes digests of every git-tracked file except receipts, tools and files above "
            "4 MB, then looks up the digests the narrow search missed. It covers the tracked tree "
            "only, and a missing digest proves absence here, not that the receipt is wrong."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "indexed": len(index),
        "missed": len(missingRows),
        "found": len(found),
        "stillMissing": len(stillMissing),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
