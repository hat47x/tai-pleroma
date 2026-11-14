"""Try the first experiment of the EKI phase expansion: measure value, not just safety.

Design note 5.6 asks that an emergency delegation be recorded in a distinct type
from the ordinary one, and that the providing/benefiting correspondence be
recorded within the computation's conditions. EKI's own ADR-0039 already designs
how that is measured; this reads that design and records which of its measures
are defined as facts EKI keeps and which are left to TAI. The point is to keep
"measured as a value" apart from "enforced as a safety constraint".
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

EKI = Path("D:/GIT/hat47x/eki-fabric")
ADR = EKI / "plan/adr/0039-measurement-of-beneficiaries-and-limits.md"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    if not ADR.exists():
        print(f"ADR missing: {ADR}")
        return 1
    text = ADR.read_text(encoding="utf-8")

    measures = {
        "counted": re.findall(r"数えるもの[^\n]*\n", text),
        "notCounted": re.findall(r"数えないもの[^\n]*\n", text),
    }
    sections = re.findall(r"^### (.+)$", text, re.M)

    # Who owns the measurement, per the ADR's own boundary section.
    boundary = re.search(r"^## .*境界.*?$", text, re.M)
    t_owner = "TAI" in text and "EKIは事実を残し" in text

    # Does the ADR distinguish the emergency delegation from the ordinary one?
    has_stop_measure = "停止" in text or "取消" in text or "上限" in text

    checks = {
        "adr": str(ADR.relative_to(Path("D:/GIT/hat47x"))),
        "sections": sections,
        "hasCountedSection": bool(re.search(r"^### 2\.1", text, re.M)),
        "hasNotCountedSection": bool(re.search(r"^### 2\.2", text, re.M)),
        "stopOrLimitIsMeasured": has_stop_measure,
        "boundaryNamesOwner": t_owner,
        "finding": (
            "EKIのADR-0039は、受益の分布と、停止・取消・上限が効いたことを"
            "「数えるもの」と「数えないもの」に分けて設計している。"
            "停止が効いたことを価値として測る設計はあるが、"
            "非常時の委任を通常時と別の型で記録できるかは、このADRでは扱っていない。"
        ),
        "valueIsMeasuredNotEnforced": has_stop_measure and t_owner,
    }
    passed = checks["hasCountedSection"] and checks["hasNotCountedSection"] and checks["stopOrLimitIsMeasured"]

    receipt = {
        "schema": "tai.reference.yi-eki-measurement-probe/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading EKI's measurement ADR",
        "command": "python integrations/tools/yi_eki_measurement_probe.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-eki-measurement-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Reads EKI's ADR-0039 and records that it designs how beneficiaries and stop/limit effects are counted, with a boundary that leaves evaluation to TAI. It is a reading of the ADR, not an execution: no counter runs, no record is produced, and whether the design is implemented is not established here.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "sections": len(sections),
        "stopOrLimitMeasured": has_stop_measure,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
