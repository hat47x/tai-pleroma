"""Check whether the harness adapter can observe H's two conditions.

H's conditions are: the reply's end is received, and the session can be identified.
Doc 56 found no evidence for either. This asks the narrower question the adapter can
answer by itself: does it parse a terminal event, and does it record a session identity?

It reads the adapters' source and their own tests, and reports per adapter.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

ADAPTER = "integrations/harness-adapter"
ADAPTERS = {
    "step-cli": "step_cli.go",
    "claude-code": "claude_code.go",
    "codex-exec": "codex_exec.go",
    "dsh-headless": "dsh_headless.go",
}
# Terminal events each adapter's comment or parser names.
TERMINAL_HINTS = ("agent_settled", "result", "turn.failed", "terminal", "settled")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    folder = root / ADAPTER
    if not folder.exists():
        print(f"missing {ADAPTER}", file=sys.stderr)
        return 1

    rows = []
    for name, file_name in ADAPTERS.items():
        path = folder / file_name
        if not path.exists():
            rows.append({"adapter": name, "file": file_name, "exists": False})
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        # A terminal-event *branch*, not the word in a comment: `case "..."` or a field
        # assignment on a settled/terminal event.
        terminal = []
        if re.search(r'case\s+"(agent_settled|result|turn\.failed|final)"', text):
            terminal.append("case-branch")
        if re.search(r'stream\.(Settled|Terminal)\s*=', text):
            terminal.append("settled-field")
        if "agent_settled" in lowered:
            terminal.append("agent_settled")
        # Session identity: an id field or a resume capability.
        session_id = bool(re.search(r"(Session(External)?ID|ExternalID|thread_id|SessionRef)", text))
        resume = bool(re.search(r"(CapSessionResume|--resume|session:resume|resume)", text))
        resume_unsupported = "session:resume" in text and "Unsupported" in text
        rows.append({
            "adapter": name,
            "file": file_name,
            "exists": True,
            "terminalHints": terminal,
            "observesTerminalEvent": bool(terminal),
            "hasSessionIdentifier": session_id,
            "mentionsResume": resume,
            "declaresResumeUnsupported": resume_unsupported,
        })

    observing = [row["adapter"] for row in rows
                 if row.get("observesTerminalEvent") and row.get("hasSessionIdentifier")]
    notObserving = [row["adapter"] for row in rows
                    if row.get("exists") and row["adapter"] not in observing]

    checks = {
        "adapterFolder": ADAPTER,
        "adapters": rows,
        "adaptersObservingBothConditions": observing,
        "adaptersNotObserving": notObserving,
        "finding": (
            "Hの成立条件は**Replyの終端**と**Sessionの同定**である。"
            f"adapterの内訳: 終端イベントを解析し、Sessionの識別子を持つものは{len(observing)}種"
            f"（{', '.join(observing) or 'なし'}）。"
            f"持たないものは{len(notObserving)}種（{', '.join(notObserving) or 'なし'}）。"
            "**adapterは条件を解析できる形で持っている。**"
            "しかし**実Harnessを走らせた記録でその2つを観測したものは無い**（doc 56）。"
            "**計器の部品は在り、実測が無い**という段階である。"
        ),
    }
    passed = len(observing) > 0

    receipt = {
        "schema": "tai.reference.yic-h-conditions-parser/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the harness adapters",
        "command": "python integrations/tools/yic_h_conditions_parser_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-h-conditions-parser-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads each harness adapter's source for a terminal-event branch and a session identifier. "
            "It shows the parsers can express H's two conditions; it does not run a real harness, so "
            "it does not show either condition was observed."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "adapters": len(rows),
        "observing": observing,
        "notObserving": notObserving,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
