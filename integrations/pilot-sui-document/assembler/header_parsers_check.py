"""Check SUI's header parsers and the actor-ref fingerprint helper."""

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

    workdir = Path(tempfile.mkdtemp(prefix="sui-parsers-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "parsers-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from sui_sensemaking_api.access_control import (
        normalize_policy_ref,
        parse_csv_header,
        parse_visibility,
    )
    from sui_sensemaking_api.observability import compute_actor_ref_hash

    csv_cases = {
        "none": parse_csv_header(None),
        "empty": parse_csv_header(""),
        "plain": parse_csv_header("a,b"),
        "spaces": parse_csv_header(" a , b "),
        "nullToken": parse_csv_header("a,null,b"),
        "emptyItems": parse_csv_header("a,,b"),
        "upperNull": parse_csv_header("NULL,a"),
    }
    policy_cases = {
        "none": normalize_policy_ref(None),
        "spaces": normalize_policy_ref("  p1  "),
        "empty": normalize_policy_ref(""),
        "nullLiteral": normalize_policy_ref("null"),
        "upperNull": normalize_policy_ref("NULL"),
    }
    visibility_cases = {
        "none": parse_visibility(None),
        "public": parse_visibility("Public"),
        "restricted": parse_visibility("Restricted"),
        "spaces": parse_visibility(" Public "),
        "caseMismatch": parse_visibility("public"),
        "unknown": parse_visibility("Secret"),
    }
    hash_cases = {
        "none": compute_actor_ref_hash(None),
        "empty": compute_actor_ref_hash(""),
        "user": compute_actor_ref_hash("user-1"),
        "length": len(compute_actor_ref_hash("user-1") or ""),
        "stable": compute_actor_ref_hash("user-1") == compute_actor_ref_hash("user-1"),
        "differs": compute_actor_ref_hash("user-1") != compute_actor_ref_hash("user-2"),
    }
    checks = {
        "csv": {key: list(value) for key, value in csv_cases.items()},
        "policyRef": policy_cases,
        "visibility": visibility_cases,
        "actorRefHash": hash_cases,
    }
    passed = (
        checks["csv"]["none"] == []
        and checks["csv"]["plain"] == ["a", "b"]
        and checks["csv"]["spaces"] == ["a", "b"]
        and checks["csv"]["nullToken"] == ["a", "b"]
        and checks["csv"]["emptyItems"] == ["a", "b"]
        and checks["csv"]["upperNull"] == ["a"]
        and policy_cases["none"] is None
        and policy_cases["spaces"] == "p1"
        and policy_cases["empty"] is None
        and policy_cases["nullLiteral"] is None
        and policy_cases["upperNull"] is None
        and checks["visibility"]["public"] == "Public"
        and checks["visibility"]["spaces"] == "Public"
        and checks["visibility"]["caseMismatch"] is None
        and checks["visibility"]["unknown"] is None
        and hash_cases["none"] is None
        and hash_cases["empty"] is None
        and hash_cases["length"] == 16
        and hash_cases["stable"] is True
        and hash_cases["differs"] is True
    )
    receipt = {
        "schema": "tai.reference.sui-header-parsers/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 calling SUI's parsing helpers directly",
        "command": f"python integrations/pilot-sui-document/assembler/header_parsers_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-parsers-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Calls parse_csv_header, normalize_policy_ref, parse_visibility, and compute_actor_ref_hash on representative and degenerate inputs. It does not send these values through HTTP headers.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
