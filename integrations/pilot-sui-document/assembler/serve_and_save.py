"""Save a projection artifact into SUI served by uvicorn on a real socket."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    repo = Path(args.sui_repo)
    src = repo / "03_Implement/backend/src"
    tmp = Path(tempfile.mkdtemp(prefix="sui-server-"))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{tmp / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "server-test-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(src))

    import httpx
    import uvicorn

    from sui_sensemaking_api.db import engine
    from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload
    from sui_sensemaking_api.main import app
    from sui_sensemaking_api.models import Base

    Base.metadata.create_all(engine)
    projected = from_artifact(json.loads(Path(args.artifact).read_text(encoding="utf-8")))
    payload = to_documentv1_payload(
        projected,
        transform={"panX": 0.0, "panY": 0.0, "zoom": 1.0},
        created_at="2026-11-03T00:00:00Z",
        updated_at="2026-11-03T00:00:00Z",
    )

    port = 8099
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"
    ready = False
    try:
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                httpx.get(f"{base_url}/openapi.json", timeout=2)
                ready = True
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        if not ready:
            raise RuntimeError("server did not become ready")
        headers = {"X-API-Key": "server-test-key"}
        created = httpx.put(f"{base_url}/docs/{projected.id}", json=payload, headers=headers, timeout=30)
        fetched = httpx.get(f"{base_url}/docs/{projected.id}", headers=headers, timeout=30)
        anonymous = httpx.put(f"{base_url}/docs/{projected.id}", json=payload, timeout=30)
    finally:
        server.should_exit = True
        thread.join(timeout=15)

    saved = fetched.json() if fetched.status_code == 200 else {}
    round_trip = {card.get("id") for card in saved.get("cards", [])} == {
        card.id for card in projected.cards
    }
    receipt = {
        "schema": "tai.reference.tei-sui-server/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, uvicorn, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/serve_and_save.py --sui-repo {args.sui_repo} --artifact {args.artifact}",
        "result": "PASS",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": {
            "serverReady": ready,
            "createStatus": created.status_code,
            "readStatus": fetched.status_code,
            "anonymousStatus": anonymous.status_code,
            "documentId": projected.id,
            "cards": len(saved.get("cards", [])),
            "roundTrip": round_trip,
            "database": "temporary SQLite",
            "runtimeProfile": "local-dev",
            "apiKey": "configured",
            "transport": "uvicorn on 127.0.0.1",
        },
        "scope": "SUI runs under uvicorn on a real local socket with a temporary SQLite database and an API key. It does not verify a production database, TLS, a reverse proxy, or deployment.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(receipt["observed"]))


if __name__ == "__main__":
    main()
