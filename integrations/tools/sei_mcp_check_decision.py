"""Call SEI's MCP check_decision for an allow and a deny case."""

import json
import os
import queue
import re
import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "evaluations/artifacts/sei-decision-projection.json"
RECEIPT = ROOT / "evaluations/records/SEI-TEI-mcp-check-2026-11-03.json"


def run(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def main():
    sei_repo = Path(os.environ.get("SEI_REPO", r"D:\GIT\hat47x\sei-cognition")) / "runtime" / "go"
    workdir = Path(tempfile.mkdtemp(prefix="tei-sei-mcp-check-", dir=os.environ.get("GOTMPDIR") or None))
    binary = workdir / ("sei.exe" if os.name == "nt" else "sei")
    build = run(["go", "build", "-o", str(binary), "./cmd/sei"], sei_repo)
    if build.returncode != 0:
        print(build.stderr, file=os.sys.stderr)
        return 1

    record = json.loads(ARTIFACT.read_text(encoding="utf-8"))["decision"]
    store = workdir / "store"
    run([str(binary), "init", "-data-root", str(store)], sei_repo)
    run(
        [
            str(binary), "add", "recommendation", "-data-root", str(store), "-id", "rec-mcp",
            "-statement", record["statement"], "-rationale", record["rationale"], "-responsible", "person:alice",
        ],
        sei_repo,
    )
    run(
        [
            str(binary), "add", "decision", "-data-root", str(store), "-id", record["refId"],
            "-statement", record["statement"], "-rationale", record["rationale"],
            "-recommendation", "rec-mcp", "-responsible", "person:alice",
        ],
        sei_repo,
    )
    run(
        [
            str(binary), "add", "decision", "-data-root", str(store), "-id", "decision-no-owner",
            "-statement", record["statement"], "-rationale", record["rationale"],
        ],
        sei_repo,
    )

    process = subprocess.Popen(
        [str(binary), "mcp", "-data-root", str(store)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace", bufsize=1,
    )
    lines = queue.Queue()
    threading.Thread(target=lambda: [lines.put(line) for line in process.stdout], daemon=True).start()

    def send(payload, expect_id):
        process.stdin.write(json.dumps(payload) + "\n")
        process.stdin.flush()
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                body = json.loads(lines.get(timeout=max(0.1, deadline - time.time())))
            except queue.Empty:
                break
            if body.get("id") == expect_id:
                return body
        return {}

    def payload(response):
        content = response.get("result", {}).get("content") or []
        for item in content:
            if item.get("type") == "text":
                try:
                    return json.loads(item["text"])
                except json.JSONDecodeError:
                    return {}
        return {}

    def verdict(response):
        return payload(response).get("verdict")

    send(
        {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "tai", "version": "0"}},
        },
        1,
    )
    allow = send(
        {
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": "check_decision", "arguments": {"decision": record["refId"], "require_recommendation": True}},
        },
        2,
    )
    deny = send(
        {
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "check_decision", "arguments": {"decision": "decision-no-owner"}},
        },
        3,
    )
    process.stdin.close()
    process.terminate()
    process.wait(timeout=15)

    checks = {
        "allowVerdict": verdict(allow) == "allow",
        "denyVerdict": verdict(deny) == "deny",
        "allowHasBinding": bool(payload(allow).get("binding", {}).get("decision_digest")),
        "denyHasReasons": bool(payload(deny).get("reasons")),
    }
    passed = all(checks.values())
    receipt = {
        "schema": "tai.reference.tei-sei-mcp-check/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with a locally built sei CLI and a temporary record store",
        "command": "python integrations/tools/sei_mcp_check_decision.py",
        "result": "PASS" if passed else "FAIL",
        "observed": {"checks": checks, "allowResult": allow.get("result"), "denyResult": deny.get("result")},
        "scope": "Calls SEI's MCP check_decision for one allow and one deny case. It does not test a real AI client or Authority verification.",
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(workdir, ignore_errors=True)
    print(json.dumps({"passed": passed, "checks": checks}))


if __name__ == "__main__":
    raise SystemExit(main())
