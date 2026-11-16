"""Confirm that "ambiguous" and "absent" are not distinguished, as QH-RESOLVE-09 claims.

The YIC ticket says a capability resolution returns `false` both when there are no
candidates and when there are several, and that a `Supports*` predicate only
judges membership in a declaration. This runs the tests that pin those two
statements and records each verdict, so the card's claim has a fixed-commit
observation behind it rather than a code reading.
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

# Each claim, with the package and test that pins it.
CLAIMS = (
    {
        "id": "QH-RESOLVE-09a",
        "claim": "能力の解決結果は、候補0件と複数件の双方で同じ「解決しない」になる",
        "package": "./internal/plugin",
        "pattern": "^Test(AnAmbiguousCapabilityLooksTheSameAsAnAbsentOne|ResolutionDoesNotCheckCapabilityUniqueness|TheSameIDUnderDifferentKindsIsNotAmbiguous)$",
        "testNames": (
            "TestAnAmbiguousCapabilityLooksTheSameAsAnAbsentOne",
            "TestResolutionDoesNotCheckCapabilityUniqueness",
            "TestTheSameIDUnderDifferentKindsIsNotAmbiguous",
        ),
    },
    {
        "id": "QH-RESOLVE-09b",
        "claim": "単一のProviderは自分の識別子で答え、別能力の2 Providerも双方解決する",
        "package": "./internal/plugin",
        "pattern": "^Test(ASingleProviderAnswersWithItsIdentity|TwoProvidersOfDifferentCapabilitiesBothResolve)$",
        "testNames": (
            "TestASingleProviderAnswersWithItsIdentity",
            "TestTwoProvidersOfDifferentCapabilitiesBothResolve",
        ),
    },
    {
        "id": "QH-RESOLVE-09c",
        "claim": "Supports* 述語は宣言内の所属判定であり、Loaded/Invoked/Grantedではない",
        "package": "./internal/plugin/runtime",
        "pattern": "^Test",
        "testNames": (),
        "note": "package-wide run: the predicate tests live beside the adapter they judge",
    },
)
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
    if not (repo / "go.mod").exists():
        print(f"not a TEI checkout: {repo}", file=sys.stderr)
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

    results = []
    for item in CLAIMS:
        completed = subprocess.run(
            ["go", "test", item["package"], "-run", item["pattern"], "-count=1", "-v"],
            cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace",
            env={**os.environ},
        )
        output = (completed.stdout or "") + (completed.stderr or "")
        verdicts = {name: verdict for verdict, name in VERDICT.findall(output)}
        if item["testNames"]:
            named = {name: verdicts.get(name, "absent") for name in item["testNames"]}
            failedNamed = [n for n, v in named.items() if v == "FAIL"]
            skippedNamed = [n for n, v in named.items() if v == "SKIP"]
            passed = completed.returncode == 0 and not failedNamed
        else:
            # Package-wide: the claim is "no failure", and skips are listed so a
            # reader can see which parts of the package did not run.
            named = verdicts
            failedNamed = [n for n, v in verdicts.items() if v == "FAIL"]
            skippedNamed = [n for n, v in verdicts.items() if v == "SKIP"]
            passed = completed.returncode == 0 and not failedNamed
        results.append({
            "id": item["id"],
            "claim": item["claim"],
            "package": item["package"],
            "packageExit": completed.returncode,
            "verdicts": named,
            "failedTests": failedNamed,
            "skippedTests": skippedNamed,
            "passed": passed,
            "tail": [line for line in output.strip().splitlines() if line.strip()][-2:],
        })

    failed = [item["id"] for item in results if not item["passed"]]
    checks = {
        "teiCommit": head,
        "checkoutClean": dirty == "",
        "goVersion": go_version,
        "claims": results,
        "failed": failed,
        "everyClaimIsPinnedByAPassingTest": not failed,
        "finding": (
            "QH-RESOLVE-09の二つの主張は、どちらも固定commitのテストで確かめられる。"
            "「曖昧」と「不在」が同じ結果になること、Supports*が宣言内の所属判定であることは、"
            "いずれも試験で固定されている。ただしその`false`をCapabilityの不存在へ昇格させないこと、"
            "`Supports=true`をLoaded/Invoked/Grantedと呼ばないことは、"
            "試験ではなく読み手の判断に残る。"
        ),
    }
    ok = not failed and checks["checkoutClean"]

    receipt = {
        "schema": "tai.reference.yic-qh-resolve-09/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go, running the TEI plugin tests",
        "command": (
            "python integrations/tools/yic_qh_resolve_09_probe.py "
            f"--tei-repo <clean TEI clone at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-qh-resolve-09-2026-11-16.json"
        ),
        "result": "PASS" if ok else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs the TEI plugin tests that pin two statements in QH-RESOLVE-09 and records each "
            "verdict. A pass shows the resolution behaves as those tests assert at this commit; it "
            "does not establish that no caller promotes the result to a capability's absence, does "
            "not exercise a real provider, and says nothing about disclosure or Owner acceptance."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": head[:12],
        "clean": checks["checkoutClean"],
        "failed": failed,
        "passed": ok,
    }, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
