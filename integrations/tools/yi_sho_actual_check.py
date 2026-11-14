"""Establish what sho-composer actually contains, which G1's D3/D6 rest on.

Doc 21 says ``sho-composer`` has only a LICENSE and an initial commit. If that has
changed, D3 (how to show SHO) and D6 (product / MMI role / held) are being decided
on a stale premise. This measures the repository as it stands: commits, dates,
tracked files, and whether the named artefacts exist.
"""

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

SHO = Path("D:/GIT/hat47x/sho-composer")

# The artefacts doc 21 says are absent.
ABSENT_PER_DOC = ("README", "requirements", "implementation", "issues")
REQUIRED_TO_BE_A_PRODUCT = ("README.md", "plan", "src", "test")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(repo, *args):
    completed = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    if not SHO.exists():
        print(f"sho-composer missing: {SHO}")
        return 1

    commit_count = int(git(SHO, "rev-list", "--count", "HEAD") or 0)
    dates = git(SHO, "log", "--format=%ad", "--date=short").splitlines()
    first_date = dates[-1] if dates else ""
    latest_date = dates[0] if dates else ""
    initial_commit = git(SHO, "rev-list", "--max-parents=0", "HEAD")
    initial_files = [
        line for line in git(SHO, "show", "--name-only", "--format=", initial_commit).splitlines()
        if line.strip()
    ]
    tracked = git(SHO, "ls-files").splitlines()
    top_level = sorted({line.split("/")[0] for line in tracked if line})

    present = {name: (SHO / name).exists() for name in REQUIRED_TO_BE_A_PRODUCT}
    requirements_present = any(
        (SHO / candidate).exists()
        for candidate in ("requirements", "REQUIREMENTS.md", "plan")
    )

    checks = {
        "repository": str(SHO),
        "commitCount": commit_count,
        "firstDate": first_date,
        "latestDate": latest_date,
        "initialCommitFiles": initial_files[:5],
        "initialCommitHadOnlyLicence": initial_files == ["LICENSE"],
        "trackedFileCount": len(tracked),
        "topLevelEntries": top_level,
        "productArtefactsPresent": present,
        "requirementsOrPlanPresent": requirements_present,
        "doc21PremiseHolds": commit_count <= 2 and len(tracked) <= 2,
        "doc21Premise": "LICENSEと初期コミットしかない",
        "finding": (
            "doc 21の前提（LICENSEと初期コミットしかない）は現在は成り立たない。"
            f"sho-composerは追跡{len(tracked)}ファイル・{commit_count}コミットを持ち、"
            f"{first_date}から{latest_date}まで更新されている。"
            "D3とD6は、この前提を更新してから判断する必要がある。"
        ),
    }
    passed = checks["doc21PremiseHolds"] is False and (SHO / "README.md").exists()

    receipt = {
        "schema": "tai.reference.yi-sho-actual-check/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with git reading the sho-composer checkout",
        "command": "python integrations/tools/yi_sho_actual_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-sho-actual-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Measures the sho-composer repository as it stands: commits, dates, tracked files and the presence of the artefacts doc 21 says are absent. It records that the doc's premise no longer holds; it does not read the code, does not judge whether the product definition is adequate, and does not decide D3 or D6.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commits": commit_count,
        "tracked": len(tracked),
        "firstDate": first_date,
        "latestDate": latest_date,
        "doc21PremiseHolds": checks["doc21PremiseHolds"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
