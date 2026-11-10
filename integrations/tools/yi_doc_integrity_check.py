"""Check the YI Constellation document set for index and link integrity.

The set has 48 analysis files with dense cross-references. A file that is not in
the README index, or a relative link whose target is gone, makes a reader's
route break silently. This walks all of them and reports.
"""

import argparse
import hashlib
import json
import os
import re
import time
from pathlib import Path

LINK = re.compile(r"\]\(([^)\s]+)\)")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    base = root / "docs/yi-constellation"
    readme = (base / "README.md").read_text(encoding="utf-8")
    analysis = sorted((base / "analysis").glob("*.md"))

    not_indexed = []
    broken = []
    links = 0
    for path in analysis:
        stem = path.stem
        if path.name not in readme:
            not_indexed.append(path.name)
        text = path.read_text(encoding="utf-8")
        for match in LINK.finditer(text):
            target = match.group(1).split("#", 1)[0]
            if not target or target.startswith(("http", "mailto:")):
                continue
            links += 1
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                broken.append(f"{path.name} -> {target}")

    # The README's own links.
    readme_broken = []
    for match in LINK.finditer(readme):
        target = match.group(1).split("#", 1)[0]
        if not target or target.startswith(("http", "mailto:")):
            continue
        links += 1
        resolved = (base / target).resolve()
        if not resolved.exists():
            readme_broken.append(f"README.md -> {target}")

    # Candidate identifiers must agree between the requirement list and G1.
    candidates = (base / "analysis/05-要件候補.md").read_text(encoding="utf-8")
    packet = (base / "analysis/18-G1レビューパケット.md").read_text(encoding="utf-8")
    listed = set(re.findall(r"RQ-YI-0\d\d", candidates))
    # The packet covers candidates in two tables: the 15 kept as requirements
    # (``| 001 |``) and the 10 moved to existing requirements (``| 003 輔相…``).
    packet_ids = set(re.findall(r"\|\s*(0\d\d)\b", packet))
    packet_rq = {f"RQ-YI-{n}" for n in packet_ids}
    missing_from_packet = sorted(listed - packet_rq)
    unknown_in_packet = sorted(packet_rq - listed)

    checks = {
        "analysisFiles": len(analysis),
        "links": links,
        "notIndexedInReadme": not_indexed,
        "brokenLinks": broken,
        "brokenReadmeLinks": readme_broken,
        "candidatesInList": len(listed),
        "candidatesInPacket": len(packet_rq),
        "missingFromPacket": missing_from_packet,
        "unknownInPacket": unknown_in_packet,
        "everyFileIsIndexed": not not_indexed,
        "everyLinkResolves": not broken and not readme_broken,
        "candidateSetsAgree": not missing_from_packet and not unknown_in_packet,
    }
    passed = (
        checks["everyFileIsIndexed"]
        and checks["everyLinkResolves"]
        and checks["candidateSetsAgree"]
    )
    receipt = {
        "schema": "tai.reference.yi-doc-integrity/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading docs/yi-constellation",
        "command": "python integrations/tools/yi_doc_integrity_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-doc-integrity-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Reads every analysis file under docs/yi-constellation and checks that each is named in the README index, that every relative link resolves, and that the requirement IDs in the candidate list and the G1 packet agree. It does not check whether the prose is right, whether a reading holds, or whether an Owner accepted a candidate.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "files": len(analysis),
        "links": links,
        "notIndexed": not_indexed,
        "broken": broken + readme_broken,
        "missingFromPacket": missing_from_packet,
        "unknownInPacket": unknown_in_packet,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
