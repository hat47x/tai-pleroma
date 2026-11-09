"""Check SEI's resume snapshot binding and the safe-text escaping of stored values."""

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


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args, cwd):
    return subprocess.run(
        [str(part) for part in args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sei-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    sei_repo = Path(args.sei_repo) / "runtime" / "go"
    workdir = Path(tempfile.mkdtemp(prefix="tei-sei-resume-", dir=os.environ.get("GOTMPDIR") or None))
    binary = workdir / ("sei.exe" if os.name == "nt" else "sei")
    build = run(["go", "build", "-o", binary, "./cmd/sei"], sei_repo)
    if build.returncode != 0:
        print(build.stderr, file=sys.stderr)
        return 1

    store = workdir / "store"
    run([binary, "init", "-data-root", store], sei_repo)
    record = json.loads(Path(args.artifact).read_text(encoding="utf-8"))["decision"]
    # A statement carrying a newline and a bidi override: the human view must escape it.
    hostile = record["statement"] + "\nsecond line \u202e reversed"
    add = run(
        [
            binary, "add", "decision", "-data-root", store, "-id", "d-resume",
            "-statement", hostile, "-rationale", record["rationale"], "-responsible", "person:alice",
        ],
        sei_repo,
    )

    resume_json = run([binary, "resume", "-data-root", store, "--json"], sei_repo)
    resume_text = run([binary, "resume", "-data-root", store], sei_repo)
    body = json.loads(resume_json.stdout) if resume_json.stdout.strip().startswith("{") else {}

    no_store = run([binary, "resume", "-data-root", workdir / "absent"], sei_repo)
    bad_digest = run(
        [
            binary, "resume", "-data-root", store, "--json",
            "-record-id", "d-resume", "-snapshot-digest", "sha256:" + "0" * 64,
        ],
        sei_repo,
    )
    missing_record = run(
        [
            binary, "resume", "-data-root", store, "--json",
            "-record-id", "d-absent", "-snapshot-digest", body.get("snapshot_digest", ""),
        ],
        sei_repo,
    )
    partial = run([binary, "resume", "-data-root", store, "-record-id", "d-resume"], sei_repo)
    good_record = run(
        [
            binary, "resume", "-data-root", store, "--json",
            "-record-id", "d-resume", "-snapshot-digest", body.get("snapshot_digest", ""),
        ],
        sei_repo,
    )

    checks = {
        "addExit": add.returncode,
        "resumeExit": resume_json.returncode,
        "bundleID": body.get("bundle_id"),
        "snapshotDigest": body.get("snapshot_digest"),
        "recordCount": body.get("record_count"),
        "humanViewEscapesNewline": "\\n" in resume_text.stdout,
        "humanViewEscapesBidi": "\\u202e" in resume_text.stdout,
        "humanViewHasNoRawBidi": "\u202e" not in resume_text.stdout,
        "humanViewKeepsFirstLine": record["statement"] in resume_text.stdout,
        "noStoreExit": no_store.returncode,
        "noStoreMessage": "run `sei init` first" in (no_store.stderr + no_store.stdout),
        "badDigestExit": bad_digest.returncode,
        "badDigestMessage": "snapshot digest mismatch" in (bad_digest.stderr + bad_digest.stdout),
        "missingRecordExit": missing_record.returncode,
        "missingRecordMessage": "not found in the expected snapshot" in (
            missing_record.stderr + missing_record.stdout
        ),
        "partialFlagsExit": partial.returncode,
        "goodRecordExit": good_record.returncode,
        "goodRecordPointer": (json.loads(good_record.stdout).get("source_record") or {}).get("json_pointer")
        if good_record.stdout.strip().startswith("{")
        else None,
    }
    passed = (
        checks["addExit"] == 0
        and checks["resumeExit"] == 0
        and bool(checks["snapshotDigest"])
        and checks["humanViewEscapesNewline"] is True
        and checks["humanViewEscapesBidi"] is True
        and checks["humanViewHasNoRawBidi"] is True
        and checks["humanViewKeepsFirstLine"] is True
        and checks["noStoreExit"] != 0
        and checks["noStoreMessage"] is True
        and checks["badDigestExit"] != 0
        and checks["badDigestMessage"] is True
        and checks["missingRecordExit"] != 0
        and checks["missingRecordMessage"] is True
        and checks["partialFlagsExit"] != 0
        and checks["goodRecordExit"] == 0
        and (checks["goodRecordPointer"] or "").startswith("/records/")
    )
    receipt = {
        "schema": "tai.reference.sei-resume/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with a locally built sei CLI and a temporary store",
        "command": f"python integrations/tools/sei_resume_check.py --sei-repo {args.sei_repo} --artifact {args.artifact} --out evaluations/records/SEI-TEI-resume-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Adds a decision whose statement carries a newline and a bidi override, then reads resume as JSON and as text, and probes a missing store, a wrong digest, an unknown record, and partial flags. It does not test a store corrupted after resume.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(workdir, ignore_errors=True)
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
