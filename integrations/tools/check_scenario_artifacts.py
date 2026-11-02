"""Check that the SCN-002 artifacts carry the documented identifiers."""

import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = {
    "sei": ("evaluations/artifacts/sei-decision-projection.json", ["decision"], "decision-1"),
    "eki": ("evaluations/artifacts/eki-task-request-projection.json", ["taskRequest"], "dev.example.transform"),
    "mmi": ("evaluations/artifacts/mmi-format-profile-projection.json", ["profile"], "profile-a"),
    "sui": ("evaluations/artifacts/documentv1-projection.json", ["document", "document"], "doc-1"),
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    results = {}
    for name, (path, keys, wanted) in ARTIFACTS.items():
        payload = json.loads((ROOT / path).read_text(encoding="utf-8"))
        node = payload
        for key in keys:
            node = node[key]
        found = wanted in json.dumps(node, ensure_ascii=False)
        results[name] = {"found": found, "identifier": wanted, "artifact": path, "digest": digest(ROOT / path)}

    all_found = all(item["found"] for item in results.values())
    receipt = {
        "schema": "tai.reference.scn-002-artifact-links/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12",
        "command": "python integrations/tools/check_scenario_artifacts.py",
        "result": "PASS" if all_found else "FAIL",
        "observed": {"artifacts": results, "allFound": all_found, "count": len(results)},
        "scope": "Checks that the four SCN-002 artifacts exist and contain the documented identifiers. It does not prove that a product would accept them.",
    }
    out = ROOT / "evaluations/records/SCN-002-artifact-links-2026-11-03.json"
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"allFound": all_found, "count": len(results)}))
    return 0 if all_found else 1


if __name__ == "__main__":
    raise SystemExit(main())
