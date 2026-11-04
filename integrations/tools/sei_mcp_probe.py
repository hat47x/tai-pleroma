"""Probe SEI's MCP stdio server with the JSON-RPC calls an AI tool would send."""

import json
import os
import queue
import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "evaluations/artifacts/sei-decision-projection.json"
RECEIPT = ROOT / "evaluations/records/SEI-TEI-mcp-2026-11-03.json"


def run(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def main():
    sei_repo = Path(os.environ.get("SEI_REPO", r"D:\GIT\hat47x\sei-cognition")) / "runtime" / "go"
    workdir = Path(tempfile.mkdtemp(prefix="tei-sei-mcp-", dir=os.environ.get("GOTMPDIR") or None))
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
            str(binary), "add", "decision", "-data-root", str(store), "-id", record["refId"],
            "-statement", record["statement"], "-rationale", record["rationale"],
            "-responsible", "person:alice", "-source", "tai-tei-projection",
        ],
        sei_repo,
    )

    process = subprocess.Popen(
        [str(binary), "mcp", "-data-root", str(store)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    lines = queue.Queue()

    def reader():
        for line in process.stdout:
            lines.put(line)

    threading.Thread(target=reader, daemon=True).start()

    def send(payload, expect_id):
        process.stdin.write(json.dumps(payload) + "\n")
        process.stdin.flush()
        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                line = lines.get(timeout=max(0.1, deadline - time.time()))
            except queue.Empty:
                break
            body = json.loads(line)
            if body.get("id") == expect_id:
                return body
        return {}

    init = send(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "tai", "version": "0"},
            },
        },
        1,
    )
    tools = send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, 2)
    call = send(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "resume", "arguments": {}},
        },
        3,
    )

    process.stdin.close()
    process.terminate()
    process.wait(timeout=15)

    tool_names = [tool.get("name") for tool in tools.get("result", {}).get("tools", [])]
    call_text = json.dumps(call.get("result", {}))
    checks = {
        "initialize": init.get("result", {}).get("protocolVersion") is not None,
        "toolsListed": bool(tool_names),
        "resumeTool": "resume" in tool_names,
        "callOk": "error" not in call,
        "callMentionsRecord": record["refId"] in call_text or record["statement"][:10] in call_text,
    }
    passed = all(checks.values())
    receipt = {
        "schema": "tai.reference.tei-sei-mcp/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with a locally built sei CLI and a temporary record store",
        "command": "python integrations/tools/sei_mcp_probe.py",
        "result": "PASS" if passed else "FAIL",
        "observed": {
            "checks": checks,
            "tools": tool_names,
            "initializeResult": init.get("result"),
            "callResult": call.get("result"),
        },
        "scope": "Sends initialize, tools/list and tools/call resume over SEI's stdio MCP server. It does not test a real AI client, session namespacing or write tools.",
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(workdir, ignore_errors=True)
    print(json.dumps({"passed": passed, "checks": checks, "tools": tool_names}))


if __name__ == "__main__":
    raise SystemExit(main())
