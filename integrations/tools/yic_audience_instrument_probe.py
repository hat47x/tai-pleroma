"""Check whether SUI's access decision varies with the audience, not just the tenant.

P is the stage with no instrument. Before building one, this asks the narrower
question a reader would ask: does the product's own decision function take a
recipient into account at all? `AccessRequest` has `subject` (who is asking) and
`resource` (what is asked for); an audience is who the result may be shown to, which
is a different thing.

The probe drives `resolve_access_decision` with a recording adapter and compares two
requests that differ only in the requester's roles and groups. If the decision is
identical either way, the function is not judging the recipient.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

SUI = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(r"D:\GIT\hat47x\sui-sensemaking")
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


def decision(subject, adapter):
    return resolve_access_decision(
        adapter=adapter,
        request=AccessRequest(
            action="read",
            auth=AuthContext(actor_ref="user-1", user_id="user-1"),
            tenant=TenantContext(
                tenant_id="tenant-a", membership_id="m-a", resolved_by="verified_claim"
            ),
            resource=AccessResource(doc_id="doc-1", tenant_id="tenant-a"),
            subject=subject,
        ),
        fail_safe_mode="deny",
        require_tenant_scope=True,
    )


out = {}
fields = sorted(AccessRequest.__dataclass_fields__)
out["requestFields"] = fields
out["hasAudienceField"] = any("audience" in f.lower() for f in fields)
out["hasRecipientField"] = any("recipient" in f.lower() for f in fields)

a = decision(AccessSubject(actor_ref="user-1", roles=("reader",)), Recording())
b = decision(AccessSubject(actor_ref="user-2", roles=("admin",), groups=("g-admin",)), Recording())
out["allowWithReader"] = a.allow
out["allowWithAdmin"] = b.allow
out["sameDecision"] = (a.allow, a.reason) == (b.allow, b.reason)
print(json.dumps(out))
"""


def main():
    artifact = sys.argv[1] if len(sys.argv) > 1 else "evaluations/artifacts/scn-003-document.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "evaluations/records/YIC-audience-instrument-2026-11-18.json"

    root = Path(__file__).resolve().parents[2]
    script_file = Path(os.environ.get("TEMP", "/tmp")) / "yic-audience-probe.py"
    script_file.write_text(SCRIPT, encoding="utf-8")
    # Translate the temp path to its WSL mount form without embedding a workspace path.
    drive = script_file.drive.rstrip(":").lower()
    wsl_path = "/mnt/" + drive + script_file.as_posix()[2:]

    sui_drive = SUI.drive.rstrip(":").lower()
    backend_wsl = "/mnt/" + sui_drive + SUI.as_posix()[2:] + "/03_Implement/backend"
    completed = subprocess.run(
        ["wsl", "-d", DISTRO, "--", "env", "-u", "PATH", "bash", "-lc",
         "export PATH=/usr/bin:/bin; "
         f"cd {backend_wsl} && $HOME/suivenv/bin/python {wsl_path}"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800,
    )
    body = (completed.stdout or "").strip()
    if not body.startswith("{"):
        print((completed.stderr or body)[:400], file=sys.stderr)
        return 1
    observed = json.loads(body)

    head = subprocess.run(
        ["git", "-C", str(SUI), "rev-parse", "HEAD"], capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    ).stdout.strip()

    import hashlib

    def digest(path):
        return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()

    observed.update({
        "suiCommit": head,
        "distro": DISTRO,
        "finding": (
            "SUIの`AccessRequest`に`audience`も`recipient`も無く、"
            "`subject`（誰が求めているか）と`resource`（何を求めるか）だけがある。"
            "依頼者のroles/groupsを変えても判定が同じなら、"
            "**この関数は受信者を判定していない**。"
            "Pの計器を作るには、まず受信者を表す欄が要る。"
        ),
        "whatWouldBeNeededForP": (
            "AccessRequestに受信者（audience）を表す欄を追加し、"
            "同じresource・異なるaudienceで判定が変わることを示す試験。"
        ),
    })
    passed = (
        observed.get("hasAudienceField") is False
        and observed.get("hasRecipientField") is False
        and observed.get("sameDecision") is True
    )

    receipt = {
        "schema": "tai.reference.yic-audience-instrument/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": f"Windows host running WSL {DISTRO}, driving SUI's access decision",
        "command": (
            "python integrations/tools/yic_audience_instrument_probe.py "
            f"<artifact> {out}"
        ),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": artifact, "digest": digest(root / artifact)},
        "observed": observed,
        "scope": (
            "Calls SUI's resolve_access_decision twice with requests that differ only in the "
            "requester's roles and groups, and records whether the decision changed and whether the "
            "request type has any field naming an audience. It shows the function does not judge a "
            "recipient; it does not prove that no other SUI entry could, and it does not test a real "
            "PDP."
        ),
    }
    (root / out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: observed[k] for k in (
        "hasAudienceField", "hasRecipientField", "sameDecision", "allowWithReader", "allowWithAdmin"
    ) if k in observed}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
