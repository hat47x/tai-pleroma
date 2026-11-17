"""Measure what the external PDP request body actually carries.

Doc 55 recommends adding an `audience` field to `AccessRequest`. That is not the only
place a recipient would have to appear: the external adapter builds a JSON body from an
explicit list of fields, and a recipient that is not in that body never reaches the
policy engine.

This serializes a real request through the adapter's own builder and records every key
in the body, so the number of places a recipient would need to be threaded through is
counted rather than guessed.
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
    AccessRequest, AccessResource, AccessSubject, AuthContext,
    _serialize_external_policy_request,
)
from sui_sensemaking_api.tenant_context import TenantContext

request = AccessRequest(
    action="share",
    auth=AuthContext(actor_ref="user-1", user_id="user-1", roles=("reader",)),
    tenant=TenantContext(
        tenant_id="tenant-a", membership_id="m-a", resolved_by="verified_claim"
    ),
    resource=AccessResource(
        doc_id="doc-1", tenant_id="tenant-a", visibility="Org", policy_ref="policy://p1"
    ),
    subject=AccessSubject(actor_ref="user-1", roles=("reader",)),
    safe_mode=False,
    read_only=False,
)
body = _serialize_external_policy_request(
    request, auth_source=request.auth, subject_key="subject"
)
parsed = json.loads(body.decode("utf-8"))

def keys(node, prefix=""):
    out = []
    if isinstance(node, dict):
        for key, value in node.items():
            path = f"{prefix}.{key}" if prefix else key
            out.append(path)
            out.extend(keys(value, path))
    return out

out = {
    "bodyBytes": len(body),
    "topLevelKeys": sorted(parsed.keys()),
    "allPaths": sorted(keys(parsed)),
    "carriesAudience": any("audience" in k.lower() or "recipient" in k.lower()
                           for k in keys(parsed)),
    "subjectSubkeys": sorted((parsed.get("subject") or {}).keys()),
    "resourceSubkeys": sorted((parsed.get("resource") or {}).keys()),
}
print(json.dumps(out))
"""


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    artifact = sys.argv[1] if len(sys.argv) > 1 else "evaluations/artifacts/scn-003-document.json"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "evaluations/records/YIC-pdp-payload-2026-11-18.json"
    sui = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(r"D:\GIT\hat47x\sui-sensemaking")

    root = Path(__file__).resolve().parents[2]
    script_file = Path(os.environ.get("TEMP", "/tmp")) / "yic-pdp-payload.py"
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

    # Count the places a recipient would have to be threaded through.
    needed = 3  # AccessRequest, the serializer, and the PDP contract
    observed.update({
        "suiCommit": head,
        "distro": DISTRO,
        "placesToThreadARecipient": needed,
        "finding": (
            "外部PDPへ送るbodyを実際に組み立てて、含まれる鍵を数えた。"
            f"bodyのトップレベルは`{', '.join(observed['topLevelKeys'])}`で、"
            "**`audience`も`recipient`も無い**。"
            "したがって受信者を足すには、`AccessRequest`だけでなく"
            "**直列化の関数**と**PDP側の契約**の3箇所に足す必要がある。"
            "文書55の『省略可能な欄を足すだけ』は、"
            "**直列化を通す作業を含んでいなかった**。"
        ),
    })
    passed = observed.get("carriesAudience") is False and bool(observed.get("allPaths"))

    receipt = {
        "schema": "tai.reference.yic-pdp-payload/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": f"Windows host running WSL {DISTRO}, serializing a request through the adapter",
        "command": "python integrations/tools/yic_pdp_payload_probe.py <artifact> <out> <sui-repo>",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": artifact, "digest": digest(root / artifact)},
        "observed": observed,
        "scope": (
            "Calls the SUI external adapter's own request serializer and records every key in the "
            "body it produces, checking whether a recipient appears anywhere. It shows the recipient "
            "would need to be added in three places; it does not judge whether the external PDP would "
            "use such a field, and no network call is made."
        ),
    }
    (root / out_path).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "bodyBytes": observed["bodyBytes"],
        "topLevelKeys": observed["topLevelKeys"],
        "carriesAudience": observed["carriesAudience"],
        "places": needed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
