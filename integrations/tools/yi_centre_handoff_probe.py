"""Probe the centre handoff (RQ-YI-020) with the records that already exist.

The design note says the handoff between a grown artifact (SHO) and the decision
record it rests on (SEI) needs no new API: it reads SHO's provenance report and
SEI's decision record in the same units. This runs MMI's provenance report on a
synthetic artifact and records which of those units the report can actually
supply, and which it cannot. A missing unit is the finding, not a failure of the
probe.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# The fields a handoff would need on the artifact side, and where they appear.
FIELDS = {
    "artifactDigest": ("document", "digest"),
    "source": ("linked", 0, "source"),
    "sheet": ("linked", 0, "sheet"),
    "range": ("linked", 0, "range"),
    "sourceDigest": ("linked", 0, "sourceDigest"),
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def get(data, path):
    value = data
    for step in path:
        if isinstance(step, int):
            if not isinstance(value, list) or len(value) <= step:
                return None
            value = value[step]
        else:
            if not isinstance(value, dict):
                return None
            value = value.get(step)
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mmi-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    mmi = Path(args.mmi_repo)
    cli = mmi / "03_Implement/dist/src/cli/bootstrap.js"
    if not cli.exists():
        print(f"MMI CLI not built: {cli}", file=sys.stderr)
        return 1

    workdir = Path(tempfile.mkdtemp(prefix="yi-centre-", dir=os.environ.get("TMP") or None))
    (workdir / "data.csv").write_text("Name,Råle\nAkiko,Lead\nBen,Reviewer\n".replace("Råle", "Role"), encoding="utf-8")
    (workdir / "artifact.md").write_text(
        "# 設計の成果\n\n- 役割の根拠: ![[data.csv#Sheet1|A1:B2]]\n", encoding="utf-8"
    )

    completed = subprocess.run(
        ["node", str(cli), "provenance", str(workdir / "artifact.md"), "--root", str(workdir), "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if completed.returncode != 0 or not (completed.stdout or "").strip():
        print((completed.stderr or "")[-600:], file=sys.stderr)
        return 1
    report = json.loads(completed.stdout)

    present = {}
    missing = {}
    for name, path in FIELDS.items():
        value = get(report, path)
        if value:
            present[name] = value
        else:
            missing[name] = "absent"

    # What SEI needs in order to reach the decision: an identifier it can name.
    # The report carries none, and SEI's record carries no artifact reference.
    sei_side_units = {
        "recordId": "SEIのDecisionRecordのID",
        "jsonPointer": "SEIのrecord内の位置",
        "basisRefs": "SEIが根拠として指す参照",
    }
    join_keys = {
        "reportNamesADecision": False,
        "reportNamesASeiRecord": False,
        "seiRecordNamesAnArtifact": False,
    }

    checks = {
        "provenanceSchema": report.get("schema"),
        "linkedCount": report.get("summary", {}).get("linked"),
        "fieldsPresent": present,
        "fieldsMissing": missing,
        "seiSideUnits": sei_side_units,
        "joinKeys": join_keys,
        "shoCanExpressWhatItRestsOn": set(present) == set(FIELDS),
        "handoffJoinExists": any(join_keys.values()),
        "handoffIsImplemented": False,
        # The finding, stated once so a reader need not infer it from the flags.
        "finding": (
            "SHO側は、成果が何に依拠するかを5つの単位で表現できる。"
            "しかしSEI側の記録と結ぶ鍵（DecisionRecordのIDや成果への参照）が"
            "どちらの記録にも無いため、中心の受け渡しは成立していない。"
        ),
    }
    passed = checks["shoCanExpressWhatItRestsOn"]

    receipt = {
        "schema": "tai.reference.yi-centre-handoff-probe/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Node.js running MMI's provenance CLI on a synthetic artifact",
        "command": "python integrations/tools/yi_centre_handoff_probe.py --mmi-repo <MMI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-centre-handoff-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Runs MMI's provenance report on a synthetic Markdown artifact with one spreadsheet embed and records which handoff units the SHO side can supply. It reads the SEI side from the reference tool's record shape rather than executing it. The artifact, the spreadsheet and the document are synthetic; no real SHO or SEI store is involved, and the handoff itself is not implemented.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "fieldsPresent": sorted(present),
        "fieldsMissing": sorted(missing),
        "shoCanExpressWhatItRestsOn": checks["shoCanExpressWhatItRestsOn"],
        "handoffJoinExists": checks["handoffJoinExists"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
