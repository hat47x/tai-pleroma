"""Check whether receipts cite a checkout path that still exists.

Eleven receipts record a `--tei-repo` path under a worktree that is not on disk any more.
A receipt is supposed to let a reader re-run the command it records. If the path it names
is gone, the command cannot be re-run, and the receipt's reproducibility is weaker than
its `command` field suggests.

This reads every receipt, extracts checkout paths from its `command`, and reports which
are missing. It reports; it does not fail, because a missing worktree may be expected for
a historical receipt.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

# `--xxx-repo <path>` and `--xxx-root <path>` are the forms the pilots use.
FLAG = re.compile(r"--[a-z-]*(?:repo|root|checkout)\s+(?P<path>[^\s\"']+)")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    rows = []
    for receipt in sorted((root / "evaluations/records").glob("*.json")):
        try:
            data = json.loads(receipt.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        command = str(data.get("command", ""))
        if not command:
            continue
        for match in FLAG.finditer(command):
            cited = match.group("path")
            # Only judge paths that look local and absolute.
            if not re.match(r"^[A-Za-z]:[\\/]", cited):
                continue
            rows.append({
                "receipt": receipt.name,
                "flag": match.group(0).split()[0],
                "citedPath": cited,
                "exists": Path(cited).exists(),
            })

    missing = [row for row in rows if not row["exists"]]
    byPath = {}
    for row in missing:
        byPath.setdefault(row["citedPath"], []).append(row["receipt"])

    checks = {
        "receiptsWithAPathFlag": len({row["receipt"] for row in rows}),
        "pathsChecked": len(rows),
        "missingPaths": [
            {"path": path, "citedBy": len(names), "receipts": names[:5]}
            for path, names in byPath.items()
        ],
        "missingCount": len(missing),
        "receiptsAffected": sorted({row["receipt"] for row in missing}),
        "finding": (
            "receiptの`command`に書かれたローカルのcheckoutパスが"
            "**現在も存在するか**を確かめた。"
            f"検査した{len(rows)}件のうち**{len(missing)}件**が、"
            "既に存在しないパスを指している。"
            "**receiptは再実行できる形で書かれているとは限らない。**"
            "パスが消えていれば、commandを写しても再現できない。"
        ),
    }
    # Reporting only: a historical receipt may legitimately name a worktree that was
    # cleaned up. The finding is the list, not a failure.
    passed = len(rows) > 0

    receipt = {
        "schema": "tai.reference.yic-cited-path-exists/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading every receipt's command",
        "command": "python integrations/tools/yic_cited_path_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-cited-path-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads each receipt's `command` string, extracts local absolute paths passed to "
            "repo/root/checkout flags, and tests whether each still exists. It reports paths that "
            "are gone; it does not attempt to re-run any command, and a missing worktree may be an "
            "expected consequence of cleanup rather than a defect."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "paths": len(rows),
        "missing": len(missing),
        "distinctMissing": len(byPath),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
