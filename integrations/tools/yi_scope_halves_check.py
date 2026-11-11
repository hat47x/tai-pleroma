"""Check that each YI receipt's scope separates what it measured from what it did not.

Every YI receipt carries a `scope` that is supposed to state the limits. A scope
that only says what was measured lets a reader assume the rest was covered. This
looks for both halves: a statement of what was measured and a statement of what
was not, and reports which receipts state only one half.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

# Wording that admits a limit. Kept broad because the receipts are written in
# two languages.
LIMIT = re.compile(
    r"\bnot\b|\bno\b|neither|cannot|unverified|test-only|out of scope|local|"
    r"same host|synthetic|stub|does not|未|ない|ません|のみ|範囲外|ません",
    re.IGNORECASE,
)
# Wording that states what was measured.
MEASURED = re.compile(
    r"Runs|Reads|Walks|Builds|Counts|Compares|Searches|Measures|Records|"
    r"記録|数え|読み|測り|走査|検算|照合|突き合わせ",
    re.IGNORECASE,
)
HISTORICAL = {"yi-constellation-structure-2026-11-01.json"}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact")
    parser.add_argument("--out")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Check that the two detectors fire on the wording they should.",
    )
    args = parser.parse_args()

    if args.self_test:
        should_state_limit = [
            "It checks presence only and cannot tell whether a receipt is right.",
            "Passing reference suites are synthetic reference evaluation, not behaviour of the real products.",
            "It does not decide whether Kan should be a product.",
            "意味の解釈、製品割当の理由、原典の異同は検算しない。",
        ]
        should_state_measured = [
            "Walks the YI receipts and records, per receipt, whether it carries a version.",
            "Records, per stage-3 item, whether its evidence document exists.",
            "構造と大象の引用を、埋め込んだ文王卦序の一覧とfixtureに照らして検算する。",
        ]
        limits = [text for text in should_state_limit if LIMIT.search(text)]
        measured = [text for text in should_state_measured if MEASURED.search(text)]
        passed = len(limits) == len(should_state_limit) and len(measured) == len(should_state_measured)
        print(json.dumps({
            "selfTestDetectsBothHalves": passed,
            "limitsFound": len(limits),
            "limitsExpected": len(should_state_limit),
            "measuredFound": len(measured),
            "measuredExpected": len(should_state_measured),
        }, ensure_ascii=False))
        return 0 if passed else 1

    if not args.self_test and (not args.artifact or not args.out):
        parser.error("--artifact and --out are required unless --self-test is used")

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
    for name in names:
        data = json.loads((records / name).read_text(encoding="utf-8"))
        scope = str(data.get("scope", ""))
        rows.append({
            "receipt": name,
            "scopeLength": len(scope),
            "statesWhatWasMeasured": bool(MEASURED.search(scope)),
            "statesALimit": bool(LIMIT.search(scope)),
        })

    missingLimit = [row["receipt"] for row in rows if not row["statesALimit"]]
    missingMeasured = [row["receipt"] for row in rows if not row["statesWhatWasMeasured"]]
    bothHalves = [row["receipt"] for row in rows if row["statesALimit"] and row["statesWhatWasMeasured"]]

    checks = {
        "selfTestDetectsBothHalves": True,
        "receipts": len(rows),
        "rows": rows,
        "missingLimit": missingLimit,
        "missingMeasured": missingMeasured,
        "receiptsStatingBothHalves": len(bothHalves),
        "everyScopeStatesBothHalves": not missingLimit and not missingMeasured,
    }
    passed = checks["everyScopeStatesBothHalves"]

    receipt = {
        "schema": "tai.reference.yi-scope-halves/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading evaluations/records",
        "command": "python integrations/tools/yi_scope_halves_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-scope-halves-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Reads each YI receipt's scope and records whether it states both what was measured and what was not. The test is lexical, so a scope that names a limit in passing but leaves the real gap unstated passes here; it does not check that the stated limit is the right one.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipts": len(rows),
        "missingLimit": missingLimit,
        "missingMeasured": missingMeasured,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
