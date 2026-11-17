"""Check what the nearest thing to a P step can and cannot decide.

The I/R/P/T/C/H table stops at R for every card, because none names a recipient.
Before concluding "nothing in the Product addresses P", this runs the read preflight
TEI exposes and records what it says about Audience and Disclosure. The comment on
the type claims it does not check either; this runs the tests that pin its actual
behaviour, so the limit is observed rather than read.
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

# The suite that pins the preflight's behaviour, and the specific limits to keep.
PACKAGE = "./internal/plugin/management"
PATTERN = "^TestDocumentReadPreflight"
TYPE_FILE = "internal/plugin/management/document_preflight.go"
VERDICT = re.compile(r"^\s*---\s+(PASS|FAIL|SKIP):\s+(\S+)", re.M)

# Phrases the type comment uses to disclaim, and the question each answers.
DISCLAIMERS = (
    {"phrase": "does not discover a Document", "question": "対象文書の発見"},
    {"phrase": "read its bytes", "question": "本文byteの読取"},
    {"phrase": "check Audience/Disclosure", "question": "受信者別の開示判定"},
    {"phrase": "grant publication", "question": "公開の許可"},
)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    repo = Path(args.tei_repo).resolve()
    type_file = repo / TYPE_FILE
    if not type_file.exists():
        print(f"missing {TYPE_FILE} under {repo}", file=sys.stderr)
        return 1

    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], cwd=repo,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"], cwd=repo,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()

    completed = subprocess.run(
        ["go", "test", PACKAGE, "-run", PATTERN, "-count=1", "-v"],
        cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ},
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    verdicts = {name: verdict for verdict, name in VERDICT.findall(output)}
    failed = [name for name, value in verdicts.items() if value == "FAIL"]
    skipped = [name for name, value in verdicts.items() if value == "SKIP"]

    source = type_file.read_text(encoding="utf-8")
    disclaimers = [
        {**item, "presentInSource": item["phrase"] in source}
        for item in DISCLAIMERS
    ]

    checks = {
        "teiCommit": head,
        "checkoutClean": dirty == "",
        "package": PACKAGE,
        "typeFile": TYPE_FILE,
        "testsRun": len(verdicts),
        "testsPassed": len([v for v in verdicts.values() if v == "PASS"]),
        "failed": failed,
        "skipped": skipped,
        "verdicts": verdicts,
        "disclaimers": disclaimers,
        "disclaimsAudienceAndDisclosure": all(
            item["presentInSource"]
            for item in disclaimers
            if "Audience" in item["phrase"] or "publication" in item["phrase"]
        ),
        "everyTestPassed": bool(verdicts) and not failed,
        "finding": (
            "TEIの`document_preflight`は、Documentを発見せず、byteを読み、"
            "Audience/Disclosureを検査せず、公開を許可しないと型のコメントで明示している。"
            "この検査はその宣言と、選択解決の挙動を固定するテストを実行して確認した。"
            "したがって、P（受信者別の開示）を判定する経路は、少なくともこの入口には無い。"
        ),
    }
    passed = checks["everyTestPassed"] and checks["disclaimsAudienceAndDisclosure"] and checks["checkoutClean"]

    receipt = {
        "schema": "tai.reference.yic-preflight-disclosure-boundary/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go, running the TEI plugin-management preflight tests",
        "command": (
            "python integrations/tools/yic_preflight_disclosure_boundary.py "
            f"--tei-repo <clean TEI clone at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-preflight-disclosure-2026-11-17.json"
        ),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs the tests that pin TEI's document read preflight and checks that the type's own "
            "comment disclaims discovering the document, reading bytes, checking Audience/Disclosure "
            "and granting publication. It shows the preflight is not a recipient-specific decision; it "
            "does not prove that no other TEI entry can decide disclosure, and it does not exercise any "
            "release or publication route."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": head[:12],
        "clean": checks["checkoutClean"],
        "tests": len(verdicts),
        "failed": failed,
        "disclaims": checks["disclaimsAudienceAndDisclosure"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
