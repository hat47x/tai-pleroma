"""Bind a TEI projection artifact into SUI's local reference directory and read it back."""

import argparse
import hashlib
import json
import os
import socket
import sys
import tempfile
import threading
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

    workdir = Path(tempfile.mkdtemp(prefix="sui-tei-ref-", dir=os.environ.get("GOTMPDIR") or None))
    artifact = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    doc_id = artifact.get("document", {}).get("id") or "doc-1"
    reference = workdir / "tei-reference"
    bound = reference / "tenants" / "local-default" / doc_id
    bound.mkdir(parents=True, exist_ok=True)
    (bound / "documentv1-projection.json").write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (reference / "epistemic-bindings.json").write_text(
        json.dumps(
            {
                "bindings": [
                    {
                        "tenantId": "local-default",
                        "docId": doc_id,
                        "artifactKind": "documentv1-projection",
                    }
                ]
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    os.environ["SUI_DATABASE_URL"] = f"sqlite+pysqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "ref-key"
    os.environ["SUI_TEI_REFERENCE_DIR"] = str(reference)
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    import httpx
    import uvicorn
    from sqlalchemy import text

    from sui_sensemaking_api.db import engine
    from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload
    from sui_sensemaking_api.main import app
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
    projected = from_artifact(artifact)
    payload = to_documentv1_payload(
        projected,
        transform={"panX": 0.0, "panY": 0.0, "zoom": 1.0},
        created_at="2026-11-03T00:00:00Z",
        updated_at="2026-11-03T00:00:00Z",
    )

    port = free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    headers = {"X-API-Key": "ref-key"}
    created = projection = missing = None
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                httpx.get(f"{base}/openapi.json", timeout=2)
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        created = httpx.put(f"{base}/docs/{doc_id}", json=payload, headers=headers, timeout=60)
        projection = httpx.get(f"{base}/docs/{doc_id}/epistemic/projection", headers=headers, timeout=30)
        missing = httpx.get(f"{base}/docs/doc-unbound/epistemic/projection", headers=headers, timeout=30)
    finally:
        server.should_exit = True
        thread.join(timeout=20)

    body = projection.json() if projection is not None and projection.status_code == 200 else {}
    missing_body = missing.json() if missing is not None else {}
    checks = {
        "createStatus": created.status_code if created else None,
        "projectionStatus": projection.status_code if projection else None,
        "artifactEchoed": artifact.get("schema", "") in json.dumps(body, ensure_ascii=False),
        "unknownBindingStatus": missing.status_code if missing else None,
        "unknownBindingCode": (missing_body.get("detail") or {}).get("code"),
    }
    passed = (
        checks["createStatus"] in (200, 201)
        and checks["projectionStatus"] == 200
        and checks["artifactEchoed"]
        and checks["unknownBindingStatus"] == 404
        and checks["unknownBindingCode"] == "epistemic_binding_not_found"
    )
    receipt = {
        "schema": "tai.reference.sui-tei-reference/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with SUI reading a local TEI reference directory",
        "command": "python integrations/pilot-sui-document/assembler/tei_reference_check.py --sui-repo <SUI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/SUI-TEI-reference-2026-11-03.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Binds one TEI projection artifact into SUI's local reference directory and reads it back through the document API. SUI echoes the artifact verbatim; consumer-side schema validation is out of scope.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
