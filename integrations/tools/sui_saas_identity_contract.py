"""Check SUI's broker-token identity verification with a local JWKS stub."""

import base64
import json
import os
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SUI_SRC = None
TOKEN = {"value": ""}
JWKS = {"keys": []}


class RecordingStore:
    def __init__(self):
        self.created = []

    def create_auth_session(self, **kwargs):
        self.created.append(kwargs)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        payload = json.dumps(JWKS).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        self.rfile.read(int(self.headers.get("content-length", "0")))
        payload = json.dumps({"access_token": TOKEN["value"], "token_type": "Bearer", "expires_in": 3600}).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


def b64url(value):
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def main():
    os.environ.update(
        {
            "SUI_ADMIN_API_KEY": "test-admin-key",
            "SUI_SAAS_AUTH_SESSION_HASH_KEY": "a" * 64,
            "SUI_TENANT_CLAIM_NAME": "tenant_ref",
        }
    )
    sys.path.insert(0, SUI_SRC)

    import jwt
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from sui_sensemaking_api import models
    from sui_sensemaking_api import oauth_bff as bff

    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_numbers = private.public_key().public_numbers()

    def encode_int(value):
        length = (value.bit_length() + 7) // 8
        return b64url(value.to_bytes(length, "big"))

    JWKS["keys"] = [
        {
            "kty": "RSA",
            "use": "sig",
            "kid": "key-1",
            "alg": "RS256",
            "n": encode_int(public_numbers.n),
            "e": encode_int(public_numbers.e),
        }
    ]

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    jwks_uri = f"{base}/jwks"

    engine = create_engine("sqlite+pysqlite:///:memory:")
    models.Base.metadata.create_all(engine)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with Session(engine) as db:
        db.add(models.TenantRow(id="tenant-a", display_name="Tenant A", created_at=now, updated_at=now))
        db.add(
            models.IdentityProviderRow(
                id="idp-1",
                issuer="https://idp.example",
                audience="sui-client",
                protocol="oidc",
                jwks_uri=jwks_uri,
                created_at=now,
                updated_at=now,
            )
        )
        db.add(models.UserRow(id="user-1", display_name="User One", created_at=now, updated_at=now))
        db.add(
            models.UserIdentityRow(
                user_id="user-1",
                provider="idp-1",
                external_uid="sub-1",
                identity_provider_id="idp-1",
                subject="sub-1",
                created_at=now,
            )
        )
        db.add(
            models.TenantIdentityProviderRow(
                tenant_id="tenant-a",
                identity_provider_id="idp-1",
                external_tenant_ref="ext-tenant-1",
                lifecycle_state="active",
                created_at=now,
                updated_at=now,
            )
        )
        db.commit()

        claims = {
            "iss": "https://idp.example",
            "aud": "sui-client",
            "sub": "sub-1",
            "tenant_ref": "ext-tenant-1",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
        }
        token = jwt.encode(
            claims,
            private.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            ),
            algorithm="RS256",
            headers={"kid": "key-1"},
        )
        user_id, claim = bff._verify_broker_identity(db=db, token=token)

        TOKEN["value"] = token
        from starlette.applications import Starlette
        from starlette.requests import Request
        from sui_sensemaking_api import oauth_broker_client as broker

        store = RecordingStore()
        app = Starlette()
        app.state.runtime_profile = "saas-multitenant"
        app.state.saas_auth_session_store = store
        app.state.saas_auth_session_hash_key = b"a" * 64
        app.state.saas_oauth_broker_config = broker.ExternalOauthBrokerConfig(
            token_endpoint=f"{base}/token",
            client_id="client-1",
            client_secret="secret-1",
            redirect_uri="https://sui.example/session/callback",
            timeout_seconds=5,
        )
        pending = json.dumps({"state": "state-1", "code_verifier": "v" * 43, "next": "/docs"})
        cookie_name = bff._OAUTH_PENDING_COOKIE
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/session/callback",
            "query_string": b"",
            "headers": [(b"cookie", f"{cookie_name}={pending}".encode())],
            "app": app,
            "scheme": "https",
            "server": ("sui.example", 443),
        }
        redirect = bff.handle_callback(
            request=Request(scope), db=db, code="code-1", state="state-1", error=None
        )

    server.shutdown()

    checks = {
        "userResolved": user_id == "user-1",
        "tenantResolved": claim.tenant_id == "tenant-a",
        "providerResolved": claim.identity_provider_id == "idp-1",
        "subjectResolved": claim.subject == "sub-1",
        "callbackStatus": redirect.status_code == 302,
        "sessionCookie": any(bff._AUTH_SESSION_COOKIE in value for value in redirect.headers.getlist("set-cookie")),
        "sessionPersisted": bool(store.created),
        "sessionPrincipal": store.created[0]["principal_id"] == "user-1" if store.created else False,
        "sessionTenant": store.created[0]["active_tenant_id"] == "tenant-a" if store.created else False,
    }
    passed = all(checks.values())
    receipt = {
        "schema": "tai.reference.sui-saas-identity/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, SUI modules and models imported from the local checkout, an in-memory SQLite database, and a local JWKS stub",
        "command": "python integrations/tools/sui_saas_identity_contract.py --sui-src <SUI>/03_Implement/backend/src",
        "result": "PASS" if passed else "FAIL",
        "observed": {"checks": checks, "tenantId": claim.tenant_id},
        "scope": "Runs the callback with a broker-issued RS256 token through SUI's JWKS, issuer/audience, subject and tenant-claim checks, then records that a session cookie is minted and persisted to the configured store. The store is a recording double, not the product's durable store.",
    }
    Path("evaluations/records/SUI-saas-identity-2026-11-03.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"passed": passed, "checks": checks}))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: script --sui-src <path>")
        raise SystemExit(2)
    SUI_SRC = sys.argv[2]
    main()
