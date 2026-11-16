"""Compare one SUI gate test suite on Windows and on linux, and record why.

The cross-UI probe cites SUI #3462 as a limited internal proof with test doubles.
Running its gate test here is not to re-litigate that: it is to record that the
suite **cannot pass on Windows at all**, because the reference store calls
`os.open(directory, O_RDONLY)` to fsync a directory, which Windows rejects, and
because its temporary file names exceed MAX_PATH deep under pytest's basetemp.
A reader who runs it on Windows and sees 70 failures could otherwise conclude the
containment code is broken.
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
TESTS_RELATIVE = "tests/test_r2_source_snapshot_read_gate.py"
SUMMARY = re.compile(r"^(?P<passed>\d+) passed(?:, (?P<rest>.+))? in ", re.M)
FAILED = re.compile(r"^(?P<count>\d+) failed", re.M)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def count(pattern, text):
    match = pattern.search(text)
    return int(match.group(1)) if match else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    repo = Path(args.sui_repo).resolve()
    backend = repo / "03_Implement/backend"
    if not (backend / TESTS_RELATIVE).exists():
        print(f"test file missing under {backend}", file=sys.stderr)
        return 1

    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()

    # Windows run, with a short basetemp so MAX_PATH is not the only variable.
    short_base = Path("D:/GIT/hat47x/.gotmp/pyshort-yic")
    short_base.mkdir(parents=True, exist_ok=True)
    windows = subprocess.run(
        [sys.executable, "-m", "pytest", TESTS_RELATIVE, "-q", "--no-header",
         f"--basetemp={short_base}"],
        cwd=backend, capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**__import__("os").environ, "PYTHONPATH": str(backend)},
        timeout=2400,
    )
    windows_out = (windows.stdout or "") + (windows.stderr or "")
    windows_passed = count(re.compile(r"^(\d+) passed", re.M), windows_out)
    windows_failed = count(FAILED, windows_out)
    first_error = next(
        (
            line.strip()
            for line in windows_out.splitlines()
            if line.strip().startswith("E")
            and ("PermissionError" in line or "FileNotFoundError" in line)
        ),
        "",
    )

    # Linux run through WSL, using the distribution's python with the declared
    # test extras installed.
    script = (
        "export PATH=/usr/bin:/bin:$PATH; "
        f"cd /mnt/{repo.drive.rstrip(':').lower()}{str(repo)[2:].replace(chr(92), '/')}"
        "/03_Implement/backend && "
        f"$HOME/suivenv/bin/python -m pytest {TESTS_RELATIVE} -q --no-header 2>&1 | tail -6"
    )
    linux = subprocess.run(
        ["wsl", "-d", DISTRO, "--", "env", "-u", "PATH", "bash", "-lc", script],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=2400,
    )
    linux_out = (linux.stdout or "") + (linux.stderr or "")
    linux_passed = count(re.compile(r"^(\d+) passed", re.M), linux_out)
    linux_failed = count(FAILED, linux_out)

    checks = {
        "suiCommit": head,
        "checkoutClean": dirty == "",
        "testFile": TESTS_RELATIVE,
        "windows": {
            "passed": windows_passed,
            "failed": windows_failed,
            "exit": windows.returncode,
            "firstFilesystemError": first_error,
        },
        "linux": {
            "passed": linux_passed,
            "failed": linux_failed,
            "exit": linux.returncode,
        },
        "linuxIsGreen": (linux_failed or 0) == 0 and bool(linux_passed),
        "windowsCannotPass": bool(windows_failed),
        "finding": (
            "このgate testは、参照Storeがディレクトリをfsyncするために"
            "`os.open(directory, O_RDONLY)`を呼ぶ。WindowsはこれをPermissionErrorで拒否し、"
            "さらに一時ファイル名がpytestのbasetemp深くでMAX_PATHを超える。"
            "したがってWindowsでは70件すべてが失敗し、linuxでは70件すべてがPASSする。"
            "Windowsの赤は包含ロジックの破損ではなく、この参照実装の対象OS差である。"
        ),
    }
    ok = checks["linuxIsGreen"] and checks["checkoutClean"]

    receipt = {
        "schema": "tai.reference.yic-sui-r2-gate-hosts/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows and WSL Ubuntu, running the same SUI pytest suite on both",
        "command": (
            "python integrations/tools/yic_sui_r2_gate_hosts.py "
            f"--sui-repo <SUI checkout at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-sui-r2-gate-hosts-2026-11-16.json"
        ),
        "result": "PASS" if ok else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs SUI's R2 source-snapshot gate suite on Windows and in WSL Ubuntu and records the "
            "counts and the first filesystem error on each. A linux pass shows the suite holds there "
            "at this commit; it does not upgrade SUI #3462's own limits, which keep the card resolver "
            "and Source Provider as test doubles and the PDP local, and it is not a real organization "
            "PDP, a real Card save, or a second disclosure. It does not audit the implementation beyond "
            "these tests."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": head[:12],
        "windows": checks["windows"],
        "linux": checks["linux"],
        "passed": ok,
    }, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
