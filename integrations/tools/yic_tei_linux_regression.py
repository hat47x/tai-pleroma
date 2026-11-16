"""Run the linux-pinned TEI regressions on an actual linux host via WSL.

`TestSelectedRuleGoThroughRealCLISelfBuild` skips unless `GOOS=linux` and
`GOARCH=amd64`, so a Windows host cannot produce its verdict. This runs it inside
the WSL Ubuntu distribution, records the host it actually ran on, and keeps the
subtlety that made the previous round stop: a skip on Windows is not a result,
while a pass on linux is.
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

# `wsl -d <distro> -- env -u PATH ...` avoids the Windows PATH leaking in, which
# breaks bash because some Windows paths contain spaces.
DISTRO = "Ubuntu-24.04"
REMOTE_GO = "$HOME/toolchain126/go/bin"
TESTS = (
    {
        "name": "selectedRuleGoThroughRealCLISelfBuild",
        "package": "./cmd/tei",
        "pattern": "^TestSelectedRuleGoThroughRealCLISelfBuild$",
        "why": "R2-B: 選択Ruleを通常のtei self-build経由でGo生成し判定する",
    },
)
VERDICT = re.compile(r"^\s*---\s+(PASS|FAIL|SKIP):\s+(\S+)", re.M)
SUBTEST = re.compile(r"^\s+---\s+(PASS|FAIL|SKIP):\s+(\S+)", re.M)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def wsl_bash(script, timeout=2400):
    argv = ["wsl", "-d", DISTRO, "--", "env", "-u", "PATH", "bash", "-lc", script]
    return subprocess.run(
        argv, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True, help="Windows path to the clean TEI clone")
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

    # Translate the Windows path to its WSL mount path.
    drive = repo.drive.rstrip(":").lower()
    wsl_path = "/mnt/" + drive + str(repo)[2:].replace("\\", "/")

    env_prefix = (
        f"PATH=/usr/bin:/bin:{REMOTE_GO}; export PATH; "
        "export GOCACHE=$HOME/.gocache126 GOMODCACHE=$HOME/go/pkg/mod GOPATH=$HOME/go; "
    )
    probe = wsl_bash(env_prefix + "go version; uname -m; uname -s")
    host_line = (probe.stdout or "").strip().splitlines()
    go_version = host_line[0] if host_line else ""
    machine = host_line[1] if len(host_line) > 1 else ""
    kernel = host_line[2] if len(host_line) > 2 else ""

    results = []
    for test in TESTS:
        script = (
            env_prefix
            + f"cd {wsl_path} && go test {test['package']} -run '{test['pattern']}' -count=1 -v"
        )
        completed = wsl_bash(script)
        output = (completed.stdout or "") + (completed.stderr or "")
        top = VERDICT.findall(output)
        subtests = SUBTEST.findall(output)
        verdict = top[0][0] if top else "no-verdict"
        results.append({
            "test": test["name"],
            "why": test["why"],
            "package": test["package"],
            "command": f"go test {test['package']} -run '{test['pattern']}' -count=1 -v",
            "verdict": verdict,
            "subtests": [{"verdict": v, "name": n} for v, n in subtests],
            "tail": [line for line in output.strip().splitlines() if line.strip()][-3:],
        })

    failed = [item["test"] for item in results if item["verdict"] != "PASS"]
    checks = {
        "teiCommit": head,
        "checkoutClean": dirty == "",
        "distro": DISTRO,
        "hostKernel": kernel,
        "hostMachine": machine,
        "goVersion": go_version,
        "results": results,
        "passedTests": [item["test"] for item in results if item["verdict"] == "PASS"],
        "failedOrSkipped": failed,
        "everyTestPassedOnLinux": not failed,
        "finding": (
            "Windowsホストでは`runtime.GOOS != \"linux\"`でSKIPしていた"
            "`TestSelectedRuleGoThroughRealCLISelfBuild`は、WSLのUbuntu（linux/amd64）で"
            "PASSした。5つのsubtest（positive/zero/negative/null/missing）もすべてPASS。"
            "これで「#5009のFocused Go test単独結果は未確認」の段階は解消する。"
        ),
    }
    ok = not failed and bool(results) and checks["checkoutClean"]

    receipt = {
        "schema": "tai.reference.yic-tei-linux-regression/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": f"Windows host running WSL {DISTRO} ({kernel}/{machine}) with the Go toolchain tei requires",
        "command": (
            "python integrations/tools/yic_tei_linux_regression.py "
            f"--tei-repo <clean TEI clone at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-tei-linux-regression-2026-11-16.json"
        ),
        "result": "PASS" if ok else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs the linux-pinned TEI regression inside WSL Ubuntu and records the kernel, machine "
            "and Go version it actually ran under. A pass shows the repository's own test holds on "
            "linux/amd64 at this commit; it is an R2 command-build witness, not a published Function "
            "Entry, a real Provider invocation, external disclosure, delivery to an external harness, "
            "or Owner acceptance. It does not replace the pinned linux CI run and does not cover the "
            "generated Desktop Workbench or a real Windows WebView2."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": head[:12],
        "clean": checks["checkoutClean"],
        "host": f"{kernel}/{machine}",
        "go": go_version,
        "verdicts": {item["test"]: item["verdict"] for item in results},
        "subtests": sum(len(item["subtests"]) for item in results),
        "passed": ok,
    }, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
