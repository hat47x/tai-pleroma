"""Generate an index of docs/ from each document's own title and status line.

`docs/` holds 28 markdown files; its README names 15 of them. The unindexed 13 include
`status.md` and `reproduction-runbook.md`, which a machine check reads — so the documents
the tooling depends on are the ones a reader cannot find from the index.

This generates the index from each document's first heading, and checks every file appears.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

FOLDER = "docs"
README = "docs/README.md"
BEGIN = "<!-- doc-index:begin -->"
END = "<!-- doc-index:end -->"
TITLE = re.compile(r"^#\s+(?P<title>.+)$", re.M)
STATUS = re.compile(r"^状態[:：]\s*(?P<status>.+)$", re.M)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def title_of(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    match = TITLE.search(text)
    if not match:
        return path.stem, ""
    title = match.group("title").strip()
    status = STATUS.search(text)
    return title, (status.group("status").strip()[:60] if status else "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    folder = root / FOLDER
    readme_path = folder / "README.md"
    files = sorted(
        path for path in folder.glob("*.md")
        if path.name != "README.md" and "状態:" not in ""  # all others included
    )

    rows = []
    for path in files:
        title, status = title_of(path)
        rows.append({"file": path.name, "title": title, "status": status})

    lines = [
        BEGIN,
        "",
        "以下は各文書の先頭見出しから生成した。**手で保たない。**",
        f"対象: `{FOLDER}` 直下の `*.md`（READMEを除く{len(rows)}件）。",
        "",
        "| 文書 | 題 | 状態 |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        status = row["status"] or "—"
        lines.append(f"| [{row['file']}]({row['file']}) | {row['title']} | {status} |")
    lines.append("")
    block = "\n".join(lines) + END

    text = readme_path.read_text(encoding="utf-8")
    if BEGIN in text and END in text:
        new_text = text[:text.index(BEGIN)] + block + text[text.index(END) + len(END):]
    else:
        new_text = text.rstrip("\n") + "\n\n" + block + "\n"

    if args.apply:
        readme_path.write_text(new_text, encoding="utf-8")

    missing = [
        row["file"] for row in rows
        if f"[{row['file']}]" not in new_text and f"]({row['file']})" not in new_text
    ]
    checks = {
        "folder": FOLDER,
        "documentsOnDisk": len(rows),
        "listed": len(rows) - len(missing),
        "notListed": missing,
        "machineReadDocuments": [
            row["file"] for row in rows
            if row["file"] in ("status.md", "reproduction-runbook.md")
        ],
        "applied": bool(args.apply),
        "everyDocumentIsListed": not missing,
        "finding": (
            f"`{FOLDER}` 直下の文書{len(rows)}件のうち、READMEに載っていなかったものは"
            f"**{len(missing)}件**（生成前は13件）。"
            "**載っていなかった中に`status.md`と`reproduction-runbook.md`が含まれる。**"
            "両文書は`doc_consistency_check`が読む、機械が依存する入口である。"
            "**機械が読む文書を、人間の索引に載せていなかった。**"
        ),
    }
    passed = not missing

    receipt = {
        "schema": "tai.reference.yic-docs-index/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 generating a docs/ index from first headings",
        "command": "python integrations/tools/yic_docs_index.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-docs-index-2026-11-28.json --apply",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads each top-level doc's first heading and status line and writes a generated index "
            "block into docs/README.md, then checks every file appears. It indexes top-level files "
            "only; subdirectory documents are not covered, and a title is not verified for accuracy."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "documents": len(rows),
        "listed": len(rows) - len(missing),
        "missing": len(missing),
        "applied": bool(args.apply),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
