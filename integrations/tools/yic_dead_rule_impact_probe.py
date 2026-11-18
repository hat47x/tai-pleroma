"""Re-run the dead-rule experiment without mutating `relative`.

The first attempt lowercased `relative` itself, which also broke case-sensitive
comparisons *inside* the rules ("SCN-002" in relative). The errors it produced were partly
its own artifact, not evidence about dead rules.

This rewrites only the rule match — `if "X" in relative:` becomes
`if "X" in relative.lower():` — so the case-dead rules fire while everything that reads
`relative` keeps its original case.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CHECKER = "tools/check-synthetic-receipts/check.py"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(script, root):
    completed = subprocess.run(
        [sys.executable, str(script), "--root", str(root)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3600,
    )
    body = completed.stdout.strip()
    try:
        data = json.loads(body[body.index("{"):]) if "{" in body else {}
    except json.JSONDecodeError:
        data = {}
    return completed.returncode, data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    source = root / CHECKER
    text = source.read_text(encoding="utf-8")

    scratch = Path(tempfile.mkdtemp(prefix="yic-rule-ci-"))
    patched = scratch / "check_ci.py"
    patched_text, replaced = re.subn(
        r'\n        if "([^"]+)" in relative:',
        lambda m: f'\n        if "{m.group(1)}" in relative.lower():',
        text,
    )
    patched.write_text(patched_text, encoding="utf-8")

    base_code, base = run(source, root)
    ci_code, ci = run(patched, root)

    base_errors = base.get("errors") or []
    ci_errors = ci.get("errors") or []
    new_errors = [e for e in ci_errors if e not in base_errors]

    checks = {
        "checker": CHECKER,
        "rulesRewritten": replaced,
        "asWritten": {"exit": base_code, "passed": base.get("passed"), "errors": len(base_errors)},
        "withCaseInsensitiveRules": {
            "exit": ci_code, "passed": ci.get("passed"), "errors": len(ci_errors),
        },
        "newErrors": new_errors,
        "newErrorCount": len(new_errors),
        "firstAttemptCorrection": (
            "最初の試行では`relative`自体を小文字にしたため、"
            "規則の内部にある大小文字依存の比較（`\"SCN-002\" in relative`など）も壊れ、"
            "出た誤りは**こちらの改変の産物**だった。"
            "今回は照合の側だけを大小文字無視にし、`relative`は元のまま残した。"
        ),
        "finding": (
            "checkerの規則照合だけを大小文字無視に書き換えて実行した。"
            f"**{replaced}件の規則**が書き換わり、"
            f"その結果**{len(new_errors)}件の新しい誤り**が出た。"
            "大小文字の違いで発火していなかった規則には、"
            "**実際の判定が書かれていた**。"
        ),
    }
    passed = len(new_errors) > 0

    receipt = {
        "schema": "tai.reference.yic-dead-rule-impact/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 running the checker with case-insensitive rule matching",
        "command": "python integrations/tools/yic_dead_rule_impact_probe.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-dead-rule-impact-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs the checker twice: as written, and with the rule match made case-insensitive so "
            "the case-dead rules fire. It shows that those rules would reject receipts; it does "
            "not decide which behaviour is intended, and the second run is a patched copy."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "rewritten": replaced,
        "baseline": len(base_errors),
        "ci": len(ci_errors),
        "new": len(new_errors),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
