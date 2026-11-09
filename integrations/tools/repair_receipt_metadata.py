"""Record the pre-convention receipts and add the safe metadata they can carry.

Two repairs only:

1. `publicationAllowed: false` on receipts that lack it. The publication gate is
   blocked, so this states the standing position rather than inventing a result.
2. A standard limitation sentence on receipts whose scope has none. The sentence
   adds no claim; it makes the existing limit explicit.

Fields that would require guessing (synthetic, evidenceKind, result, date) are
NOT invented. Those receipts are listed in historical-receipts.json instead, and
the strict gate skips them with that reason.
"""

import argparse
import json
from pathlib import Path

LIMITATION = (
    " このreceiptは実行時点の記録であり、ここに書いた範囲を超える主張はしない。"
)
NEEDS_GUESS = ("schema", "synthetic", "evidenceKind", "date", "result")
REASON = "2026-11-02より前の体裁確立前のreceipt。当時の記録として保持し、証拠としては数えない。"
MARKER = "このreceiptは実行時点の記録であり"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", default="evaluations/records")
    parser.add_argument("--historical", default="evaluations/records/historical-receipts.json")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    records = root / args.records

    publication_added = []
    limitation_added = []
    historical = {}

    for path in sorted(records.glob("*.json")):
        if path.name == "historical-receipts.json":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        changed = False

        if "publicationAllowed" not in data:
            data["publicationAllowed"] = False
            publication_added.append(path.name)
            changed = True

        absent = [key for key in NEEDS_GUESS if key not in data]
        scope = data.get("scope")
        if isinstance(scope, str) and scope.strip() and MARKER not in scope:
            from_limitation_check = True
        else:
            from_limitation_check = False

        if absent:
            historical[path.name] = {"missing": absent, "reason": REASON}

        if changed:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        del from_limitation_check

    # The limitation pass is separate so a rewrite above cannot lose it.
    for path in sorted(records.glob("*.json")):
        if path.name == "historical-receipts.json":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        scope = data.get("scope")
        if not isinstance(scope, str) or not scope.strip():
            continue
        if MARKER in scope:
            continue
        if any(word in scope for word in (" not ", "not ", "しません", "しない", "ではない", "未実施", "未証明", "cannot")):
            continue
        data["scope"] = scope.rstrip() + LIMITATION
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        limitation_added.append(path.name)

    (root / args.historical).write_text(
        json.dumps(
            {
                "schema": "tai.reference.historical-receipts/v0",
                "synthetic": False,
                "evidenceKind": "inspection",
                "publicationAllowed": False,
                "date": "2026-11-06",
                "count": len(historical),
                "reason": REASON,
                "receipts": dict(sorted(historical.items())),
                "scope": "Lists receipts that predate the metadata convention and are kept as historical records. They are not counted as evidence, and their missing fields are not invented. This file does not validate their content.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "publicationAllowedAdded": len(publication_added),
                "limitationAdded": len(limitation_added),
                "historical": len(historical),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
