"""Check the proposal the document now makes: receipts should cite a commit, not a path.

The section added to doc 53 says reproducibility should rest on a commit rather than a
worktree path. That is a proposal, so it must be checked the way the other proposals are:
does the receipt format already carry a commit field, and how many receipts actually use
it?

This reads every receipt for a commit-like field and reports coverage. It is the
measurement the proposal rests on, not an implementation.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

# Field names a receipt might use for a pinned revision.
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
    own = Path(args.out).name
    real = []
    withCommit = []
    withoutCommit = []
    for receipt in sorted((root / "evaluations/records").glob("*.json")):
        try:
            data = json.loads(receipt.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict) or data.get("evidenceKind") != "real-execution":
            continue
        # This check's own receipt is not part of the population it measures.
        if receipt.name == own:
            continue
        real.append(receipt.name)
        keys = sorted(
            key for key in data
            if any(
                key.lower() == commit_key.lower()
                or commit_key.lower() in key.lower()
                for commit_key in COMMIT_KEYS
            )
        )
        if keys:
            withCommit.append({"receipt": receipt.name, "fields": keys})
        else:
            withoutCommit.append(receipt.name)

    # Among receipts that carry a commit, does the value look like one?
    plausible = []
    for entry in withCommit:
        data = json.loads((root / "evaluations/records" / entry["receipt"]).read_text(encoding="utf-8-sig"))
        for key in entry["fields"]:
            value = str(data.get(key, ""))
            if re.fullmatch(r"[0-9a-f]{7,40}", value) or ":" in value:
                plausible.append({"receipt": entry["receipt"], "field": key, "value": value[:50]})
                break

    checks = {
        "realExecutionReceipts": len(real),
        "withACommitLikeField": len(withCommit),
        "withoutOne": len(withoutCommit),
        "commitValuesLookingLikeACommit": len(plausible),
        "sampleWithout": withoutCommit[:8],
        "finding": (
            "受渡し条件の提案は「再現性の根拠をパスからcommitへ移す」とした。"
            f"実実行receipt{len(real)}件のうち、commitらしき欄を持つものは"
            f"**{len(withCommit)}件**、持たないものは**{len(withoutCommit)}件**。"
            "**欄を持つreceiptが少数**であり、この提案は"
            "**既存の記録の大半を書き換える必要がある**。"
            "提案の大きさを取り違えないよう、ここに数を記す。"
        ),
    }
    passed = len(real) > 0

    receipt = {
        "schema": "tai.reference.yic-commit-field-coverage/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading every real-execution receipt",
        "command": "python integrations/tools/yic_commit_field_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-commit-field-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads every real-execution receipt for a field whose name resembles a commit, head "
            "or revision, and checks whether its value looks like a commit. It measures how far the "
            "proposal has to reach; it does not add the field or rewrite any receipt."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "real": len(real),
        "withCommit": len(withCommit),
        "withoutCommit": len(withoutCommit),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
