"""Drive SUI's OAuth broker client against a local stub and record the contract."""

import hashlib
import json
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SUI_SRC = None
CAPTURED = []
MODE = {"value": "ok"}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("content-length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        CAPTURED.append({"form": dict(urllib.parse.parse_qsl(raw)), "contentType": self.headers.get("content-type")})
        if MODE["value"] == "reject":
            self.send_response(400)
            self.send_header("content-length", "0")
            self.end_headers()
            return
        if MODE["value"] == "unexpected":
            body = {"access_token": "at", "token_type": "Bearer", "expires_in": 3600, "bogusField": 1}
        else:
            body = {"access_token": "at", "token_type": "Bearer", "expires_in": 3600, "id_token": "jwt"}
        payload = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


def main():
    sys.path.insert(0, SUI_SRC)
    from sui_sensemaking_api import oauth_broker_client as broker

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    endpoint = f"http://127.0.0.1:{server.server_address[1]}/token"
    config = broker.ExternalOauthBrokerConfig(
        token_endpoint=endpoint,
        client_id="client-1",
        client_secret="secret-1",
        redirect_uri="https://sui.example/callback",
        timeout_seconds=5,
    )

    tokens = broker.exchange_code_for_tokens(config=config, code="code-1", code_verifier="verifier-1")
    form = CAPTURED[0]["form"]

    MODE["value"] = "reject"
    rejected = False
    try:
        broker.exchange_code_for_tokens(config=config, code="code-2", code_verifier="verifier-2")
    except broker.OauthBrokerInvalidResponseError:
        rejected = True

    MODE["value"] = "unexpected"
    unexpected = False
    try:
        broker.exchange_code_for_tokens(config=config, code="code-3", code_verifier="verifier-3")
    except broker.OauthBrokerInvalidResponseError:
        unexpected = True

    server.shutdown()

    checks = {
        "grantType": form.get("grant_type") == "authorization_code",
        "code": form.get("code") == "code-1",
        "redirectUri": form.get("redirect_uri") == "https://sui.example/callback",
        "clientId": form.get("client_id") == "client-1",
        "clientSecret": form.get("client_secret") == "secret-1",
        "codeVerifier": form.get("code_verifier") == "verifier-1",
        "formContentType": CAPTURED[0]["contentType"] == "application/x-www-form-urlencoded",
        "accessToken": tokens.access_token == "at",
        "tokenType": tokens.token_type == "Bearer",
        "expiresIn": tokens.expires_in == 3600,
        "idToken": tokens.id_token == "jwt",
        "rejectsHttpError": rejected,
        "rejectsUnexpectedField": unexpected,
    }
    passed = all(checks.values())
    digest = "sha256:" + hashlib.sha256(json.dumps(CAPTURED, sort_keys=True).encode("utf-8")).hexdigest()
    receipt = {
        "schema": "tai.reference.sui-saas-oauth-contract/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, SUI modules imported from the local checkout, and an in-process stub server",
        "command": "python integrations/tools/sui_saas_oauth_contract.py --sui-src <SUI>/03_Implement/backend/src",
        "result": "PASS" if passed else "FAIL",
        "observed": {"checks": checks, "captured": CAPTURED, "digest": digest},
        "scope": "Calls SUI's OAuth broker token-exchange client against a local stub. It does not run the browser redirect, verify a real IdP, or issue a session.",
    }
    Path("evaluations/records/SUI-saas-oauth-contract-2026-11-03.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"passed": passed, "checks": checks}))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: script --sui-src <path>")
        raise SystemExit(2)
    SUI_SRC = sys.argv[2]
    main()
