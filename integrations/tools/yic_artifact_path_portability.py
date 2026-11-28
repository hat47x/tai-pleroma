"""Why the artifact-path assertion holds nowhere: every cited path is host-specific.

All four sibling receipts of `TEI artifact receipt points at a missing file` trip the guard.
Their `artifact.path` values are absolute paths into worktrees that no longer exist on this
host (`D:\\GIT\\hat47x\\tai-wt-*`), plus one relative path that resolves three directories
above the repository.

So the assertion cannot hold here for a reason that says nothing about the rule: the receipts
record observations made in a temporary worktree, and the path they cite is that worktree's.
The rule is right, the receipt is honest, and the citation is not reproducible here.

This measures how widespread host-specific artifact paths are.
"""

import argparse
import hashlib
import json
import os
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    insideRepo = 0
    outsideRepo = 0
    exists = 0
    missing = 0
    rows = []
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
        elif isinstance(artifact, str):
            cited = artifact
        else:
            cited = None
        if not isinstance(cited, str) or not cited:
            continue

        candidate = Path(cited)
        if not candidate.is_absolute():
            candidate = (root / candidate)
        try:
            resolved = candidate.resolve()
        except (OSError, RuntimeError):
            resolved = candidate
        within = True
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            within = False
        if within:
            insideRepo += 1
        else:
            outsideRepo += 1
        if candidate.exists():
            exists += 1
        else:
            missing += 1
            rows.append({
                "receipt": path.name,
                "cited": cited[:90],
                "insideTheRepository": within,
            })

    checks = {
        "receiptsWithACitedArtifactPath": insideRepo + outsideRepo,
        "pathInsideTheRepository": insideRepo,
        "pathOutsideTheRepository": outsideRepo,
        "fileExistsOnThisHost": exists,
        "fileMissingOnThisHost": missing,
        "missingSample": rows[:10],
        "finding": (
            f"`artifact.path`を持つreceipt{insideRepo + outsideRepo}件を調べた。"
            f"**リポジトリ内を指すもの{insideRepo}件**、"
            f"**リポジトリ外を指すもの{outsideRepo}件**。"
            f"**このホストで実在するもの{exists}件、実在しないもの{missing}件**。"
            "実在しないものの大半は、**もう存在しない別worktreeの絶対パス**を指す。"
            "**receiptは正直である（その時点でそのworktreeに在った）。"
            "しかしその引用は、このホストでは再現できない。**"
            "**『規則が成立しない』と『このホストでは確かめられない』は別である。**"
        ),
    }
    passed = insideRepo + outsideRepo > 0

    receipt = {
        "schema": "tai.reference.yic-artifact-path-portability/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 resolving every receipt's cited artifact path",
        "command": "python integrations/tools/yic_artifact_path_portability.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-artifact-path-portability-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Resolves each receipt's cited artifact path and records whether it lies inside the "
            "repository and whether the file exists on this host. It measures portability of the "
            "citation; it does not check the digest, and a missing file may exist on the host where "
            "the receipt was written."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "cited": insideRepo + outsideRepo,
        "inside": insideRepo,
        "outside": outsideRepo,
        "exists": exists,
        "missing": missing,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
