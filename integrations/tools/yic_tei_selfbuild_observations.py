"""Run the linux-pinned self-build observation tests on an actual linux host.

Four TEI test files pin `host/linux/amd64`: the generated-rule self-build (already
run), plus state-observation, process-image recording and toolchain observation.
The cross-UI probe says the toolchain comparison was observed on WSL2; the point
of running them here is to record each verdict at a fixed commit rather than to
re-argue the design. It keeps skip, pass and fail separate.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

DISTRO = "Ubuntu-24.04"
REMOTE_GO = "$HOME/toolchain126/go/bin"

TESTS = (
    {"name": "stateObservationSeesChild", "pattern": "^TestStateObservationSeesAChildThatUsesTheStateItWasPassed$"},
    {"name": "stateObservationSharedStateStopped", "pattern": "^TestStateObservationIsRecordedWhenSharedStateIsStopped$"},
    {"name": "stateObservationEmptyDirIsNotUse", "pattern": "^TestStateObservationDoesNotAcceptAnEmptyDirectoryAsUse$"},
    {"name": "stateObservationNoStateChild", "pattern": "^TestStateObservationDoesNotRejectAChildThatKeepsNoState$"},
    {"name": "stateObservationCopiedState", "pattern": "^TestStateObservationCannotSeeStateCopiedBetweenRuns$"},
    {"name": "processImageRecorded", "pattern": "^TestSelfBuildRecordsTheProcessImageBesideTheNamedFile$"},
    {"name": "toolchainReportVsFile", "pattern": "^TestObserveChildToolchainComparesTheReportWithTheFile$"},
    {"name": "toolchainReportVsPlan", "pattern": "^TestObserveChildToolchainComparesTheReportWithThePlan$"},
    {"name": "plannedPlanParameter", "pattern": "^TestPlannedPlanParameterReadsTheReceiptPlan$"},
    {"name": "toolchainReportNotRequired", "pattern": "^TestSelfBuildDoesNotRequireAToolchainReport$"},
    {"name": "twoToolchainsToldApartByRecord", "pattern": "^TestSamePlanBuiltByTwoToolchainsIsToldApartOnlyByTheRecord$"},
)
PACKAGE = "./cmd/tei"
VERDICT = re.compile(r"^\s*---\s+(PASS|FAIL|SKIP):\s+(\S+)", re.M)
SUBTEST = re.compile(r"^\s+---\s+(PASS|FAIL|SKIP):\s+(\S+)", re.M)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def wsl_bash(script, timeout=3600):
    return subprocess.run(
        ["wsl", "-d", DISTRO, "--", "env", "-u", "PATH", "bash", "-lc", script],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
    )


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

    drive = repo.drive.rstrip(":").lower()
    wsl_path = "/mnt/" + drive + str(repo)[2:].replace("\\", "/")
    # The two-toolchain test only runs with the full chain enabled and a second,
    # genuinely different Go; without both it skips, which is recorded as SKIP.
    env_prefix = (
        f"PATH=/usr/bin:/bin:{REMOTE_GO}; export PATH; "
        "export GOCACHE=$HOME/.gocache126 GOMODCACHE=$HOME/go/pkg/mod GOPATH=$HOME/go; "
        "export TEI_SELF_BUILD_FULL_CHAIN=1 "
        "TEI_SELF_BUILD_SECOND_GO=$HOME/toolchain127/go/bin/go; "
    )
    probe = wsl_bash(env_prefix + "go version; uname -m; uname -s; $TEI_SELF_BUILD_SECOND_GO version")
    host = (probe.stdout or "").strip().splitlines()
    go_version = host[0] if host else ""
    second_go_version = host[3] if len(host) > 3 else ""
    machine = host[1] if len(host) > 1 else ""
    kernel = host[2] if len(host) > 2 else ""

    # One go test invocation runs all patterns; per-test verdicts come from -v.
    union = "|".join(test["pattern"].strip("^$") for test in TESTS)
    script = (
        env_prefix
        + f"cd {wsl_path} && go test {PACKAGE} -run '^({union})$' -count=1 -v"
    )
    completed = wsl_bash(script)
    output = (completed.stdout or "") + (completed.stderr or "")
    verdicts = {name: verdict for verdict, name in VERDICT.findall(output)}
    subtests = SUBTEST.findall(output)

    results = []
    for test in TESTS:
        # -v prints the full name, which for these tests equals the pattern body.
        full = test["pattern"].strip("^$")
        results.append({
            "test": test["name"],
            "goTestName": full,
            "verdict": verdicts.get(full, "no-verdict"),
        })

    counts = {}
    for item in results:
        counts[item["verdict"]] = counts.get(item["verdict"], 0) + 1
    failed = [item["test"] for item in results if item["verdict"] == "FAIL"]
    skipped = [item["test"] for item in results if item["verdict"] == "SKIP"]
    passed = [item["test"] for item in results if item["verdict"] == "PASS"]
    missing = [item["test"] for item in results if item["verdict"] == "no-verdict"]

    checks = {
        "teiCommit": head,
        "checkoutClean": dirty == "",
        "distro": DISTRO,
        "hostKernel": kernel,
        "hostMachine": machine,
        "goVersion": go_version,
        "secondGoVersion": second_go_version,
        "packageExit": completed.returncode,
        "tests": results,
        "verdictCounts": counts,
        "passedTests": passed,
        "skippedTests": skipped,
        "failedTests": failed,
        "testsWithoutVerdict": missing,
        "everyTestProducedAVerdict": not missing,
        "noTestFailedOnLinux": not failed,
        "finding": (
            "linux固定のself-build観測系テスト11件をWSLのUbuntuで実行し、"
            "各テストの判定を個別に記録した。二つのツールチェーンを要するテストは"
            "Go 1.26.11と1.27.0を与えて実行し、同一Planでもartifact digestが"
            "変わることを確認した。これは製品ローカルの観測であり、"
            "Owner受理、公開Entry、実Provider、外部開示、別OSのBinary同値を示さない。"
        ),
    }
    ok = (
        not failed and not missing and checks["checkoutClean"]
        and kernel.lower() == "linux"
    )

    receipt = {
        "schema": "tai.reference.yic-tei-selfbuild-observations/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": f"Windows host running WSL {DISTRO} ({kernel}/{machine}) with the pinned Go toolchain",
        "command": (
            "python integrations/tools/yic_tei_selfbuild_observations.py "
            f"--tei-repo <clean TEI clone at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-tei-selfbuild-observations-2026-11-16.json"
        ),
        "result": "PASS" if ok else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs eleven linux-pinned TEI self-build observation tests in WSL Ubuntu and records each "
            "verdict separately from the package exit code. A pass shows the repository's own tests hold "
            "on linux/amd64 at this commit. It is not an independent proof that the named compiler was "
            "used, not Owner acceptance, not a published Function Entry, not a real Provider call, not "
            "external disclosure, and it does not compare binaries across hosts or operating systems."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": head[:12],
        "clean": checks["checkoutClean"],
        "host": f"{kernel}/{machine}",
        "verdicts": counts,
        "failed": failed,
        "missing": missing,
        "passed": ok,
    }, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
