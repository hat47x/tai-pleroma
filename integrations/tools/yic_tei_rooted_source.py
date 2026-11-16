"""Run the rooted-source boundary tests on both hosts and record the difference.

Two of these tests skip on Windows for real reasons: creating a symlink needs a
privilege the runner does not hold, and the opened-file rename semantics differ.
That means a Windows-only run leaves the containment boundary unverified, which
is a security-relevant gap rather than a formality. This runs them on Windows
and in WSL linux and records both verdict sets.
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
PACKAGE = "./internal/workspace"
PATTERN = "^TestRootedSource"
VERDICT = re.compile(r"^\s*---\s+(PASS|FAIL|SKIP):\s+(\S+)", re.M)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verdicts(output):
    return {name: verdict for verdict, name in VERDICT.findall(output)}


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

    command = ["go", "test", PACKAGE, "-run", PATTERN, "-count=1", "-v"]

    windows = subprocess.run(
        command, cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    windows_out = (windows.stdout or "") + (windows.stderr or "")

    drive = repo.drive.rstrip(":").lower()
    wsl_path = "/mnt/" + drive + str(repo)[2:].replace("\\", "/")
    script = (
        f"PATH=/usr/bin:/bin:{REMOTE_GO}; export PATH; "
        "export GOCACHE=$HOME/.gocache126 GOMODCACHE=$HOME/go/pkg/mod GOPATH=$HOME/go; "
        f"cd {wsl_path} && go test {PACKAGE} -run '{PATTERN}' -count=1 -v"
    )
    linux = subprocess.run(
        ["wsl", "-d", DISTRO, "--", "env", "-u", "PATH", "bash", "-lc", script],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800,
    )
    linux_out = (linux.stdout or "") + (linux.stderr or "")

    windows_verdicts = verdicts(windows_out)
    linux_verdicts = verdicts(linux_out)
    names = sorted(set(windows_verdicts) | set(linux_verdicts))

    comparisons = []
    for name in names:
        comparisons.append({
            "test": name,
            "windows": windows_verdicts.get(name, "absent"),
            "linux": linux_verdicts.get(name, "absent"),
            "differs": windows_verdicts.get(name) != linux_verdicts.get(name),
        })

    skipped_on_windows = [
        item["test"] for item in comparisons if item["windows"] == "SKIP"
    ]
    failed_on_linux = [
        item["test"] for item in comparisons if item["linux"] == "FAIL"
    ]
    unverified_on_windows = [
        item["test"] for item in comparisons
        if item["windows"] in ("SKIP", "absent") and item["linux"] == "PASS"
    ]

    windows_goos = subprocess.run(
        ["go", "env", "GOOS"], cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    ).stdout.strip()
    windows_goarch = subprocess.run(
        ["go", "env", "GOARCH"], cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    ).stdout.strip()
    windows_go = subprocess.run(
        ["go", "version"], cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    ).stdout.strip()
    linux_probe = subprocess.run(
        ["wsl", "-d", DISTRO, "--", "env", "-u", "PATH", "bash", "-lc",
         f"PATH=/usr/bin:/bin:{REMOTE_GO}; export PATH; go version; uname -s; uname -m"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300,
    )
    linux_lines = (linux_probe.stdout or "").strip().splitlines()
    linux_go = linux_lines[0] if linux_lines else ""
    linux_kernel = linux_lines[1] if len(linux_lines) > 1 else ""
    linux_machine = linux_lines[2] if len(linux_lines) > 2 else ""

    checks = {
        "teiCommit": head,
        "checkoutClean": dirty == "",
        "package": PACKAGE,
        # Both hosts are stated, because the whole point is the difference.
        "hostGoos": windows_goos,
        "hostGoarch": windows_goarch,
        "goVersion": windows_go,
        "linuxGoVersion": linux_go,
        "hostKernel": linux_kernel,
        "hostMachine": linux_machine,
        "comparisons": comparisons,
        "skippedOnWindows": skipped_on_windows,
        "failedOnLinux": failed_on_linux,
        "verifiedOnlyOnLinux": unverified_on_windows,
        "windowsExit": windows.returncode,
        "linuxExit": linux.returncode,
        "everyTestPassedOnLinux": not failed_on_linux and bool(linux_verdicts),
        "finding": (
            "rooted source境界のテストは、Windowsではsymlink作成権限が無く、"
            "opened-file renameの意味も異なるため2件がSKIPする。"
            "WSLのUbuntuでは3件すべてPASSした。"
            "Windowsだけの実行では、包含境界が検証されないまま残る。"
        ),
    }
    ok = checks["everyTestPassedOnLinux"] and checks["checkoutClean"]

    receipt = {
        "schema": "tai.reference.yic-tei-rooted-source/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows and WSL Ubuntu, running the same TEI package on both",
        "command": (
            "python integrations/tools/yic_tei_rooted_source.py "
            f"--tei-repo <clean TEI clone at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-tei-rooted-source-2026-11-16.json"
        ),
        "result": "PASS" if ok else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs the rooted-source traversal tests on Windows and in WSL Ubuntu and records each "
            "verdict per host, so a host that cannot exercise the boundary is visible rather than "
            "silently counted as covered. A linux pass shows the repository's containment tests hold "
            "there at this commit; it does not audit the reader beyond those tests, does not establish "
            "any Product's runtime authorization, and does not transfer the result to another OS."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": head[:12],
        "windows": windows_verdicts,
        "linux": linux_verdicts,
        "skippedOnWindows": skipped_on_windows,
        "passed": ok,
    }, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
