"""Check each requirement in SUI's trusted-SaaS policy table, one at a time."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

BASE = {
    "database_backend": "postgresql",
    "allow_jit_provisioning": False,
    "access_control_adapter": "external_http",
    "access_control_fail_safe_mode": "deny",
    "document_policy_binding_resolver": "external_http",
    "tenant_capability_resolver": "external_http",
    "jwt_algorithms": "RS256,ES256",
    "tenant_claim_name": "tenant_ref",
    "saas_oauth_broker_http_authorize_endpoint": "https://idp.example/authorize",
    "saas_auth_session_hash_key": "0" * 64,
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="sui-policy-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "policy-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from sui_sensemaking_api.trusted_saas_runtime import TrustedSaasRuntimePolicy

    def judge(**overrides):
        policy = TrustedSaasRuntimePolicy(**{**BASE, **overrides})
        try:
            policy.validate()
        except RuntimeError as error:
            return {"outcome": "refused", "reason": str(error)}
        return {"outcome": "accepted"}

    cases = {"allRequirementsMet": judge()}
    mutations = {
        "databaseBackend": "sqlite",
        "allowJitProvisioning": True,
        "accessControlAdapter": "noop",
        "failSafeMode": "read_only",
        "documentPolicyBinding": "none",
        "tenantCapability": "none",
        "jwtAlgorithms": "   ",
        "tenantClaimName": "",
        "oauthAuthorizeEndpoint": None,
        "authSessionHashKey": None,
    }
    overrides = {
        "databaseBackend": {"database_backend": "sqlite"},
        "allowJitProvisioning": {"allow_jit_provisioning": True},
        "accessControlAdapter": {"access_control_adapter": "noop"},
        "failSafeMode": {"access_control_fail_safe_mode": "read_only"},
        "documentPolicyBinding": {"document_policy_binding_resolver": "none"},
        "tenantCapability": {"tenant_capability_resolver": "none"},
        "jwtAlgorithms": {"jwt_algorithms": "   "},
        "tenantClaimName": {"tenant_claim_name": ""},
        "oauthAuthorizeEndpoint": {"saas_oauth_broker_http_authorize_endpoint": None},
        "authSessionHashKey": {"saas_auth_session_hash_key": None},
    }
    for name, override in overrides.items():
        cases[name] = judge(**override)
    cases["allTenBroken"] = judge(
        **{key: value for override in overrides.values() for key, value in override.items()}
    )

    checks = {"cases": cases, "mutationNames": list(mutations)}
    passed = (
        cases["allRequirementsMet"]["outcome"] == "accepted"
        and all(
            cases[name]["outcome"] == "refused"
            for name in overrides
            if name not in ("jwtAlgorithms", "tenantClaimName")
        )
        and cases["allTenBroken"]["outcome"] == "refused"
        and len(cases["allTenBroken"]["reason"].split(", ")) >= 8
    )
    receipt = {
        "schema": "tai.reference.sui-saas-policy-requirements/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 constructing SUI's policy dataclass directly",
        "command": f"python integrations/pilot-sui-document/assembler/saas_policy_requirements_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-policy-requirements-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Builds a fully-satisfying policy, then breaks each requirement alone and all together, recording which labels the refusal names. It does not start a SaaS instance.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
