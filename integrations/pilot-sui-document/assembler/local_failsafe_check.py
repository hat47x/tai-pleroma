"""Check SUI's local fail-safe ladder: which checks short-circuit before a PDP is consulted."""

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

    workdir = Path(tempfile.mkdtemp(prefix="sui-failsafe-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "failsafe-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from sui_sensemaking_api.access_control import (
        AccessControlInvalidPolicyError,
        AccessControlUnreachableError,
        AccessDecision,
        AccessRequest,
        AccessResource,
        AuthContext,
        TenantContext,
        apply_local_failsafe,
        apply_tenant_boundary_guard,
        resolve_access_decision,
    )

    def request(**kwargs):
        resource = AccessResource(
            doc_id="doc-1",
            visibility=kwargs.get("visibility"),
            policy_ref=kwargs.get("policy_ref"),
            tenant_id=kwargs.get("resource_tenant", "tenant-1"),
        )
        return AccessRequest(
            action=kwargs.get("action", "read"),
            auth=AuthContext(actor_ref="user-1", user_id="user-1", provider="header"),
            resource=resource,
            tenant=TenantContext(
                tenant_id=kwargs.get("tenant", "tenant-1"),
                membership_id=None,
                resolved_by="header",
            ),
            safe_mode=kwargs.get("safe_mode", False),
            read_only=kwargs.get("read_only", False),
        )

    def decide(**kwargs):
        mode = kwargs.pop("mode", "deny")
        adapter_kind = kwargs.pop("adapter", "allow")
        if adapter_kind == "unreachable":
            from sui_sensemaking_api.access_control import ExternalPolicyAdapterConfig

            class _Adapter:
                name = "boom"

                def authorize(self, request):  # noqa: ARG002
                    raise AccessControlUnreachableError("down")

            adapter = _Adapter()
        elif adapter_kind == "invalid_policy":

            class _Adapter:
                name = "boom"

                def authorize(self, request):  # noqa: ARG002
                    raise AccessControlInvalidPolicyError("bad")

            adapter = _Adapter()
        elif adapter_kind == "deny":
            adapter = DenyAdapter()
        elif adapter_kind == "string":

            class _Adapter:
                name = "boom"

                def authorize(self, request):  # noqa: ARG002
                    return "not-a-decision"

            adapter = _Adapter()
        else:
            adapter = AllowAdapter()
        decision = resolve_access_decision(
            adapter=adapter, request=request(**kwargs), fail_safe_mode=mode, require_tenant_scope=True
        )
        return {"allow": decision.allow, "readOnly": decision.read_only, "reason": decision.reason}

    from sui_sensemaking_api.access_control import AccessControlAdapter

    class AllowAdapter(AccessControlAdapter):
        name = "allow"

        def authorize(self, request):  # noqa: ARG002
            return AccessDecision(allow=True)

    class DenyAdapter(AccessControlAdapter):
        name = "deny"

        def authorize(self, request):  # noqa: ARG002
            return AccessDecision(allow=False, reason="policy")

    cases = {
        "baselineAllow": decide(),
        "safeModeExport": decide(action="export", safe_mode=True),
        "safeModeRead": decide(action="read", safe_mode=True),
        "readOnlyWrite": decide(action="write", read_only=True),
        "readOnlyRead": decide(action="read", read_only=True),
        "restrictedNoPolicyDeny": decide(action="write", visibility="Restricted", mode="deny"),
        "restrictedNoPolicyReadOnly": decide(action="write", visibility="Restricted", mode="read_only"),
        "restrictedWithPolicy": decide(action="write", visibility="Restricted", policy_ref="p1"),
        "publicNoPolicy": decide(action="write", visibility="Public"),
        "tenantMismatch": decide(tenant="tenant-1", resource_tenant="tenant-2"),
        "adapterDeny": decide(adapter="deny"),
        "adapterUnreachableDeny": decide(adapter="unreachable", mode="deny"),
        "adapterUnreachableReadOnly": decide(adapter="unreachable", action="read", mode="read_only"),
        "adapterInvalidPolicy": decide(adapter="invalid_policy", mode="read_only"),
        "adapterReturnsString": decide(adapter="string", mode="read_only"),
    }
    checks = {"cases": cases}
    passed = (
        cases["baselineAllow"]["allow"] is True
        and cases["safeModeExport"]["allow"] is False
        and cases["safeModeExport"]["reason"] == "safe_mode"
        and cases["safeModeRead"]["allow"] is True
        and cases["readOnlyWrite"]["allow"] is False
        and cases["readOnlyWrite"]["reason"] == "read_only"
        and cases["readOnlyRead"]["allow"] is True
        and cases["readOnlyRead"]["readOnly"] is False
        and cases["restrictedNoPolicyDeny"]["allow"] is False
        and cases["restrictedNoPolicyDeny"]["reason"] == "policy_ref_missing"
        and cases["restrictedNoPolicyReadOnly"]["allow"] is False
        and cases["restrictedWithPolicy"]["allow"] is True
        and cases["publicNoPolicy"]["allow"] is True
        and cases["tenantMismatch"]["allow"] is False
        and cases["tenantMismatch"]["reason"] == "tenant_mismatch"
        and cases["adapterDeny"]["allow"] is False
        and cases["adapterUnreachableDeny"]["allow"] is False
        and cases["adapterUnreachableDeny"]["reason"] == "policy_ref_unreachable"
        and cases["adapterUnreachableReadOnly"]["allow"] is True
        and cases["adapterReturnsString"]["allow"] is True
        and cases["adapterReturnsString"]["reason"] == "adapter_error"
    )
    receipt = {
        "schema": "tai.reference.sui-local-failsafe/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 calling SUI's access-decision functions directly",
        "command": f"python integrations/pilot-sui-document/assembler/local_failsafe_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-failsafe-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Runs fifteen decision cases through resolve_access_decision with stub adapters: the local ladder, tenant boundary, and adapter failures in both fail-safe modes. It does not call a real PDP. The caller-set read_only flag is not propagated to a read decision: the local ladder only trips on write/export/share, so a read request is answered by the adapter with read_only=False.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
