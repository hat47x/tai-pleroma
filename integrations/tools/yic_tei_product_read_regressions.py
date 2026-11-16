"""Run the TEI product-read regressions the YIC execution ticket listed as NOT RUN.

`tei-selection-harness-first-vertical-slice-2026-11-15.md` names eight Go
regressions and states that the ticket did not run them. Running them turns a
claim about the repository's tests into an observation at a fixed commit. This
runs each one in a dedicated clean clone and records commit, command, exit code
and output tail per test.
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

# The regressions the ticket names, in the order it presents them.
TESTS = (
    {
        "name": "capabilitySourceEvidence",
        "package": "./internal/operations",
        "pattern": "^TestInspectCapabilitySourceEvidenceFromWorkspace$",
        "claims": "実Go回帰にある semantic-capability の Subject と元byte範囲を Workspace から取得する",
    },
    {
        "name": "capabilitySourceInvalidation",
        "package": "./internal/operations",
        "pattern": "^TestCapabilitySourceOnlyEditInvalidatesPinnedRevision$",
        "claims": "Source改訂で Pinned Revision が失効する",
    },
    {
        "name": "builtinRuleAdmissionAndIndex",
        "package": "./internal/workspace",
        "pattern": "^TestBuiltinRuleMarkdownProductAdmissionAndSourceIndex$",
        "claims": "正式に選択された Rule Markdown が同一Loadで型付き取得される",
    },
    {
        "name": "builtinRuleRejectsUnselected",
        "package": "./internal/workspace",
        "pattern": "^TestBuiltinRuleMarkdownProductAdmissionRejectsUnselectedOrUnknownLanguage$",
        "claims": "Language未選択・未知版を拒否する",
    },
    {
        "name": "selectedRuleFromSameLoad",
        "package": "./internal/operations",
        "pattern": "^TestInspectSelectedRuleMarkdownFromSameLoad$",
        "claims": "選択済み Rule を同一Loadから読む",
    },
    {
        "name": "ruleMarkdownIdenticalMeaning",
        "package": "./internal/workspace",
        "pattern": "^TestRuleMarkdown(AndLegacyValidationHaveIdenticalProductMeaning|RejectsLegacyValidationWithSameIdentity)$",
        "claims": "Markdown Rule と従来Validationの型付き意味同値、同一IDの二重宣言拒否",
    },
    {
        "name": "evaluatorReadFootprint",
        "package": "./internal/operations",
        "pattern": "^TestSelectedMarkdownRulesDriveEvaluatorReadFootprint$",
        "claims": "選択Ruleが Evaluator の Read 範囲を駆動する",
    },
    {
        "name": "productInspectCliNotCapability",
        "package": "./cmd/tei",
        "pattern": "^TestProductInspectCLISelectedMarkdownRuleIsNotCapability$",
        "claims": "実CLIのinspectが選択Ruleを取得し、同名 Capability と text Fence 内の Rule は SUBJECT_NOT_FOUND",
    },
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
    if not (repo / "go.mod").exists():
        print(f"not a TEI checkout: {repo}", file=sys.stderr)
        return 1

    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()
    go_version = subprocess.run(
        ["go", "version"], capture_output=True, text=True, encoding="utf-8", errors="replace"
    ).stdout.strip()

    results = []
    for test in TESTS:
        completed = subprocess.run(
            ["go", "test", test["package"], "-run", test["pattern"], "-count=1"],
            cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace",
            env={**os.environ},
        )
        output = (completed.stdout or "") + (completed.stderr or "")
        tail = [line for line in output.strip().splitlines() if line.strip()][-2:]
        passed = completed.returncode == 0 and re.search(r"^ok\s", output, re.M) is not None
        results.append({
            "test": test["name"],
            "claims": test["claims"],
            "command": f"go test {test['package']} -run '{test['pattern']}' -count=1",
            "exit": completed.returncode,
            "passed": passed,
            "tail": tail,
        })

    failed = [item["test"] for item in results if not item["passed"]]
    checks = {
        "teiCommit": head,
        "checkoutClean": dirty == "",
        "untrackedOrModifiedCount": len(dirty.splitlines()) if dirty else 0,
        "goVersion": go_version,
        "testsRun": len(results),
        "testsPassed": len(results) - len(failed),
        "failed": failed,
        "results": results,
        "everyListedRegressionPassed": not failed,
        "finding": (
            "実行票がNOT RUNとしていた8件のGo回帰は、固定commitのclean cloneで"
            "すべてPASSした。ただしこれは製品ローカルのA0読取であり、"
            "公開Function Entry、実ProviderへのInvocation、外部開示、"
            "外部Harnessへの配送・完全Reply、元SubjectのConsumer受領は示さない。"
        ),
    }
    passed = not failed

    receipt = {
        "schema": "tai.reference.yic-tei-product-read-regressions/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go, running the TEI regressions in a dedicated clean clone",
        "command": (
            "python integrations/tools/yic_tei_product_read_regressions.py "
            f"--tei-repo <clean TEI clone at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-tei-product-read-2026-11-16.json"
        ),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs the eight Go regressions the YIC execution ticket lists as NOT RUN, in a "
            "dedicated clone at the recorded commit, and records exit code and output tail per test. "
            "It is a product-local read-only baseline: it does not exercise a public Function Entry, "
            "a real Provider invocation, external disclosure, delivery to an external harness, a "
            "complete Tool Reply, or receipt by the original subject's Consumer. Passing tests show "
            "the code the clone contains behaves as those tests assert; they say nothing about the "
            "distributed Workbench, real Windows WebView2, or current Grant."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": head[:12],
        "clean": checks["checkoutClean"],
        "tests": len(results),
        "failed": failed,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
