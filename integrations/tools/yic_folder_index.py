"""Generate a directory index for any top-level folder, from each document's heading.

Two directories have the same defect the last two rounds fixed in `tools/` and `docs/`:

  * `analysis/` holds twelve documents and has no README at all.
  * `evaluations/` holds twenty-one top-level documents and its README names eight.

The defect has one shape — an index that is maintained by hand, or not at all — so the
repair has one shape too: generate the index from each document's own heading, and check
that every document appears.

This tool takes the folder as an argument so the same code serves every directory, and a
second check walks all of them.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

BEGIN = "<!-- index:begin -->"
END = "<!-- index:end -->"
TITLE = re.compile(r"^#\s+(?P<title>.+)$", re.M)
STATUS = re.compile(r"^状態[:：]\s*(?P<status>.+)$", re.M)
FOLDERS = ("analysis", "docs", "evaluations", "scenarios", "presentations", "research")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def title_of(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    match = TITLE.search(text)
    title = match.group("title").strip() if match else path.stem
    status = STATUS.search(text)
    return title, (status.group("status").strip()[:60] if status else "")


def build(root, folder):
    path = root / folder
    documents = sorted(
        item for item in path.glob("*.md") if item.name != "README.md"
    )
    rows = []
    for item in documents:
        title, status = title_of(item)
        rows.append({"file": item.name, "title": title, "status": status})

    lines = [
        BEGIN,
        "",
        f"以下は`{folder}/`直下の各文書の先頭見出しから生成した。**手で保たない。**",
        f"対象: `*.md`（READMEを除く{len(rows)}件）。",
        "",
        "| 文書 | 題 | 状態 |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| [{row['file']}]({row['file']}) | {row['title']} | {row['status'] or '—'} |")
    lines.append("")
    return rows, "\n".join(lines) + END


def apply(root, folder, block, created):
    readme = root / folder / "README.md"
    if not readme.exists():
        readme.write_text(
            f"# {folder}\n\nこのディレクトリの文書の索引。\n\n{block}\n", encoding="utf-8"
        )
        return True
    text = readme.read_text(encoding="utf-8")
    if BEGIN in text and END in text:
        new_text = text[:text.index(BEGIN)] + block + text[text.index(END) + len(END):]
    else:
        new_text = text.rstrip("\n") + "\n\n" + block + "\n"
    readme.write_text(new_text, encoding="utf-8")
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--folder", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    folder_path = root / args.folder
    if not folder_path.is_dir():
        print(f"not a directory: {args.folder}", file=__import__("sys").stderr)
        return 1

    rows, block = build(root, args.folder)
    readme_existed = (folder_path / "README.md").exists()
    created = apply(root, args.folder, block, not readme_existed) if args.apply else False

    readme = folder_path / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    missing = [row["file"] for row in rows if f"[{row['file']}](" not in text]

    checks = {
        "folder": args.folder,
        "documentsOnDisk": len(rows),
        "readmeExisted": readme_existed,
        "readmeCreated": created,
        "listed": len(rows) - len(missing),
        "missingFromIndex": missing,
        "applied": bool(args.apply),
        "everyDocumentIsListed": not missing,
        "finding": (
            f"`{args.folder}/`直下の文書{len(rows)}件の索引を、各文書の先頭見出しから生成した。"
            f"READMEは{'既存を更新' if readme_existed else '無かったので作成'}し、"
            f"掲載{len(rows) - len(missing)}件・欠落{len(missing)}件。"
            "**索引を手で保つ限り腐る**ので、生成と検査の両方を置く。"
        ),
    }
    passed = not missing

    receipt = {
        "schema": "tai.reference.yic-folder-index/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 generating a folder index from document headings",
        "command": f"python integrations/tools/yic_folder_index.py --folder {args.folder} --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-folder-index-2026-11-28.json --apply",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Generates a table of a folder's top-level markdown documents from their first heading "
            "and status line, and writes it into that folder's README. It indexes names and first "
            "headings; it does not verify the headings describe the documents, and nested "
            "subdirectories are not covered."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "folder": args.folder,
        "documents": len(rows),
        "listed": len(rows) - len(missing),
        "created": created,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
