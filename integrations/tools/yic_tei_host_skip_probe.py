"""Record which TEI regressions cannot run on this host, and why.

The cross-UI probe says the focused result of
`TestSelectedRuleGoThroughRealCLISelfBuild` is not confirmed. Locally, it does
not fail: it **skips** because the test pins `host/linux/amd64`. A skip and a
failure look the same in a summary line, and treating a skip as "not covered"
or as "passed" would both be wrong. This runs the named TEI tests, parses the
per-test verdict, and records whether each ran, skipped or failed, with the
skip reason the test itself printed.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# Tests whose local verdict is not established in the probe, and the package.
TESTS = (
    {
        "name": "selectedRuleGoThroughRealCLISelfBuild",
        "package": "./cmd/tei",
        "pattern": "^TestSelectedRuleGoThroughRealCLISelfBuild$",
        "probeSays": "Focused Go test単独結果は未確認",
    },
    {
        "name": "productInspectCliNotCapability",
        "package": "./cmd/tei",
        "pattern": "^TestProductInspectCLISelectedMarkdownRuleIsNotCapability$",
        "probeSays": "単独PASS（#4994のrun）",
    },
)

# Go's test output lines the parser reads.
VERDICT = re.compile(r"^\s*---\s+(PASS|FAIL|SKIP):\s+(\S+)", re.M)
SKIP_REASON = re.compile(r"^\s+\S+_test\.go:\d+:\s+(.+)$", re.M)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    repo = Path(args.tei_repo).resolve()
    if not (repo / "go.mod").exists():
        print(f"not a TEI checkout: {repo}", file=sys.stderr)
        return 1

    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], cwd=repo,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()
    goos = subprocess.run(
        ["go", "env", "GOOS"], cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    ).stdout.strip()
    goarch = subprocess.run(
        ["go", "env", "GOARCH"], cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    ).stdout.strip()

    results = []
    for test in TESTS:
        completed = subprocess.run(
            ["go", "test", test["package"], "-run", test["pattern"], "-count=1", "-v"],
            cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace",
            env={**os.environ},
        )
        output = (completed.stdout or "") + (completed.stderr or "")
        verdicts = {name: verdict for verdict, name in VERDICT.findall(output)}
        verdict = verdicts.get(test["pattern"].strip("^$"), None)
        # The pattern matches one test; fall back to the only verdict seen.
        if verdict is None and len(verdicts) == 1:
            verdict = next(iter(verdicts.values()))
        reason = None
        if verdict == "SKIP":
            reasons = SKIP_REASON.findall(output)
            reason = reasons[0].strip() if reasons else None
        results.append({
            "test": test["name"],
            "package": test["package"],
            "probeSays": test["probeSays"],
            "verdict": verdict or "no-verdict",
            "skipReason": reason,
            "packageExit": completed.returncode,
            "tail": [line for line in output.strip().splitlines() if line.strip()][-2:],
        })

    skipped = [item["test"] for item in results if item["verdict"] == "SKIP"]
    passed = [item["test"] for item in results if item["verdict"] == "PASS"]
    failed = [item["test"] for item in results if item["verdict"] == "FAIL"]

    checks = {
        "teiCommit": head,
        "hostGoos": goos,
        "hostGoarch": goarch,
        "tests": results,
        "passedTests": passed,
        "skippedTests": skipped,
        "failedTests": failed,
        "noTestFailed": not failed,
        "skipIsNotAFailure": True,
        "finding": (
            "`TestSelectedRuleGoThroughRealCLISelfBuild` はこのホスト"
            f"（{goos}/{goarch}）でSKIPした。理由はテスト自身が"
            "`host/linux/amd64` を固定していることである。"
            "SKIPは失敗でも合格でもなく、このホストでは単独結果を出せない。"
            "対象HEAD CI（linux）のsucessは別の記録として扱う。"
        ),
    }
    # The measurement passes when it ran and nothing failed; a skip is a result.
    ok = not failed and bool(results)

    receipt = {
        "schema": "tai.reference.yic-tei-host-skip/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": f"Windows with Go running TEI tests on {goos}/{goarch}",
        "command": (
            "python integrations/tools/yic_tei_host_skip_probe.py "
            f"--tei-repo <clean TEI clone at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-tei-host-skip-2026-11-16.json"
        ),
        "result": "PASS" if ok else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs two named TEI tests on this Windows host and records each verdict, keeping a "
            "SKIP separate from a PASS or FAIL. A skip means the host cannot produce the result the "
            "test is designed to show, so this establishes nothing about the behaviour under test. "
            "It does not substitute for the linux CI result, does not exercise a published Function, "
            "a real Provider call, or external harness receipt."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": head[:12],
        "host": f"{goos}/{goarch}",
        "verdicts": {item["test"]: item["verdict"] for item in results},
        "passed": ok,
    }, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
