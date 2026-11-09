"""Check SUI's agent credential read path: allowlist, redaction, and write refusal."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

HASH_KEY = "0" * 64


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def error_code(response):
    if response is None or response.status_code < 400:
        return None
    try:
        detail = response.json().get("detail")
    except ValueError:
        return None
    return detail.get("code") if isinstance(detail, dict) else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="sui-agentread-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "agent-read-key"
    os.environ["SUI_AGENT_CREDENTIAL_HASH_KEY"] = HASH_KEY
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from datetime import datetime, timedelta, timezone

    from fastapi.testclient import TestClient
    from sqlalchemy import text

    from sui_sensemaking_api.agent_credentials import AGENT_CREDENTIAL_HEADER, AgentCredentialRepository
    from sui_sensemaking_api.db import SessionLocal, engine
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
    granted_id = projected.id
    header_headers = {"X-API-Key": "agent-read-key"}

    review_targets = [card for card in payload.get("cards", []) if card.get("id")]
    if review_targets:
        review_targets[0] = {**review_targets[0], "textReviewed": True}
    payload["cards"] = [
        {**card, "textReviewed": True} if index == 0 and card.get("id") else card
        for index, card in enumerate(payload.get("cards", []))
    ]

    with TestClient(app) as client:
        created = client.put(f"/docs/{granted_id}", json=payload, headers=header_headers)
    with SessionLocal() as db:
        raw_token = AgentCredentialRepository(db, tenant_id="local-default").register(
            agent_id="agent-reader",
            label="Reader",
            created_by="local-user",
            expires_at=(datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            doc_ids=(granted_id,),
            hash_key=bytes.fromhex(HASH_KEY),
            now=datetime.now(timezone.utc),
        )
        db.commit()
    # The deployment-level business key still gates every route, so send it too.
    agent_headers = {AGENT_CREDENTIAL_HEADER: raw_token, "X-API-Key": "agent-read-key"}
    with TestClient(app) as client:
        # local-dev does not wire the agent hash key (only saas-multitenant does),
        # so supply it here to exercise the credentialed path.
        pre_wired = getattr(app.state, "agent_credential_hash_key", None)
        app.state.agent_credential_hash_key = bytes.fromhex(HASH_KEY)
        allowed = client.get(f"/docs/{granted_id}", headers=agent_headers)
        write_attempt = client.put(f"/docs/{granted_id}", json=payload, headers=agent_headers)
        list_attempt = client.get("/docs", headers=agent_headers)
        derived_attempt = client.get(f"/docs/{granted_id}/similar-candidate-groups", headers=agent_headers)
        unlisted = client.get("/docs/doc-not-granted", headers=agent_headers)
        mixed = client.get(
            f"/docs/{granted_id}",
            headers={**agent_headers, "X-Sui-Sensemaking-Authorization": "Bearer member-token"},
        )
        bad_token = client.get(
            f"/docs/{granted_id}",
            headers={AGENT_CREDENTIAL_HEADER: "suiag_notatoken", "X-API-Key": "agent-read-key"},
        )
        audit_ok = client.post(
            f"/docs/{granted_id}/context-audit",
            json={
                "operation": "query",
                "safeMode": True,
                "equivalenceKey": "a" * 64,
                "bundleHash": "b" * 64,
                "command": "context-query",
                "channel": "mcp",
            },
            headers=agent_headers,
        )
        audit_wrong_channel = client.post(
            f"/docs/{granted_id}/context-audit",
            json={
                "operation": "query",
                "safeMode": True,
                "equivalenceKey": "a" * 64,
                "bundleHash": "b" * 64,
                "command": "context-query",
                "channel": "api",
            },
            headers=agent_headers,
        )

    view = allowed.json() if allowed.status_code == 200 else {}
    cards = view.get("cards") or []
    checks = {
        "createStatus": created.status_code,
        "allowedStatus": allowed.status_code,
        "allowedHasEtag": "etag" in {key.lower() for key in allowed.headers},
        "cardCount": len(cards),
        "reviewedCardHasText": any(card.get("text") for card in cards),
        "unreviewedCardsWithheld": all(
            card.get("text") is None or card.get("text") == "" for card in cards if card.get("textReviewed") is not True
        ),
        "viewKeys": sorted(view.keys()),
        "titleWithheld": view.get("title") is None,
        "writeAttemptStatus": write_attempt.status_code,
        "writeAttemptCode": error_code(write_attempt),
        "listStatus": list_attempt.status_code,
        "listIds": [item.get("id") for item in list_attempt.json()] if list_attempt.status_code == 200 else None,
        "listTitlesWithheld": all(
            item.get("title") is None for item in list_attempt.json()
        ) if list_attempt.status_code == 200 else None,
        "listCreatorWithheld": all(
            item.get("created_by") is None for item in list_attempt.json()
        ) if list_attempt.status_code == 200 else None,
        "hashKeyWiredByProfile": pre_wired is not None,
        "derivedStatus": derived_attempt.status_code,
        "derivedCode": error_code(derived_attempt),
        "ungrantedStatus": unlisted.status_code,
        "ungrantedCode": error_code(unlisted),
        "mixedStatus": mixed.status_code,
        "mixedCode": error_code(mixed),
        "badTokenStatus": bad_token.status_code,
        "auditStatus": audit_ok.status_code,
        "auditWrongChannelStatus": audit_wrong_channel.status_code,
    }
    passed = (
        checks["createStatus"] == 200
        and checks["allowedStatus"] == 200
        and checks["allowedHasEtag"] is False
        and checks["cardCount"] > 0
        and checks["reviewedCardHasText"] is True
        and checks["unreviewedCardsWithheld"] is True
        and checks["titleWithheld"] is True
        and checks["writeAttemptStatus"] == 403
        and checks["writeAttemptCode"] == "agent_write_not_enabled"
        and checks["listStatus"] == 200
        and checks["listIds"] == [granted_id]
        and checks["listTitlesWithheld"] is True
        and checks["listCreatorWithheld"] is True
        and checks["derivedStatus"] == 403
        and checks["derivedCode"] == "agent_route_not_enabled"
        and checks["ungrantedStatus"] == 404
        and checks["ungrantedCode"] == "agent_document_not_granted"
        and checks["mixedStatus"] == 400
        and checks["mixedCode"] == "agent_credential_conflict"
        and checks["badTokenStatus"] == 401
        and checks["auditStatus"] == 200
        and checks["auditWrongChannelStatus"] == 403
    )
    receipt = {
        "schema": "tai.reference.sui-agent-read-path/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, FastAPI TestClient, and a temporary SQLite database",
        "command": f"python integrations/pilot-sui-document/assembler/agent_read_path_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-agent-read-path-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Registers one agent credential through the repository, then reads the granted document, attempts a write, a list, a derived view, an ungranted document, a mixed credential request, a bogus token, and two audit channels. It checks the allowlist and redaction rules, not a real external agent.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
