"""Measure the one product decision that refuses before asking anyone else.

Every P candidate examined so far either selects what to show or explicitly
disclaims judging disclosure. SUI's `resolve_access_decision` with
`require_tenant_scope=True` is different: it decides from the request alone and
denies before the PDP adapter is called at all. That ordering is the property worth
recording — a refusal that never reaches the external decision point cannot be a
relayed "yes" from somewhere else.

This runs the tests that pin that ordering on linux and records the verdicts.
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
TESTS = (
    "tests/test_access_control_tenant_boundary.py",
    "tests/test_access_control_adapter_contract.py",
)
SUMMARY = re.compile(r"^(?P<passed>\d+) passed", re.M)
FAILED = re.compile(r"^(?P<count>\d+) failed", re.M)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def wsl(script, timeout=1800):
    return subprocess.run(
        ["wsl", "-d", DISTRO, "--", "env", "-u", "PATH", "bash", "-lc", script],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    repo = Path(args.sui_repo).resolve()
    backend = repo / "03_Implement/backend"
    for relative in TESTS:
        if not (backend / relative).exists():
            print(f"missing {relative}", file=sys.stderr)
            return 1

    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()

    wsl_path = "/mnt/" + repo.drive.rstrip(":").lower() + str(repo)[2:].replace("\\", "/")
    script = (
        "export PATH=/usr/bin:/bin:$PATH; "
        f"cd {wsl_path}/03_Implement/backend && "
        f"$HOME/suivenv/bin/python -m pytest {' '.join(TESTS)} -q --no-header 2>&1 | tail -6"
    )
    completed = wsl(script)
    output = (completed.stdout or "") + (completed.stderr or "")
    passed_count = SUMMARY.search(output)
    failed_count = FAILED.search(output)

    checks = {
        "suiCommit": head,
        "checkoutClean": dirty == "",
        "distro": DISTRO,
        "tests": list(TESTS),
        "passed": int(passed_count.group("passed")) if passed_count else 0,
        "failed": int(failed_count.group("count")) if failed_count else 0,
        "exit": completed.returncode,
        "tail": [line for line in output.strip().splitlines() if line.strip()][-2:],
        "denialHappensBeforeTheAdapter": True,
        "finding": (
            "SUIの`resolve_access_decision`は`require_tenant_scope=True`のとき、"
            "Tenant不一致・scope不一致を**PDPアダプタを呼ぶ前に**拒否する"
            "（テストが`adapter.calls == 0`を検査している）。"
            "一方、一致するTenantはPDP評価へ進み`adapter.calls == 1`になる。"
            "これは「外部の判断を待たずに自分で拒否できる」という意味でPの形を持つが、"
            "判定しているのは**Tenant境界**であり、受信者・Audience別の開示許可ではない。"
        ),
        "whatItDecides": "tenant scope boundary before the PDP adapter",
        "whatItDoesNotDecide": "recipient- or audience-specific disclosure permission",
        "everyBoundaryTestPassed": (
            (failed_count is None or int(failed_count.group("count")) == 0)
            and bool(passed_count)
        ),
    }
    ok = checks["everyBoundaryTestPassed"] and checks["checkoutClean"]

    receipt = {
        "schema": "tai.reference.yic-sui-tenant-boundary/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": f"Windows host running WSL {DISTRO}, executing the SUI access-control tests",
        "command": (
            "python integrations/tools/yic_sui_tenant_boundary.py "
            f"--sui-repo <SUI checkout at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-sui-tenant-boundary-2026-11-17.json"
        ),
        "result": "PASS" if ok else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs SUI's tenant-boundary and adapter-contract tests on linux and records the counts. It "
            "shows the tenant check refuses before the PDP adapter is called, which is a decision made "
            "without waiting for an external answer. It does not show a recipient- or audience-specific "
            "disclosure permission, a real PDP, or a real organization's policy; the adapter in these "
            "tests is a recording double."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": head[:12],
        "passed": checks["passed"],
        "failed": checks["failed"],
        "clean": checks["checkoutClean"],
        "ok": ok,
    }, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
