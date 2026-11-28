"""Verify the generated docs index lists every top-level document.

The index is generated, but a generated block drifts if the generator is not re-run. This
re-reads the block and checks every `docs/*.md` appears and the declared count is right.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

README = "docs/README.md"
BEGIN = "<!-- doc-index:begin -->"
END = "<!-- doc-index:end -->"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    readme = root / README
    text = readme.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        print("generated block missing", file=sys.stderr) if False else None
        return 1
    block = text[text.index(BEGIN):text.index(END) + len(END)]

    documents = sorted(
        path.name for path in (root / "docs").glob("*.md") if path.name != "README.md"
    )
    listed = [name for name in documents if f"[{name}](" in block]
    missing = [name for name in documents if name not in listed]

    declared = re.search(r"（READMEを除く(\d+)件）", block)
    checks = {
        "readme": README,
        "documentsOnDisk": len(documents),
        "listedInBlock": len(listed),
        "missingFromBlock": missing,
        "declaredCount": int(declared.group(1)) if declared else None,
        "countAgrees": bool(declared) and int(declared.group(1)) == len(documents),
        "finding": (
            f"`docs/` 直下の文書{len(documents)}件のうち、生成索引に載っているもの"
            f"{len(listed)}件、載っていないもの{len(missing)}件。"
            "**索引は生成されるが、生成を実行しない限り腐る。**"
            "ここで毎回突き合わせ、文書を足して再生成を忘れた場合に検出する。"
        ),
    }
    passed = not missing and checks["countAgrees"]

    receipt = {
        "schema": "tai.reference.yic-docs-index-freshness/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 comparing docs/README's generated block with docs/",
        "command": "python integrations/tools/yic_docs_index_freshness.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-docs-index-freshness-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads the generated index block and checks every top-level doc appears and the declared "
            "count matches. It checks completeness and counts only; subdirectories and title accuracy "
            "are not covered."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "documents": len(documents),
        "listed": len(listed),
        "missing": len(missing),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    import sys

    raise SystemExit(main())
