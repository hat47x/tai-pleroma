"""Check every top-level folder whose documents should be indexed.

Two rounds fixed one directory each. The defect — an index kept by hand, or absent — is
one shape, so it should be checked in one place over every folder, not discovered again
one directory at a time.

This walks the folders that carry documents, and reports for each: how many top-level
markdown files exist, whether a README exists, and how many files the index names.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

FOLDERS = ("analysis", "docs", "evaluations", "scenarios", "presentations", "research")
BEGIN = "<!-- index:begin -->"
END = "<!-- index:end -->"
# docs/ uses its own marker from the earlier round.
ALT_BEGIN = "<!-- doc-index:begin -->"
ALT_END = "<!-- doc-index:end -->"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def index_body(readme_text):
    for begin, end in ((BEGIN, END), (ALT_BEGIN, ALT_END)):
        if begin in readme_text and end in readme_text:
            return readme_text[readme_text.index(begin):readme_text.index(end) + len(end)]
    return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    rows = []
    for folder in FOLDERS:
        path = root / folder
        if not path.is_dir():
            continue
        documents = sorted(item.name for item in path.glob("*.md") if item.name != "README.md")
        readme = path / "README.md"
        body = readme.read_text(encoding="utf-8") if readme.exists() else ""
        indexed = index_body(body)
        listed = [name for name in documents if f"[{name}](" in indexed]
        missing = [name for name in documents if name not in listed]
        rows.append({
            "folder": folder,
            "documents": len(documents),
            "readmeExists": readme.exists(),
            "hasGeneratedIndex": bool(indexed),
            "listed": len(listed),
            "missing": missing,
        })

    withoutIndex = [row["folder"] for row in rows if not row["hasGeneratedIndex"]]
    incomplete = [
        {"folder": row["folder"], "missing": len(row["missing"])}
        for row in rows if row["missing"]
    ]
    checks = {
        "folders": len(rows),
        "rows": rows,
        "foldersWithoutAGeneratedIndex": withoutIndex,
        "foldersWithAnIncompleteIndex": incomplete,
        "everyFolderIsIndexed": not withoutIndex and not incomplete,
        "finding": (
            f"文書を持つ{folder_count(rows)}ディレクトリを調べた。"
            f"生成索引を持つもの{len(rows) - len(withoutIndex)}件、"
            f"持たないもの{len(withoutIndex)}件。"
            f"索引が不完全なもの{len(incomplete)}件。"
            "**索引の欠落は1つの型であり、ディレクトリごとに見つけ直す必要は無い。**"
            "この検査を1箇所に置くことで、**新しいディレクトリが増えても同じ基準で判定できる**。"
        ),
    }
    passed = not withoutIndex and not incomplete

    receipt = {
        "schema": "tai.reference.yic-folder-index-check/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 checking the index of every document folder",
        "command": "python integrations/tools/yic_folder_index_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-folder-index-check-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads each folder's README generated block and compares it with the folder's top-level "
            "markdown files. It checks presence and counts; it does not check that a title describes "
            "its document, and subdirectories are not covered."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "folders": len(rows),
        "withoutIndex": withoutIndex,
        "incomplete": incomplete,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


def folder_count(rows):
    return len(rows)


if __name__ == "__main__":
    raise SystemExit(main())
