"""Run two SUI instances against one PostgreSQL and check cross-instance ETag behaviour."""

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    import pgserver

    workdir = Path(tempfile.mkdtemp(prefix="sui-multi-", dir=os.environ.get("GOTMPDIR") or None))
    server = pgserver.get_server(str(workdir / "pg"))
    uri = server.get_uri()
    src = str(Path(args.sui_repo) / "03_Implement/backend/src")
    base_env = {
        **os.environ,
        "SUI_DATABASE_URL": uri,
        "SUI_RUNTIME_PROFILE": "local-dev",
        "SUI_LLM_PROVIDER": "none",
        "SUI_LOG_LEVEL": "ERROR",
        "SUI_API_KEY": "multi-key",
        "PYTHONPATH": src,
    }
    base_env.pop("SUI_ADMIN_API_KEY", None)
    os.environ.update({k: v for k, v in base_env.items() if k.startswith("SUI_")})
    sys.path.insert(0, src)

    import httpx
    from sqlalchemy import text

    from sui_sensemaking_api.db import engine
    from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload
    from sui_sensemaking_api.models import Base

    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                "insert into tenants (id, display_name, lifecycle_state, created_at, updated_at) "
                "values ('local-default', 'Local', 'active', '2026-11-03T00:00:00Z', '2026-11-03T00:00:00Z') "
                "on conflict (id) do nothing"
            )
        )
    projected = from_artifact(json.loads(Path(args.artifact).read_text(encoding="utf-8")))
    payload = to_documentv1_payload(
        projected,
        transform={"panX": 0.0, "panY": 0.0, "zoom": 1.0},
        created_at="2026-11-03T00:00:00Z",
        updated_at="2026-11-03T00:00:00Z",
    )

    ports = [free_port(), free_port()]
    processes = []
    for port in ports:
        processes.append(
            subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "sui_sensemaking_api.main:app", "--host", "127.0.0.1", "--port", str(port), "--log-level", "error"],
                env=base_env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        )
    bases = [f"http://127.0.0.1:{port}" for port in ports]
    headers = {"X-API-Key": "multi-key"}
    ready = False
    created = cross_read = None
    updated = stale = None
    try:
        deadline = time.time() + 90
        while time.time() < deadline:
            try:
                httpx.get(f"{bases[0]}/openapi.json", timeout=2)
                httpx.get(f"{bases[1]}/openapi.json", timeout=2)
                ready = True
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        if not ready:
            raise RuntimeError("instances did not become ready")
        created = httpx.put(f"{bases[0]}/docs/{projected.id}", json=payload, headers=headers, timeout=60)
        etag_a = created.headers.get("ETag")
        cross_read = httpx.get(f"{bases[1]}/docs/{projected.id}", headers=headers, timeout=60)
        etag_b = cross_read.headers.get("ETag")
        updated = httpx.put(
            f"{bases[1]}/docs/{projected.id}",
            json={**payload, "title": "from-b"},
            headers={**headers, "If-Match": etag_b},
            timeout=60,
        )
        stale = httpx.put(
            f"{bases[0]}/docs/{projected.id}",
            json={**payload, "title": "from-a"},
            headers={**headers, "If-Match": etag_a},
            timeout=60,
        )
    finally:
        for process in processes:
            process.terminate()
        for process in processes:
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()

    checks = {
        "instancesReady": ready,
        "createStatus": created.status_code if created else None,
        "crossReadStatus": cross_read.status_code if cross_read else None,
        "crossUpdateStatus": updated.status_code if updated else None,
        "staleUpdateStatus": stale.status_code if stale else None,
    }
    passed = (
        checks["instancesReady"]
        and checks["createStatus"] in (200, 201)
        and checks["crossReadStatus"] == 200
        and checks["crossUpdateStatus"] == 200
        and checks["staleUpdateStatus"] == 409
    )
    receipt = {
        "schema": "tai.reference.sui-multi-instance/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with one embedded PostgreSQL and two SUI processes",
        "command": "python integrations/pilot-sui-document/assembler/postgres_multi_instance_check.py --sui-repo <SUI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/SUI-TEI-multi-instance-2026-11-03.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Runs two SUI processes against one PostgreSQL, creates on the first, reads and updates on the second, and confirms the first instance's stale ETag is refused. Both processes ran on the same host.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
