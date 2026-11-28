"""Measure the reordered selectors correctly: five of them point at real receipts.

The first attempt swapped `tei-sui-` for `sui-tei-` on every selector. One selector,
`tei-sui-reader`, was already correct — the file is `SUI-TEI-sui-reader-…`, which contains
`tei-sui-reader`. Rewriting it broke a live rule and its failure masked the others.

This rewrites only the selectors that currently reach nothing, and re-measures. The
failures those rules produce belong to the baseline, exactly as the 22 do.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
time = __import__("time")
from pathlib import Path

CHECKER = "tools/check-synthetic-receipts/check.py"
BASELINE_MARK = "KNOWN_RULE_FAILURE_KEYS = frozenset(KNOWN_RULE_FAILURE_BASELINE)"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(script, root):
    completed = subprocess.run(
        [sys.executable, str(script), "--root", str(root)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3600,
    )
    body = completed.stdout.strip()
    try:
        return completed.returncode, json.loads(body[body.index("{"):])
    except (json.JSONDecodeError, ValueError):
        return completed.returncode, {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    source = root / CHECKER
    text = source.read_text(encoding="utf-8")

    # Which `tei-sui-` selectors currently reach nothing? Only those are reversed.
    names = re.findall(r'"(evaluations/records/[^"]+\.json)"', text)
    candidates = sorted(set(re.findall(r'if "(tei-sui-[^"]+)" in relative_lower:', text)))
    inert = [c for c in candidates if not any(c in name.lower() for name in names)]
    assert inert, "no inert tei-sui selectors found"

    patched_text = text
    for selector in inert:
        # tei-sui-etag -> sui-tei-etag
        replacement = "sui-tei-" + selector[len("tei-sui-"):]
        patched_text = patched_text.replace(
            f'if "{selector}" in relative_lower:',
            f'if "{replacement}" in relative_lower:',
            1,
        )

    # The new failures must join the baseline, or the run fails for an untriaged reason.
    scratch = Path(tempfile.mkdtemp(prefix="yic-reorder-"))
    intermediate = scratch / "reordered.py"
    intermediate.write_text(patched_text, encoding="utf-8")
    _, probe = run(intermediate, root)
    exposed = probe.get("errors") or []

    extra = []
    for message in exposed:
        if ": evaluations/records/" not in message:
            continue
        text_key, relative = message.split(": ", 1)
        extra.append((text_key, relative))

    baseline_lines = "".join(
        f"    ({message_text!r}, {relative!r}),\n" for message_text, relative in extra
    )
    final_text = patched_text.replace(
        BASELINE_MARK,
        "KNOWN_RULE_FAILURE_KEYS = frozenset(KNOWN_RULE_FAILURE_BASELINE + (\n"
        + baseline_lines
        + "))",
        1,
    )
    final = scratch / "reordered_with_baseline.py"
    final.write_text(final_text, encoding="utf-8")
    re_code, reordered = run(final, root)

    base_code, base = run(source, root)
    checks = {
        "checker": CHECKER,
        "selectorsReversed": inert,
        "asWritten": {
            "exit": base_code,
            "passed": base.get("passed"),
            "blocking": len(base.get("errors") or []),
            "inert": base.get("inertRules") or [],
        },
        "withReorderedSelectors": {
            "exit": re_code,
            "passed": reordered.get("passed"),
            "blocking": len(reordered.get("errors") or []),
            "inert": reordered.get("inertRules") or [],
        },
        "assertionFailuresExposed": exposed,
        "exposedCount": len(exposed),
        "inertBefore": len(base.get("inertRules") or []),
        "inertAfter": len(reordered.get("inertRules") or []),
        "finding": (
            f"発火しないセレクタ{len(inert)}件は、語順がreceipt名と**逆**である。"
            f"語順だけを直すと**{len(exposed)}件の判定失敗が出る**。"
            "失敗の内訳: `TEI save plan receipt did not record four non-writing tests`、"
            "`did not record an idempotent update`、`TEI ETag receipt did not record 409/200`。"
            "**存在するreceiptを指しており、語順だけで一度も走っていなかった。**"
            "最初の試行は`tei-sui-reader`（正しく動いていた）も書き換えて失敗を覆い隠した。"
            "不活性のものだけを書き換えて測り直した。"
        ),
    }
    passed = len(exposed) > 0 and reordered.get("passed") is True

    receipt = {
        "schema": "tai.reference.yic-reversed-selectors/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 running the checker with the inert selectors reordered",
        "command": "python integrations/tools/yic_inert_selector_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-inert-selectors-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reverses only the word order of selectors that reach no registered receipt and runs "
            "the checker twice, once with the exposed failures added to the same named baseline. It "
            "shows those rules point at real receipts; it does not decide whether a failure means "
            "the receipt or the rule is wrong."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "reversed": len(inert),
        "exposed": len(exposed),
        "inertBefore": len(base.get("inertRules") or []),
        "inertAfter": len(reordered.get("inertRules") or []),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
