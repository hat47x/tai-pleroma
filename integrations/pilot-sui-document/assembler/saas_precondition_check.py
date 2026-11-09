"""Check SUI's SaaS PUT precondition helper (expected 428/400/409 answers)."""

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

    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from fastapi import HTTPException

    from sui_sensemaking_api.routes.docs import _require_saas_document_precondition

    def probe(**kwargs):
        try:
            _require_saas_document_precondition(**kwargs)
        except HTTPException as error:
            detail = error.detail if isinstance(error.detail, dict) else {}
            return error.status_code, detail.get("code")
        return None, None

    update_missing = probe(if_match=None, if_none_match=None, document_exists=True)
    create_missing = probe(if_match=None, if_none_match=None, document_exists=False)
    both = probe(if_match='"abc"', if_none_match="*", document_exists=True)
    wildcard_update = probe(if_match="*", if_none_match=None, document_exists=True)
    wildcard_list = probe(if_match='"abc", *', if_none_match=None, document_exists=True)
    create_bad_value = probe(if_match=None, if_none_match='"abc"', document_exists=False)
    create_existing = probe(if_match=None, if_none_match="*", document_exists=True)
    update_ok = probe(if_match='"abc"', if_none_match=None, document_exists=True)
    create_ok = probe(if_match=None, if_none_match="*", document_exists=False)

    checks = {
        "updateMissing": list(update_missing),
        "createMissing": list(create_missing),
        "bothGiven": list(both),
        "wildcardUpdate": list(wildcard_update),
        "wildcardInList": list(wildcard_list),
        "createBadValue": list(create_bad_value),
        "createExisting": list(create_existing),
        "updateAccepted": list(update_ok),
        "createAccepted": list(create_ok),
    }
    passed = (
        update_missing == (428, "document_precondition_required")
        and create_missing == (428, "document_precondition_required")
        and both == (400, "document_precondition_conflict")
        and wildcard_update == (428, "document_precondition_required")
        and wildcard_list == (428, "document_precondition_required")
        and create_bad_value == (400, "document_precondition_invalid")
        and create_existing == (409, "document_already_exists")
        and update_ok == (None, None)
        and create_ok == (None, None)
    )
    receipt = {
        "schema": "tai.reference.sui-saas-precondition/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 calling SUI's precondition helper directly",
        "command": f"python integrations/pilot-sui-document/assembler/saas_precondition_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-saas-precondition-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Calls the SaaS precondition helper with nine header combinations and records the status and code it returns. It does not reach the helper through the HTTP route, because local-dev does not enable the tenant-session precondition.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
