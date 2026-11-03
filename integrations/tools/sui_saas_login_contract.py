"""Check the authorize-step contract of SUI's OAuth login against the local modules."""

import hashlib
import json
import os
import sys
import time
import urllib.parse
from pathlib import Path

SUI_SRC = None


def main():
    env = {
        "SUI_ADMIN_API_KEY": "test-admin-key",
        "SUI_SAAS_OAUTH_BROKER_HTTP_AUTHORIZE_ENDPOINT": "https://broker.example/authorize",
        "SUI_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT": "https://broker.example/token",
        "SUI_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI": "https://sui.example/session/callback",
        "SUI_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID": "sui-client",
        "SUI_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET": "sui-secret",
        "SUI_SAAS_AUTH_SESSION_HASH_KEY": "a" * 64,
    }
    os.environ.update(env)
    sys.path.insert(0, SUI_SRC)

    from starlette.applications import Starlette
    from starlette.requests import Request

    from sui_sensemaking_api import oauth_bff as bff

    app = Starlette()
    app.state.runtime_profile = "saas-multitenant"
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/session/login",
        "query_string": b"next=%2Fdocs",
        "headers": [],
        "app": app,
        "scheme": "https",
        "server": ("sui.example", 443),
    }
    response = bff.initiate_login(request=Request(scope), next_query="/docs")
    location = response.headers["location"]
    params = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(location).query))
    cookie = response.headers.get("set-cookie", "")
    pending = None
    for part in cookie.split(";"):
        name, _, value = part.strip().partition("=")
        if name == bff._OAUTH_PENDING_COOKIE:
            pending = value
    checks = {
        "status": response.status_code == 302,
        "authorizeEndpoint": location.startswith("https://broker.example/authorize?"),
        "responseType": params.get("response_type") == "code",
        "clientId": params.get("client_id") == "sui-client",
        "redirectUri": params.get("redirect_uri") == "https://sui.example/session/callback",
        "scope": params.get("scope") == "openid",
        "statePresent": bool(params.get("state")) and len(params.get("state", "")) >= 32,
        "pkceMethod": params.get("code_challenge_method") == "S256",
        "pkceChallenge": bool(params.get("code_challenge")) and len(params.get("code_challenge", "")) >= 43,
        "pendingCookie": pending is not None,
        "pendingHttpOnly": "httponly" in cookie.lower(),
        "pendingSecure": "secure" in cookie.lower(),
    }
    passed = all(checks.values())
    digest = "sha256:" + hashlib.sha256(location.encode("utf-8")).hexdigest()
    receipt = {
        "schema": "tai.reference.sui-saas-login-contract/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 and SUI modules imported from the local checkout",
        "command": "python integrations/tools/sui_saas_login_contract.py --sui-src <SUI>/03_Implement/backend/src",
        "result": "PASS" if passed else "FAIL",
        "observed": {
            "checks": checks,
            "authorizeParams": {key: params.get(key) for key in sorted(params)},
            "redirectDigest": digest,
        },
        "scope": "Calls SUI's login initiation with test settings and checks the redirect parameters and pending cookie. No broker, callback, token exchange, or session issuance is exercised.",
    }
    Path("evaluations/records/SUI-saas-login-contract-2026-11-03.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"passed": passed, "checks": checks}))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: script --sui-src <path>")
        raise SystemExit(2)
    SUI_SRC = sys.argv[2]
    main()
