"""Drive SUI's external SaaS adapters against a local stub and check their contracts."""

import hashlib
import json
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SUI_SRC = None
CAPTURED = []


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("content-length", "0"))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        CAPTURED.append({"path": self.path, "body": body, "authorization": self.headers.get("authorization")})
        if self.path == "/access":
            response = {"allow": True}
        elif self.path == "/binding":
            response = {"policyRef": "policy:stub-1"}
        else:
            response = {"effectiveCapabilities": ["document.read", "document.write"], "capabilityVersion": "cap-1"}
        payload = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


def digest(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True).encode("utf-8")).hexdigest()


def main():
    sys.path.insert(0, SUI_SRC)

    from sui_sensemaking_api import access_control as ac
    from sui_sensemaking_api import document_policy_binding as binding
    from sui_sensemaking_api import tenant_capability as capability
    from sui_sensemaking_api.tenant_context import TenantContext

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"

    tenant = TenantContext(tenant_id="tenant-a", membership_id="member-1", resolved_by="verified_claim")
    request = ac.AccessRequest(
        action="read",
        auth=ac.AuthContext(actor_ref="actor-1", user_id="user-1", roles=("reader",), groups=("team-a",)),
        resource=ac.AccessResource(doc_id="doc-1", visibility="Org", policy_ref="policy:1", tenant_id="tenant-a"),
        tenant=tenant,
        safe_mode=False,
        read_only=False,
    )
    adapter = ac.ExternalPolicyAccessControlAdapter(
        config=ac.ExternalPolicyAdapterConfig(
            endpoint=f"{base}/access", timeout_seconds=5, auth_mode="static_bearer", static_bearer_token="stub-token"
        )
    )
    decision = adapter.authorize(request)

    binding_resolver = binding.ExternalHttpDocumentPolicyBindingResolver(
        config=binding.ExternalDocumentPolicyBindingConfig(
            endpoint=f"{base}/binding", timeout_seconds=5, api_key="stub-key"
        )
    )
    policy_ref = binding_resolver.resolve(tenant=tenant, binding_id="binding-1", policy_version="pv-1")

    capability_resolver = capability.ExternalHttpTenantCapabilityResolver(
        config=capability.ExternalTenantCapabilityConfig(
            endpoint=f"{base}/capability", timeout_seconds=5, api_key="stub-key"
        )
    )
    snapshot = capability_resolver.resolve(db=None, principal_id="user-1", tenant=tenant)

    server.shutdown()

    access = CAPTURED[0]["body"]
    checks = {
        "accessAllow": decision.allow is True,
        "accessPayloadAction": access.get("action") == "read",
        "accessPayloadAuth": access.get("auth", {}).get("actorRef") == "actor-1",
        "accessPayloadResource": access.get("resource", {}).get("docId") == "doc-1",
        "accessPayloadTenant": access.get("tenant", {}).get("tenantId") == "tenant-a",
        "accessBearer": CAPTURED[0]["authorization"] == "Bearer stub-token",
        "bindingPayload": CAPTURED[1]["body"] == {"tenantId": "tenant-a", "bindingId": "binding-1", "policyVersion": "pv-1"},
        "bindingPolicyRef": policy_ref == "policy:stub-1",
        "capabilityPayload": CAPTURED[2]["body"]
        == {"principalId": "user-1", "tenantId": "tenant-a", "membershipId": "member-1"},
        "capabilityValues": list(snapshot.effective_capabilities) == ["document.read", "document.write"],
    }
    passed = all(checks.values())
    receipt = {
        "schema": "tai.reference.sui-saas-adapter-contract/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12, SUI modules imported from the local checkout, and an in-process stub server",
        "command": "python integrations/tools/sui_saas_adapter_contract.py --sui-src <SUI>/03_Implement/backend/src",
        "result": "PASS" if passed else "FAIL",
        "observed": {"checks": checks, "captured": CAPTURED, "digest": digest(CAPTURED)},
        "scope": "Calls SUI's three external HTTP adapters against a local stub and checks the request and response shapes. The stub always allows; this proves neither real authorization nor OAuth broker behaviour.",
    }
    out = Path("evaluations/records/SUI-saas-adapter-contract-2026-11-03.json")
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "checks": checks}))


if __name__ == "__main__":
    SUI_SRC = sys.argv[2] if len(sys.argv) > 2 else None
    if not SUI_SRC:
        print("usage: script --sui-src <path>")
        raise SystemExit(2)
    main()
