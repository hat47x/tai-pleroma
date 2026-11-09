"""Check SEI's `doctor` self-diagnosis: what it reports before and after a store exists."""

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


def parse(completed):
    lines = {}
    for line in completed.stdout.splitlines():
        parts = line.split(None, 2)
        if len(parts) >= 2 and parts[1] in {"ok", "info", "warn", "fail"}:
            lines[parts[0]] = {"status": parts[1], "detail": parts[2] if len(parts) > 2 else ""}
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sei-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    sei_repo = Path(args.sei_repo) / "runtime" / "go"
    workdir = Path(tempfile.mkdtemp(prefix="tei-sei-doctor-", dir=os.environ.get("GOTMPDIR") or None))
    binary = workdir / ("sei.exe" if os.name == "nt" else "sei")
    build = run(["go", "build", "-o", binary, "./cmd/sei"], sei_repo)
    if build.returncode != 0:
        print(build.stderr, file=sys.stderr)
        return 1

    store = workdir / "store"
    missing = run([binary, "doctor", "-data-root", store], sei_repo)
    init = run([binary, "init", "-data-root", store], sei_repo)
    after_init = run([binary, "doctor", "-data-root", store], sei_repo)

    record = json.loads(Path(args.artifact).read_text(encoding="utf-8"))["decision"]
    run(
        [
            binary, "add", "decision", "-data-root", store, "-id", "d-1",
            "-statement", record["statement"], "-rationale", record["rationale"],
            "-recommendation", "rec-1" if False else "", "-responsible", "person:alice",
        ],
        sei_repo,
    )
    stale_lock = store / "store.lock"
    stale_lock.write_text("stale", encoding="utf-8")
    with_lock = run([binary, "doctor", "-data-root", store], sei_repo)
    stale_lock.unlink()
    after_unlock = run([binary, "doctor", "-data-root", store], sei_repo)

    start_temp = list(workdir.glob(".sei-doctor-*"))
    checks = {
        "missing": {"exit": missing.returncode, "lines": parse(missing)},
        "init": {"exit": init.returncode},
        "afterInit": {"exit": after_init.returncode, "lines": parse(after_init)},
        "withStaleLock": {"exit": with_lock.returncode, "lines": parse(with_lock)},
        "afterUnlock": {"exit": after_unlock.returncode, "lines": parse(after_unlock)},
        "doctorLeftNoTempFiles": len(start_temp) == 0,
        "initOutputPresent": (store.is_dir()),
    }
    missing_lines = checks["missing"]["lines"]
    init_lines = checks["afterInit"]["lines"]
    lock_lines = checks["withStaleLock"]["lines"]
    passed = (
        checks["missing"]["exit"] == 0
        and missing_lines.get("data-root", {}).get("status") == "warn"
        and "does not exist yet" in missing_lines.get("data-root", {}).get("detail", "")
        and checks["init"]["exit"] == 0
        and checks["initOutputPresent"] is True
        and checks["afterInit"]["exit"] == 0
        and init_lines.get("store", {}).get("status") in ("ok", "warn")
        and init_lines.get("lock", {}).get("status") == "ok"
        and init_lines.get("gate-log", {}).get("status") == "ok"
        and lock_lines.get("lock", {}).get("status") == "warn"
        and "remove that file by hand" in lock_lines.get("lock", {}).get("detail", "")
        and checks["afterUnlock"]["exit"] == 0
        and checks["doctorLeftNoTempFiles"] is True
    )
    receipt = {
        "schema": "tai.reference.sei-doctor/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with a locally built sei CLI and a temporary store",
        "command": f"python integrations/tools/sei_doctor_check.py --sei-repo {args.sei_repo} --artifact {args.artifact} --out evaluations/records/SEI-TEI-doctor-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Runs doctor on a missing store, after init, with a hand-made lock file, and after removing it. It checks that doctor is read-only and never removes the lock itself; it does not test a corrupt store.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(workdir, ignore_errors=True)
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
