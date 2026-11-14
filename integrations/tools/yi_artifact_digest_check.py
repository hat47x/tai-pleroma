"""Check that each YI receipt's recorded artifact digest still matches the file.

A receipt records the digest of the artifact it measured. If that artifact has
since changed, the receipt describes a version nobody can see any more, and a
reader who opens the file now gets a different object than the receipt measured.
This recomputes each recorded digest and reports the mismatches.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

HISTORICAL = {"yi-constellation-structure-2026-11-01.json"}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    own = Path(args.out).name
    records = root / "evaluations/records"
    names = sorted(
        {
            path.name
            for path in records.glob("*.json")
            if path.name.lower().startswith(("yi-", "yi_"))
            and path.name not in HISTORICAL
            and path.name != own
        }
    )

    rows = []
    missing = []
    mismatched = []
    for name in names:
        data = json.loads((records / name).read_text(encoding="utf-8"))
        artifact = data.get("artifact") or {}
        recorded = artifact.get("digest")
        relative = artifact.get("path")
        if not recorded or not relative:
            missing.append(name)
            continue
        target = (root / relative).resolve()
        if not target.exists():
            rows.append({"receipt": name, "artifact": relative, "state": "artifact-missing"})
            mismatched.append(name)
            continue
        current = digest(target)
        agrees = current == recorded
        rows.append({
            "receipt": name,
            "artifact": relative,
            "agrees": agrees,
            "recorded": recorded[:19],
            "current": current[:19],
        })
        if not agrees:
            mismatched.append(name)

    checks = {
        "receipts": len(names),
        "receiptsWithoutArtifactDigest": missing,
        "mismatched": mismatched,
        "rows": rows,
        "everyArtifactDigestStillMatches": not mismatched,
        "everyReceiptRecordsAnArtifact": not missing,
    }
    passed = not mismatched and not missing

    receipt = {
        "schema": "tai.reference.yi-artifact-digest/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 recomputing the recorded digests",
        "command": "python integrations/tools/yi_artifact_digest_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-artifact-digest-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Recomputes the artifact digest each YI receipt records and compares it with the file as it stands now. A match shows the file has not changed since the receipt was written; it does not show the receipt measured that file correctly, and a receipt whose artifact is a stable fixture can match while its own logic has aged.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipts": len(names),
        "mismatched": mismatched,
        "missing": missing,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
