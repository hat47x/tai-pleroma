"""Measure the strongest P-shaped decision found so far: a per-resource-kind override.

SUI's shared decision entrypoint forces `source_snapshot` resources into deny-on-error
and tenant scope, even when the caller omits the requirement. That is a policy the
product applies to a category of resource without waiting for anyone, which is closer
to a disclosure decision than the four entries examined previously. It still is not
recipient-specific, and this records both facts.

Runs the boundary tests on linux and checks that the caller-forgets case is covered.
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
TESTS = "tests/test_r2_source_policy_core_boundary.py"
# Cases that show the product overriding the caller, not just honouring a request.
OVERRIDE_TESTS = (
    "test_source_tenant_scope_is_required_even_if_caller_forgets",
    "test_source_never_inherits_document_read_only_fallback",
    "test_source_other_actions_are_not_implicitly_granted",
    "test_source_never_accepts_built_in_allow_all_or_mock_adapter",
)
SUMMARY = re.compile(r"^[=\s]*(?P<passed>\d+) passed", re.M)
FAILED = re.compile(r"^[=\s]*(?P<count>\d+) failed", re.M)
PARAM = re.compile(r"\[(?P<case>[^\]]+)\]")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    repo = Path(args.sui_repo).resolve()
    backend = repo / "03_Implement/backend"
    if not (backend / TESTS).exists():
        print(f"missing {TESTS}", file=sys.stderr)
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
        f"$HOME/suivenv/bin/python -m pytest {TESTS} -v --no-header 2>&1 | tail -30"
    )
    completed = subprocess.run(
        ["wsl", "-d", DISTRO, "--", "env", "-u", "PATH", "bash", "-lc", script],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    passed_match = SUMMARY.search(output)
    failed_match = FAILED.search(output)

    # Collect the test names that actually ran, including parametrised cases.
    ran = re.findall(r"^tests/[^\s:]+::([A-Za-z0-9_]+)", output, re.M)
    ran_names = sorted(set(ran))
    overrides_ran = [name for name in OVERRIDE_TESTS if name in ran_names]
    overrides_absent = [name for name in OVERRIDE_TESTS if name not in ran_names]

    source = (backend / "src/sui_sensemaking_api/access_control.py").read_text(encoding="utf-8")
    forces_deny = 'request.resource.kind == "source_snapshot"' in source
    forces_tenant_scope = "require_tenant_scope = True" in source
    rejects_builtin_adapters = '"noop", "mock"' in source

    checks = {
        "suiCommit": head,
        "checkoutClean": dirty == "",
        "distro": DISTRO,
        "testFile": TESTS,
        "passed": int(passed_match.group("passed")) if passed_match else 0,
        "failed": int(failed_match.group("count")) if failed_match else 0,
        "exit": completed.returncode,
        "overrideTestsRan": overrides_ran,
        "overrideTestsAbsent": overrides_absent,
        "forcesDenyForSourceSnapshot": forces_deny,
        "forcesTenantScopeForSourceSnapshot": forces_tenant_scope,
        "rejectsBuiltinAdaptersForSource": rejects_builtin_adapters,
        "everyOverrideTestRan": not overrides_absent,
        "suiteGreen": (
            (failed_match is None or int(failed_match.group("count")) == 0)
            and bool(passed_match)
            and int(passed_match.group("passed")) > 0
        ),
        "summaryLineParsed": bool(passed_match),
        "whatItDecides": "source_snapshot resources are forced to deny-on-error and tenant scope",
        "whatItDoesNotDecide": "recipient- or audience-specific disclosure permission",
        "finding": (
            "SUIの`resolve_access_decision`は、`resource.kind == \"source_snapshot\"`のとき、"
            "呼出し側が`require_tenant_scope`を省いても強制的に真へ変え、"
            "`fail_safe_mode`も`deny`へ変える。さらに`noop`/`mock`アダプタを拒否する。"
            "これは**呼出し側の意図を製品が上書きする**判断であり、"
            "確認した中で最もPに近い。それでも判定対象はリソース種別であって、"
            "受信者・Audienceではない。"
        ),
    }
    passed = checks["suiteGreen"] and checks["everyOverrideTestRan"] and checks["checkoutClean"]

    receipt = {
        "schema": "tai.reference.yic-sui-source-policy/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": f"Windows host running WSL {DISTRO}, executing the SUI source policy boundary tests",
        "command": (
            "python integrations/tools/yic_sui_source_policy_boundary.py "
            f"--sui-repo <SUI checkout at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-sui-source-policy-2026-11-17.json"
        ),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs SUI's source-policy boundary tests on linux and checks that the entrypoint forces "
            "deny-on-error, tenant scope and adapter rejection for source_snapshot resources even "
            "when the caller omits the requirement. It shows the product overrides the caller for a "
            "resource kind; it does not show a recipient- or audience-specific disclosure permission, "
            "a real organization PDP, or any external delivery."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": head[:12],
        "passed": checks["passed"],
        "failed": checks["failed"],
        "overrideTestsRan": len(overrides_ran),
        "absent": overrides_absent,
        "ok": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
