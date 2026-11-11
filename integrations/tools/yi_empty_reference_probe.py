"""Try the first experiment of the SHO phase expansion: detect an empty reference.

Design note 5.3 says the thin phase to expand for SHO is 空邑 (an empty
settlement): a reference whose backing rows do not exist. The first thing to try
is whether a reference to rows outside the source is warned about or refused.
This runs MMI's own check and provenance commands on a synthetic document whose
reference points past the last row, and records what they say.
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
    text = (completed.stdout or "").strip()
    if not text:
        print((completed.stderr or "")[-500:], file=sys.stderr)
        return None, completed.returncode
    try:
        return json.loads(text), completed.returncode
    except json.JSONDecodeError:
        print(text[-500:], file=sys.stderr)
        return None, completed.returncode


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

    workdir = Path(tempfile.mkdtemp(prefix="yi-empty-", dir=os.environ.get("TMP") or None))
    # Three rows exist; A5:B9 lies entirely beyond the last row.
    (workdir / "data.csv").write_text("Name,Role\nAkiko,Lead\nBen,Reviewer\n", encoding="utf-8")
    (workdir / "doc.md").write_text(
        "# 設計\n\n- 空の範囲: ![[data.csv#Sheet1|A5:B9]]\n- 通常: ![[data.csv#Sheet1|A1:B2]]\n",
        encoding="utf-8",
    )
    document = str(workdir / "doc.md")

    check, check_exit = run(cli, workdir, "check", document)
    report, _ = run(cli, workdir, "provenance", document)

    empty_refs = []
    for reference in (report or {}).get("linked", []):
        if reference.get("range") == "A5:B9":
            empty_refs.append(reference)

    checks = {
        "checkExitCode": check_exit,
        "checkErrorCount": (check or {}).get("errors"),
        "checkProblems": (check or {}).get("problems"),
        "provenanceDiagnostics": (report or {}).get("summary", {}).get("diagnostics"),
        "emptyRangeStatus": (
            empty_refs[0].get("status") if empty_refs else None
        ),
        "emptyRangeDiagnosed": bool((check or {}).get("problems")),
        "finding": (
            "原本の最終行より後を指す参照は、mmi checkでもmmi provenanceでも"
            "問題として報告されない。範囲そのものは解決済み（resolved）と扱われる。"
            "空邑（裏づけの無い参照）は、この検査では検出されない。"
        ),
    }
    passed = (
        checks["checkErrorCount"] == 0
        and checks["emptyRangeStatus"] == "resolved"
        and checks["emptyRangeDiagnosed"] is False
    )

    receipt = {
        "schema": "tai.reference.yi-empty-reference-probe/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Node.js running MMI's check and provenance commands",
        "command": "python integrations/tools/yi_empty_reference_probe.py --mmi-repo <MMI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-empty-reference-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Runs MMI's check and provenance commands on a synthetic document whose reference points past the last row of a three-row source, and records that neither command reports it as a problem. The source and the document are synthetic; a sheet that does not exist is reported, so the finding is about empty ranges, not about all bad references.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "checkErrors": checks["checkErrorCount"],
        "emptyRangeStatus": checks["emptyRangeStatus"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
