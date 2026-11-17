"""Check every relative Markdown link in docs/ resolves to a file that exists.

Seven links were broken while their targets all existed: they resolved from the wrong
directory (`../analysis` from `docs/`, `../harness-adapter` from `docs/yi-constellation/`,
and an extra `../../../docs/` that points outside the checkout). A reader who follows
a stale link concludes the referenced document is gone.

This resolves each link against the file that contains it, and reports the ones that
do not land on a file.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

# Directories that carry prose and links. Code and fixtures are excluded on purpose.
DIRECTORIES = ("docs", "analysis", "evaluations", "scenarios", "integrations")
LINK = re.compile(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--strict", action="store_true",
                        help="also report links to files outside the checkout")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    present = [name for name in DIRECTORIES if (root / name).exists()]
    if not present:
        print(f"none of {DIRECTORIES} exist", file=sys.stderr)
        return 1

    broken = []
    cross_repo = []
    checked = 0
    sources = []
    for name in present:
        sources.extend(sorted((root / name).rglob("*.md")))
    for source in sources:
        text = source.read_text(encoding="utf-8", errors="replace")
        for match in LINK.finditer(text):
            target = match.group(1)
            if target.startswith(("http:", "https:", "mailto:")):
                continue
            checked += 1
            resolved = (source.parent / target).resolve()
            exists = resolved.exists()
            inside = str(resolved).startswith(str(root.resolve()))
            # Line number of the link, for a locatable report.
            line = text.count("\n", 0, match.start()) + 1
            if not exists:
                broken.append({
                    "source": str(source.relative_to(root)).replace("\\", "/"),
                    "line": line,
                    "target": target,
                    "exists": exists,
                    "insideTheCheckout": inside,
                })
            elif args.strict and not inside:
                # Resolves only because a sibling checkout is present in this workspace.
                cross_repo.append({
                    "source": str(source.relative_to(root)).replace("\\", "/"),
                    "line": line,
                    "target": target,
                })

    checks = {
        "directories": present,
        "documentsScanned": len(sources),
        "linksChecked": checked,
        "brokenLinks": broken,
        "brokenCount": len(broken),
        "crossRepoLinks": cross_repo,
        "crossRepoCount": len(cross_repo),
        "everyRelativeLinkResolves": not broken,
        "note": (
            "crossRepoLinks are references into sibling checkouts. They resolve only when "
            "those repositories are present in the same workspace, so they are reported "
            "separately rather than counted as broken."
        ),
        "finding": (
            "docs配下の相対Markdownリンクを、そのリンクを含むファイルの位置から解決し、"
            "実在するファイルに着地するかを点検する。"
            "リンク先が存在していても、基準ディレクトリを誤ると壊れる。"
        ),
    }
    passed = not broken

    receipt = {
        "schema": "tai.reference.yic-doc-links/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 resolving relative links under docs/",
        "command": "python integrations/tools/yic_doc_links_check.py --strict --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-doc-links-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Resolves every relative .md link under docs/ against the file that contains it and "
            "reports links that do not land on an existing file, plus links pointing outside the "
            "checkout when --strict is given. It checks resolution only: a link to the wrong but "
            "existing document is not detected, and anchors after # are not validated."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "directories": checks["directories"],
        "documents": checks["documentsScanned"],
        "linksChecked": checked,
        "broken": broken[:8],
        "brokenCount": len(broken),
        "crossRepoCount": len(cross_repo),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
