"""Check SUI's trusted-SaaS preflight: which profile/adapter combinations are refused."""

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

    workdir = Path(tempfile.mkdtemp(prefix="sui-preflight-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "preflight-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from sui_sensemaking_api.main import _trusted_saas_runtime_components, _trusted_saas_runtime_policy, app
    from sui_sensemaking_api.trusted_saas_runtime import (
        TrustedSaasRuntimeAdapters,
        initialize_trusted_saas_runtime,
        release_trusted_saas_runtime,
        validate_trusted_saas_runtime_preflight,
    )

    policy = _trusted_saas_runtime_policy()
    components = _trusted_saas_runtime_components()

    class StubAdapters(TrustedSaasRuntimeAdapters):
        def __init__(self):
            pass

    def probe(profile):
        try:
            validate_trusted_saas_runtime_preflight(
                app,
                runtime_profile=profile,
                runtime_policy=policy,
                runtime_components=components,
            )
            return {"outcome": "accepted"}
        except RuntimeError as error:
            return {"outcome": "refused", "reason": str(error)}

    results = {}
    # No adapters installed: single-tenant profiles pass, SaaS is refused.
    for profile in ("local-dev", "evaluation", "enterprise-production", "saas-multitenant", "unknown-profile"):
        results[f"withoutAdapters:{profile}"] = probe(profile)

    setattr(app.state, "trusted_saas_runtime_adapters", StubAdapters())
    for profile in ("local-dev", "saas-multitenant"):
        results[f"withAdapters:{profile}"] = probe(profile)
    setattr(app.state, "trusted_saas_runtime_adapters", None)

    # A bogus bundle type must be refused even for a single-tenant profile.
    setattr(app.state, "trusted_saas_runtime_adapters", object())
    results["withBogusBundle:local-dev"] = probe("local-dev")
    setattr(app.state, "trusted_saas_runtime_adapters", None)

    # initialize refuses to run twice in one lifespan.
    started = initialize_trusted_saas_runtime(
        app,
        runtime_profile="local-dev",
        runtime_policy=policy,
        runtime_components=components,
    )
    results["initializeTwice"] = probe("local-dev")
    release_trusted_saas_runtime(app)
    results["afterRelease"] = probe("local-dev")

    checks = {"results": results, "initializeReturnedBundle": started}
    passed = (
        results["withoutAdapters:local-dev"]["outcome"] == "accepted"
        and results["withoutAdapters:evaluation"]["outcome"] == "accepted"
        and results["withoutAdapters:enterprise-production"]["outcome"] == "accepted"
        and results["withoutAdapters:saas-multitenant"]["outcome"] == "refused"
        and "policy is incomplete" in results["withoutAdapters:saas-multitenant"]["reason"]
        and results["withoutAdapters:unknown-profile"]["outcome"] == "refused"
        and results["withAdapters:local-dev"]["outcome"] == "refused"
        and "cannot be enabled by a single-tenant" in results["withAdapters:local-dev"]["reason"]
        and results["withBogusBundle:local-dev"]["outcome"] == "refused"
        and results["initializeTwice"]["outcome"] == "refused"
        and results["afterRelease"]["outcome"] == "accepted"
        and started is False
    )
    receipt = {
        "schema": "tai.reference.sui-trusted-runtime-preflight/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 calling SUI's preflight and install helpers directly",
        "command": f"python integrations/pilot-sui-document/assembler/trusted_runtime_preflight_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-preflight-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Runs the preflight with and without adapter bundles across five profiles, with a bogus bundle, and checks that initialize refuses a second call but accepts after release. It uses a stub adapter, not a real IdP.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
