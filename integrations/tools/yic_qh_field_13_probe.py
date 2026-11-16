"""Confirm that a whole Record keeps its fields while an explicit projection drops the rest.

QH-FIELD-13 claims two things: a pure Whole Record keeps every extra field, and an
explicit two-field projection drops the others, with a required-missing field and
an explicit NULL kept apart. This runs the test that pins it at a fixed commit and
records the verdict, so the card rests on an observation.
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

PACKAGE = "./internal/plugin/transform"
PATTERN = "^TestPluginFieldProjectionKeepsOnlyExplicitConsumerFields$"
TEST_NAME = "TestPluginFieldProjectionKeepsOnlyExplicitConsumerFields"
VERDICT = re.compile(r"^\s*---\s+(PASS|FAIL|SKIP):\s+(\S+)", re.M)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    repo = Path(args.tei_repo).resolve()
    test_file = repo / "internal/plugin/transform/plugin_field_projection_conformance_test.go"
    if not test_file.exists():
        print(f"test file missing under {repo}", file=sys.stderr)
        return 1

    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], cwd=repo,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"], cwd=repo,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()
    go_version = subprocess.run(
        ["go", "version"], cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    ).stdout.strip()

    completed = subprocess.run(
        ["go", "test", PACKAGE, "-run", PATTERN, "-count=1", "-v"],
        cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ},
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    verdicts = {name: verdict for verdict, name in VERDICT.findall(output)}
    subtests = [
        {"verdict": verdict, "name": name}
        for verdict, name in re.findall(r"^\s+---\s+(PASS|FAIL|SKIP):\s+(\S+)", output, re.M)
    ]
    verdict = verdicts.get(TEST_NAME, "absent")
    failed = [
        name for name, value in verdicts.items() if value == "FAIL"
    ] + [item["name"] for item in subtests if item["verdict"] == "FAIL"]
    skipped = [
        name for name, value in verdicts.items() if value == "SKIP"
    ] + [item["name"] for item in subtests if item["verdict"] == "SKIP"]

    checks = {
        "teiCommit": head,
        "checkoutClean": dirty == "",
        "goVersion": go_version,
        "package": PACKAGE,
        "testFile": "internal/plugin/transform/plugin_field_projection_conformance_test.go",
        "verdict": verdict,
        "subtests": subtests,
        "failed": failed,
        "skipped": skipped,
        "packageExit": completed.returncode,
        "tail": [line for line in output.strip().splitlines() if line.strip()][-3:],
        "theClaimIsPinnedByAPassingTest": (
            completed.returncode == 0 and verdict == "PASS" and not failed
        ),
        "finding": (
            "QH-FIELD-13の主張は、`internal/plugin/transform`の1テストで固定されている。"
            "Whole Recordが追加Fieldを残し、明示2 Field投影が他を落とすことを、"
            "製品既存Transformで検査する。ただし出力の形が正しいことは、"
            "実Port Binding・Source完全性・RecipientのField公開権限・Provider実行を"
            "合格にしない。"
        ),
    }
    passed = checks["theClaimIsPinnedByAPassingTest"] and checks["checkoutClean"]

    receipt = {
        "schema": "tai.reference.yic-qh-field-13/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go, running the TEI plugin transform test",
        "command": (
            "python integrations/tools/yic_qh_field_13_probe.py "
            f"--tei-repo <clean TEI clone at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-qh-field-13-2026-11-16.json"
        ),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs the single TEI test that pins QH-FIELD-13 and records its verdict and subtests. A "
            "pass shows the projection keeps and drops the fields that test expects at this commit; "
            "it does not show a real port binding, source completeness, a recipient's field "
            "disclosure rights, or a provider invocation."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": head[:12],
        "clean": checks["checkoutClean"],
        "verdict": verdict,
        "subtests": len(subtests),
        "failed": failed,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
