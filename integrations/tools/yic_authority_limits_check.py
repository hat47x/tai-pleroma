"""Check that receipts quoting a Product's own authority limits keep them verbatim.

Three rounds in a row, the interesting fact was the Product declaring its own limit:
`local-read-is-not-disclosure-permission`, `selective-disclosure-is-not-access-control-or-redaction`,
`source-location-is-not-semantic-acceptance`. A receipt that paraphrases such a
string, or drops it, loses the one thing that keeps a capability claim honest. This
walks the YIC receipts and reports, per receipt, which limit strings it preserved,
and fails when a receipt records Product output that carried limits but kept none.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

# Limit strings have this shape: lowercase words joined by hyphens.
LIMIT_SHAPE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+){2,}$")
# Fields that carry Product output which normally also carries limits.
PRODUCT_OUTPUT_KEYS = ("result", "sources", "trace", "authorityLimits")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def collect(node, path, limits, result_present):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "authorityLimits" and isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and LIMIT_SHAPE.match(item):
                        limits.append({"path": "/".join(path + [key]), "limit": item})
            if key in PRODUCT_OUTPUT_KEYS:
                result_present.append("/".join(path + [key]))
            collect(value, path + [key], limits, result_present)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            collect(value, path + [str(index)], limits, result_present)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    records = root / "evaluations/records"
    own = Path(args.out).name

    rows = []
    for path in sorted(records.glob("YIC-*.json")):
        if path.name == own:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        limits, product_output = [], []
        collect(data.get("observed"), [], limits, product_output)
        unique = sorted({item["limit"] for item in limits})
        # A nested `result` block is Product output; a top-level one is our verdict.
        declares_result = any(item.endswith("result") for item in product_output)
        rows.append({
            "receipt": path.name,
            "limitsKept": len(unique),
            "limits": unique,
            "recordsProductResult": declares_result,
        })

    with_limits = [row for row in rows if row["limitsKept"] > 0]
    # Commands whose output is known to declare limits: a receipt from one of them
    # that kept none means the limits were dropped on the way into the record.
    LIMIT_BEARING = (
        "inspect",
        "model locate",
        "knowledge-context",
        "trace",
        "validate",
    )
    resultWithoutLimits = []
    for path in sorted(records.glob("YIC-*.json")):
        if path.name == own:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        text = json.dumps(data, ensure_ascii=False)
        limits, _ = [], []
        collect(data.get("observed"), [], limits, [])
        if limits:
            continue
        if any(f"cmd/tei {command}" in text or f'"tei {command}"' in text
               for command in LIMIT_BEARING):
            resultWithoutLimits.append(path.name)
    all_limits = sorted({limit for row in rows for limit in row["limits"]})

    checks = {
        "receipts": len(rows),
        "rows": rows,
        "receiptsKeepingLimits": len(with_limits),
        "receiptsRecordingProductResult": len(
            [row for row in rows if row["recordsProductResult"]]
        ),
        "productResultsWithoutKeptLimits": resultWithoutLimits,
        "distinctLimits": len(all_limits),
        "limits": all_limits,
        "everyProductResultKeepsItsLimits": not resultWithoutLimits,
        "finding": (
            "YICのreceiptがProduct出力を記録するとき、Product自身が返す"
            "`authorityLimits`をそのまま保持しているかを点検した。"
            "限界の文字列を言い換えたり落としたりすると、"
            "「できること」と「許可されていること」の区別が記録から消える。"
        ),
    }
    passed = not resultWithoutLimits

    receipt = {
        "schema": "tai.reference.yic-authority-limits-kept/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading evaluations/records",
        "command": "python integrations/tools/yic_authority_limits_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-authority-limits-2026-11-16.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads the YIC receipts and counts which Product-declared limit strings each one keeps "
            "verbatim, flagging receipts that record a Product result but keep none. It checks "
            "preservation, not interpretation: a receipt can keep every limit and still draw a "
            "conclusion the limit forbids, and a limit the Product never printed cannot be checked."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipts": len(rows),
        "withLimits": len(with_limits),
        "distinctLimits": len(all_limits),
        "productResultsWithoutLimits": resultWithoutLimits,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
