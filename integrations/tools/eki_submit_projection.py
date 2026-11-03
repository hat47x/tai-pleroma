"""Submit the projected TaskRequest to a real eki-control and record the answer."""

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def request(url, token, method="GET", body=None, idempotency_key=None):
    headers = {"Authorization": f"Bearer {token}"}
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8") or "{}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--control-binary", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--idempotency-key", default="tai-tei-projection-0001")
    args = parser.parse_args()

    record = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    generated = subprocess.run(
        [args.control_binary, "gen-token"], capture_output=True, encoding="utf-8", errors="replace"
    )
    token = ""
    token_hash = ""
    for line in generated.stdout.splitlines():
        if line.startswith("token:"):
            token = line.split(":", 1)[1].strip()
        if line.startswith("sha256:"):
            token_hash = line.split(":", 1)[1].strip()
    if not token or not token_hash:
        print(generated.stderr, file=sys.stderr)
        return 1

    workdir = Path(tempfile.mkdtemp(prefix="tei-eki-submit-", dir=os.environ.get("GOTMPDIR") or None))
    port = free_port()
    resources = record["resources"]
    config = {
        "listen": f"127.0.0.1:{port}",
        "database": str(workdir / "control.db"),
        "tokens": [{"principal": "tai", "role": "client", "token_sha256": token_hash}],
        "policy": {
            "approved_executors": [record["executor"]["id"]],
            "per_task": {
                "cpu_millis": resources["cpu_millis"],
                "memory_bytes": resources["memory_bytes"],
                "wall_time_seconds": resources["wall_time_seconds"],
                "output_bytes_max": resources["output_bytes_max"],
                "network_bytes_max": resources["network_bytes_max"],
            },
            "max_attempts": record["reliability"]["max_attempts"],
            "max_outstanding_tasks": 10,
        },
    }
    config_path = workdir / "control.json"
    config_path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")

    process = subprocess.Popen(
        [args.control_binary, "--config", str(config_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
    )
    base = f"http://127.0.0.1:{port}"
    submitted = status = repeat = None
    try:
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                status, _ = request(f"{base}/v1/tasks/tai-probe", token)
                break
            except urllib.error.HTTPError:
                status = 0
                break
            except Exception:
                time.sleep(0.5)
        if status is None:
            process.terminate()
            error_text = process.stderr.read() if process.stderr else ""
            raise RuntimeError("eki-control did not become ready: " + error_text.strip()[-500:])
        submitted, first = request(f"{base}/v1/tasks", token, "POST", record, args.idempotency_key)
        repeat, second = request(f"{base}/v1/tasks", token, "POST", record, args.idempotency_key)
        task_id = first.get("task_id") or first.get("taskId")
        status_code, status_body = request(f"{base}/v1/tasks/{task_id}", token) if task_id else (0, {})
    finally:
        process.terminate()
        process.wait(timeout=15)

    receipt = {
        "schema": "tai.reference.tei-eki-submit/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with a locally built eki-control and an embedded SQLite state store",
        "command": f"python integrations/tools/eki_submit_projection.py --control-binary <eki-control> --artifact {args.artifact}",
        "result": "PASS" if submitted == 202 and status_code == 200 else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": {
            "submitStatus": submitted,
            "repeatStatus": repeat,
            "taskId": (first or {}).get("task_id") or (first or {}).get("taskId"),
            "statusReadStatus": status_code,
            "taskStatus": (status_body or {}).get("status") or (status_body or {}).get("state"),
            "idempotent": bool(first) and bool(second) and first.get("task_id") == second.get("task_id"),
            "taskExecuted": False,
            "workerResult": False,
        },
        "scope": "Submits one projected TaskRequest to a real eki-control process. No Worker runs, so execution and results remain unverified.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt["observed"]))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
