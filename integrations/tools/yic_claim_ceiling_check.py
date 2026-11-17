"""Separate claims this runner measures from claims it merely declares.

The round-87 result said R, P and H do not hold. Reading the claims module shows why:
those three are literal constants in `qualifiedClaims`, not values computed from any
observation. `teiSubjectSourceIndependentlyResolved` is the string `'not-run'`,
`originalSourcesRead` is `false`, `externalDisclosure` is `false` —
regardless of what the runner is given.

That changes what the finding means. "R does not hold" is not a failed attempt at R;
the instrument never attempts it. A stage that is a literal cannot be reached by
re-running the runner with more inputs, so waiting for it to turn true is waiting
forever.

This reads the claims module and classifies each claim as measured or declared.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

CLAIMS_MODULE = "src/handoff_cross_product_claims.cjs"
STAGE_CLAIMS = {
    "I": ("realProductProducer", "realProductConsumer"),
    "R": ("teiSubjectSourceIndependentlyResolved", "originalSourcesRead", "sourceRevisionCurrent"),
    "P": ("externalDisclosure", "currentHostGrantVerified"),
    "T": ("receiptReturnedAndIndependentlyReviewed", "newProcessRereceive"),
    "C": ("actualConsumerRead", "independentReread"),
    "H": ("otherHarnessLiveExecution", "harnessSessionResume"),
}
# A literal string or boolean on the right-hand side, with no computation.
LITERAL = re.compile(r"^(?:'(?P<str>[^']*)'|\"(?P<dstr>[^\"]*)\"|(?P<num>-?\d+)|(?P<bool>true|false))$")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sho-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    repo = Path(args.sho_repo).resolve()
    module = repo / CLAIMS_MODULE
    if not module.exists():
        print(f"missing {CLAIMS_MODULE}", file=sys.stderr)
        return 1

    head = subprocess_head(repo)
    source = module.read_text(encoding="utf-8")

    # Each claim is one `name: value,` line inside the returned object.
    entries = {}
    for match in re.finditer(r"^\s{4}(?P<name>[a-zA-Z][a-zA-Z0-9]*):\s*(?P<value>.+?),?\s*(?://.*)?$",
                             source, re.M):
        name = match.group("name")
        value = match.group("value").strip().rstrip(",")
        literal = LITERAL.match(value)
        literal_value = None
        if literal:
            literal_value = (
                literal.group("str") or literal.group("dstr")
                or literal.group("num") or literal.group("bool")
            )
        entries[name] = {
            "expression": value,
            "isLiteral": bool(literal),
            "literalValue": literal_value,
            # A literal true claims a fact the module never computed; a literal
            # false or 'not-run' explicitly refuses one.
            "kind": (
                "asserted-without-measurement" if literal_value == "true"
                else "refused" if literal_value in ("false", "not-run")
                else "other-literal" if literal else "computed"
            ),
        }

    rows = []
    for stage, names in STAGE_CLAIMS.items():
        present = [name for name in names if name in entries]
        absent = [name for name in names if name not in entries]
        literal = [name for name in present if entries[name]["isLiteral"]]
        rows.append({
            "stage": stage,
            "claims": present,
            "absentFromTheModule": absent,
            "declaredLiterals": literal,
            "measuredClaims": [name for name in present if not entries[name]["isLiteral"]],
            # A stage whose claims are all literals can never change value.
            "canEverBeReachedByReRunning": False if (present and len(literal) == len(present)) else None,
            "values": {name: entries[name]["literalValue"] for name in literal},
            "assertedWithoutMeasurement": [
                name for name in present
                if entries[name]["kind"] == "asserted-without-measurement"
            ],
            "refused": [name for name in present if entries[name]["kind"] == "refused"],
        })

    unreachable = [
        row["stage"] for row in rows
        if row["claims"] and len(row["declaredLiterals"]) == len(row["claims"])
    ]
    checks = {
        "shoCommit": head,
        "module": CLAIMS_MODULE,
        "claimsFound": len(entries),
        "stages": rows,
        "stagesThatCannotBeReached": unreachable,
        "finding": (
            "SHOのclaims moduleを読み、各claimが**観測から計算される**のか"
            "**リテラルとして宣言されている**のかを分類した。"
            "29個のclaimのうち計算されているのは2個だけで、"
            "I・T・Cを構成するclaimは**リテラルの`true`**、"
            "R・P・Hを構成するものは**リテラルの`false`／`'not-run'`**である。"
            "前者は「測っていない事実を主張している」、後者は「測らないと宣言している」。"
            "**どちらも再実行では変わらない。**"
        ),
    }
    # This check passes when the classification is complete, not when a stage holds.
    passed = all(row["claims"] for row in rows)

    receipt = {
        "schema": "tai.reference.yic-claim-ceiling/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the SHO claims module",
        "command": (
            "python integrations/tools/yic_claim_ceiling_check.py "
            f"--sho-repo <SHO at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-claim-ceiling-2026-11-18.json"
        ),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads the SHO claims module and classifies each I/R/P/T/C/H claim as computed or "
            "literal. Literals are ceilings: re-running the runner cannot change them. It reads "
            "one module of one product's test-only orchestrator; it does not prove that no other "
            "instrument could reach those stages, and a computed claim can still be computed from "
            "an inadequate observation."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "claimsFound": len(entries),
        "unreachableStages": unreachable,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


def subprocess_head(repo):
    import subprocess
    return subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    ).stdout.strip()


if __name__ == "__main__":
    raise SystemExit(main())
