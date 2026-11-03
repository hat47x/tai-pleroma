"""Rebuild each single-record projection artifact twice and compare digests."""

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRODUCTS = {
    "sei": ("integrations/pilot-sei-decision/build_artifact.py", "integrations/pilot-sei-decision"),
    "mmi": ("integrations/pilot-mmi-format-profile/build_artifact.py", "integrations/pilot-mmi-format-profile"),
    "eki": ("integrations/pilot-eki-task-request/build_artifact.py", "integrations/pilot-eki-task-request"),
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--out", default="evaluations/records/TEI-artifacts-determinism-2026-11-03.json")
    args = parser.parse_args()

    results = {}
    for name, (script, workspace) in PRODUCTS.items():
        with tempfile.TemporaryDirectory(prefix=f"tei-det-{name}-") as tmp:
            digests = []
            for run in (1, 2):
                artifact = Path(tmp) / f"artifact-{run}.json"
                receipt = Path(tmp) / f"receipt-{run}.json"
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / script),
                        "--tei-repo",
                        args.tei_repo,
                        "--workspace",
                        str(ROOT / workspace),
                        "--out",
                        str(artifact),
                        "--receipt-out",
                        str(receipt),
                    ],
                    capture_output=True,
                    encoding="utf-8",
                    errors="replace",
                )
                if completed.returncode != 0:
                    print(completed.stderr, file=sys.stderr)
                    results[name] = {"identical": False, "error": completed.stderr.strip()}
                    break
                digests.append(digest(artifact))
            else:
                results[name] = {
                    "identical": digests[0] == digests[1],
                    "digests": digests,
                }

    all_identical = all(item.get("identical") for item in results.values())
    receipt = {
        "schema": "tai.reference.tei-artifacts-determinism/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go on PATH and Python 3.12",
        "command": "python integrations/tools/check_determinism.py --tei-repo <TEI>",
        "result": "PASS" if all_identical else "FAIL",
        "observed": {"artifacts": results, "allIdentical": all_identical, "count": len(results)},
        "scope": "Rebuilds each single-record artifact twice from the same TEI commit and compares bytes. It does not cover the SUI multi-element artifact.",
    }
    out = ROOT / args.out
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"allIdentical": all_identical, "count": len(results)}))
    return 0 if all_identical else 1


if __name__ == "__main__":
    raise SystemExit(main())
