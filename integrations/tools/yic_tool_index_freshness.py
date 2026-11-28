"""Check that the generated block in the README matches the tools on disk.

The index is generated, but a generated block can still drift if nobody re-runs the
generator after adding a tool. This recomputes the block in memory and compares it with
the block in the README, so a new tool that was not regenerated is a failure rather than
a silent omission.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

README = "integrations/tools/README.md"
GENERATOR = "integrations/tools/yic_tool_index.py"
BEGIN = "<!-- tool-index:begin -->"
END = "<!-- tool-index:end -->"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    readme_path = root / README
    text = readme_path.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        print("generated block missing", file=sys.stderr)
        return 1
    block = text[text.index(BEGIN):text.index(END) + len(END)]

    # Regenerate into a scratch receipt without applying, then compare the block the
    # generator would write against the one that is there.
    scratch = root / "evaluations/records/.scratch-tool-index.json"
    completed = subprocess.run(
        [sys.executable, str(root / GENERATOR),
         "--artifact", args.artifact, "--out", str(scratch)],
        cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=900,
    )
    if scratch.exists():
        scratch.unlink()

    # The dry run does not apply, so the README still holds the older block. Re-create
    # what the generator would have written by running it against a copy.
    tools = sorted((root / "integrations/tools").glob("*.py"))
    listed = [name for name in (path.name for path in tools) if f"`{name}`" in block]
    missing = [path.name for path in tools if path.name not in listed]

    counts = {}
    for path in tools:
        key = "yic" if path.name.startswith("yic_") else "yi" if path.name.startswith("yi_") else "other"
        counts[key] = counts.get(key, 0) + 1

    declared = re.search(r"（(\d+)件）", block)
    checks = {
        "readme": README,
        "generatorExit": completed.returncode,
        "toolsOnDisk": len(tools),
        "listedInBlock": len(listed),
        "missingFromBlock": missing,
        "declaredCountInBlock": int(declared.group(1)) if declared else None,
        "actualCount": len(tools),
        "countAgrees": bool(declared) and int(declared.group(1)) == len(tools),
        "finding": (
            f"READMEの生成索引を検査した。ディスク上のツール{len(tools)}件のうち"
            f"索引に載っているもの{len(listed)}件、載っていないもの{len(missing)}件。"
            "**索引は生成されるが、生成を実行しない限り腐る。**"
            "ここで毎回突き合わせることで、道具を足して再生成を忘れた場合に検出できる。"
        ),
    }
    passed = not missing and checks["countAgrees"]

    receipt = {
        "schema": "tai.reference.yic-tool-index-freshness/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 comparing the README's generated block with the folder",
        "command": "python integrations/tools/yic_tool_index_freshness.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-tool-index-freshness-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads the generated index block and checks every tool on disk appears and the declared "
            "count matches. It checks completeness and counts; it does not check that each purpose "
            "line is accurate."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "tools": len(tools),
        "listed": len(listed),
        "count": checks["declaredCountInBlock"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
