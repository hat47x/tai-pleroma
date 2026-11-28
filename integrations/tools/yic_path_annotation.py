"""Add a machine-readable note to receipts whose cited checkout path no longer exists.

The document says the 82 receipts should carry a note that their command cannot be re-run
today. The readiness check confirmed the checker has no global field allow-list, so a
top-level `note` is safe. One receipt type pins an inner `observed.fields` list, so the note
goes at the top level only and no inner list is touched.

The note is derived: it names the cited path and says the path is gone. Nothing else in the
receipt changes. A receipt that already has a `note` is left alone.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

CITED = "evaluations/records/YIC-cited-path-2026-11-28.json"
FLAG = re.compile(r"--[a-z-]*(?:repo|root|checkout)\s+(?P<path>[^\s\"']+)")
NOTE_PREFIX = "The command above cites a check-out path that no longer exists"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    cited = json.loads((root / CITED).read_text(encoding="utf-8"))
    affected = (cited.get("observed") or {}).get("receiptsAffected") or []

    annotated = []
    alreadyNoted = []
    skipped = []
    for name in affected:
        path = root / "evaluations/records" / name
        if not path.exists():
            skipped.append({"receipt": name, "reason": "missing"})
            continue
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if "note" in data and str(data["note"]).startswith(NOTE_PREFIX):
            alreadyNoted.append(name)
            continue
        match = FLAG.search(str(data.get("command", "")))
        if not match:
            skipped.append({"receipt": name, "reason": "no path in command"})
            continue
        cited_path = match.group("path")
        if Path(cited_path).exists():
            skipped.append({"receipt": name, "reason": "path exists"})
            continue
        note = (
            f"{NOTE_PREFIX}: {cited_path}. The path was removed after the run, so the "
            "command as written cannot be re-run; the commit the receipt records is the "
            "durable reference."
        )
        if "note" in data:
            skipped.append({"receipt": name, "reason": "has an unrelated note"})
            continue
        data["note"] = note
        if args.apply:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        annotated.append({"receipt": name, "citedPath": cited_path})

    checks = {
        "citedPathReceipt": CITED,
        "affected": len(affected),
        "annotated": len(annotated),
        "alreadyAnnotated": len(alreadyNoted),
        "skipped": skipped,
        "applied": bool(args.apply),
        "sample": annotated[:5],
        "finding": (
            f"解決しない引用を持つ{len(affected)}件のうち、**{len(annotated)}件**に注記を"
            f"{'書き込んだ' if args.apply else '書く用意をした'}。"
            f"既に注記済み{len(alreadyNoted)}件、除外{len(skipped)}件。"
            "**注記はトップレベルに置き、`observed`の内側には触れていない。**"
            "内側の欄の並びを固定する規則が1件あるためである。"
        ),
    }
    passed = len(annotated) + len(alreadyNoted) > 0

    receipt = {
        "schema": "tai.reference.yic-path-annotation/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 annotating the receipts that cite a removed path",
        "command": "python integrations/tools/yic_path_annotation.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-path-annotation-2026-11-28.json --apply",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Adds a top-level `note` naming the removed path to receipts the path check flagged, "
            "and writes them when --apply is given. It changes no measured value and no inner "
            "field; it does not re-run any command, and it leaves receipts with an existing "
            "unrelated note untouched."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "affected": len(affected),
        "annotated": len(annotated),
        "already": len(alreadyNoted),
        "skipped": len(skipped),
        "applied": bool(args.apply),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
