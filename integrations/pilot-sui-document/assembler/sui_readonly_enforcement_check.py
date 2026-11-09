"""Check whether a read-only allow actually restricts a write.

`AccessDecision` can express "allow, but read only". This calls SUI's own
resolution and enforcement functions with a stub adapter that returns exactly
that, and records whether a write is refused. A second adapter that denies is
used as a control, so a "no refusal" result is not a harness artifact.
"""

import argparse
import hashlib
import json
import os
import sys
import subprocess
import time
from pathlib import Path

PROBE = """
import json, sys

from sui_sensemaking_api.access_control import (
    AccessDecision,
    AccessRequest,
    AccessResource,
    enforce_access,
    resolve_access_decision,
)


class ReadOnlyAllow:
    name = "stub-read-only-allow"

    def authorize(self, request):
        return AccessDecision(allow=True, read_only=True, reason="stub")


class PlainDeny:
    name = "stub-deny"

    def authorize(self, request):
        return AccessDecision(allow=False, read_only=False, reason="stub")


def request_for(action):
    return AccessRequest(
        action=action,
        safe_mode=False,
        read_only=False,
        resource=AccessResource(doc_id="doc-1", visibility="Private"),
    )


def attempt(adapter, action):
    request = request_for(action)
    decision = resolve_access_decision(
        adapter=adapter, request=request, fail_safe_mode="read_only", require_tenant_scope=False
    )
    refused = False
    detail = None
    try:
        enforce_access(decision, action=action)
    except Exception as error:  # noqa: BLE001 - the refusal itself is the observation
        refused = True
        detail = str(getattr(error, "detail", error))
    return {"allow": decision.allow, "readOnly": decision.read_only, "refused": refused, "detail": detail}


results = {
    "readOnlyAllowWrite": attempt(ReadOnlyAllow(), "write"),
    "readOnlyAllowRead": attempt(ReadOnlyAllow(), "read"),
    "denyWrite": attempt(PlainDeny(), "write"),
}
print(json.dumps(results))
"""


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    src = Path(args.sui_repo) / "03_Implement/backend/src"
    completed = subprocess.run(
        [sys.executable, "-c", PROBE],
        env={**os.environ, "PYTHONPATH": str(src)},
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    lines = (completed.stdout or "").strip().splitlines()
    if completed.returncode != 0 or not lines:
        print((completed.stderr or "")[-600:], file=sys.stderr)
        return 1
    observed = json.loads(lines[-1])

    checks = {
        "adapterReturnedReadOnlyAllow": observed["readOnlyAllowWrite"]["allow"] is True
        and observed["readOnlyAllowWrite"]["readOnly"] is True,
        "writeNotRefused": observed["readOnlyAllowWrite"]["refused"] is False,
        "readAllowed": observed["readOnlyAllowRead"]["refused"] is False,
        "denyIsRefused": observed["denyWrite"]["refused"] is True,
        "observation": observed,
        "readOnlyDoesNotRestrictWrite": observed["readOnlyAllowWrite"]["refused"] is False,
    }
    passed = (
        checks["adapterReturnedReadOnlyAllow"]
        and checks["writeNotRefused"]
        and checks["denyIsRefused"]
        and checks["readAllowed"]
    )
    receipt = {
        "schema": "tai.reference.sui-readonly-enforcement/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python and SUI's access_control module called directly",
        "command": f"python integrations/pilot-sui-document/assembler/sui_readonly_enforcement_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-readonly-enforcement-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Calls SUI's resolve_access_decision and enforce_access with a stub adapter that returns allow-plus-read-only, and with a denying adapter as a control. It records that the read-only decision does not refuse a write while a deny does, so the enforcement point ignores the read-only flag. It exercises the functions directly, not an HTTP route, and the stub is not a real PDP.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: checks[key] for key in (
        "adapterReturnedReadOnlyAllow", "writeNotRefused", "readAllowed", "denyIsRefused",
    )}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
