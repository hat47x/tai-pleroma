"""Extend the citation check: does the current writing habit still cite a worktree path?

The date split said all 82 unresolvable citations predate the cutoff. The stronger
question is whether receipts written *today* still cite a path form that will not resolve
later — if they do, the fix belongs in the generator, not only in history.

`--tei-repo <path>` is a worktree path. A generator that records a commit instead would not
produce this shape. This counts, among the most recent receipts, how many still pass a
local absolute checkout path.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

FLAG = re.compile(r"--[a-z-]*(?:repo|root|checkout)\s+(?P<path>[^\s\"']+)")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--since", default="2026-11-28")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    recent = []
    citingLocalPath = []
    for receipt in sorted((root / "evaluations/records").glob("*.json")):
        if receipt.name == Path(args.out).name:
            continue
        try:
            data = json.loads(receipt.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict) or str(data.get("date", "")) < args.since:
            continue
        recent.append(receipt.name)
        for match in FLAG.finditer(str(data.get("command", ""))):
            cited = match.group("path")
            if re.match(r"^[A-Za-z]:[\\/]", cited):
                citingLocalPath.append({
                    "receipt": receipt.name,
                    "flag": match.group(0).split()[0],
                    "exists": Path(cited).exists(),
                })
                break

    unresolvableNow = [row for row in citingLocalPath if not row["exists"]]
    checks = {
        "since": args.since,
        "recentReceipts": len(recent),
        "recentCitingALocalPath": len(citingLocalPath),
        "ofThoseAlreadyMissing": len(unresolvableNow),
        "rows": citingLocalPath[:12],
        "finding": (
            f"{args.since}以降のreceipt{len(recent)}件のうち、"
            f"**{len(citingLocalPath)}件**がローカルのcheckoutパスをcommandに書いている。"
            f"そのうち**{len(unresolvableNow)}件**は現時点で既に存在しない。"
            + (
                "**現在も同じ書き方が続いている。** 履歴への注記だけでは再発する。"
                if citingLocalPath
                else "**現在は書かれていない。** 書き方は既に変わっており、履歴の注記で足りる。"
            )
        ),
    }
    passed = len(recent) > 0

    receipt = {
        "schema": "tai.reference.yic-current-citation-form/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the most recent receipts",
        "command": "python integrations/tools/yic_citation_form_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-citation-form-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Counts recent receipts whose command still cites a local absolute checkout path, and "
            "whether each path exists now. It shows whether the habit persists; it does not change "
            "any receipt, and a single date cutoff cannot prove when the habit started."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "recent": len(recent),
        "citing": len(citingLocalPath),
        "missing": len(unresolvableNow),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
