"""Record what one SCN-001 Attempt does and does not establish, claim by claim.

A run receipt with ``passed: true`` is not an outcome. This probe keeps seven
things apart for the user job "draft provisional guidance from conflicting
facility documents": the goal, the work product, the execution evidence, the
consumer evidence, the authority, the outcome and the value.

It adds no engine and no store. It only runs tools that already exist --
``reference-scn001-run`` (generate, verify), ``reference-publication-gate``
and, when a checkout is given, SHO's read-only ``sho-inspect`` -- and reads
their output. ``classify`` is the reading rule for SCN-001; it is not a shared
schema, and each product keeps its own record of meaning, grants and results.

Nothing is published and no external effect is attempted. The rows for an
external effect (unknown, partial, no-op) are exercised only by ``--self-test``
with hand-written observations, because SCN-001 has no external provider.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ESTABLISHED = "established"
LIMITED = "limited"
HOLD = "hold"
NOT_ESTABLISHED = "not-established"
NOT_RUN = "not-run"
NOT_EVALUATED = "not-evaluated"
SATISFIED = "satisfied"
VIOLATED = "violated"
UNMET = "unmet"
ABSENT = "absent"
PRESENT = "present"

EFFECTS = ("none", "no-op", "known", "partial", "unknown")


def sha256_file(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def classify(obs):
    """Turn observations into separate claims. Never returns a single verdict.

    ``obs`` keys (all optional; a missing key means "not observed"):
      toolPassed            the run or verification tool reported success
      artifactBytesVerified True / False / None (None: no artifact was compared)
      inputBindingVerified  the three observation digests agree
      receiptRunDigest      runDigest of the receipt that was verified
      attemptRunDigest      runDigest of the Attempt the claim is about
      artifactScope         scope the artifact declares for itself
      claimedPurpose        purpose the claim is made for
      reader                None, or {"ran", "error", "digest", "sameOperator"}
      receiptArtifactDigest digest the receipt records for the artifact
      recipient             None, or {"received": bool} for the intended recipient
      authorityVerified     a current owner authority was verified
      selfDeclaredApproval  the producer says it is approved
      gateRefused           the publication gate was run and refused
      published             a publication was observed
      effect                one of EFFECTS, for an external effect
      userFeedback          None, or the user's own evaluation
    """
    claims = {}

    # T-Draft: a grounded draft exists at a known place with the recorded bytes.
    stale = (
        obs.get("attemptRunDigest") is not None
        and obs.get("receiptRunDigest") != obs.get("attemptRunDigest")
    )
    out_of_scope = (
        obs.get("claimedPurpose") is not None
        and obs.get("artifactScope") is not None
        and obs.get("claimedPurpose") != obs.get("artifactScope")
    )
    bytes_verified = obs.get("artifactBytesVerified")
    if bytes_verified is False:
        draft = (NOT_ESTABLISHED, "artifact-missing-or-different-bytes")
    elif not obs.get("toolPassed"):
        draft = (NOT_ESTABLISHED, "tool-did-not-pass")
    elif bytes_verified is None:
        draft = (HOLD, "artifact-bytes-not-compared")
    elif not obs.get("inputBindingVerified"):
        draft = (HOLD, "input-binding-not-verified")
    elif stale:
        draft = (HOLD, "receipt-belongs-to-another-attempt")
    elif out_of_scope:
        draft = (HOLD, "purpose-outside-artifact-scope")
    else:
        draft = (ESTABLISHED, "bytes-and-input-binding-verified-for-this-attempt")
    claims["T-Draft"] = {"verdict": draft[0], "basis": draft[1]}

    # R-Deliver (another implementation read the bytes).
    reader = obs.get("reader")
    if not reader or not reader.get("ran"):
        other = (NOT_RUN, "no-reader-was-run")
    elif reader.get("error"):
        other = (NOT_ESTABLISHED, "reader-could-not-read: " + str(reader["error"]))
    elif reader.get("digest") != obs.get("receiptArtifactDigest"):
        # The reader's own success is not a match; only the comparison is.
        other = (NOT_ESTABLISHED, "reader-read-different-bytes")
    else:
        other = (LIMITED, "same-bytes-read-by-another-implementation")
    claims["R-Deliver.otherImplementation"] = {"verdict": other[0], "basis": other[1]}

    # R-Deliver (the recipient the goal names).
    recipient = obs.get("recipient")
    if recipient is None:
        intended = (NOT_RUN, "no-intended-recipient-observed")
    elif recipient.get("received"):
        intended = (ESTABLISHED, "intended-recipient-received")
    else:
        intended = (NOT_ESTABLISHED, "intended-recipient-did-not-receive")
    claims["R-Deliver.intendedRecipient"] = {"verdict": intended[0], "basis": intended[1]}

    # Authority: only a verified current owner authority counts.
    if obs.get("authorityVerified"):
        authority = (PRESENT, "owner-authority-verified")
    elif obs.get("selfDeclaredApproval"):
        authority = (ABSENT, "self-declared-approval-is-not-authority")
    else:
        authority = (ABSENT, "no-owner-authority-verified")
    claims["Authority.publication"] = {"verdict": authority[0], "basis": authority[1]}

    effect = obs.get("effect", "none")
    if effect not in EFFECTS:
        raise ValueError(f"unknown effect: {effect}")
    published = bool(obs.get("published"))

    # S-NoUnauthorizedPublish: a constraint, not a goal.
    if published and authority[0] != PRESENT:
        safety = (VIOLATED, "published-without-authority")
    elif effect in ("unknown", "partial") and authority[0] != PRESENT:
        safety = (HOLD, f"effect-{effect}-without-authority")
    elif obs.get("gateRefused"):
        safety = (SATISFIED, "gate-refusal-observed")
    else:
        safety = (SATISFIED, "no-publication-observed")
    claims["S-NoUnauthorizedPublish"] = {"verdict": safety[0], "basis": safety[1]}

    # P-Publish: the goal "the guidance is published". A safe stop leaves it unmet.
    if effect == "unknown":
        publish = (HOLD, "effect-unknown-until-independently-read")
    elif effect == "partial":
        publish = (NOT_ESTABLISHED, "effect-partial")
    elif published and authority[0] == PRESENT and effect == "known":
        publish = (ESTABLISHED, "authorized-publication-observed")
    elif effect == "no-op":
        publish = (UNMET, "no-op")
    elif authority[0] != PRESENT:
        publish = (UNMET, "waiting-for-authority")
    else:
        publish = (UNMET, "not-published")
    claims["P-Publish"] = {"verdict": publish[0], "basis": publish[1]}

    claims["Effect"] = {
        "verdict": effect,
        "basis": "declared-by-receipt" if effect == "none" else "observed",
        # An unknown effect must not be retried blindly (TAI #531 OX-04).
        "retryWithoutIndependentRead": False if effect in ("unknown", "partial") else None,
    }

    if obs.get("userFeedback") is None:
        value = (NOT_EVALUATED, "no-user-or-owner-evaluation")
    else:
        value = ("evaluated-by-user", "user-feedback-recorded")
    claims["Value"] = {"verdict": value[0], "basis": value[1]}
    return claims


BASE = {
    "toolPassed": True,
    "artifactBytesVerified": True,
    "inputBindingVerified": True,
    "receiptRunDigest": "sha256:a",
    "attemptRunDigest": "sha256:a",
    "artifactScope": "development-review-only",
    "claimedPurpose": "development-review-only",
    "receiptArtifactDigest": "sha256:d",
    "reader": {"ran": True, "error": None, "digest": "sha256:d", "sameOperator": True},
    "gateRefused": True,
    "published": False,
}

# Hand-written expectations, fixed before any observation. Each row changes one
# thing from BASE and names the claims that must move (and those that must not).
SELF_TEST = (
    ("baseline", {}, {
        "T-Draft": ESTABLISHED, "R-Deliver.otherImplementation": LIMITED,
        "R-Deliver.intendedRecipient": NOT_RUN, "Authority.publication": ABSENT,
        "S-NoUnauthorizedPublish": SATISFIED, "P-Publish": UNMET, "Value": NOT_EVALUATED}),
    ("O1 tool success, artifact missing", {"artifactBytesVerified": False,
        "reader": {"ran": True, "error": "not-found", "digest": None}},
        {"T-Draft": NOT_ESTABLISHED, "R-Deliver.otherImplementation": NOT_ESTABLISHED}),
    ("O1b tool success, artifact never compared", {"artifactBytesVerified": None},
        {"T-Draft": HOLD}),
    ("O2 receipt success, reader reads other bytes",
        {"reader": {"ran": True, "error": None, "digest": "sha256:other"}},
        {"T-Draft": ESTABLISHED, "R-Deliver.otherImplementation": NOT_ESTABLISHED}),
    ("O3 artifact correct, consumer did not receive",
        {"reader": None, "recipient": {"received": False}},
        {"T-Draft": ESTABLISHED, "R-Deliver.otherImplementation": NOT_RUN,
         "R-Deliver.intendedRecipient": NOT_ESTABLISHED}),
    ("O4 self-declared approval", {"selfDeclaredApproval": True},
        {"Authority.publication": ABSENT, "P-Publish": UNMET}),
    ("O4b self-declared approval and published",
        {"selfDeclaredApproval": True, "published": True, "effect": "known", "gateRefused": False},
        {"Authority.publication": ABSENT, "S-NoUnauthorizedPublish": VIOLATED, "P-Publish": UNMET}),
    ("O5 safe stop is not a total failure", {},
        {"T-Draft": ESTABLISHED, "S-NoUnauthorizedPublish": SATISFIED}),
    ("O6 safe stop is not goal success", {},
        {"S-NoUnauthorizedPublish": SATISFIED, "P-Publish": UNMET}),
    ("O7 commit, response lost", {"authorityVerified": True, "effect": "unknown", "gateRefused": False},
        {"P-Publish": HOLD, "Effect": "unknown"}),
    ("O7b unknown effect without authority", {"effect": "unknown", "gateRefused": False},
        {"S-NoUnauthorizedPublish": HOLD, "P-Publish": HOLD}),
    ("partial effect", {"authorityVerified": True, "effect": "partial", "gateRefused": False},
        {"P-Publish": NOT_ESTABLISHED, "Effect": "partial", "T-Draft": ESTABLISHED}),
    ("no-op", {"authorityVerified": True, "effect": "no-op", "gateRefused": False},
        {"P-Publish": UNMET, "Effect": "no-op", "S-NoUnauthorizedPublish": SATISFIED}),
    ("authorized publication observed",
        {"authorityVerified": True, "published": True, "effect": "known", "gateRefused": False},
        {"Authority.publication": PRESENT, "P-Publish": ESTABLISHED, "Value": NOT_EVALUATED}),
    ("O8 same bytes, receipt from another attempt", {"receiptRunDigest": "sha256:old"},
        {"T-Draft": HOLD}),
    ("O8b same bytes, other purpose", {"claimedPurpose": "publication"},
        {"T-Draft": HOLD}),
    ("user feedback recorded", {"userFeedback": "useful"},
        {"Value": "evaluated-by-user", "P-Publish": UNMET}),
)


def self_test():
    failures = []
    for name, change, expected in SELF_TEST:
        claims = classify({**BASE, **change})
        for claim, verdict in expected.items():
            if claims[claim]["verdict"] != verdict:
                failures.append(f"{name}: {claim} = {claims[claim]['verdict']}, expected {verdict}")
        if (claims["Effect"]["verdict"] in ("unknown", "partial")
                and claims["Effect"]["retryWithoutIndependentRead"] is not False):
            failures.append(f"{name}: an unknown or partial effect allows a blind retry")
    return {"cases": len(SELF_TEST), "failures": failures}


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def last_json(text):
    start = text.find("{")
    return json.loads(text[start:]) if start >= 0 else {}


def verify(tool, receipt, artifact=None):
    cmd = ["go", "run", ".", "-verify", str(receipt)]
    if artifact is not None:
        cmd += ["-artifact", str(artifact)]
    done = run(cmd, tool)
    body = {}
    try:
        body = last_json(done.stdout)
    except json.JSONDecodeError:
        pass
    return {
        "exit": done.returncode,
        "passed": body.get("passed"),
        "artifactBytesVerified": body.get("artifactBytesVerified"),
        "inputBindingVerified": body.get("inputBindingVerified"),
        "reason": body.get("reason") or (done.stderr.strip().splitlines() or [""])[-1][:200],
    }


def sho_read(sho_root, path):
    done = run(["node", "bin/sho-inspect.cjs", "inspect", str(path)], sho_root)
    body = {}
    for stream in (done.stdout, done.stderr):
        try:
            body = last_json(stream)
        except json.JSONDecodeError:
            continue
        if body:
            break
    source = body.get("source") or {}
    error = body.get("error")
    if error is None and done.returncode != 0:
        error = f"exit {done.returncode}"
    return {
        "exit": done.returncode,
        "status": body.get("status"),
        "error": error,
        "digest": ("sha256:" + source["sha256"]) if source.get("sha256") else None,
        "byteLength": source.get("byteLength"),
        "revision": source.get("revision"),
        "linkOccurrenceCount": body.get("linkOccurrenceCount"),
        "coverage": body.get("coverage"),
    }


def to_obs(check, receipt_digest, artifact_digest, attempt_digest, scope, reader=None, gate_refused=None):
    bytes_verified = check["artifactBytesVerified"] if check.get("compared") else None
    return {
        # "Tool success" is the generating run, which passed before any check below.
        "toolPassed": True,
        "artifactBytesVerified": bytes_verified,
        "inputBindingVerified": check["inputBindingVerified"],
        "receiptRunDigest": receipt_digest,
        "attemptRunDigest": attempt_digest,
        "artifactScope": scope,
        "claimedPurpose": scope,
        "receiptArtifactDigest": artifact_digest,
        "reader": reader,
        "gateRefused": gate_refused,
        "published": False,
        "authorityVerified": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--tai-root")
    parser.add_argument("--stale-run", help="an older run receipt to try against this Attempt's artifact")
    parser.add_argument("--sho-root", help="SHO checkout with dependencies installed (optional)")
    parser.add_argument("--host", default="")
    parser.add_argument("--out")
    args = parser.parse_args()

    tests = self_test()
    if args.self_test:
        print(json.dumps(tests, ensure_ascii=False))
        return 1 if tests["failures"] else 0
    if not (args.tai_root and args.out):
        parser.error("--tai-root and --out are required unless --self-test is given")

    root = Path(args.tai_root).resolve()
    tool = root / "tools/reference-scn001-run"
    gate_tool = root / "tools/reference-publication-gate"
    work = Path(tempfile.mkdtemp(prefix="scn001-outcome-"))
    review, receipt_path = work / "review.md", work / "run.json"

    # 1. One fresh Attempt: generate D-04, save it, keep its receipt.
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    fresh = run(["go", "run", ".", "-root", str(root), "-artifact-out", str(review), "-out", str(receipt_path)], tool)
    if fresh.returncode != 0 or not receipt_path.exists():
        print((fresh.stderr or fresh.stdout)[-800:], file=sys.stderr)
        return 1
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    components = receipt["components"]
    artifact_digest = components["reviewArtifact"]["artifactDigest"]
    run_digest = receipt["runDigest"]
    text = review.read_text(encoding="utf-8")
    scope = next((line.split("`")[1] for line in text.splitlines() if line.startswith("- 適用範囲:")), None)

    # 2. The same verifier, four ways.
    tampered, missing = work / "tampered.md", work / "missing.md"
    tampered.write_bytes(review.read_bytes().replace("予約不要".encode(), "予約必要".encode(), 1))
    checks = {
        "positive": {**verify(tool, receipt_path, review), "compared": True},
        "artifactNotCompared": {**verify(tool, receipt_path), "compared": False},
        "differentBytes": {**verify(tool, receipt_path, tampered), "compared": True},
        "artifactMissing": {**verify(tool, receipt_path, missing), "compared": True},
    }
    stale = None
    if args.stale_run:
        stale_path = Path(args.stale_run).resolve()
        stale_receipt = json.loads(stale_path.read_text(encoding="utf-8"))
        stale = {
            **verify(tool, stale_path, review), "compared": True,
            "receipt": os.path.relpath(stale_path, root).replace(os.sep, "/"),
            "generatedAt": stale_receipt.get("generatedAt"),
            "runDigest": stale_receipt.get("runDigest"),
            "sameArtifactDigest": stale_receipt["components"]["reviewArtifact"]["artifactDigest"] == artifact_digest,
        }

    # 3. Another product's reader, if one is available. Its absence is NOT RUN.
    readers = None
    if args.sho_root:
        sho = Path(args.sho_root).resolve()
        readers = {
            "positive": sho_read(sho, review),
            "differentBytes": sho_read(sho, tampered),
            "artifactMissing": sho_read(sho, missing),
        }

    def reader_obs(name):
        if readers is None:
            return None
        got = readers[name]
        return {"ran": True, "error": got["error"], "digest": got["digest"], "sameOperator": True}

    # 4. The publication gate decides; nothing is published.
    gate_out = work / "gate.json"
    gate_done = run(["go", "run", ".", "-status", str(root / "evaluations/SCN-001-review-status.json"),
                     "-out", str(gate_out)], gate_tool)
    gate = json.loads(gate_out.read_text(encoding="utf-8")) if gate_out.exists() else {}
    gate_refused = gate.get("allowed") is False and gate_done.returncode != 0 and bool(gate.get("blockers"))

    # 5. Claims, case by case. Expectations were written before running anything.
    expected = {
        "positive": {"T-Draft": ESTABLISHED, "S-NoUnauthorizedPublish": SATISFIED, "P-Publish": UNMET,
                     "Authority.publication": ABSENT, "R-Deliver.intendedRecipient": NOT_RUN,
                     "Value": NOT_EVALUATED,
                     "R-Deliver.otherImplementation": LIMITED if readers else NOT_RUN},
        "artifactNotCompared": {"T-Draft": HOLD},
        "differentBytes": {"T-Draft": NOT_ESTABLISHED,
                           "R-Deliver.otherImplementation": NOT_ESTABLISHED if readers else NOT_RUN},
        "artifactMissing": {"T-Draft": NOT_ESTABLISHED,
                            "R-Deliver.otherImplementation": NOT_ESTABLISHED if readers else NOT_RUN},
    }
    cases, mismatches = {}, []
    for name, check in checks.items():
        claims = classify(to_obs(check, run_digest, artifact_digest, run_digest, scope,
                                 reader_obs(name) if name != "artifactNotCompared" else reader_obs("positive"),
                                 gate_refused))
        cases[name] = {"verifier": check, "claims": claims}
        for claim, verdict in expected[name].items():
            if claims[claim]["verdict"] != verdict:
                mismatches.append(f"{name}: {claim} = {claims[claim]['verdict']}, expected {verdict}")
    if stale is not None:
        claims = classify(to_obs(stale, stale["runDigest"], artifact_digest, run_digest, scope,
                                 reader_obs("positive"), gate_refused))
        cases["staleReceipt"] = {"verifier": stale, "claims": claims}
        if claims["T-Draft"]["verdict"] != HOLD:
            mismatches.append("staleReceipt: T-Draft is not hold")

    reader_success_is_not_a_match = (
        readers is not None
        and readers["differentBytes"]["status"] == readers["positive"]["status"]
        and readers["differentBytes"]["exit"] == 0
        and readers["differentBytes"]["digest"] != artifact_digest
    )
    observed = {
        "attempt": {
            "startedAt": started,
            "generatedAt": receipt.get("generatedAt"),
            "runDigest": run_digest,
            "runPassed": receipt.get("passed"),
            "mmiCommit": components["mmi"].get("mmiCommit"),
            "mmiServer": components["mmi"].get("server"),
            "seiCommit": components["sei"].get("seiCommit"),
            "artifactDigest": artifact_digest,
            "artifactBytes": review.stat().st_size,
            "artifactScope": scope,
            "matchesStoredArtifact": artifact_digest == sha256_file(
                root / "evaluations/artifacts/SCN-001-D-04-provisional.md"),
            "runReceiptRetained": False,
        },
        "cases": cases,
        "reader": readers,
        "gate": {"allowed": gate.get("allowed"), "exit": gate_done.returncode,
                 "blockerCount": len(gate.get("blockers") or []), "refusalObserved": gate_refused},
        "selfTest": tests,
        "expectationMismatches": mismatches,
        "passedWithoutComparingArtifact": (
            checks["artifactNotCompared"]["passed"] is True
            and checks["artifactNotCompared"]["artifactBytesVerified"] is False),
        "readerSuccessIsNotAMatch": reader_success_is_not_a_match if readers else None,
        "staleReceiptVerifiesAgainstNewArtifact": (
            None if stale is None else stale["passed"] is True and stale["artifactBytesVerified"] is True),
        "intendedRecipientObserved": False,
        "ownerAuthorityVerified": False,
        "userValueEvaluated": False,
        "externalEffectExercised": False,
        "finding": (
            "技術的成果（T-Draft）は今回のAttemptの範囲で成立した。"
            "検証器は成果物を比較しなくてもpassed:trueを返すため、その場合は保留と読む。"
            "別実装のReaderは差し替えたファイルにも成功を返すので、一致はdigestの比較だけが示す。"
            "D-04は決定的に生成されるため、過去のreceiptも今回の成果物に対して検証を通る。"
            "本来の受取先による受領、Ownerの公開権限、利用者による価値評価は観測していない（false）。"
            "外部Effectのunknown・partial・no-opは、外部Providerが無いので自己試験の表でだけ確かめた。"
            "公開gateは拒否を返し、公開は行っていない。公開というGoalは未達のままである。"
        ),
    }
    passed = not mismatches and not tests["failures"] and receipt.get("passed") is True

    record = {
        "schema": "tai.reference.scn001-outcome-observation/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": args.host or "unspecified",
        "command": "python integrations/tools/scn001_outcome_probe.py --tai-root . "
                   "--stale-run evaluations/records/SCN-001-run-2026-11-01.json --sho-root <SHO> "
                   "--out evaluations/records/SCN-001-outcome-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": "evaluations/artifacts/SCN-001-D-04-provisional.md",
                     "digest": sha256_file(root / "evaluations/artifacts/SCN-001-D-04-provisional.md")},
        "observed": observed,
        "scope": "PASS means only that every claim came out as written down beforehand; it is not a "
                 "statement that the user's goal was achieved. The input documents are synthetic. The reader "
                 "is another product's implementation run by the same operator on the same host, on a copy "
                 "of the artifact, so it is not receipt by the intended recipient. No owner authority, no "
                 "human review and no user evaluation were observed, and no external effect was attempted.",
    }
    Path(args.out).write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(work, ignore_errors=True)
    print(json.dumps({"passed": passed, "mismatches": mismatches,
                      "claims": {k: v["verdict"] for k, v in cases["positive"]["claims"].items()}},
                     ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
