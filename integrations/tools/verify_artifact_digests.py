"""Verify that every pilot artifact's contractDigest matches its contract file."""

import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = {
    "sui": "evaluations/artifacts/documentv1-projection.json",
    "sei": "evaluations/artifacts/sei-decision-projection.json",
    "mmi": "evaluations/artifacts/mmi-format-profile-projection.json",
    "eki": "evaluations/artifacts/eki-task-request-projection.json",
}
CONTRACTS = {
    "sui": "integrations/pilot-sui-document/candidates/card-record/contract.json",
    "sei": "integrations/pilot-sei-decision/candidates/decision-record/contract.json",
    "mmi": "integrations/pilot-mmi-format-profile/candidates/format-profile-record/contract.json",
    "eki": "integrations/pilot-eki-task-request/candidates/task-request-record/contract.json",
}


def main():
    results = {}
    for name, artifact_path in ARTIFACTS.items():
        artifact_file = ROOT / artifact_path
        contract_file = ROOT / CONTRACTS[name]
        artifact = json.loads(artifact_file.read_text(encoding="utf-8"))
        contract_bytes = contract_file.read_bytes().replace(b"\r\n", b"\n")
        expected = "sha256:" + hashlib.sha256(contract_bytes).hexdigest()
        found = artifact.get("source", {}).get("contract", {}).get("contractDigest")
        if name == "sui":
            # The multi-record document artifact keeps per-record contract digests.
            matches = [
                entry.get("contractDigest") == expected
                for entry in artifact.get("source", {}).get("contracts", {}).values()
            ]
            results[name] = {"match": any(matches), "expected": expected, "found": "per-record"}
            continue
        results[name] = {"match": found == expected, "expected": expected, "found": found}

    all_match = all(item["match"] for item in results.values())
    receipt = {
        "schema": "tai.reference.tei-artifact-digests/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12",
        "command": "python integrations/tools/verify_artifact_digests.py",
        "result": "PASS" if all_match else "FAIL",
        "observed": {"artifacts": results, "allMatch": all_match, "count": len(results)},
        "scope": "Recomputes each artifact's contractDigest from the contract file with LF normalization. It does not verify sourceDigest or the generator binary.",
    }
    out = ROOT / "evaluations/records/TEI-artifact-digests-2026-11-03.json"
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"allMatch": all_match, "count": len(results)}))
    return 0 if all_match else 1


if __name__ == "__main__":
    raise SystemExit(main())
