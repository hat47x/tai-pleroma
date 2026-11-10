"""Check that the plan's landing paths exist and do not contradict themselves.

G2 moves accepted candidates into product documents; G5 updates the summary
decks and value documents. The plan names, per repository, where to write, what
to touch, and what not to touch. If a named path does not exist, or if the same
path is named both to touch and not to touch, the plan would send work to a
contradictory target.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

WORKSPACE = Path("D:/GIT/hat47x")
PLAN = "docs/yi-constellation/analysis/07-計画.md"

# The repositories the plan's table names, and where each lives on disk.
REPOS = {
    "tai-pleroma": "tai-pleroma",
    "sui-sensemaking": "sui-sensemaking",
    "markdown-matrix-injector": "markdown-matrix-injector",
    "sei-cognition": "sei-cognition",
    "tei-platform": "tei-platform",
    "eki-fabric": "eki-fabric",
    "cultural-substrate-weaving": "cultural-substrate-weaving",
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    plan = (root / PLAN).read_text(encoding="utf-8")

    rows = {}
    for line in plan.splitlines():
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 4 or cells[0] not in REPOS:
            continue
        places = re.findall(r"`([^`]+)`", cells[1])
        touch = re.findall(r"`([^`]+)`", cells[2])
        avoid = re.findall(r"`([^`]+)`", cells[3])
        rows[cells[0]] = {"places": places, "touch": touch, "avoid": avoid}

    missing_repos = []
    missing_paths = []
    present = {}
    for name, row in rows.items():
        repo = WORKSPACE / REPOS[name]
        if not repo.exists():
            missing_repos.append(name)
            continue
        present[name] = []
        # 置き場所 may be a directory or a file; both must resolve.
        for place in row["places"]:
            target = repo / place
            if target.exists():
                present[name].append(place)
            else:
                missing_paths.append(f"{name}:{place}")
        # A touch target that is a concrete file must exist as well.
        # A bare file name in 触る is relative to 置き場所; a name with a
        # slash is relative to the repository.
        for touched in row["touch"]:
            candidates = [repo / touched]
            candidates += [repo / place / touched for place in row["places"]]
            if not any(candidate.exists() for candidate in candidates):
                missing_paths.append(f"{name}:touch:{touched}")

    contradictions = [
        f"{name}:{path}"
        for name, row in rows.items()
        for path in row["touch"]
        if path in row["avoid"]
    ]

    checks = {
        "plan": PLAN,
        "repositoriesInTable": sorted(rows),
        "repositoriesMissing": missing_repos,
        "placesNamed": sum(len(row["places"]) for row in rows.values()),
        "pathsPresent": present,
        "pathsMissing": missing_paths,
        "touchAvoidContradictions": contradictions,
        "everyRepoSits": not missing_repos,
        "everyPathExists": not missing_paths,
        "noPathIsBothTouchedAndAvoided": not contradictions,
    }
    passed = (
        checks["everyRepoSits"]
        and checks["everyPathExists"]
        and checks["noPathIsBothTouchedAndAvoided"]
    )
    receipt = {
        "schema": "tai.reference.yi-landing-paths/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the plan and the product repositories",
        "command": "python integrations/tools/yi_landing_paths_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-landing-paths-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Reads section 4 of the plan, resolves each named repository, 置き場所 and backticked 触る path on disk, and records which of them exist and whether any path is named both to touch and not to touch. It checks paths only: it does not open them, does not check whether writing there is authorised, and cannot judge the prose in the 触る and 触らない columns beyond the backticked paths.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "repos": len(rows),
        "places": checks["placesNamed"],
        "missingRepos": missing_repos,
        "missingPaths": missing_paths,
        "contradictions": contradictions,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
