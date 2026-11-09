"""Check how SUI builds its policy components, especially the fallbacks that hide misconfiguration."""

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

    workdir = Path(tempfile.mkdtemp(prefix="sui-builders-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "builders-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from sui_sensemaking_api.access_control import (
        ExternalPolicyAccessControlAdapter,
        MockAccessControlAdapter,
        NoopAccessControlAdapter,
        build_access_control_adapter,
    )
    from sui_sensemaking_api.document_policy_binding import build_document_policy_binding_resolver
    from sui_sensemaking_api.tenant_capability import (
        ExternalHttpTenantCapabilityResolver,
        UnavailableTenantCapabilityResolver,
        build_tenant_capability_resolver,
    )

    def describe(adapter):
        return type(adapter).__name__

    access_cases = {}
    for name in ("noop", "mock", "unknown-value", "external_http", "http", "external"):
        try:
            access_cases[name] = {"built": describe(build_access_control_adapter(adapter_name=name))}
        except RuntimeError as error:
            access_cases[name] = {"refused": str(error)}
    access_cases["mock_deny"] = {
        "built": describe(build_access_control_adapter(adapter_name="mock", mock_allow=False, mock_reason="deny"))
    }

    tenant_resolver = describe(build_tenant_capability_resolver())
    binding_resolver = describe(build_document_policy_binding_resolver())

    checks = {
        "accessControl": access_cases,
        "unknownAdapterFallsBackToNoop": access_cases["unknown-value"]["built"] == "NoopAccessControlAdapter",
        "mockAdapterBuilt": access_cases["mock"]["built"] == "MockAccessControlAdapter",
        "externalWithoutEndpointRefused": "refused" in access_cases["external_http"],
        "tenantResolver": tenant_resolver,
        "tenantResolverUnavailableWithoutEndpoint": tenant_resolver == "UnavailableTenantCapabilityResolver",
        "documentBindingResolver": binding_resolver,
        "isExternalTypes": {
            "accessControl": isinstance(
                build_access_control_adapter(adapter_name="noop"), NoopAccessControlAdapter
            ),
            "tenant": isinstance(build_tenant_capability_resolver(), UnavailableTenantCapabilityResolver),
        },
        "externalAdapterClassExists": ExternalPolicyAccessControlAdapter is not None,
        "externalTenantClassExists": ExternalHttpTenantCapabilityResolver is not None,
        "mockClassExists": MockAccessControlAdapter is not None,
    }
    passed = (
        checks["unknownAdapterFallsBackToNoop"] is True
        and checks["mockAdapterBuilt"] is True
        and checks["externalWithoutEndpointRefused"] is True
        and checks["tenantResolverUnavailableWithoutEndpoint"] is True
    )
    receipt = {
        "schema": "tai.reference.sui-policy-component-builders/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 calling SUI's policy-component builders",
        "command": f"python integrations/pilot-sui-document/assembler/policy_component_builders_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-builders-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Calls three builders with six access-control names and default settings. It records that an unknown adapter name silently becomes noop, that external_http refuses without an endpoint, and that the tenant resolver degrades to Unavailable. It does not start a SaaS instance.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
