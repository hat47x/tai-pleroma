"""Check that every YI document states what it is, in a predictable place.

The workspace rules require distinguishing 要件 / 仮説 / 提案 / 受理済み / 実装済み /
検証済み / NOT RUN. A reader cannot do that if the document never says which it is, or
says it only deep in the body. This checks that each YI document carries a `状態:` line
before its first section heading, and reports the ones that do not.

It checks the presence and position of that line, not its truth: a document can
declare "提案" and still be treated as accepted by its readers.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

FOLDER = "docs/yi-constellation"
STATUS_LINE = re.compile(
    r"^(?:(?:>\s*)?(?:-\s*)?\*\*|)(?:状態|Status)\*{0,2}\s*[:：]",
    re.M | re.I,
)
# `> **Proposed / NOT RUN**` states the same thing without the label.
# Any bold span in the preamble, wherever on the line it begins.
BOLD_STATEMENT = re.compile(r"\*\*(?P<inside>[^*]+)\*\*", re.M)
STATUS_VOCABULARY = (
    "Proposed", "NOT RUN", "提案", "記録", "索引", "草案", "論考",
    "設計判断", "実行票", "実行計画", "計画", "未受理",
    # Positions and scope statements that also say what the document is.
    "位置付け", "仕様", "候補", "現行資格", "追補", "引渡し", "runbook",
)
# A document may name its own kind in a bold heading that starts with one of these.
KIND_WORDS = ("Runbook", "Runbook：", "位置付け")
FIRST_HEADING = re.compile(r"^##\s", re.M)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    folder = root / FOLDER
    if not folder.exists():
        print(f"missing {FOLDER}", file=sys.stderr)
        return 1

    documents = sorted(folder.rglob("*.md"))
    rows = []
    for path in documents:
        text = path.read_text(encoding="utf-8", errors="replace")
        relative = str(path.relative_to(root)).replace("\\", "/")
        heading = FIRST_HEADING.search(text)
        status = STATUS_LINE.search(text)
        # A bold statement in the preamble that carries status vocabulary also counts.
        bold = None
        for match in BOLD_STATEMENT.finditer(text):
            if heading is not None and match.start() > heading.start():
                break
            if any(word in match.group("inside") for word in STATUS_VOCABULARY):
                bold = match
                break
        candidates = [m for m in (status, bold) if m is not None]
        marker = min(candidates, key=lambda m: m.start()) if candidates else None
        early = (
            marker is not None
            and (heading is None or marker.start() < heading.start())
        )
        rows.append({
            "document": relative,
            "hasStatusLine": marker is not None,
            "shape": (
                "labelled" if status is not None
                else "bold-statement" if bold is not None
                else "none"
            ),
            "statusBeforeFirstSection": early,
            "isIndexOrReadme": path.name == "README.md",
        })

    # README files are indexes; they carry no status of their own.
    subject = [row for row in rows if not row["isIndexOrReadme"]]
    missing = [row["document"] for row in subject if not row["hasStatusLine"]]
    late = [
        row["document"] for row in subject
        if row["hasStatusLine"] and not row["statusBeforeFirstSection"]
    ]

    checks = {
        "folder": FOLDER,
        "documents": len(rows),
        "documentsWithAStatusLine": len([r for r in subject if r["hasStatusLine"]]) + len(
            [r for r in rows if r["isIndexOrReadme"]]
        ),
        "nonIndexDocuments": len(subject),
        "documentsWithoutAStatusLine": missing,
        "withoutStatusLineCount": len(missing),
        "statusLineAfterFirstSection": late,
        "shapesUsed": {
            shape: len([r for r in subject if r["shape"] == shape])
            for shape in ("labelled", "bold-statement", "none")
        },
        "everyDocumentStatesWhatItIs": not missing,
        "everyStatusLineOpensTheDocument": not late,
        "finding": (
            "YI文書が、自分が何であるか（提案・記録・受理済み・NOT RUN など）を"
            "最初の節より前に述べているかを点検する。"
            "`状態:`・`**状態：**`・`- **状態**：`・`> **Status:**`の4つの書き方を認める。"
            "索引であるREADMEは対象外とする。"
        ),
    }
    passed = not missing and not late

    receipt = {
        "schema": "tai.reference.yic-status-line-check/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the YI documents",
        "command": "python integrations/tools/yic_status_line_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-status-line-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Checks that every non-index YI document carries a `状態:` line before its first section. "
            "It checks presence and position only: a document can state '提案' and still be read as "
            "accepted, and a status line whose date or wording is wrong is not detected."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "documents": len(rows),
        "withoutStatus": len(missing),
        "late": len(late),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
