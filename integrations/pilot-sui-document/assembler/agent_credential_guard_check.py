"""Check SUI's rule for agent credentials that run without audit export."""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PROBE = """
import json, sys
from sui_sensemaking_api.settings import settings
from sui_sensemaking_api.agent_credentials import agent_audit_is_not_exported

print(json.dumps({
    "agentEnabled": bool(settings.agent_credential_hash_key or settings.agent_oauth_audience),
    "auditExported": bool(settings.audit_export_enabled and settings.audit_allow_in_safe_mode),
    "guard": agent_audit_is_not_exported(settings),
}))
"""


def run_probe(env):
    work = Path(tempfile.mkdtemp(prefix="sui-agent-guard-", dir=os.environ.get("GOTMPDIR") or None))
    complete = {**env, "SUI_DATABASE_URL": f"sqlite+pysqlite:///{work / 'sui.db'}"}
    completed = subprocess.run(
        [sys.executable, "-c", PROBE],
        env=complete,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    try:
        return json.loads(completed.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        return {"error": (completed.stdout + completed.stderr)[-400:]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", default=os.environ.get("SUI_REPO", r"D:\GIT\hat47x\sui-wt-latest"))
    args = parser.parse_args()
    sui = Path(args.sui_repo) / "03_Implement/backend/src"
    base = {
        **os.environ,
        "SUI_RUNTIME_PROFILE": "local-dev",
        "SUI_LLM_PROVIDER": "none",
        "SUI_API_KEY": "guard-key",
        "SUI_AGENT_CREDENTIAL_HASH_KEY": "0" * 64,
        "PYTHONPATH": str(sui),
    }
    base.pop("SUI_ADMIN_API_KEY", None)
    without_audit = {**base, "SUI_AUDIT_EXPORT_ENABLED": "false", "SUI_AUDIT_ALLOW_IN_SAFE_MODE": "false"}
    with_audit = {**base, "SUI_AUDIT_EXPORT_ENABLED": "true", "SUI_AUDIT_ALLOW_IN_SAFE_MODE": "true"}

    unguarded = run_probe(without_audit)
    guarded = run_probe(with_audit)
    checks = {
        "agentEnabled": unguarded.get("agentEnabled") is True,
        "guardRaised": unguarded.get("guard") is True,
        "auditExportedClearsGuard": guarded.get("auditExported") is True and guarded.get("guard") is False,
    }
    passed = all(checks.values())
    receipt = {
        "schema": "tai.reference.sui-agent-credential-guard/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with SUI in local-dev profile",
        "command": "python integrations/pilot-sui-document/assembler/agent_credential_guard_check.py --sui-repo <SUI>",
        "result": "PASS" if passed else "FAIL",
        "observed": checks,
        "scope": "Calls SUI's agent_audit_is_not_exported rule with agent credentials enabled, once without audit export (expects True) and once with audit export plus SafeMode export (expects False). It reads the rule, not the startup log.",
    }
    out = Path(__file__).resolve().parents[3] / "evaluations/records/SUI-TEI-agent-guard-2026-11-06.json"
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "checks": checks}))


if __name__ == "__main__":
    raise SystemExit(main())
