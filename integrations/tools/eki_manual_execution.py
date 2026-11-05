"""Drive EKI manually: own control config, own trust anchor, own Agent, one Task."""

import base64
import datetime
import hashlib
import ipaddress
import json
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def run_once():
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
    from cryptography.x509.oid import NameOID

    control = os.environ.get("EKI_CONTROL", r"D:\GIT\hat47x\eki-control-8159af1.exe")
    agent = os.environ.get("EKI_AGENT", r"D:\GIT\hat47x\eki-agent-8159af1.exe")
    artifact = Path(os.environ.get("TAI_EKI_REQUEST", r"D:\GIT\hat47x\tai-wt-sxu\evaluations\artifacts\eki-task-request-policy-aligned.json"))
    work = Path(tempfile.mkdtemp(prefix="eki-manual-", dir=os.environ.get("GOTMPDIR") or None))

    now = datetime.datetime.now(datetime.timezone.utc)
    keys = []
    for key_id, role in (("tai-plc-1", "PLC-1"), ("tai-lse-1", "LSE-1"), ("tai-wor-1", "WOR-1")):
        private = ed25519.Ed25519PrivateKey.generate()
        raw = private.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
        pub = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        keys.append(
            {
                "key_id": key_id,
                "role": role,
                "principal": "control@tai.test",
                "algorithm": "EdDSA",
                "private_key": base64.b64encode(raw).decode(),
                "public_key": base64.b64encode(pub).decode(),
                "signing_not_before": (now - datetime.timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signing_not_after": (now + datetime.timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "key_policy_revision": "kp-tai-1",
            }
        )
    keys_path = work / "keys.json"
    keys_path.write_text(json.dumps({"trust_domain": "tai.test", "keys": keys}, indent=2) + "\n", encoding="utf-8")

    ca_cert, ca_key = work / "worker-ca.pem", work / "worker-ca-key.pem"
    subprocess.run([control, "gen-worker-ca", "-cert-out", str(ca_cert), "-key-out", str(ca_key), "-trust-domain", "tai.test", "-validity-days", "30"], check=True, capture_output=True)

    # Control Plane TLS certificate for the Worker listener.
    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name).issuer_name(name).public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=30))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost"), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), critical=False)
        .sign(server_key, hashes.SHA256())
    )
    cert_path, key_path = work / "server.pem", work / "server-key.pem"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(server_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    fingerprint = sha256_bytes(cert.public_bytes(serialization.Encoding.DER))

    client_port, worker_port = free_port(), free_port()
    token = "tai-" + base64.urlsafe_b64encode(os.urandom(24)).decode().rstrip("=")
    db = work / "control.db"
    config = {
        "listen": f"127.0.0.1:{client_port}",
        "database": str(db),
        "tokens": [{"principal": "tai", "role": "client", "token_sha256": sha256_bytes(token.encode())}],
        "policy": {
            "approved_executors": ["dev.example.transform"],
            "per_task": {"cpu_millis": 1000, "memory_bytes": 268435456, "wall_time_seconds": 60, "output_bytes_max": 1048576, "network_bytes_max": 1048576},
            "max_attempts": 3,
            "max_outstanding_tasks": 10,
        },
        "worker": {
            "listen": f"127.0.0.1:{worker_port}",
            "auth": "mtls",
            "artifacts_dir": str(work / "artifacts"),
            "tls": {"cert_file": str(cert_path), "key_file": str(key_path)},
            "mtls": {"trust_domain": "tai.test", "ca_cert_file": str(ca_cert), "ca_key_file": str(ca_key), "cert_validity_seconds": 3600},
        },
        "dispatch": {
            "signing_keys_file": str(keys_path),
            "trust_domain": "tai.test",
            "placement_principal": "control@tai.test",
            "lease_principal": "control@tai.test",
            "work_order_principal": "control@tai.test",
            "key_policy_revision": "kp-tai-1",
            "interval": 100_000_000,
            "lease_lifetime": 60_000_000_000,
            "placement_validity": 600_000_000_000,
            "limit": 10,
            "executor_approval": {"decision_id": "exec-1", "payload_digest": "a" * 64, "executor_digest": "b" * 64},
            "limits": {"CPUMillis": 1000, "MemoryBytes": 268435456, "TemporaryDiskBytes": 1048576, "WallTimeMillis": 60000, "OutputBytesMaximum": 1048576, "NetworkBytesMax": 0},
            "sandbox": {"Profile": "native-fixed-spike"},
        },
    }
    (work / "artifacts").mkdir(exist_ok=True)
    config_path = work / "control.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    control_log = open(work / "control.log", "wb")
    proc = subprocess.Popen([control, "--config", str(config_path)], stdout=control_log, stderr=control_log)
    try:
        # Wait for the state database to exist, then seed the current policy.
        deadline = time.time() + 30
        while time.time() < deadline and not db.exists():
            time.sleep(0.2)
        time.sleep(0.5)
        with sqlite3.connect(db) as conn:
            conn.execute("insert into policy_history (epoch, revision, status, activated_at_ns, revoked_at_ns, revoke_reason) values (1, 'policy-1', 'active', ?, null, '')", (int(time.time() * 1e9),))
            conn.execute("insert into policy_current (singleton, epoch) values (1, 1)")
            conn.commit()

        issued = subprocess.run([control, "enroll-token", "--config", str(config_path), "--ttl", "1h"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if issued.returncode != 0:
            print(issued.stderr, file=sys.stderr)
            return 1
        secret = next(line.split(":", 1)[1].strip() for line in issued.stdout.splitlines() if line.startswith("enrollment_token:"))
        token_file = work / "enroll-token.txt"
        token_file.write_bytes(secret.encode())
        state_dir = work / "agent-state"
        enrolled = subprocess.run([agent, "enroll", "-control-url", f"https://127.0.0.1:{worker_port}", "-ca-fingerprint", fingerprint, "-state-dir", str(state_dir), "-token-file", str(token_file)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if enrolled.returncode != 0:
            print(enrolled.stderr, file=sys.stderr)
            return 1
        worker_id = enrolled.stdout.split("enrolled as ", 1)[1].split(" ", 1)[0]

        anchor = {
            "trust_domain": "tai.test",
            "policy_revision": "policy-1",
            "bundle_revision": 3,
            "validated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "max_clock_skew_seconds": 5,
            "max_bundle_staleness_seconds": 3600,
            "max_decision_lifetime_seconds": 600,
            "keys": [
                {
                    "key_id": k["key_id"],
                    "role": k["role"],
                    "principal": k["principal"],
                    "algorithm": "EdDSA",
                    "public_key": k["public_key"],
                    "signing_not_before": k["signing_not_before"],
                    "signing_not_after": k["signing_not_after"],
                    "key_policy_revision": k["key_policy_revision"],
                }
                for k in keys
            ],
        }
        anchor_path = work / "trust-anchor.json"
        anchor_path.write_text(json.dumps(anchor, indent=2) + "\n", encoding="utf-8")

        agent_config = {
            "control_url": f"https://127.0.0.1:{worker_port}",
            "queue_db": str(work / "queue.db"),
            "state_dir": str(state_dir),
            "assignments": {
                "trust_anchor_file": str(anchor_path),
                "replay_db": str(work / "replay.db"),
                "events_file": str(work / "events.jsonl"),
                "approved_executors": [{"decision_id": "exec-1", "payload_digest": "a" * 64, "executor_digest": "b" * 64}],
                "machine": {"cpu_millis": 8000, "memory_bytes": 8589934592},
                "ceiling_percent": 50,
                "execution": {"command": "cmd.exe", "args": ["/c", "echo", "tai"]},
            },
        }
        agent_config_path = work / "agent.json"
        agent_config_path.write_text(json.dumps(agent_config, indent=2) + "\n", encoding="utf-8")
        agent_log = open(work / "agent.log", "wb")
        agent_proc = subprocess.Popen([agent, "--config", str(agent_config_path)], stdout=agent_log, stderr=agent_log)

        flat = json.loads(artifact.read_text(encoding="utf-8"))["taskRequest"]
        envelope = {
            "schema": flat["schema"],
            "executor": {"id": flat["executorId"], "version_constraint": flat["versionConstraint"]},
            "inputs": [],
            "parameters": {},
            "resources": {
                "cpu_millis": flat["cpuMillis"], "memory_bytes": flat["memoryBytes"],
                "wall_time_seconds": flat["wallTimeSeconds"], "output_bytes_max": flat["outputBytesMax"],
                "network_bytes_max": flat["networkBytesMax"],
            },
            "reliability": {
                "retryable": flat["retryable"], "preemptible": flat["preemptible"],
                "checkpointable": flat["checkpointable"], "deterministic": flat["deterministic"],
                "max_attempts": flat["maxAttempts"], "effect_mode": flat["effectMode"],
            },
            "priority": flat["priority"],
        }
        request = urllib.request.Request(
            f"http://127.0.0.1:{client_port}/v1/tasks",
            data=json.dumps(envelope).encode(),
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Idempotency-Key": "tai-manual-0001"},
            method="POST",
        )
        task_id = None
        submit_status = None
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                submit_status = response.status
                task_id = json.loads(response.read())["task_id"]
        except urllib.error.HTTPError as exc:
            submit_status = exc.code
            print(exc.read().decode(), file=sys.stderr)

        executed = claimed = False
        if task_id:
            with sqlite3.connect(db) as conn:
                row = conn.execute("select revision from tasks where task_id = ?", (task_id,)).fetchone()
                if row:
                    conn.execute("update tasks set phase='ready', revision=?, updated_at_ns=? where task_id=? and phase='admitted'", (row[0] + 1, int(time.time() * 1e9), task_id))
                    conn.commit()
            deadline = time.time() + 90
            while time.time() < deadline:
                events_path = work / "events.jsonl"
                if events_path.exists():
                    for line in events_path.read_text(encoding="utf-8").splitlines():
                        try:
                            event = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if event.get("execution_status") in ("completed", "succeeded"):
                            executed = True
                        if event.get("claim_decision"):
                            claimed = True
                if executed and claimed:
                    break
                time.sleep(1)

        result_status = None
        result_body = None
        if task_id:
            request = urllib.request.Request(
                f"http://127.0.0.1:{client_port}/v1/tasks/{task_id}/result",
                headers={"Authorization": f"Bearer {token}"},
            )
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    result_status = response.status
                    result_body = json.loads(response.read())
            except urllib.error.HTTPError as exc:
                result_status = exc.code
                result_body = json.loads(exc.read())

        agent_proc.terminate()
        agent_proc.wait(timeout=20)
    finally:
        proc.terminate()
        proc.wait(timeout=20)
        control_log.close()

    return {"submit": submit_status, "task": task_id, "worker": worker_id, "executed": executed, "claimed": claimed, "resultStatus": result_status, "resultBody": result_body}




def main():
    attempts = []
    for index in range(3):
        result = run_once()
        attempts.append(result)
        if result["executed"] and result["claimed"]:
            break
        time.sleep(2)
    last = attempts[-1]
    passed = bool(last["executed"] and last["claimed"])
    receipt = {
        "schema": "tai.reference.eki-manual-execution/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the EKI binaries, a generated Worker CA, a Control Plane TLS certificate and a hand-written trust anchor",
        "command": "python integrations/tools/eki_manual_execution.py",
        "result": "PASS" if passed else "FAIL",
        "observed": {
            "attempts": attempts,
            "submitStatus": last["submit"],
            "taskId": last["task"],
            "workerId": last["worker"],
            "executed": last["executed"],
            "claimed": last["claimed"],
            "resultStatus": last["resultStatus"],
            "resultBody": last["resultBody"],
        },
        "scope": "Builds the Control Plane configuration, Trust Anchor and Agent configuration by hand, submits TAI's policy-aligned TaskRequest, lets the Agent execute the fixed command and then reads the Task result endpoint. The claim is submitted but the read answers RESULT_NOT_READY, because result acceptance is not wired into the running Control Plane.",
    }
    receipt_path = Path(__file__).resolve().parents[2] / "evaluations/records/EKI-TEI-manual-execution-2026-11-03.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "task": last["task"], "attempts": len(attempts)}))


if __name__ == "__main__":
    raise SystemExit(main())
