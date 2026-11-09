"""Check SUI's context bundle construction."""

import argparse
import hashlib
import json
import os
import platform
import socket
import sys
import tempfile
import threading
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]



def observe_stub_visibility(bundle, *, expected_exclusion_reason="unreviewed_filtered"):
    """Inspect a real HTTP response against the fixed A2-minimal-v1 stub scope.

    Return counts, not card IDs or text. This is *not* evidence of user-data
    recall, independent source revision, disclosure authorization, or meaning.
    """
    errors = []
    counts = {}
    result = {
        "passed": False,
        "errors": errors,
        "counts": counts,
        "selectionScope": "A2-minimal-v1 fixed synthetic stub only",
        "sourceRevisionMatched": "not-checked",
        "disclosureAuthorization": "not-checked",
        "candidateCompleteness": "not-established",
    }
    if not isinstance(bundle, dict) or bundle.get("schemaVersion") != "1.0.0":
        errors.append("expected ContextBundleResponse v1")
        return result
    selected = bundle.get("selected")
    evidence = bundle.get("evidence")
    relations = bundle.get("relations")
    flags = bundle.get("reviewFlags")
    reasons = bundle.get("excludedReason")
    meta = bundle.get("truncationMeta")
    if not isinstance(selected, list) or not isinstance(evidence, list) or not isinstance(relations, list):
        errors.append("selected/evidence/relations must be arrays")
        return result
    if not isinstance(flags, dict) or not isinstance(reasons, list) or not isinstance(meta, dict):
        errors.append("reviewFlags/excludedReason/truncationMeta malformed")
        return result

    ids = []
    for i, item in enumerate(selected):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            errors.append(f"selected[{i}] has no ID")
        else:
            ids.append(item["id"])
        if not isinstance(item, dict) or item.get("reviewed") is not True:
            errors.append(f"selected[{i}] is not reviewed")
    if len(ids) != len(set(ids)):
        errors.append("selected contains duplicate IDs")
    selected_ids = set(ids)

    refs = set()
    unreviewed = set()
    counter_opinions = set()
    for i, item in enumerate(evidence):
        if not isinstance(item, dict) or not isinstance(item.get("cardId"), str) or not item["cardId"]:
            errors.append(f"evidence[{i}] has no cardId")
            continue
        card_id = item["cardId"]
        refs.add(card_id)
        if item.get("reviewed") is False:
            unreviewed.add(card_id)
        if item.get("kind") == "counter_opinion":
            counter_opinions.add(card_id)
    for i, item in enumerate(relations):
        if not isinstance(item, dict):
            errors.append(f"relations[{i}] is not an object")
            continue
        for field in ("from", "to"):
            if not isinstance(item.get(field), str) or not item[field]:
                errors.append(f"relations[{i}].{field} missing")
            else:
                refs.add(item[field])
    reference_only = refs - selected_ids
    counts.update({
        "selected": len(selected_ids),
        "referenceOnly": len(reference_only),
        "unreviewedReferenceOnly": len(unreviewed & reference_only),
        "counterOpinionReferenceOnly": len(counter_opinions & reference_only),
    })
    if type(flags.get("reviewed")) is not int or type(flags.get("unreviewed")) is not int:
        errors.append("reviewFlags counts are not integers")
    elif flags["reviewed"] != len(selected_ids) or flags["unreviewed"] != 0:
        errors.append("reviewFlags disagree with strict selected")
    if not all(isinstance(reason, str) for reason in reasons):
        errors.append("invalid excludedReason")
    if meta.get("stubDatasetId") != "A2-minimal-v1" or meta.get("holdState") != "hold:stub_dataset_contract_only":
        errors.append("not the fixed A2-minimal-v1 stub")
    if expected_exclusion_reason not in ("unreviewed_filtered", "safe_mode_unreviewed_text"):
        errors.append("unknown strict-filter exclusion expectation")
    elif expected_exclusion_reason not in reasons:
        errors.append(f"strict-filter exclusion reason not observed: {expected_exclusion_reason}")
    if (len(selected_ids), len(reference_only), len(unreviewed & reference_only),
            len(counter_opinions & reference_only)) != (1, 1, 1, 1):
        errors.append("unexpected A2-minimal-v1 selected/reference-only shape")
    result["passed"] = not errors
    if errors:
        counts.clear()  # never emit a success-like count from malformed data
    return result

def compare_strict_filter_profiles(reviewed_only, include_unreviewed):
    """Compare two fixed-stub responses, not all possible Source candidates.

    A request to include unreviewed cards under strict SafeMode must not
    promote their text into selected. Reference-only metadata remains a
    separate disclosure/authorization question.
    """
    primary = observe_stub_visibility(reviewed_only)
    alternate = observe_stub_visibility(
        include_unreviewed, expected_exclusion_reason="safe_mode_unreviewed_text"
    )
    fields = ("selected", "evidence", "relations", "contradictions")
    same_projection = (
        primary["passed"] and alternate["passed"]
        and all(reviewed_only.get(field) == include_unreviewed.get(field) for field in fields)
    )
    query_hashes = (
        reviewed_only.get("queryCanonicalHash"),
        include_unreviewed.get("queryCanonicalHash"),
    )
    hashes_distinct = (
        all(isinstance(x, str) and bool(x) for x in query_hashes)
        and query_hashes[0] != query_hashes[1]
    )
    reasons_distinct = (
        primary["passed"] and alternate["passed"]
        and reviewed_only.get("excludedReason") != include_unreviewed.get("excludedReason")
    )
    passed = primary["passed"] and alternate["passed"] and same_projection and hashes_distinct and reasons_distinct
    return {
        "passed": passed,
        "reviewedOnlyPassed": primary["passed"],
        "includeUnreviewedStrictPassed": alternate["passed"],
        "sameSelectedEvidenceRelationsAndConstraints": bool(same_projection),
        "differentQueryCanonicalHashes": bool(hashes_distinct),
        "differentExclusionReason": bool(reasons_distinct),
        "reviewedOnlyCounts": primary["counts"] if passed else {},
        "includeUnreviewedStrictCounts": alternate["counts"] if passed else {},
        "scope": "fixed A2 synthetic stub, strict SafeMode; no real source, disclosure, or Owner acceptance",
    }


def identical_context_responses(first, second):
    """Deep equality of two same-attempt HTTP JSON bodies, not digest verification.

    This compares in memory and reports only a boolean, never a card ID/text.
    It is NOT proof of cross-runtime canonicalization or source revision.
    """
    return isinstance(first, dict) and bool(first) and isinstance(second, dict) and first == second


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="sui-bundle-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite+pysqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "bundle-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    import httpx
    import uvicorn
    from sqlalchemy import text

    from sui_sensemaking_api.db import engine
    from sui_sensemaking_api.main import app
    from sui_sensemaking_api.models import Base

    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                "insert into tenants (id, display_name, lifecycle_state, created_at, updated_at) "
                "values ('local-default', 'Local', 'active', '2026-11-03T00:00:00Z', '2026-11-03T00:00:00Z') "
                "on conflict (id) do nothing"
            )
        )

    port = free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    headers = {"X-API-Key": "bundle-key"}
    query = {
        "queryId": "q-1",
        "goal": "summarize current state",
        "scope": "document",
        "depth": 2,
        "constraints": {},
        "reviewFilter": "reviewedOnly",
        "safeModePolicy": "strict",
        "outputMode": "summary",
        "previewConfirmed": True,
    }
    body = {"query": query, "stubDatasetId": "A2-minimal-v1"}
    first = second = no_preview = include_unreviewed = None
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                httpx.get(f"{base}/openapi.json", timeout=2)
                break
            except httpx.HTTPError:
                time.sleep(0.5)
        first = httpx.post(f"{base}/context/bundle", json=body, headers=headers, timeout=60)
        second = httpx.post(f"{base}/context/bundle", json=body, headers=headers, timeout=60)
        include_unreviewed = httpx.post(
            f"{base}/context/bundle",
            json={"query": {**query, "reviewFilter": "includeUnreviewed"},
                  "stubDatasetId": "A2-minimal-v1"},
            headers=headers, timeout=60,
        )
        no_preview = httpx.post(
            f"{base}/context/bundle",
            json={"query": {**query, "previewConfirmed": False}, "stubDatasetId": "A2-minimal-v1"},
            headers=headers,
            timeout=60,
        )
    finally:
        server.should_exit = True
        thread.join(timeout=20)

    first_body = first.json() if first is not None and first.status_code == 200 else {}
    second_body = second.json() if second is not None and second.status_code == 200 else {}
    alternate_body = (
        include_unreviewed.json()
        if include_unreviewed is not None and include_unreviewed.status_code == 200
        else {}
    )
    checks = {
        "firstStatus": first.status_code if first is not None else None,
        "secondStatus": second.status_code if second is not None else None,
        "includeUnreviewedStrictStatus": (
            include_unreviewed.status_code if include_unreviewed is not None else None
        ),
        "bundleHash": first_body.get("bundleHash"),
        "deterministic": bool(first_body.get("bundleHash")) and first_body.get("bundleHash") == second_body.get("bundleHash"),
        "sameAttemptResponseIdentical": identical_context_responses(first_body, second_body),
        "hasQueryHash": isinstance(first_body.get("queryCanonicalHash"), str),
        "noPreviewStatus": no_preview.status_code if no_preview is not None else None,
        "noPreviewCode": (no_preview.json().get("detail") or {}).get("code") if no_preview is not None else None,
    }
    visibility = observe_stub_visibility(first_body)
    checks["visibility"] = visibility
    checks["filterContrast"] = compare_strict_filter_profiles(first_body, alternate_body)
    passed = (
        visibility["passed"]
        and checks["filterContrast"]["passed"]
        and checks["includeUnreviewedStrictStatus"] == 200
        and checks["firstStatus"] == 200
        and isinstance(checks["bundleHash"], str)
        and checks["deterministic"]
        and checks["sameAttemptResponseIdentical"]
        and checks["secondStatus"] == 200
        and checks["hasQueryHash"]
        and checks["noPreviewStatus"] == 422
        and checks["noPreviewCode"] == "preview_required"
    )
    receipt = {
        "schema": "tai.reference.sui-context-bundle/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": f"{platform.system()} / loopback SUI local-dev profile",
        "inputDataKind": "synthetic-A2-minimal-v1-stub",
        "command": "python integrations/pilot-sui-document/assembler/context_bundle_check.py --sui-repo <SUI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/SUI-TEI-context-bundle-2026-11-03.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "artifactUsage": "reference-metadata-only; artifact bytes NOT consumed by SUI /context/bundle",
        "consumedInput": {"kind": "synthetic-stub", "stubDatasetId": "A2-minimal-v1",
                          "sourceRevisionMatched": False},
        "observed": checks,
        "scope": "Executes SUI local-dev /context/bundle against A2-minimal-v1 synthetic stub; separately observes selected vs reference-only metadata (counts only), same-attempt response content equality, strict reviewedOnly vs includeUnreviewed filter contrast, hash stability, plus preview refusal. Does NOT establish cross-runtime digest interoperability, candidate completeness, matching external Source revision, disclosure authorization, or human decision.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
