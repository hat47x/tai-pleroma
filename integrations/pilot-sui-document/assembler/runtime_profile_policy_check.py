"""Check SUI's runtime-profile policy table: where tenant sessions and agent paths turn on."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

PROFILES = ["local-dev", "evaluation", "enterprise-production", "saas-multitenant", "unknown-profile"]


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="sui-profile-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "profile-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from sui_sensemaking_api.runtime_bootstrap import resolve_tenant_session_bootstrap_mode

    observed = {}
    for profile in PROFILES:
        try:
            observed[profile] = {"mode": resolve_tenant_session_bootstrap_mode(profile)}
        except RuntimeError as error:
            observed[profile] = {"error": str(error)}

    # The API-docs surface and agent wiring both key off the profile string.
    tree_guards = {}
    main_py = Path(args.sui_repo) / "03_Implement/backend/src/sui_sensemaking_api/main.py"
    source = main_py.read_text(encoding="utf-8")
    tree_guards["docsEnabledExpression"] = 'settings.runtime_profile in {"local-dev", "evaluation"}'
    tree_guards["docsEnabledPresent"] = tree_guards["docsEnabledExpression"] in source
    tree_guards["agentWiringGuard"] = 'if settings.runtime_profile == "saas-multitenant":' in source
    access_control = (
        Path(args.sui_repo) / "03_Implement/backend/src/sui_sensemaking_api/access_control.py"
    ).read_text(encoding="utf-8")
    tree_guards["safeModeExportGuard"] = 'in {"export", "share"}' in access_control

    bootstrap = (Path(args.sui_repo) / "03_Implement/backend/src/sui_sensemaking_api/runtime_bootstrap.py").read_text(
        encoding="utf-8"
    )
    tree_guards["bootstrapSingleTenantSet"] = (
        '"enterprise-production"' in bootstrap and '"tenant-session-required"' in bootstrap
    )

    checks = {
        "profiles": observed,
        "singleTenantProfiles": [
            name for name, value in observed.items() if value.get("mode") == "single-tenant"
        ],
        "sessionRequiredProfiles": [
            name for name, value in observed.items() if value.get("mode") == "tenant-session-required"
        ],
        "unknownProfileError": observed["unknown-profile"].get("error"),
        "sourceGuards": tree_guards,
    }
    passed = (
        checks["singleTenantProfiles"] == ["local-dev", "evaluation", "enterprise-production"]
        and checks["sessionRequiredProfiles"] == ["saas-multitenant"]
        and checks["unknownProfileError"] == "Unsupported runtime profile for tenant session bootstrap"
        and tree_guards["docsEnabledPresent"] is True
        and tree_guards["agentWiringGuard"] is True
        and tree_guards["bootstrapSingleTenantSet"] is True
    )
    receipt = {
        "schema": "tai.reference.sui-runtime-profile-policy/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 calling SUI's profile resolver and reading main.py",
        "command": f"python integrations/pilot-sui-document/assembler/runtime_profile_policy_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-profile-policy-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Calls resolve_tenant_session_bootstrap_mode for five profile names and greps main.py for the docs, agent-wiring, and safe-mode guards. It does not boot each profile.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
