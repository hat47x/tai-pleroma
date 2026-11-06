"""Check SUI's auth-assurance classification table."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="sui-assurance-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "assurance-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from sui_sensemaking_api.access_control import AuthContext
    from sui_sensemaking_api.auth_assurance import build_auth_assurance_metadata

    fixed_now = datetime(2026, 11, 6, 12, 0, 0, tzinfo=timezone.utc)

    def classify(**kwargs):
        auth = AuthContext(
            actor_ref="user-1",
            user_id="user-1",
            provider="saas_jwt",
            amr=kwargs.get("amr"),
            acr=kwargs.get("acr"),
            aal=kwargs.get("aal"),
            auth_time=kwargs.get("auth_time"),
        )
        return build_auth_assurance_metadata(auth, now=fixed_now)

    cases = {
        "noAmr": classify(),
        "singleFactor": classify(amr="pwd"),
        "twoTokens": classify(amr="pwd,totp"),
        "mfaOnly": classify(amr="mfa"),
        "webauthnOnly": classify(amr="webauthn"),
        "upperCase": classify(amr="MFA"),
        "aal3": classify(amr="pwd", aal="aal3"),
        "aalUnknownAcrHigh": classify(acr="urn:ietf:params:acr:high"),
        "aalLowWinsOverAcrHigh": classify(acr="high", aal="aal1"),
        "freshAuth": classify(auth_time=(fixed_now - timedelta(minutes=10)).isoformat()),
        "staleAuth": classify(auth_time=(fixed_now - timedelta(hours=2)).isoformat()),
        "exactly15min": classify(auth_time=(fixed_now - timedelta(minutes=15)).isoformat()),
        "futureAuth": classify(auth_time=(fixed_now + timedelta(hours=1)).isoformat()),
        "zuluAuth": classify(auth_time="2026-11-06T11:50:00Z"),
        "naiveAuth": classify(auth_time="2026-11-06T11:50:00"),
        "garbageAuth": classify(auth_time="not-a-time"),
    }
    checks = {"cases": cases}
    passed = (
        cases["noAmr"] == {"hasStepUp": False, "amrClass": "unknown", "assuranceLevel": "unknown", "authAgeBucket": "unknown"}
        and cases["singleFactor"]["amrClass"] == "single_factor"
        and cases["singleFactor"]["hasStepUp"] is False
        and cases["twoTokens"]["amrClass"] == "multi_factor"
        and cases["twoTokens"]["hasStepUp"] is True
        and cases["mfaOnly"]["hasStepUp"] is True
        and cases["upperCase"]["hasStepUp"] is True
        and cases["aal3"]["assuranceLevel"] == "high"
        and cases["aalUnknownAcrHigh"]["assuranceLevel"] == "high"
        and cases["aalLowWinsOverAcrHigh"]["assuranceLevel"] == "low"
        and cases["freshAuth"]["authAgeBucket"] == "fresh"
        and cases["staleAuth"]["authAgeBucket"] == "stale"
        and cases["exactly15min"]["authAgeBucket"] == "fresh"
        and cases["futureAuth"]["authAgeBucket"] == "unknown"
        and cases["zuluAuth"]["authAgeBucket"] == "fresh"
        and cases["naiveAuth"]["authAgeBucket"] == "fresh"
        and cases["garbageAuth"]["authAgeBucket"] == "unknown"
    )
    receipt = {
        "schema": "tai.reference.sui-auth-assurance/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 calling SUI's auth-assurance builder directly",
        "command": f"python integrations/pilot-sui-document/assembler/auth_assurance_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-auth-assurance-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Classifies 16 synthetic AuthContext values (AMR shapes, AAL/ACR precedence, fresh/stale/future/naive timestamps) at a fixed now. It does not read a real IdP assertion.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
