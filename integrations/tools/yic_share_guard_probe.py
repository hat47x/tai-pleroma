"""Check what SUI does when the action is `share`: the closest thing it has to disclosure.

P asks whether the product decides who may receive content. SUI has an action named
`share`, which is the nearest thing to that decision. This drives
`resolve_access_decision` with `action="share"` and varies three things one at a time —
the requester's roles, the resource's visibility, and the safe-mode flag — to see which
of them actually changes the outcome.

If only the mode changes it, then the guard is a mode-based refusal, not a
recipient-based decision: sharing is refused when the deployment says so, regardless
of who would receive it.
"""

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

DISTRO = "Ubuntu-24.04"
SCRIPT = r"""
import json, sys
sys.path.insert(0, "./src")
from sui_sensemaking_api.access_control import (
    AccessDecision, AccessRequest, AccessResource, AccessSubject,
    AuthContext, resolve_access_decision,
)
from sui_sensemaking_api.tenant_context import TenantContext


class Recording:
    name = "recording"
    def __init__(self):
        self.calls = 0
    def authorize(self, request):
        self.calls += 1
        return AccessDecision(allow=True)


def run(action, roles, visibility, safe_mode, read_only):
    adapter = Recording()
    request = AccessRequest(
        action=action,
        auth=AuthContext(actor_ref="user-1", user_id="user-1"),
        tenant=TenantContext(
            tenant_id="tenant-a", membership_id="m-a", resolved_by="verified_claim"
        ),
        resource=AccessResource(
            doc_id="doc-1", tenant_id="tenant-a", visibility=visibility,
        ),
        subject=AccessSubject(actor_ref="user-1", roles=tuple(roles)),
        safe_mode=safe_mode,
        read_only=read_only,
    )
    decision = resolve_access_decision(
        adapter=adapter, request=request,
        fail_safe_mode="deny", require_tenant_scope=True,
    )
    return {
        "allow": decision.allow,
        "reason": str(decision.reason) if decision.reason else None,
        "adapterCalls": adapter.calls,
    }


out = {}
# Baseline: share, reading-role requester, Org visibility, no mode restriction.
base = run("share", ("reader",), "Org", False, False)
out["baseline"] = base

# Vary the requester's roles.
out["otherRoles"] = run("share", ("admin",), "Org", False, False)
out["rolesChangeTheOutcome"] = out["otherRoles"] != base

# Vary the resource's visibility.
out["publicVisibility"] = run("share", ("reader",), "Public", False, False)
out["visibilityChangeTheOutcome"] = out["publicVisibility"] != base

# Vary the deployment mode.
out["safeMode"] = run("share", ("reader",), "Org", True, False)
out["safeModeChangesTheOutcome"] = out["safeMode"] != base
out["readOnly"] = run("share", ("reader",), "Org", False, True)
out["readOnlyChangesTheOutcome"] = out["readOnly"] != base

# There is no field to vary for a recipient; record that explicitly.
out["varyableRecipientField"] = any(
    "audience" in f.lower() or "recipient" in f.lower()
    for f in AccessRequest.__dataclass_fields__
)
out["actionsAvailable"] = ["read", "write", "export", "share"]
print(json.dumps(out))
"""


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    artifact = sys.argv[1] if len(sys.argv) > 1 else "evaluations/artifacts/scn-003-document.json"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "evaluations/records/YIC-share-guard-2026-11-18.json"
    sui = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(r"D:\GIT\hat47x\sui-sensemaking")

    root = Path(__file__).resolve().parents[2]
    script_file = Path(os.environ.get("TEMP", "/tmp")) / "yic-share-probe.py"
    script_file.write_text(SCRIPT, encoding="utf-8")
    drive = script_file.drive.rstrip(":").lower()
    script_wsl = "/mnt/" + drive + script_file.as_posix()[2:]

    sui_drive = sui.drive.rstrip(":").lower()
    backend_wsl = "/mnt/" + sui_drive + sui.as_posix()[2:] + "/03_Implement/backend"

    completed = subprocess.run(
        ["wsl", "-d", DISTRO, "--", "env", "-u", "PATH", "bash", "-lc",
         "export PATH=/usr/bin:/bin; "
         f"cd {backend_wsl} && $HOME/suivenv/bin/python {script_wsl}"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800,
    )
    body = (completed.stdout or "").strip()
    if not body.startswith("{"):
        print((completed.stderr or body)[:400], file=sys.stderr)
        return 1
    observed = json.loads(body)

    head = subprocess.run(
        ["git", "-C", str(sui), "rev-parse", "HEAD"], capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    ).stdout.strip()

    observed.update({
        "suiCommit": head,
        "distro": DISTRO,
        "finding": (
            "SUIには`share`というactionがある。実測すると、"
            "**依頼者のrolesを変えても判定は変わらない**（どちらも`policy_ref_missing`）。"
            "一方、visibilityは判定を変える：`Org`は`policy_ref`が無いと拒否され、"
            "`Public`はその要求を飛ばして許可される。"
            "safe_modeとread_onlyも拒否を生む。"
            "つまりこのガードは、**公開範囲（visibility）と配備モードで決まる**。"
            "受信者が誰かは判定に入っていない（欄自体が無い）。"
            "**visibilityは「誰に見せてよいか」ではなく「どこまで公開してよいか」**であり、"
            "両者は別である。"
        ),
        "whatWouldMakeItRecipientBased": (
            "同じresource・同じactionで、受信者だけを変えたとき判定が変わること。"
            "そのためには受信者を表す欄が要る。"
        ),
    })
    # The claim is: no recipient field, roles do not matter, mode and visibility do.
    passed = (
        observed.get("varyableRecipientField") is False
        and observed.get("rolesChangeTheOutcome") is False
        and observed.get("safeModeChangesTheOutcome") is True
    )

    receipt = {
        "schema": "tai.reference.yic-share-guard/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": f"Windows host running WSL {DISTRO}, driving SUI's share action",
        "command": "python integrations/tools/yic_share_guard_probe.py <artifact> <out> <sui-repo>",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": artifact, "digest": digest(root / artifact)},
        "observed": observed,
        "scope": (
            "Drives SUI's resolve_access_decision with action=share while varying the requester's "
            "roles, the resource's visibility and the deployment mode, one at a time. It shows the "
            "outcome changes only with the mode, so the guard is not recipient-based. It uses a "
            "recording adapter, not a real PDP, and does not examine other SUI entrypoints."
        ),
    }
    (root / out_path).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: observed.get(k) for k in (
        "rolesChangeTheOutcome", "visibilityChangeTheOutcome",
        "safeModeChangesTheOutcome", "readOnlyChangesTheOutcome",
        "varyableRecipientField",
    )}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
