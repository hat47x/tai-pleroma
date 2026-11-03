"""Check SUI's OAuth callback error contract without an identity provider."""

import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SUI_SRC = None
MODE = {"value": "reject"}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers.get("content-length", "0")))
        if MODE["value"] == "reject":
            self.send_response(400)
        else:
            self.send_response(500)
        self.send_header("content-length", "0")
        self.end_headers()

    def log_message(self, *args):
        pass


def build_request(app, cookie_value=None, cookie_name="sui_oauth_pending"):
    headers = []
    if cookie_value is not None:
        headers.append((b"cookie", f"{cookie_name}={cookie_value}".encode()))
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/session/callback",
        "query_string": b"",
        "headers": headers,
        "app": app,
        "scheme": "https",
        "server": ("sui.example", 443),
    }
    from starlette.requests import Request

    return Request(scope)


def main():
    os.environ.update(
        {
            "SUI_ADMIN_API_KEY": "test-admin-key",
            "SUI_SAAS_OAUTH_BROKER_HTTP_AUTHORIZE_ENDPOINT": "https://broker.example/authorize",
            "SUI_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT": "https://broker.example/token",
            "SUI_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI": "https://sui.example/session/callback",
            "SUI_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID": "sui-client",
            "SUI_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET": "sui-secret",
            "SUI_SAAS_AUTH_SESSION_HASH_KEY": "a" * 64,
        }
    )
    sys.path.insert(0, SUI_SRC)

    from fastapi import HTTPException
    from starlette.applications import Starlette

    from sui_sensemaking_api import oauth_bff as bff
    from sui_sensemaking_api import oauth_broker_client as broker

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    config = broker.ExternalOauthBrokerConfig(
        token_endpoint=f"http://127.0.0.1:{server.server_address[1]}/token",
        client_id="sui-client",
        client_secret="sui-secret",
        redirect_uri="https://sui.example/session/callback",
        timeout_seconds=5,
    )

    app = Starlette()
    app.state.runtime_profile = "saas-multitenant"
    app.state.saas_oauth_broker_config = config

    cookie_name = bff._OAUTH_PENDING_COOKIE
    pending = json.dumps({"state": "state-1", "code_verifier": "v" * 43, "next": "/docs"})
    checks = {}

    def expect(expected, name, *, request, **kwargs):
        def run():
            try:
                bff.handle_callback(request=request, db=None, **kwargs)
            except HTTPException as exc:
                return exc.status_code, (exc.detail or {}).get("code")
            return None, None

        status, error = run()
        checks[name] = status == expected

    expect(400, "missingPending", request=build_request(app), code="c", state="state-1", error=None)
    expect(
        400,
        "brokerDenied",
        request=build_request(app, pending, bff._OAUTH_PENDING_COOKIE),
        code="c",
        state="state-1",
        error="access_denied",
    )
    expect(
        400,
        "stateMismatch",
        request=build_request(app, pending, bff._OAUTH_PENDING_COOKIE),
        code="c",
        state="state-2",
        error=None,
    )
    expect(400, "missingCode", request=build_request(app, pending, bff._OAUTH_PENDING_COOKIE), code=None, state="state-1", error=None)

    app.state.saas_oauth_broker_config = None
    expect(503, "brokerNotConfigured", request=build_request(app, pending, bff._OAUTH_PENDING_COOKIE), code="c", state="state-1", error=None)
    app.state.saas_oauth_broker_config = config

    MODE["value"] = "reject"
    expect(400, "brokerRejects", request=build_request(app, pending, bff._OAUTH_PENDING_COOKIE), code="c", state="state-1", error=None)
    MODE["value"] = "unavailable"
    expect(503, "brokerUnavailable", request=build_request(app, pending, bff._OAUTH_PENDING_COOKIE), code="c", state="state-1", error=None)

    server.shutdown()

    passed = all(checks.values())
    receipt = {
        "schema": "tai.reference.sui-saas-callback-contract/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, SUI modules imported from the local checkout, and an in-process broker stub",
        "command": "python integrations/tools/sui_saas_callback_contract.py --sui-src <SUI>/03_Implement/backend/src",
        "result": "PASS" if passed else "FAIL",
        "observed": {"checks": checks},
        "scope": "Exercises the callback's rejection paths: pending cookie, state, missing code, unconfigured broker, broker rejection and unavailability. A successful login needs a signed IdP token and provisioned identities, which this test does not provide.",
    }
    Path("evaluations/records/SUI-saas-callback-contract-2026-11-03.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"passed": passed, "checks": checks}))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: script --sui-src <path>")
        raise SystemExit(2)
    SUI_SRC = sys.argv[2]
    main()
