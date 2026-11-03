"""Record the projected SEI decision through SEI's own CLI and verify the bundle."""

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "evaluations/artifacts/sei-decision-projection.json"
RECEIPT = ROOT / "evaluations/records/SEI-TEI-cli-2026-11-03.json"


def run(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def main():
    sei_repo = Path(os.environ.get("SEI_REPO", r"D:\GIT\hat47x\sei-cognition")) / "runtime" / "go"
    workdir = Path(tempfile.mkdtemp(prefix="tei-sei-cli-", dir=os.environ.get("GOTMPDIR") or None))
    binary = workdir / ("sei.exe" if os.name == "nt" else "sei")
    build = run(["go", "build", "-o", str(binary), "./cmd/sei"], sei_repo)
    if build.returncode != 0:
        print(build.stderr, file=os.sys.stderr)
        return 1

    record = json.loads(ARTIFACT.read_text(encoding="utf-8"))["decision"]
    store = workdir / "store"
    init = run([str(binary), "init", "-data-root", str(store)], sei_repo)
    add = run(
        [
            str(binary),
            "add",
            "decision",
            "-data-root",
            str(store),
            "-id",
            record["refId"],
            "-statement",
            record["statement"],
            "-rationale",
            record["rationale"],
            "-source",
            "tai-tei-projection",
        ],
        sei_repo,
    )
    resume = run([str(binary), "resume", "-data-root", str(store)], sei_repo)
    bundle = workdir / "bundle.json"
    export = run([str(binary), "export", "-data-root", str(store), "-output", str(bundle)], sei_repo)
    verify = run([str(binary), "verify", "-input", str(bundle)], sei_repo)

    snapshot = re.search(r"Snapshot SHA-256: (sha256:[0-9a-f]+)", resume.stdout)
    checks = {
        "init": init.returncode == 0,
        "add": add.returncode == 0 and '"recorded":"decision"' in add.stdout,
        "resume": resume.returncode == 0 and record["refId"] in resume.stdout,
        "export": export.returncode == 0 and bundle.exists(),
        "verify": verify.returncode == 0,
        "snapshotDigest": bool(snapshot),
    }
    passed = all(checks.values())
    receipt = {
        "schema": "tai.reference.tei-sei-cli/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with a locally built sei CLI and a temporary record store",
        "command": "python integrations/tools/sei_cli_record.py",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": str(ARTIFACT.relative_to(ROOT)).replace("\\", "/")},
        "seiCommit": run(["git", "rev-parse", "HEAD"], Path(os.environ.get("SEI_REPO", r"D:\GIT\hat47x\sei-cognition"))).stdout.strip(),
        "observed": {
            "checks": checks,
            "recordId": record["refId"],
            "snapshotDigest": snapshot.group(1) if snapshot else None,
            "resume": resume.stdout.splitlines()[:5],
        },
        "scope": "Records the projected decision through SEI's CLI, reads the snapshot, exports a bundle and verifies it. The store is temporary and no policy gate is exercised.",
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(workdir, ignore_errors=True)
    print(json.dumps({"passed": passed, "checks": checks}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
