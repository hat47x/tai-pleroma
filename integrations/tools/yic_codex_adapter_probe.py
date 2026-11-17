"""Check what the codex-exec adapter's tests establish, and whether it can ever run here.

Doc 56 recorded that `codex-exec` has no execution record. The adapter and its tests
exist. This runs them and records each test's outcome, plus whether the CLI is present on
this host, so "no record" is distinguished from "not implemented".

The tests are bounded: they exercise parsing, refusal paths and probes with a scripted
runner. Whether the real CLI is installed is a separate fact, recorded separately.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import time
from pathlib import Path

ADAPTER = "integrations/harness-adapter"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(cmd, cwd):
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=3600,
    )


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

    # The tests whose names begin with TestCodexExec.
    listed = run(["go", "test", "./...", "-run", "TestCodexExec", "-count=1", "-v"], folder)
    output = (listed.stdout or "") + (listed.stderr or "")
    passes = re.findall(r"^--- PASS: (TestCodexExec\w+)", output, re.M)
    skips = re.findall(r"^--- SKIP: (TestCodexExec\w+)", output, re.M)
    failures = re.findall(r"^--- FAIL: (TestCodexExec\w+)", output, re.M)

    # Is the CLI on this host?
    cli = shutil.which("codex")
    go_version = run(["go", "version"], folder).stdout.strip()

    # Does any evidence file mention codex?
    evidence = root / ADAPTER / "evidence"
    mentions = []
    for path in sorted(evidence.glob("*.json")):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if "codex" in text.lower():
            mentions.append(path.name)

    checks = {
        "adapterFolder": ADAPTER,
        "goVersion": go_version,
        "testsPassed": sorted(passes),
        "testsSkipped": sorted(skips),
        "testsFailed": sorted(failures),
        "codexCliOnThisHost": bool(cli),
        "codexCliPath": cli,
        "evidenceMentioningCodex": mentions,
        "finding": (
            "`codex-exec` adapterのtestsを実行した。"
            f"{len(passes)}件がPASS・{len(skips)}件がSKIP・{len(failures)}件がFAIL。"
            f"このホストにcodex CLIは**{'在る' if cli else '無い'}**。"
            f"evidenceにcodexへの言及は**{len(mentions)}件**。"
            "**「実行記録が無い」は「実装が無い」ではない。** "
            "testsはscriptedなrunnerで解析と拒否経路を確かめており、"
            "実CLIの起動は確かめていない。"
        ),
        "whatTheTestsDoNotEstablish": (
            "実codex CLIの起動、認証、sandbox、Tool権限。"
            "testsは`scripted`なrunnerを差し替えており、外部プロセスを起動しない。"
        ),
    }
    passed = bool(passes) and not failures

    receipt = {
        "schema": "tai.reference.yic-codex-adapter-tests/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": f"Windows with {go_version or 'Go'} running the adapter's own tests",
        "command": "python integrations/tools/yic_codex_adapter_probe.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-codex-adapter-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs the codex-exec adapter's own Go tests and records which passed, whether the codex "
            "CLI exists on this host, and whether any evidence file mentions it. The tests use a "
            "scripted runner, so this shows the adapter's parsing and refusal paths, not a launch of "
            "the real CLI."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "passed": len(passes),
        "skipped": len(skips),
        "failed": len(failures),
        "cli": bool(cli),
        "evidenceMentions": len(mentions),
        "result": "PASS" if passed else "FAIL",
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
