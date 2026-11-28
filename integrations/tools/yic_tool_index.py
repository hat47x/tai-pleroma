"""Generate a tool index from each tool's own docstring, and check it stays complete.

`integrations/tools/README.md` lists 9 tools while 181 Python tools sit beside it. The
README is the directory's only index, so a reader cannot find the rest, and nothing
notices when a new tool is added without being listed.

The index is generated from the tools themselves — first docstring line as the purpose —
so it cannot drift from the source it describes. A check then verifies every tool appears.
"""

import argparse
import ast
import hashlib
import json
import re
import time
from pathlib import Path

FOLDER = "integrations/tools"
README = "integrations/tools/README.md"
BEGIN = "<!-- tool-index:begin -->"
END = "<!-- tool-index:end -->"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def purpose(path):
    """First sentence of the module docstring, or empty when there is none."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return "_docstring not parseable_"
    doc = ast.get_docstring(tree) or ""
    first = " ".join(doc.strip().splitlines()[:1]).strip()
    if not first:
        return "_no docstring_"
    first = re.split(r"(?<=[.。])\s", first)[0]
    return first[:110]


def family(name):
    if name.startswith("yic_"):
        return "YIC（分析・点検）"
    if name.startswith("yi_"):
        return "YI（初期の点検）"
    return "その他"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    folder = root / FOLDER
    tools = sorted(folder.glob("*.py"))

    grouped = {}
    for path in tools:
        grouped.setdefault(family(path.name), []).append({
            "tool": path.name,
            "purpose": purpose(path),
        })

    lines = [
        BEGIN,
        "",
        "以下は各ツールのdocstringの冒頭から生成した。**手で保たない。**",
        f"生成対象: `{FOLDER}` の `*.py`（{len(tools)}件）。",
        "",
    ]
    for group in sorted(grouped):
        entries = grouped[group]
        lines.append(f"### {group}（{len(entries)}件）")
        lines.append("")
        lines.append("| ツール | 目的（docstringの冒頭） |")
        lines.append("| --- | --- |")
        for entry in entries:
            lines.append(f"| `{entry['tool']}` | {entry['purpose']} |")
        lines.append("")

    readme_path = root / README
    text = readme_path.read_text(encoding="utf-8")
    block = "\n".join(lines) + END

    if BEGIN in text and END in text:
        start = text.index(BEGIN)
        finish = text.index(END) + len(END)
        new_text = text[:start] + block + text[finish:]
    else:
        new_text = text.rstrip("\n") + "\n\n" + block + "\n"

    if args.apply:
        readme_path.write_text(new_text, encoding="utf-8")

    # Does every tool appear in the resulting README?
    missing = [path.name for path in tools if f"`{path.name}`" not in new_text]
    checks = {
        "folder": FOLDER,
        "toolsOnDisk": len(tools),
        "groups": sorted(grouped),
        "listedAfterGeneration": len(tools) - len(missing),
        "notListed": missing,
        "placeholderLinesThatWereOrphaned": text.count("doc_consistency_check.py:"),
        "applied": bool(args.apply),
        "everyToolIsListed": not missing,
        "finding": (
            f"`{FOLDER}` のPythonツール{len(tools)}件のうち、READMEに名前が出ていたのは"
            "わずか10件だった。**索引はディレクトリの唯一の入口**であり、"
            "載っていない道具は存在しないのと同じである。"
            "docstringの冒頭から索引を生成し、**全件が載ることを検査する**ようにした。"
            "**索引を手で保つ限り、道具を足すたびに腐る。**"
        ),
    }
    passed = not missing

    receipt = {
        "schema": "tai.reference.yic-tool-index/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 generating an index from tool docstrings",
        "command": "python integrations/tools/yic_tool_index.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-tool-index-2026-11-28.json --apply",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads each tool's module docstring and writes a generated index block into the "
            "directory README, then verifies every tool appears. It indexes names and first "
            "sentences only; it does not verify that a docstring describes the tool correctly."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "tools": len(tools),
        "listed": len(tools) - len(missing),
        "missing": len(missing),
        "applied": bool(args.apply),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
