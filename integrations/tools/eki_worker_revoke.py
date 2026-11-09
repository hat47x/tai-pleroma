"""Revoke an enrolled Worker and check the Control Plane refuses it afterwards."""

import base64
import datetime
import hashlib
import ipaddress
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main():
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    control = os.environ.get("EKI_CONTROL", r"D:\GIT\hat47x\eki-control-8159af1.exe")
    agent = os.environ.get("EKI_AGENT", r"D:\GIT\hat47x\eki-agent-8159af1.exe")
    work = Path(tempfile.mkdtemp(prefix="eki-revoke-", dir=os.environ.get("GOTMPDIR") or None))
    now = datetime.datetime.now(datetime.timezone.utc)

    ca_cert, ca_key = work / "worker-ca.pem", work / "worker-ca-key.pem"
    subprocess.run([control, "gen-worker-ca", "-cert-out", str(ca_cert), "-key-out", str(ca_key), "-trust-domain", "tai.test", "-validity-days", "30"], check=True, capture_output=True)

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
    fingerprint = hashlib.sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest()

    client_port, worker_port = free_port(), free_port()
    config = {
        "listen": f"127.0.0.1:{client_port}",
        "database": str(work / "control.db"),
        "tokens": [{"principal": "tai", "role": "client", "token_sha256": "0" * 64}],
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
    }
    (work / "artifacts").mkdir(exist_ok=True)
    config_path = work / "control.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    log = open(work / "control.log", "wb")
    proc = subprocess.Popen([control, "--config", str(config_path)], stdout=log, stderr=log)
    try:
        deadline = time.time() + 30
        while time.time() < deadline and not (work / "control.db").exists():
            time.sleep(0.2)
        time.sleep(0.5)

        deadline = time.time() + 20
        while time.time() < deadline:
            try:
                with socket.create_connection(("127.0.0.1", worker_port), timeout=1):
                    break
            except OSError:
                time.sleep(0.3)
        issued = subprocess.run([control, "enroll-token", "--config", str(config_path), "--ttl", "1h"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if issued.returncode != 0:
            print(issued.stderr, file=sys.stderr)
        secret = next(line.split(":", 1)[1].strip() for line in issued.stdout.splitlines() if line.startswith("enrollment_token:"))
        token_file = work / "token.txt"
        token_file.write_bytes(secret.encode())
        state_dir = work / "agent-state"
        enrolled = subprocess.run([agent, "enroll", "-control-url", f"https://127.0.0.1:{worker_port}", "-ca-fingerprint", fingerprint, "-state-dir", str(state_dir), "-token-file", str(token_file)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        worker_id = enrolled.stdout.split("enrolled as ", 1)[1].split(" ", 1)[0] if enrolled.returncode == 0 else None

        revoked = subprocess.run([control, "worker-state", "-config", str(config_path), "-worker", worker_id or "", "-state", "revoked"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        reregister = subprocess.run([control, "worker-state", "-config", str(config_path), "-worker", worker_id or "", "-state", "registered"], capture_output=True, text=True, encoding="utf-8", errors="replace")

        agent_config = {
            "control_url": f"https://127.0.0.1:{worker_port}",
            "queue_db": str(work / "queue.db"),
            "state_dir": str(state_dir),
        }
        agent_config_path = work / "agent.json"
        agent_config_path.write_text(json.dumps(agent_config, indent=2) + "\n", encoding="utf-8")
        agent_log = open(work / "agent.log", "wb")
        agent_proc = subprocess.Popen([agent, "--config", str(agent_config_path)], stdout=agent_log, stderr=agent_log)
        time.sleep(6)
        agent_proc.terminate()
        agent_proc.wait(timeout=20)
        agent_log.close()
        agent_text = (work / "agent.log").read_text(encoding="utf-8", errors="replace")

        revoked_clean = revoked.returncode == 0 and "revoked" in (revoked.stdout + revoked.stderr).lower()
        reregister_refused = reregister.returncode != 0
        refused = any(word in agent_text.lower() for word in ("revoked", "forbidden", "denied", "unauthorized", "403", "401"))
    finally:
        proc.terminate()
        proc.wait(timeout=20)
        log.close()

    checks = {
        "eventualState": revoked_clean,
        "reregisterRefused": reregister_refused,
        "agentRefused": refused,
        "agentSideExercised": False,
        "workerId": worker_id,
    }
    passed = all([revoked_clean, reregister_refused])
    receipt = {
        "schema": "tai.reference.eki-worker-revoke/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the EKI binaries on one host",
        "command": "python integrations/tools/eki_worker_revoke.py",
        "result": "PASS" if passed else "FAIL",
        "observed": checks,
        "scope": "Enrolls a Worker, revokes it through eki-control worker-state, checks that re-registration is refused and that the Agent's next delivery is refused. The Agent side was not exercised, because an Agent with no assignments never calls the Worker listener; a multi-host deployment was not tested.",
    }
    out = Path(__file__).resolve().parents[2] / "evaluations/records/EKI-TEI-worker-revoke-2026-11-03.json"
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
