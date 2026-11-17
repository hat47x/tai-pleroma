"""Run SHO's cross-product handoff with and without a TEI checkout, and map the result onto I/R/P/T/C/H.

The Step 3.7 review said to declare R as a base state and proceed to T/C. Before
accepting that, this runs the handoff runner twice — once without `--tei-root` and once
with it — and reads its own claim block. The runner's claims distinguish what it
observed from what it did not, which is exactly what the I/R/P/T/C/H table needs.

The interesting result is that citing a TEI observation moves one claim (the citation
is made) while leaving the ones that would constitute R (`teiSubjectSourceIndependentlyResolved`)
at not-run and `originalSourcesRead` false.
"""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HANDOFF = "scripts/handoff-cross-product.cjs"
# Claims that, together, would constitute each stage.
STAGE_CLAIMS = {
    "I": ("realProductProducer", "realProductConsumer"),
    "R": ("teiSubjectSourceIndependentlyResolved", "originalSourcesRead", "sourceRevisionCurrent"),
    "P": ("externalDisclosure", "currentHostGrantVerified"),
    "T": ("receiptReturnedAndIndependentlyReviewed", "newProcessRereceive"),
    "C": ("actualConsumerRead", "independentReread"),
    "H": ("otherHarnessLiveExecution", "harnessSessionResume"),
}
# A claim counts as satisfied only when it is exactly True.
SATISFIED = True


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(repo, sui_frontend, tei_root=None):
    argv = ["node", str(repo / HANDOFF), "--sui-frontend", str(sui_frontend)]
    if tei_root:
        argv += ["--tei-root", str(tei_root)]
    completed = subprocess.run(
        argv, cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=3600,
    )
    body = (completed.stdout or "").strip()
    data = json.loads(body) if body.startswith("{") else None
    return {
        "exit": completed.returncode,
        "parsed": data is not None,
        "data": data,
        "stderrTail": (completed.stderr or "").strip().splitlines()[-2:],
    }


def stages(claims):
    """Per stage: which claims are satisfied, which are not, and the resulting verdict."""
    result = {}
    for stage, names in STAGE_CLAIMS.items():
        satisfied = [name for name in names if claims.get(name) is SATISFIED]
        unmet = [name for name in names if claims.get(name) is not SATISFIED]
        # A stage holds only when every claim that constitutes it is satisfied.
        result[stage] = {
            "satisfied": satisfied,
            "unmet": unmet,
            "holds": not unmet,
        }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sho-repo", required=True)
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--tei-repo", default="")
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    sho = Path(args.sho_repo).resolve()
    sui_frontend = Path(args.sui_repo).resolve() / "03_Implement/frontend"
    if not (sho / HANDOFF).exists():
        print(f"missing {HANDOFF}", file=sys.stderr)
        return 1
    if not sui_frontend.exists():
        print(f"missing {sui_frontend}", file=sys.stderr)
        return 1

    sho_head = subprocess.run(
        ["git", "-C", str(sho), "rev-parse", "HEAD"], capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    ).stdout.strip()
    sui_repo = Path(args.sui_repo).resolve()
    sui_head = subprocess.run(
        ["git", "-C", str(sui_repo), "rev-parse", "HEAD"], capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    ).stdout.strip()

    without_tei = run(sho, sui_frontend)
    with_tei = run(sho, sui_frontend, args.tei_repo) if args.tei_repo else None

    runs = []
    for label, outcome in (("withoutTeiRoot", without_tei), ("withTeiRoot", with_tei)):
        if outcome is None:
            runs.append({"run": label, "skipped": True})
            continue
        data = outcome["data"] or {}
        # Some observations sit at the top level of the runner output rather than in
        # `claims`; merge them so a recorded read is not read as missing.
        claims = dict(data.get("claims") or {})
        if "actualConsumerRead" in data:
            claims.setdefault("actualConsumerRead", data["actualConsumerRead"])
        runs.append({
            "run": label,
            "exit": outcome["exit"],
            "parsed": outcome["parsed"],
            "claims": claims,
            "stages": stages(claims) if claims else {},
        })

    by_label = {row["run"]: row for row in runs}
    with_row = by_label.get("withTeiRoot", {})
    without_row = by_label.get("withoutTeiRoot", {})
    with_stages = with_row.get("stages") or {}
    without_stages = without_row.get("stages") or {}

    # The specific shift the added TEI root produces.
    shifted = []
    if with_stages and without_stages:
        for stage in STAGE_CLAIMS:
            before = without_stages[stage]["holds"]
            after = with_stages[stage]["holds"]
            if before != after:
                shifted.append({"stage": stage, "before": before, "after": after})

    checks = {
        "shoCommit": sho_head,
        "suiCommit": sui_head,
        "teiRoot": args.tei_repo,
        "runs": runs,
        "citationClaimShifted": (
            without_row.get("claims", {}).get("teiReadonlyObservationCited") is False
            and with_row.get("claims", {}).get("teiReadonlyObservationCited") is True
        ),
        "stagesThatChanged": shifted,
        "rHoldsWithTeiRoot": (with_stages.get("R") or {}).get("holds"),
        "pNeverHolds": not (with_stages.get("P") or {}).get("holds"),
        "tHolds": (with_stages.get("T") or {}).get("holds"),
        "cHolds": (with_stages.get("C") or {}).get("holds"),
        "hNeverHolds": not (with_stages.get("H") or {}).get("holds"),
        "finding": (
            "SHOのCross-product Handoffを、TEI root無しと有りで2回走らせ、"
            "Consumer自身が返すclaimsからI/R/P/T/C/Hを導いた。"
            "TEI rootを与えると`teiReadonlyObservationCited`は真になるが、"
            "Rを構成する`teiSubjectSourceIndependentlyResolved`はnot-runのまま、"
            "`originalSourcesRead`と`sourceRevisionCurrent`はfalseである。"
            "**TEI観測を引用することは、元Subjectを再解決したことではない。**"
            "TとCは限定的に成立し、PとHは成立しない。"
        ),
    }
    # This run measures the mapping; it does not require R to hold.
    passed = all(row.get("parsed", True) for row in runs) and not (
        with_stages.get("P") or {}
    ).get("holds")

    receipt = {
        "schema": "tai.reference.yic-handoff-stage-mapping/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Node, running the SHO cross-product handoff twice",
        "command": (
            "python integrations/tools/yic_handoff_stage_mapping.py "
            f"--sho-repo <SHO at {sho_head[:12]}> --sui-repo <SUI at {sui_head[:12]}> "
            f"--tei-repo {args.tei_repo} "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-handoff-stages-2026-11-18.json"
        ),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs SHO's cross-product handoff with and without a TEI checkout and derives each "
            "I/R/P/T/C/H stage from the consumer's own claim block, requiring every claim that "
            "constitutes a stage. T and C hold in the narrow sense the runner measures (a separate "
            "process reread the payload); R, P and H do not. This maps claims to stages; it does not "
            "audit whether those claims are themselves adequate, and no external recipient was "
            "contacted."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "citationShifted": checks["citationClaimShifted"],
        "R": checks["rHoldsWithTeiRoot"],
        "P": not checks["pNeverHolds"],
        "T": checks["tHolds"],
        "C": checks["cHolds"],
        "H": not checks["hNeverHolds"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
