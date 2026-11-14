"""Classify SCN-001's negative cases into the six states of the TAI expansion.

Design note 5.1 asks for the first trial of TAI's thin phase: "classify SCN-001's
negative examples into the six states -- not connected, not accepted, not
decided, not executed, unconfirmed, refused." Distinguishing those six keeps a
failure from being read as the wrong kind of stop. This runs SCN-001, reads each
case's own check, and records which state each negative example belongs to and
which states have no example at all.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# The six states the expansion names, with the checks that observe them.
STATES = {
    "notConnected": {
        "label": "未接続",
        "observed_by": [],
        "meaning": "接続そのものが無い",
    },
    "notAccepted": {
        "label": "不受理",
        "observed_by": [],
        "meaning": "製品が受け取らない",
    },
    "notDecided": {
        "label": "未受理",
        "observed_by": ["N-02"],
        "meaning": "記録はあるが、判断として受理されていない",
    },
    "notExecuted": {
        "label": "未実行",
        "observed_by": ["N-05"],
        "meaning": "判断はあるが実行されていない",
    },
    "unconfirmed": {
        "label": "未確認",
        "observed_by": ["N-03", "P-04"],
        "meaning": "根拠が取得できない、または権限が確認できない",
    },
    "refused": {
        "label": "拒否",
        "observed_by": ["N-01", "N-04", "N-06", "N-07", "N-08", "N-09", "N-10"],
        "meaning": "構造の検査が拒否する",
    },
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tai-root", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(args.tai_root)
    tool = root / "tools/reference-scn001"
    if not (tool / "main.go").exists():
        print(f"reference tool missing: {tool}", file=sys.stderr)
        return 1

    workdir = Path(tempfile.mkdtemp(prefix="yi-classify-", dir=os.environ.get("TMP") or None))
    receipt_path = workdir / "scn001.json"
    completed = subprocess.run(
        ["go", "run", ".", "-fixture", "testdata/scn001.json", "-out", str(receipt_path)],
        cwd=tool, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if completed.returncode != 0 or not receipt_path.exists():
        print((completed.stderr or "")[-600:], file=sys.stderr)
        return 1
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

    cases = {case["id"]: case for case in receipt.get("cases", [])}
    source = (tool / "main.go").read_text(encoding="utf-8")

    # Every check id that appears in the reference, so an unnamed state is visible.
    ids = sorted(set(re.findall(r'"(P-0\d|N-\d\d)"', source)))
    named = set()
    for state in STATES.values():
        named.update(state["observed_by"])
    # Negative checks that no state claims.
    unclassified = [identifier for identifier in ids if identifier.startswith("N-") and identifier not in named]
    # States with no check at all.
    absent = [name for name, state in STATES.items() if not state["observed_by"]]

    observed = {}
    for name, state in STATES.items():
        observed[name] = {
            "label": state["label"],
            "meaning": state["meaning"],
            "checks": state["observed_by"],
            "checkStatuses": {
                check: (cases.get(check) or {}).get("status") for check in state["observed_by"]
            },
        }

    checks = {
        "states": observed,
        "referencePassed": receipt.get("passed") is True,
        "negativeChecksInReference": [identifier for identifier in ids if identifier.startswith("N-")],
        "unclassifiedChecks": unclassified,
        "statesWithoutAnExample": absent,
        "everyStateHasAnExample": not absent,
        "everyNegativeCheckIsClassified": not unclassified,
        "finding": (
            "SCN-001の負例は、拒否（構造の検査）・未確認（取得できない根拠）・"
            "未受理（判断が未受理のまま）・未実行（委任が対象外）に分かれる。"
            "未接続と不受理には、対応する例が無い。"
            "この二つは、SCN-001の検査が製品間の接続を扱わないために例を持てない。"
        ),
    }
    passed = checks["referencePassed"] and not unclassified

    out = {
        "schema": "tai.reference.yi-state-classification/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go running the SCN-001 reference",
        "command": "python integrations/tools/yi_state_classification.py --tai-root . --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-state-classification-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Runs SCN-001 and maps its negative checks onto the six states named in the design note, recording which states have an example and which do not. The mapping is the author's reading of each check's text, not something the reference declares; the fixture is synthetic and no real product is involved.",
    }
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "statesWithoutAnExample": absent,
        "unclassifiedChecks": unclassified,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
