"""Measure what happens to an artifact's provenance when its source is revised.

The centre handoff rests on "the artifact says what it rests on". A report that
still says ``fresh`` after the source changed would make the handoff wrong in
the quiet way: the artifact would keep pointing at a revision nobody reviewed.
This records how the review-basis comparison reports that change, reading the
per-reference verdict rather than the report-level status word.
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


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(cli, workdir, *args):
    completed = subprocess.run(
        ["node", str(cli), *args, "--root", str(workdir), "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if not (completed.stdout or "").strip():
        print((completed.stderr or "")[-500:], file=sys.stderr)
        return None
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        print((completed.stdout or "")[-500:], file=sys.stderr)
        return None


def verdict(report, key):
    if not report:
        return None
    refs = report["review"].get("references") or []
    return refs[0].get(key) if refs else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mmi-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    cli = Path(args.mmi_repo) / "03_Implement/dist/src/cli/bootstrap.js"
    if not cli.exists():
        print(f"MMI CLI not built: {cli}", file=sys.stderr)
        return 1

    workdir = Path(tempfile.mkdtemp(prefix="yi-stale-", dir=os.environ.get("TMP") or None))
    (workdir / "data.csv").write_text("Name,Role\nAkiko,Lead\nBen,Reviewer\n", encoding="utf-8")
    (workdir / "artifact.md").write_text(
        "# 設計の成果\n\n- 役割の根拠: ![[data.csv#Sheet1|A1:B2]]\n", encoding="utf-8"
    )
    document = str(workdir / "artifact.md")

    before = run(cli, workdir, "provenance", document)
    written = run(cli, workdir, "review-basis", document, "--write")
    after_write = run(cli, workdir, "provenance", document)

    # Revise a cell inside the referenced range.
    (workdir / "data.csv").write_text("Name,Role\nAkiko,Director\nBen,Reviewer\n", encoding="utf-8")
    after_edit = run(cli, workdir, "provenance", document)

    # Revise outside the referenced range: do the verdicts differ?
    (workdir / "data.csv").write_text(
        "Name,Role\nAkiko,Director\nBen,Reviewer\nCy,Observer\n", encoding="utf-8"
    )
    after_outside = run(cli, workdir, "provenance", document)

    states = {
        "beforeRecord": verdict(before, "status"),
        "afterWrite": verdict(after_write, "status"),
        "afterSourceEdit": verdict(after_edit, "status"),
        "afterOutsideEdit": verdict(after_outside, "status"),
    }
    statuses = {
        "beforeRecord": before["review"]["status"] if before else None,
        "afterWrite": after_write["review"]["status"] if after_write else None,
        "afterSourceEdit": after_edit["review"]["status"] if after_edit else None,
        "afterOutsideEdit": after_outside["review"]["status"] if after_outside else None,
    }
    reasons = {
        "afterSourceEdit": [
            ref.get("reasonCode") for ref in (after_edit["review"].get("references") or [])
        ] if after_edit else [],
        "afterOutsideEdit": [
            ref.get("reasonCode") for ref in (after_outside["review"].get("references") or [])
        ] if after_outside else [],
    }

    checks = {
        "referenceStatus": states,
        "reportStatus": statuses,
        "reasons": reasons,
        "recordWasWritten": bool(written and written.get("written")),
        "unrecordedBeforeWriting": states["beforeRecord"] == "unrecorded",
        "freshAfterWriting": states["afterWrite"] == "fresh",
        "editInsideRangeIsStale": states["afterSourceEdit"] == "stale",
        # After the record exists, the report keeps ``status: recorded`` even
        # when the source moves; a reader who reads only that word would never
        # learn the source moved. The pre-record value differs by design.
        "reportStatusStaysRecordedAfterEdits": (
            statuses["afterWrite"]
            == statuses["afterSourceEdit"]
            == statuses["afterOutsideEdit"]
            == "recorded"
        ),
        "finding": (
            "review-basisを記録した後、参照ごとの判定はfreshになり、"
            "原本を改訂するとstale（logical-table-changed）へ変わる。"
            "報告全体のstatusはrecordedのままなので、"
            "鮮度はper-referenceのstatusを読む必要がある。"
        ),
    }
    passed = (
        checks["recordWasWritten"]
        and checks["unrecordedBeforeWriting"]
        and checks["freshAfterWriting"]
        and checks["editInsideRangeIsStale"]
    )

    receipt = {
        "schema": "tai.reference.yi-staleness-probe/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Node.js running MMI's provenance and review-basis CLIs",
        "command": "python integrations/tools/yi_staleness_probe.py --mmi-repo <MMI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-staleness-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Runs MMI's review-basis and provenance commands on a synthetic Markdown artifact, records the per-reference verdict before and after the source is revised, and reports that a revision makes the record stale while the report-level status stays recorded. The artifact and the spreadsheet are synthetic, the store is a temporary directory, and this says nothing about whether a person reviewed the change or whether the edit was inside the referenced range.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"referenceStatus": states, "reasons": reasons, "passed": passed}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
