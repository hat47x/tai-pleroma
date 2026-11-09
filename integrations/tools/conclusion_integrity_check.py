"""Check that the conclusion's evidence links are live and actually PASS.

The judgement cites receipts and documents. A citation that points at a missing
file, or at a receipt whose result is not PASS, would let the conclusion stand on
nothing. This walks the citations and checks both.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

CONCLUSIONS = (
    "analysis/tei-pilot-conclusion-2026-11-06.md",
    "docs/tei-pilot-status-brief.md",
)
LINK = re.compile(r"\]\(([^)\#]+)(#[^)]*)?\)")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    missing = []
    not_pass = []
    checked = set()
    for relative in CONCLUSIONS:
        source = root / relative
        if not source.exists():
            missing.append(relative)
            continue
        text = source.read_text(encoding="utf-8")
        for match in LINK.finditer(text):
            target = match.group(1)
            if target.startswith("http"):
                continue
            resolved = (source.parent / target).resolve()
            key = str(resolved)
            if key in checked:
                continue
            checked.add(key)
            if not resolved.exists():
                missing.append(f"{relative} -> {target}")
                continue
            if resolved.suffix != ".json":
                continue
            try:
                data = json.loads(resolved.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                not_pass.append(f"{target} (unparsable)")
                continue
            if data.get("result") != "PASS":
                not_pass.append(f"{target} (result={data.get('result')!r})")

    checks = {
        "documentsChecked": list(CONCLUSIONS),
        "linksChecked": len(checked),
        "missing": missing,
        "receiptsNotPass": not_pass,
        "everyCitedLinkExists": not missing,
        "everyCitedReceiptIsPass": not not_pass,
    }
    passed = checks["everyCitedLinkExists"] and checks["everyCitedReceiptIsPass"]
    receipt = {
        "schema": "tai.reference.conclusion-integrity/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the conclusion and its citations",
        "command": "python integrations/tools/conclusion_integrity_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/TEI-conclusion-integrity-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Walks the links in the conclusion and the status brief, and checks that every cited receipt exists and reports PASS. It does not check whether a cited receipt supports the sentence it is attached to, so a live link is not proof that the claim is right.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "links": len(checked),
        "missing": missing,
        "notPass": not_pass,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
