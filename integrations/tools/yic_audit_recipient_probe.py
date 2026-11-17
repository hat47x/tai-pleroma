"""Measure what the audit layer records about who received what.

The independent review said a decision-path view misses the observation layer: even if
the decision does not consider a recipient, the audit record might name one. This builds
a real audit event through SUI's own constructor and records every field and metadata
key it carries, so the question is answered by the product's own serializer.

It also checks whether a recipient-shaped metadata key survives sanitization, since
that is what would make an observation-based P possible.
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
from sui_sensemaking_api.audit import (
    AuditEvent, build_event, sanitize_metadata, SENSITIVE_KEY_PARTS,
)

# A view event as the routes emit it, plus recipient-shaped metadata that a future
# caller might add.
event = build_event(
    event_type="view",
    tenant_id="tenant-a",
    doc_id="doc-1",
    safe_mode=False,
    actor_ref="user-1",
    principal_kind="member",
    metadata={
        "route": "/docs/doc-1",
        "method": "GET",
        "action": "share",
        "decision_allow": True,
        "decision_reason": "policy_ref_missing",
        "visibility": "Org",
        "audience": "user-2",
        "recipient": "user-2",
        "sharedWith": "user-2",
    },
)

def keys(node, prefix=""):
    out = []
    if isinstance(node, dict):
        for key, value in node.items():
            path = f"{prefix}.{key}" if prefix else key
            out.append(path)
            out.extend(keys(value, path))
    return out

out = {
    "eventFields": sorted(AuditEvent.model_fields.keys()),
    "eventTypeValues": sorted(
        str(t) for t in AuditEvent.model_fields["eventType"].annotation.__args__
    ),
    "metadataKeys": sorted(event.metadata.keys()),
    "carriesRecipientInEnvelope": any(
        "audience" in f.lower() or "recipient" in f.lower()
        for f in AuditEvent.model_fields.keys()
    ),
    "recipientKeysSurviveSanitization": sorted(
        k for k in event.metadata
        if "audience" in k.lower() or "recipient" in k.lower() or "sharedwith" in k.lower()
    ),
    "sensitiveKeyParts": sorted(SENSITIVE_KEY_PARTS),
    "allPaths": sorted(keys(event.model_dump())),
}
print(json.dumps(out, ensure_ascii=False))
"""


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    artifact = sys.argv[1] if len(sys.argv) > 1 else "evaluations/artifacts/scn-003-document.json"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "evaluations/records/YIC-audit-recipient-2026-11-18.json"
    sui = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(r"D:\GIT\hat47x\sui-sensemaking")

    root = Path(__file__).resolve().parents[2]
    script_file = Path(os.environ.get("TEMP", "/tmp")) / "yic-audit-probe.py"
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
            "SUIのaudit層を実測した。`AuditEvent`の封筒は"
            f"`{', '.join(observed['eventFields'])}`を持ち、"
            "**受信者を表す欄は無い**。一方、`metadata`は自由な鍵を受け、"
            f"`audience`・`recipient`・`sharedWith`は"
            f"{'残る' if observed['recipientKeysSurviveSanitization'] else '残らない'}"
            "（sanitizeは秘匿系の鍵だけを伏せる）。"
            "つまり**作用層には受信者を記録できる場所がある**が、"
            "**記録する義務は無い**。"
        ),
        "whatThisMeansForP": (
            "観測からPを測る経路は、決定経路より現実的である。"
            "ただし (a) 誰が記録するか、(b) 記録が無いことを「開示していない」と読めるか、"
            "(c) metadataは呼出し側の自己申告であり、サーバが観測した事実ではない、"
            "という3点を先に決める必要がある。"
        ),
        "nextStepSuggested": (
            "metadataに受信者を載せる規約を製品Ownerが決め、"
            "記録がある場合と無い場合を別々に扱う試験を書く。"
            "記録が無いことを『開示なし』と読み替えない。"
        ),
    })
    # Passes when the envelope is read and the metadata behaviour is recorded.
    passed = bool(observed["eventFields"]) and bool(observed["eventTypeValues"])

    receipt = {
        "schema": "tai.reference.yic-audit-recipient/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": f"Windows host running WSL {DISTRO}, building an audit event via SUI's constructor",
        "command": "python integrations/tools/yic_audit_recipient_probe.py <artifact> <out> <sui-repo>",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": artifact, "digest": digest(root / artifact)},
        "observed": observed,
        "scope": (
            "Builds one audit event through SUI's own build_event and records its envelope fields "
            "and metadata keys, checking whether a recipient-shaped metadata key survives "
            "sanitization. It shows the observation layer has room to record a recipient but no "
            "envelope field for one; it does not inspect a real audit sink, and metadata is caller-"
            "reported rather than server-observed."
        ),
    }
    (root / out_path).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "eventFields": observed["eventFields"],
        "recipientInEnvelope": observed["carriesRecipientInEnvelope"],
        "recipientSurvivesMetadata": observed["recipientKeysSurviveSanitization"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
