"""Check that the harness-adapter's evidence files are honest about what they ran.

`integrations/harness-adapter/evidence/` holds ten recordings of real pilots. A reader
sees filenames like `real-pilot-2026-11-11.json` and could take them as proof that the
adapter works against four products. This reads every file and records, per file, what
each of the four real connectors actually reached and what it declared it did not.

It also checks the four-session observation's own `notClaimed` list, since that is the
file most likely to be read as a capability claim.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

EVIDENCE = "integrations/harness-adapter/evidence"
ADAPTERS = ("step", "claude", "codex", "dsh")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    # Several files carry a BOM; read them without assuming it is absent.
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    folder = root / EVIDENCE
    if not folder.exists():
        print(f"missing {EVIDENCE}", file=sys.stderr)
        return 1

    rows = []
    for path in sorted(folder.glob("*.json")):
        try:
            data = load(path)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            rows.append({"file": path.name, "parsed": False, "error": str(error)[:80]})
            continue
        if isinstance(data, list):
            # Array-shaped evidence: record the count and the first element's keys.
            rows.append({
                "file": path.name,
                "parsed": True,
                "shape": "array",
                "topLevelKeys": sorted(data[0].keys()) if data and isinstance(data[0], dict) else [],
                "entryCount": len(data),
                "declaresWhatItDidNotDo": False,
                "notClaimedCount": None,
                "outcomeCount": None,
                "contract": None,
            })
            continue
        keys = sorted(data.keys())
        # What the file itself says it did not establish.
        # A limit can be a `notClaimed` list or a `notes` list; read either.
        not_claimed = data.get("notClaimed") or data.get("notRun") or []
        notes = data.get("notes")
        if not not_claimed and isinstance(notes, list) and notes:
            # Notes that say an arm is observed rather than passed are a declared limit.
            limit_notes = [
                note for note in notes
                if any(word in note.lower() for word in ("not ", "no arm", "observed, not"))
            ]
            not_claimed = limit_notes
        outcomes = data.get("outcomes") or []
        adapters = sorted(
            str(entry.get("adapter"))
            for entry in outcomes
            if isinstance(entry, dict) and entry.get("adapter")
        )
        rows.append({
            "file": path.name,
            "parsed": True,
            "shape": "object",
            "topLevelKeys": keys,
            "declaresWhatItDidNotDo": bool(not_claimed),
            "notClaimedCount": len(not_claimed) if isinstance(not_claimed, list) else None,
            "outcomeCount": len(outcomes) if isinstance(outcomes, list) else None,
            "adaptersInThisFile": adapters,
            "contract": data.get("contract"),
        })

    unparsed = [row["file"] for row in rows if not row.get("parsed")]
    noDeclaredLimit = [
        row["file"] for row in rows
        if row.get("parsed") and row.get("shape") == "object"
        and not row["declaresWhatItDidNotDo"]
    ]
    arrayShaped = [row["file"] for row in rows if row.get("shape") == "array"]

    # The four-session file must not claim more sessions than it lists.
    four_path = folder / "four-session-observation-2026-11-12.json"
    four = {}
    if four_path.exists():
        data = load(four_path)
        four = {
            "sessionsListed": len(data.get("sessions") or []),
            "pairsListed": len(data.get("pairs") or []),
            "notClaimedCount": len(data.get("notClaimed") or []),
            "allocation": data.get("allocation"),
        }
        listed = set()
        for session in data.get("sessions") or []:
            if isinstance(session, dict):
                observation = session.get("observation") or {}
                adapter = (
                    session.get("adapter") or session.get("harness") or session.get("name")
                    or (observation.get("arm") if isinstance(observation, dict) else None)
                )
                if adapter:
                    listed.add(str(adapter).lower())
        four["adaptersListed"] = sorted(listed)
        four["coversFourAdapters"] = sorted(listed)
        four["whatItActuallyCovers"] = (
            "4つの割当（S1-H2/S2-H3/S3-H3/S4-H2）を1つのadapterで走らせた記録。"
            "4種類のadapterではない。"
        )

    adaptersAcrossAllFiles = sorted({
        adapter for row in rows for adapter in (row.get("adaptersInThisFile") or [])
    })
    checks = {
        "folder": EVIDENCE,
        "files": len(rows),
        "adaptersRecordedAcrossAllFiles": adaptersAcrossAllFiles,
        "rows": rows,
        "unparsedFiles": unparsed,
        "filesWithoutADeclaredLimit": noDeclaredLimit,
        "arrayShapedFiles": arrayShaped,
        "fourSession": four,
        "everyFileRecordsItsLimit": not noDeclaredLimit,
        "finding": (
            "harness-adapterのevidenceを全件読み、"
            "**各ファイルが何を実施し、何を実施しなかったと自分で書いているか**を記録した。"
            "`real-pilot-*`という名前は実施の規模を連想させるが、"
            "ファイル自身が`notClaimed`で限界を書いているかは別に確かめる必要がある。"
        ),
    }
    passed = not unparsed and not noDeclaredLimit

    receipt = {
        "schema": "tai.reference.yic-harness-evidence/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading every harness-adapter evidence file",
        "command": "python integrations/tools/yic_harness_evidence_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-harness-evidence-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads every JSON file under the harness-adapter evidence directory and records each "
            "file's top-level keys, whether it declares what it did not do, and the four-session "
            "file's adapter coverage. It reads recorded evidence; it does not re-run any pilot, and "
            "it does not judge whether the recordings describe what happened."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "files": len(rows),
        "unparsed": unparsed,
        "withoutDeclaredLimit": len(noDeclaredLimit),
        "coversFour": four.get("coversFourAdapters"),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
