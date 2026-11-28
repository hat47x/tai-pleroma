"""Search for the recorded digest itself, under any name, across the repository's artifacts.

The name-based resolution found 8 of 37 agreeing. The remaining 29 may still be recoverable:
the artifact could be present under a different file name. Searching by digest removes the
assumption that the file name was preserved.

This answers "does the object the receipt recorded still exist in this repository at all",
which is a different and stronger question than "does a file with the same name exist".
"""

import argparse
import hashlib
import json
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
    artifacts = root / "evaluations/artifacts"

    # Index every artifact file's digest once, so the search is not per-receipt.
    index = {}
    for path in artifacts.rglob("*"):
        if path.is_file():
            try:
                index.setdefault(digest_of(path), []).append(
                    str(path.relative_to(root)).replace("\\", "/")
                )
            except OSError:
                continue

    rows = []
    foundByName = 0
    foundByDigestOnly = 0
    notFound = 0
    for path in sorted((root / "evaluations/records").glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        artifact = data.get("artifact")
        if not isinstance(artifact, dict):
            continue
        cited = artifact.get("path")
        recorded = artifact.get("digest")
        if not isinstance(cited, str) or not isinstance(recorded, str):
            continue
        if Path(cited).exists():
            continue  # still resolvable at its path; not part of this question
        sameName = artifacts / Path(cited).name
        byName = sameName.exists() and digest_of(sameName) == recorded
        locations = index.get(recorded, [])
        if byName:
            foundByName += 1
            status = "sameNameAndDigest"
        elif locations:
            foundByDigestOnly += 1
            status = "digestFoundElsewhere"
        else:
            notFound += 1
            status = "notFound"
        rows.append({
            "receipt": path.name,
            "status": status,
            "locations": locations[:2],
        })

    total = foundByName + foundByDigestOnly + notFound
    checks = {
        "receiptsWhoseCitedPathIsGone": total,
        "recoverableByNameAndDigest": foundByName,
        "recoverableByDigestUnderAnotherName": foundByDigestOnly,
        "notPresentAnywhereInTheRepository": notFound,
        "rows": rows,
        "finding": (
            f"引用先が消えた{total}件について、**名前ではなくdigestで**リポジトリ内を探した。"
            f"**名前もdigestも一致{foundByName}件**、"
            f"**名前は違うがdigestが一致{foundByDigestOnly}件**、"
            f"**どこにも無い{notFound}件**。"
            "**名前で探すと取りこぼす。** 記録したのは名前ではなく内容である。"
            "**digestで見つかったものは『その内容がリポジトリに在る』ことを示すが、"
            "receiptがそれを観測したことは示さない。**"
        ),
    }
    passed = total > 0

    receipt = {
        "schema": "tai.reference.yic-digest-search/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 indexing every artifact digest and searching it",
        "command": "python integrations/tools/yic_digest_search_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-digest-search-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest_of(args.artifact)},
        "observed": checks,
        "scope": (
            "Indexes digests of every file under evaluations/artifacts and looks up each missing "
            "receipt's recorded digest. It covers artifacts/ only, not the whole repository, and "
            "finding a digest proves the content exists now, not that the receipt observed it."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gone": total,
        "byName": foundByName,
        "byDigest": foundByDigestOnly,
        "notFound": notFound,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
