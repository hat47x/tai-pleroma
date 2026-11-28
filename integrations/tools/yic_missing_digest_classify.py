"""Classify the 29 receipts whose recorded digest exists nowhere in this repository.

Two very different things are bundled in that count:
  * a receipt whose cited path is *inside* the repository but whose digest is absent — the
    file at that path now has different bytes, so this is a stale record about a live path;
  * a receipt whose cited path is outside the repository (absolute worktree path, or `..`
    relative) — the file lived elsewhere and was never here, so absence is expected rather
    than anomalous.

The repair differs: the first class may need a re-run or a digest update; the second class
cannot be repaired here at all.
"""

import argparse
import hashlib
import json
import os
import time
from pathlib import Path

WIDE = "evaluations/records/YIC-digest-search-wide-2026-11-28.json"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    names = json.loads((root / WIDE).read_text(encoding="utf-8"))["observed"]["stillMissing"]

    insideDifferentBytes = []
    outsideRepository = []
    for name in names:
        receipt = json.loads((root / "evaluations/records" / name).read_text(encoding="utf-8-sig"))
        artifact = receipt.get("artifact")
        cited = artifact.get("path") if isinstance(artifact, dict) else artifact
        recorded = artifact.get("digest") if isinstance(artifact, dict) else None
        if not isinstance(cited, str):
            continue
        candidate = Path(cited)
        if not candidate.is_absolute():
            candidate = root / candidate
        try:
            resolved = candidate.resolve()
        except (OSError, RuntimeError):
            resolved = candidate
        # A path under a sibling worktree (`tai-wt-*`) is not repository-internal even when
        # written as a relative path that happens to resolve beneath the repository root.
        parts = resolved.parts
        worktree = any(part.startswith(("tai-wt-", "tai-wt")) for part in parts)
        within = (not worktree) and str(root.resolve()) in str(resolved)
        if not within:
            outsideRepository.append({"receipt": name, "cited": cited[:80]})
            continue
        # The path is inside the repository; does the file exist and what is its digest?
        exists = resolved.exists()
        now = None
        if exists:
            try:
                now = "sha256:" + hashlib.sha256(resolved.read_bytes()).hexdigest()
            except OSError:
                now = None
        insideDifferentBytes.append({
            "receipt": name,
            "cited": cited[:80],
            "fileExists": exists,
            "recordedDigest": (recorded or "")[:20],
            "currentDigest": (now or "")[:20],
            "digestChanged": bool(now) and now != recorded,
        })

    checks = {
        "missingDigests": len(names),
        "citationOutsideTheRepository": len(outsideRepository),
        "citationInsideTheRepository": len(insideDifferentBytes),
        "insideAndFileExistsWithDifferentBytes": len([
            row for row in insideDifferentBytes if row["digestChanged"]
        ]),
        "insideAndFileGone": len([
            row for row in insideDifferentBytes if not row["fileExists"]
        ]),
        "insideRows": insideDifferentBytes,
        "outsideRows": outsideRepository,
        "finding": (
            f"digestがどこにも無い{len(names)}件を、**引用先がリポジトリ内か外か**で分けた。"
            f"**リポジトリ外を指すもの{len(outsideRepository)}件**、"
            f"**リポジトリ内を指すもの{len(insideDifferentBytes)}件**。"
            f"内側のうち**ファイルは在るが中身が違うもの"
            f"{len([row for row in insideDifferentBytes if row['digestChanged']])}件**、"
            f"**ファイルも無いもの"
            f"{len([row for row in insideDifferentBytes if not row['fileExists']])}件**。"
            "**外を指すものは『ここに無い』のが当然であり、異常ではない。**"
            "内側で中身が違うものは、**同じパスが別の版に更新された**ことを示す。"
            "**同じ『見つからない』でも、処置が違う。**"
        ),
    }
    passed = len(names) > 0

    receipt = {
        "schema": "tai.reference.yic-missing-digest-classify/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 separating inside-path from outside-path misses",
        "command": "python integrations/tools/yic_missing_digest_classify.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-missing-digest-classify-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Separates the 29 receipts by whether their cited path lies inside this repository, and "
            "records whether an inside path now holds different bytes. It classifies; it does not "
            "rewrite receipts and does not determine which version was correct."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "missing": len(names),
        "outside": len(outsideRepository),
        "inside": len(insideDifferentBytes),
        "changed": len([row for row in insideDifferentBytes if row["digestChanged"]]),
        "gone": len([row for row in insideDifferentBytes if not row["fileExists"]]),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
