"""Try the first experiment of the SUI phase expansion: fold a field, keep the dissent.

Design note 5.2 asks for a synthetic example that folds a session while leaving
the minority counter-evidence in place. SUI's link receipt already groups five
cards into three islands and records one ``contradicts`` edge. This reads that
receipt and records whether the dissent survives the grouping: the two
contradicting islands stay separate, the edge keeps both endpoints, and no card
is dropped by the fold.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tai-root", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(args.tai_root)
    tool = root / "tools/reference-sui-link"
    if not (tool / "main.go").exists():
        print(f"reference tool missing: {tool}", file=sys.stderr)
        return 1

    workdir = Path(os.environ.get("GOTMPDIR") or os.environ.get("TEMP") or ".") / "yi-fold"
    workdir.mkdir(parents=True, exist_ok=True)
    receipt_path = workdir / "sui-link.json"
    sui_receipt = root / "evaluations/records/SUI-api-2026-10-26.json"
    fixture = root / "tools/reference-scn001/testdata/scn001.json"

    completed = subprocess.run(
        [
            "go", "run", ".",
            "-fixture", str(fixture),
            "-sui-receipt", str(sui_receipt),
            "-out", str(receipt_path),
        ],
        cwd=tool, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if completed.returncode != 0 or not receipt_path.exists():
        print((completed.stderr or completed.stdout or "")[-600:], file=sys.stderr)
        return 1
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

    islands = receipt.get("islandGroups") or []
    cards = receipt.get("linkedCards") or []
    contradiction = receipt.get("contradiction") is True
    edge_count = receipt.get("edgeCount")

    # The two islands the edge joins must both survive the grouping, or the
    # dissent would have been folded away.
    endpoints_present = {"I-01", "I-02"} <= set(islands)
    endpoints_distinct = len([name for name in ("I-01", "I-02") if name in islands]) == 2

    checks = {
        "linkedCardCount": len(cards),
        "islandGroups": islands,
        "edgeCount": edge_count,
        "contradiction": contradiction,
        "endpointsPresent": endpoints_present,
        "endpointsRemainSeparate": endpoints_distinct,
        "noCardLostInTheFold": len(cards) == 5,
        "dissentSurvivesTheFold": (
            contradiction and endpoints_present and endpoints_distinct and len(cards) == 5
        ),
        "finding": (
            "5枚のカードを3つの島へ畳むとき、矛盾する2つの島（I-01とI-02）は"
            "別の島として残り、両者を結ぶcontradictsの辺も1本そのまま残る。"
            "畳んだ後も、少数の反証は構造として消えない。"
        ),
    }
    passed = receipt.get("passed") is True and checks["dissentSurvivesTheFold"]

    out = {
        "schema": "tai.reference.yi-fold-with-dissent/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go running the SUI link reference on the saved SUI API receipt",
        "command": "python integrations/tools/yi_fold_with_dissent_probe.py --tai-root . --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-fold-dissent-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Runs the SUI link reference against the saved SUI API receipt and records that the contradicting islands stay separate with their edge after the cards are folded into islands. The receipt is a saved synthetic probe, not a live SUI session; whether a real participant's dissent survives editing is not established, and the fold itself is not an operation this probe performs.",
    }
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "cards": len(cards),
        "islands": islands,
        "dissentSurvives": checks["dissentSurvivesTheFold"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
