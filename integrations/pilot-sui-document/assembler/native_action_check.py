"""Check SUI's native Action v1 receiver: disabled by default, then guarded when enabled."""

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="sui-action-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "action-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from fastapi.testclient import TestClient
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

    projected = from_artifact(json.loads(Path(args.artifact).read_text(encoding="utf-8")))
    payload = to_documentv1_payload(
        projected,
        transform={"panX": 0.0, "panY": 0.0, "zoom": 1.0},
        created_at="2026-11-03T00:00:00Z",
        updated_at="2026-11-03T00:00:00Z",
    )
    headers = {"X-API-Key": "action-key"}
    doc_id = projected.id
    card_id = (payload.get("cards") or [{}])[0].get("id") or "card-1"

    def action(revision, *, card=card_id, x=100.0, y=50.0):
        return {
            "protocolVersion": "1",
            "applicationID": "sui",
            "resourceID": doc_id,
            "actionID": "sui.move",
            "expectedRevision": revision,
            "payload": {"cardId": card, "x": x, "y": y},
        }

    def code_of(response):
        if response is None:
            return None
        body = response.json() if response.content else {}
        return body.get("error") if isinstance(body, dict) else None

    result = {}
    with TestClient(app) as client:
        created = client.put(f"/docs/{doc_id}", json=payload, headers=headers)
        fetched = client.get(f"/docs/{doc_id}", headers=headers)
        revision = (fetched.headers.get("etag") or '""').strip('"')
        hop = {
            **headers,
            "X-TEI-Action": "commit",
            "Content-Type": "application/json",
        }
        disabled = client.post(f"/docs/{doc_id}/action-commit", json=action(revision), headers=hop)
        app.state.sui_native_action_v1_enabled = True
        missing_header = client.post(f"/docs/{doc_id}/action-commit", json=action(revision), headers={**headers, "Content-Type": "application/json"})
        bad_origin = client.post(
            f"/docs/{doc_id}/action-commit",
            json=action(revision),
            headers={**hop, "Origin": "https://elsewhere.example"},
        )
        stale = client.post(f"/docs/{doc_id}/action-commit", json=action("0" * 64), headers=hop)
        unknown_card = client.post(f"/docs/{doc_id}/action-commit", json=action(revision, card="card-absent"), headers=hop)
        read_only = client.post(
            f"/docs/{doc_id}/action-commit", json=action(revision), headers={**hop, "X-Read-Only": "1"}
        )
        committed = client.post(f"/docs/{doc_id}/action-commit", json=action(revision), headers=hop)
        replay = client.post(f"/docs/{doc_id}/action-commit", json=action(revision), headers=hop)
        after = client.get(f"/docs/{doc_id}", headers=headers)
        archived = client.post(f"/docs/{doc_id}/archive", headers=headers)
        archived_commit = client.post(
            f"/docs/{doc_id}/action-commit",
            json=action((after.headers.get("etag") or '""').strip('"')),
            headers=hop,
        )

    moved = None
    for card in (after.json().get("cards") or []):
        if card.get("id") == card_id:
            moved = {"x": card.get("x"), "y": card.get("y")}
    checks = {
        "createStatus": created.status_code,
        "disabledStatus": disabled.status_code,
        "disabledCode": code_of(disabled),
        "missingHeaderStatus": missing_header.status_code,
        "badOriginStatus": bad_origin.status_code,
        "badOriginCode": code_of(bad_origin),
        "staleRevisionStatus": stale.status_code,
        "staleRevisionCode": code_of(stale),
        "unknownCardStatus": unknown_card.status_code,
        "unknownCardCode": code_of(unknown_card),
        "readOnlyStatus": read_only.status_code,
        "commitStatus": committed.status_code,
        "commitBody": committed.json() if committed.content else {},
        "movedPosition": moved,
        "readAfterStatus": after.status_code,
        "replayStatus": replay.status_code,
        "replayCode": code_of(replay),
        "archiveStatus": archived.status_code,
        "archivedCommitStatus": archived_commit.status_code,
        "archivedCommitCode": code_of(archived_commit),
    }
    passed = (
        checks["createStatus"] == 200
        and checks["disabledStatus"] == 404
        and checks["disabledCode"] == "action_denied"
        and checks["missingHeaderStatus"] == 403
        and checks["badOriginStatus"] == 403
        and checks["staleRevisionStatus"] == 409
        and checks["staleRevisionCode"] == "revision_conflict"
        and checks["unknownCardStatus"] == 400
        and checks["unknownCardCode"] == "invalid_payload"
        and checks["readOnlyStatus"] == 403
        and checks["commitStatus"] == 200
        and checks["movedPosition"] == {"x": 100.0, "y": 50.0}
        and checks["replayStatus"] == 409
        and checks["replayCode"] == "revision_conflict"
        and checks["archiveStatus"] == 204
        and checks["archivedCommitStatus"] == 423
        and checks["archivedCommitCode"] == "action_denied"
    )
    receipt = {
        "schema": "tai.reference.sui-native-action-v1/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/native_action_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-native-action-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Calls SUI's Action v1 receiver with the feature flag off, then turns it on in-process and exercises header, origin, revision, card, read-only, replay and archive cases. It does not run a real TEI Host or verify authenticated sessions.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
