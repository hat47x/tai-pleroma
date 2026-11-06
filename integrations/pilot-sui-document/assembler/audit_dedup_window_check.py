"""Check SUI's audit dedup window boundaries on the dispatcher itself."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


class RecordingTransport:
    name = "recording"

    def __init__(self, fail=False):
        self.sent = []
        self.fail = fail

    def send(self, event):
        if self.fail:
            raise RuntimeError("sink unavailable")
        self.sent.append(event)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="sui-dedupwin-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "dedup-window-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from sui_sensemaking_api.audit import AuditDispatcher, AuditEvent

    key = ("export-audit", "local-default", "doc-1", "bundle", "export-alpha")

    def event(index):
        return AuditEvent(
            eventId=f"audit-dedup-{index}",
            occurredAt="2026-11-06T00:00:00+00:00",
            eventType="export",
            tenantId="local-default",
            docId="doc-1",
            safeMode=False,
            metadata={"seq": index},
        )

    # window = 0 disables dedup entirely.
    zero_transport = RecordingTransport()
    zero = AuditDispatcher(
        enabled=True,
        allow_in_safe_mode=True,
        transport=zero_transport,
        queue_size=8,
        dedup_window_seconds=0.0,
    )
    zero_result = [zero.emit(event(index), dedup_key=key) for index in range(3)]

    # a positive window suppresses the repeat.
    transport = RecordingTransport()
    short = AuditDispatcher(
        enabled=True,
        allow_in_safe_mode=True,
        transport=transport,
        queue_size=8,
        dedup_window_seconds=0.2,
    )
    first = short.emit(event(1), dedup_key=key)
    immediate = short.emit(event(2), dedup_key=key)
    time.sleep(0.35)
    after_window = short.emit(event(3), dedup_key=key)

    # no dedup key => never suppressed.
    plain_transport = RecordingTransport()
    plain = AuditDispatcher(
        enabled=True,
        allow_in_safe_mode=True,
        transport=plain_transport,
        queue_size=8,
        dedup_window_seconds=0.2,
    )
    plain_results = [plain.emit(event(index)) for index in range(2)]

    # a failed send must stay retryable, so the key is not recorded.
    failing_transport = RecordingTransport(fail=True)
    failing = AuditDispatcher(
        enabled=True,
        allow_in_safe_mode=True,
        transport=failing_transport,
        queue_size=8,
        dedup_window_seconds=5.0,
    )
    failed = failing.emit(event(1), dedup_key=key)
    failed_again = failing.emit(event(2), dedup_key=key)

    checks = {
        "zeroWindowSentCount": len(zero_transport.sent),
        "zeroWindowReasons": [result.reason for result in zero_result],
        "firstReason": first.reason,
        "firstSent": first.sent,
        "immediateReason": immediate.reason,
        "immediateSent": immediate.sent,
        "windowSentCount": len(transport.sent),
        "afterWindowReason": after_window.reason,
        "afterWindowSent": after_window.sent,
        "plainSentCount": len(plain_transport.sent),
        "plainReasons": [result.reason for result in plain_results],
        "failedReason": failed.reason,
        "failedAgainReason": failed_again.reason,
        "failedSentCount": len(failing_transport.sent),
    }
    passed = (
        checks["zeroWindowSentCount"] == 3
        and checks["firstSent"] is True
        and checks["immediateSent"] is False
        and checks["immediateReason"] == "duplicate"
        and checks["windowSentCount"] == 2
        and checks["afterWindowSent"] is True
        and checks["plainSentCount"] == 2
        and checks["failedReason"] == "send_failed"
        and checks["failedSentCount"] == 0
    )
    receipt = {
        "schema": "tai.reference.sui-audit-dedup-window/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 driving SUI's AuditDispatcher with an in-process recording transport",
        "command": f"python integrations/pilot-sui-document/assembler/audit_dedup_window_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-dedup-window-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Emits the same dedup key with a zero window, a 0.2s window (immediate repeat, then after the window), without a key, and against a failing transport. It does not test the HTTP transport or a restart.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
