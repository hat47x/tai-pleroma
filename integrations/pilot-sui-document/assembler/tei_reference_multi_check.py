"""Bind two different TEI artifacts to two documents and read each back."""

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
    parser.add_argument("--sei-artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="sui-tei-ref2-", dir=os.environ.get("GOTMPDIR") or None))
    doc_artifact = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    sei_artifact = json.loads(Path(args.sei_artifact).read_text(encoding="utf-8"))
    doc_a = doc_artifact.get("document", {}).get("id") or "doc-1"
    doc_b = "doc-2"
    reference = workdir / "tei-reference"
    for doc_id, kind, payload in [
        (doc_a, "documentv1-projection", doc_artifact),
        (doc_b, "epistemic-context", sei_artifact),
    ]:
        bound = reference / "tenants" / "local-default" / doc_id
        bound.mkdir(parents=True, exist_ok=True)
        (bound / f"{kind}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (reference / "epistemic-bindings.json").write_text(
        json.dumps(
            {
                "bindings": [
                    {"tenantId": "local-default", "docId": doc_a, "artifactKind": "documentv1-projection"},
                    {"tenantId": "local-default", "docId": doc_b, "artifactKind": "epistemic-context"},
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
    projected = from_artifact(doc_artifact)
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
    created = first = second = unbound = None
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                httpx.get(f"{base}/openapi.json", timeout=2)
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        created = httpx.put(f"{base}/docs/{doc_a}", json=payload, headers=headers, timeout=60)
        first = httpx.get(f"{base}/docs/{doc_a}/epistemic/projection", headers=headers, timeout=30)
        second = httpx.get(f"{base}/docs/{doc_b}/epistemic/projection", headers=headers, timeout=30)
        unbound = httpx.get(f"{base}/docs/doc-unbound/epistemic/projection", headers=headers, timeout=30)
    finally:
        server.should_exit = True
        thread.join(timeout=20)

    first_text = json.dumps(first.json(), ensure_ascii=False) if first is not None and first.status_code == 200 else ""
    second_text = json.dumps(second.json(), ensure_ascii=False) if second is not None and second.status_code == 200 else ""
    checks = {
        "createStatus": created.status_code if created else None,
        "firstStatus": first.status_code if first else None,
        "secondStatus": second.status_code if second else None,
        "firstHasDocumentSchema": doc_artifact.get("schema", "") in first_text,
        "secondHasSeiSchema": sei_artifact.get("schema", "") in second_text,
        "firstNotSei": sei_artifact.get("schema", "") not in first_text,
        "secondNotDocument": doc_artifact.get("schema", "") not in second_text,
        "unboundStatus": unbound.status_code if unbound else None,
    }
    passed = all(
        [
            checks["createStatus"] in (200, 201),
            checks["firstStatus"] == 200,
            checks["secondStatus"] == 200,
            checks["firstHasDocumentSchema"],
            checks["secondHasSeiSchema"],
            checks["firstNotSei"],
            checks["secondNotDocument"],
            checks["unboundStatus"] == 404,
        ]
    )
    receipt = {
        "schema": "tai.reference.sui-tei-reference-multi/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with SUI reading a local TEI reference directory holding two bindings",
        "command": "python integrations/pilot-sui-document/assembler/tei_reference_multi_check.py --sui-repo <SUI> --artifact evaluations/artifacts/scn-003-document.json --sei-artifact evaluations/artifacts/sei-decision-projection.json --out evaluations/records/SUI-TEI-reference-multi-2026-11-03.json",
        "result": "PASS" if passed else "FAIL",
        "artifacts": {"document": digest(args.artifact), "sei": digest(args.sei_artifact)},
        "observed": checks,
        "scope": "Binds two different TEI artifacts to two documents through SUI's local reference directory and checks that each document returns only its own artifact. SUI echoes artifacts verbatim.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
