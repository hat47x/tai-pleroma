"""Check that the README index lists every YI document and links it correctly.

The YI README is the entry point: 53 files are checked by yi_doc_integrity_check for
being indexed, but that checker works on the analysis folder. This one checks the
whole YI tree — that every .md file under docs/yi-constellation is reachable from the
README, directly or through the decks index, and that the link it uses resolves.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

FOLDER = "docs/yi-constellation"
README = "docs/yi-constellation/README.md"
LINK = re.compile(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    folder = root / FOLDER
    readme = root / README
    if not readme.exists():
        print(f"missing {README}", file=sys.stderr)
        return 1

    documents = [
        path for path in sorted(folder.rglob("*.md"))
        if path.resolve() != readme.resolve()
    ]
    readme_text = readme.read_text(encoding="utf-8")
    readme_links = set()
    broken = []
    for match in LINK.finditer(readme_text):
        target = match.group(1)
        if target.startswith(("http:", "https:", "mailto:")):
            continue
        resolved = (readme.parent / target).resolve()
        if not resolved.exists():
            broken.append(target)
        try:
            readme_links.add(resolved)
        except OSError:
            continue

    # A document can also be reached through a linked index (decks/README.md).
    reachable = set(readme_links)
    for linked in list(readme_links):
        if linked.suffix == ".md" and linked.exists():
            for match in LINK.finditer(linked.read_text(encoding="utf-8", errors="replace")):
                target = match.group(1)
                if target.startswith(("http:", "https:", "mailto:")):
                    continue
                candidate = (linked.parent / target).resolve()
                if candidate.exists():
                    reachable.add(candidate)

    unindexed = [
        str(path.relative_to(root)).replace("\\", "/")
        for path in documents
        if path.resolve() not in reachable
    ]

    checks = {
        "folder": FOLDER,
        "documents": len(documents),
        "readmeLinks": len(readme_links),
        "brokenReadmeLinks": broken,
        "unindexedDocuments": unindexed,
        "unindexedCount": len(unindexed),
        "everyDocumentIsReachableFromTheReadme": not unindexed,
        "everyReadmeLinkResolves": not broken,
        "finding": (
            "YI READMEから、配下の全Markdown文書へ到達できるかを点検する。"
            "索引を経由した到達も認める。リンク先が実在することも確かめる。"
        ),
    }
    passed = not unindexed and not broken

    receipt = {
        "schema": "tai.reference.yic-readme-coverage/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the YI README and its links",
        "command": "python integrations/tools/yic_readme_coverage_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-readme-coverage-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Walks every .md under docs/yi-constellation and checks it is reachable from the README "
            "directly or through one linked index, and that README links resolve. It checks reach "
            "ability only: a document reached through a stale link that still resolves is not "
            "detected, and non-.md files are not indexed by this check."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "documents": len(documents),
        "unindexed": len(unindexed),
        "broken": broken,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
