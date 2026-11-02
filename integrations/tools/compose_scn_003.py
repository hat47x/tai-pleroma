"""Compose a SUI document artifact with the SEI decision as an extra card."""

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--out", default="evaluations/artifacts/scn-003-document.json")
    parser.add_argument("--receipt-out", default="evaluations/records/SCN-003-compose-2026-11-03.json")
    args = parser.parse_args()

    sui_path = ROOT / "evaluations/artifacts/documentv1-projection.json"
    sei_path = ROOT / "evaluations/artifacts/sei-decision-projection.json"
    sui = json.loads(sui_path.read_text(encoding="utf-8"))
    sei = json.loads(sei_path.read_text(encoding="utf-8"))

    composed = copy.deepcopy(sui)
    decision = sei["decision"]
    eki = json.loads((ROOT / "evaluations/artifacts/eki-task-request-projection.json").read_text(encoding="utf-8"))
    mmi = json.loads((ROOT / "evaluations/artifacts/mmi-format-profile-projection.json").read_text(encoding="utf-8"))
    task = eki["taskRequest"]
    profile = mmi["profile"]

    additions = [
        ("card-decision-1", f"[{decision['refId']}] {decision['statement']}", "sei:decision-1"),
        ("card-task-1", f"[{task['executorId']}] {task['versionConstraint']}", "eki:task-request"),
        ("card-profile-1", f"[{profile['id']}] {profile['label']}", "mmi:format-profile"),
    ]
    reading_order = composed["document"].get("readingOrder")
    for card_id, text, source in additions:
        composed["document"]["cards"].append(
            {"id": card_id, "text": text, "x": 0.0, "y": 0.0, "sources": [source]}
        )
        if isinstance(reading_order, list):
            reading_order.append(card_id)
    composed["scn003"] = {
        "decisionRef": decision["refId"],
        "decisionArtifact": digest(sei_path),
        "taskExecutor": task["executorId"],
        "profileId": profile["id"],
    }

    out_path = ROOT / args.out
    out_path.write_text(json.dumps(composed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    receipt_path = ROOT / args.receipt_out
    validate_out = receipt_path.with_suffix(".validate.json")
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "integrations/pilot-sui-document/assembler/validate_against_sui.py"),
            "--sui-repo",
            args.sui_repo,
            "--artifact",
            str(out_path),
            "--out",
            str(validate_out),
        ],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        print(completed.stderr, file=sys.stderr)
        return 1
    validated = json.loads(validate_out.read_text(encoding="utf-8"))
    valid = bool(validated.get("observed", {}).get("documentV1Valid"))

    receipt = {
        "schema": "tai.reference.scn-003-compose/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 and the SUI consumer",
        "command": "python integrations/tools/compose_scn_003.py --sui-repo <SUI>",
        "result": "PASS" if valid else "FAIL",
        "artifact": {"path": args.out, "digest": digest(out_path)},
        "observed": {
            "valid": valid,
            "cards": len(composed["document"]["cards"]),
            "decisionRef": decision["refId"],
            "taskExecutor": task["executorId"],
            "profileId": profile["id"],
            "cardIds": [card_id for card_id, _, _ in additions],
        },
        "scope": "Adds the SEI decision, EKI task request, and MMI format profile as SUI cards and validates the composed artifact with the SUI consumer. It does not save the document or change SUI.",
    }
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt["observed"]))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
