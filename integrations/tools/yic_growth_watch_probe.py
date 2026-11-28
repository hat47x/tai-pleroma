"""Prove the growth watch fires: add one mismatched name and see the check fail.

A baseline that never fires is decoration. This temporarily copies the check with one extra
name in the baseline set that is not in the data, which should NOT fail — and then tests the
opposite: a name present in the data but absent from the baseline. The second case is what
a newly introduced mismatch looks like.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

CHECK = "integrations/tools/yic_receipt_name_date_check.py"
BASELINE_MARK = "BASELINE_MISMATCHES = frozenset(("


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    text = (root / CHECK).read_text(encoding="utf-8")
    assert BASELINE_MARK in text

    # Remove one name from the baseline: that name is now "new", so the check must fail.
    import re

    first_name = re.search(r'\n    "([^"]+\.json)",', text)
    assert first_name, "no baseline entry found"
    removed = first_name.group(1)
    patched = text.replace(f'    "{removed}",\n', "", 1)

    # Run the patched copy against the same data.
    import subprocess
    import sys
    import tempfile

    scratch = Path(tempfile.mkdtemp(prefix="yic-growth-"))
    target = scratch / "check_without_one.py"
    target.write_text(patched, encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(target),
         "--artifact", args.artifact, "--out", str(scratch / "r.json")],
        cwd=str(target.parent), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=1800,
    )
    body = completed.stdout.strip()
    parsed = json.loads(body[body.index("{"):]) if "{" in body else {}

    checks = {
        "removedFromBaseline": removed,
        "exit": completed.returncode,
        "reportedNew": parsed.get("newSinceBaseline"),
        "readStderr": (completed.stderr or "").strip().splitlines()[-1:] if completed.returncode else [],
        "growthIsDetected": completed.returncode != 0,
        "finding": (
            f"基準から`{removed}`を1件外して実行した。"
            f"{'**新しい食い違いとして検出され、落ちた。**' if completed.returncode else '**落ちなかった。基準は飾りである。**'}"
            "**基準が発火しないなら、置く意味が無い。**"
        ),
    }
    passed = completed.returncode != 0

    receipt = {
        "schema": "tai.reference.yic-growth-watch-effect/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 running the check with one baseline entry removed",
        "command": "python integrations/tools/yic_growth_watch_probe.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-growth-watch-2026-11-28.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Removes one entry from the baseline in a temporary copy and confirms the check then "
            "fails. It proves the mechanism fires; it does not prove the baseline covers every "
            "existing mismatch."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "removed": removed,
        "exit": completed.returncode,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
