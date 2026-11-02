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
    card_id = "card-decision-1"
    composed["document"]["cards"].append(
        {
            "id": card_id,
            "text": f"[{decision['refId']}] {decision['statement']}",
            "x": 0.0,
            "y": 0.0,
            "sources": ["sei:decision-1"],
        }
    )
    reading_order = composed["document"].get("readingOrder")
    if isinstance(reading_order, list):
        reading_order.append(card_id)
    composed["scn003"] = {
        "decisionRef": decision["refId"],
        "decisionArtifact": digest(sei_path),
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
            "cardId": card_id,
        },
        "scope": "Adds the SEI decision as one SUI card and validates the composed artifact with the SUI consumer. It does not save the document or change SUI.",
    }
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt["observed"]))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
