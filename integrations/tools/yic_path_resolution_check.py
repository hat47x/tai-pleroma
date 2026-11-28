"""For receipts citing a path that no longer exists, try the same filename in-repo.

The portability measurement found 37 receipts whose cited artifact is gone. For 24 of them
the cited path is absolute into a deleted worktree, and the same filename exists at
`evaluations/artifacts/`. If the recorded digest matches the in-repo file, the citation is
recoverable; if it does not, the two files are different bytes and the old record cannot be
corroborated by the new one.

This measures which case each falls into, and never rewrites a receipt.
"""

import argparse
import hashlib
import json
import os
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
    candidates = root / "evaluations/artifacts"
    rows = []
    matched = 0
    different = 0
    unresolvable = 0
    for path in sorted((root / "evaluations/records").glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        artifact = data.get("artifact")
        if isinstance(artifact, dict):
            cited = artifact.get("path")
            recorded = artifact.get("digest")
        elif isinstance(artifact, str):
            cited = artifact
            recorded = None
        else:
            continue
        if not isinstance(cited, str) or not cited:
            continue
        if Path(cited).exists():
            continue
        # The cited file is gone; look for the same file name inside the repository.
        replacement = candidates / Path(cited).name
        if not replacement.exists():
            unresolvable += 1
            rows.append({
                "receipt": path.name,
                "cited": cited[:70],
                "sameNameInRepo": False,
            })
            continue
        now = digest_of(replacement)
        recordedText = recorded if isinstance(recorded, str) else None
        agrees = bool(recordedText) and recordedText.removeprefix("sha256:") == now.removeprefix("sha256:")
        if agrees:
            matched += 1
        else:
            different += 1
        rows.append({
            "receipt": path.name,
            "cited": cited[:70],
            "sameNameInRepo": True,
            "recordedDigest": (recordedText or "")[:20],
            "inRepoDigest": now[:20],
            "digestAgrees": agrees,
        })

    checks = {
        "receiptsWhoseCitedPathIsGone": matched + different + unresolvable,
        "sameFileNameExistsInRepo": matched + different,
        "digestAgrees": matched,
        "digestDiffers": different,
        "noSameNameFound": unresolvable,
        "rows": rows,
        "finding": (
            f"引用先が消えたreceipt{matched + different + unresolvable}件について、"
            f"**同名ファイルがリポジトリ内に在るか**を調べた。"
            f"在るもの{matched + different}件、無いもの{unresolvable}件。"
            f"そのうち**digestが一致するもの{matched}件**、**一致しないもの{different}件**。"
            "**一致しても『同じ内容の別の複製が在る』ことしか言えない。**"
            "そのreceiptが観測した対象が、この複製だったことは言えない。"
            "**一致しない場合は、複製が違うのか、記録が古いのか、区別できない。**"
        ),
    }
    passed = matched + different + unresolvable > 0

    receipt = {
        "schema": "tai.reference.yic-path-resolution/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 resolving missing artifact paths by file name",
        "command": "python integrations/tools/yic_path_resolution_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-path-resolution-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest_of(args.artifact)},
        "observed": checks,
        "scope": (
            "For receipts whose cited artifact path no longer exists, looks for the same file name "
            "under evaluations/artifacts and compares digests. It measures recoverability by name "
            "only; it does not rewrite any receipt or assert that the in-repo file is the one the "
            "receipt observed."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gone": matched + different + unresolvable,
        "sameName": matched + different,
        "agrees": matched,
        "differs": different,
        "none": unresolvable,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
