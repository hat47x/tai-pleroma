"""Validate every projected record against SUI's own model, not against the contract.

The conformance flow compares the projection with expectations written next to the
contract, so it is not independent of the meaning. SUI's DocumentV1 model is an
outside source of truth. This takes each present fixture case, projects it through
the TEI candidate, and asks SUI's model whether the resulting document is valid.
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

CONTRACTS = {
    "document-record": ("document", "text-record-template"),
    "card-record": ("cards", "text-record-template"),
    "island-record": ("islands", "text-record-template"),
    "edge-record": ("edges", "text-record-template"),
}

PROBE = """
import json, sys
from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload
from sui_sensemaking_api.models import DocumentV1

artifact = json.load(open(sys.argv[1], encoding="utf-8"))
try:
    payload = to_documentv1_payload(
        from_artifact(artifact),
        transform={"panX": 0.0, "panY": 0.0, "zoom": 1.0},
        created_at="2026-11-03T00:00:00Z",
        updated_at="2026-11-03T00:00:00Z",
    )
    model = DocumentV1.model_validate(payload)
except Exception as error:  # noqa: BLE001 - the reason is reported, not raised
    print(json.dumps({"valid": False, "reason": f"{type(error).__name__}: {error}"}))
else:
    print(json.dumps({"valid": True, "reason": None}))
"""


# SUI's consumer requires the Edge endpoint kinds even though its model declares
# them optional, so the pilot's kind-less edge records are refused there. The
# three cases below are that mismatch, not a projection failure.
KNOWN_INVALID = [
    "edge-record:absent-kinds",
    "edge-record:absent-one-kind",
    "edge-record:null-kind-is-omitted",
]


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args, cwd, stdin_text=None):
    return subprocess.run(
        [str(part) for part in args],
        cwd=cwd, input=stdin_text, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def build(tei_repo, contract, strategy, out_dir):
    built = run(
        ["go", "run", "./tools/reference-generator-selection/cmd/tei-generator-build",
         "-contract", contract, "-strategy", strategy, "-out", out_dir],
        cwd=tei_repo,
    )
    if built.returncode != 0:
        return None, (built.stderr or built.stdout).strip().splitlines()[-1:]
    binary = Path(out_dir) / ("candidate.exe" if os.name == "nt" else "candidate")
    compiled = run(["go", "build", "-o", binary, "main.go"], cwd=out_dir)
    if compiled.returncode != 0:
        return None, compiled.stderr.strip().splitlines()[-1:]
    return str(binary), None


# The fixtures reference card-1, card-2 and island-1, so the wrapping document
# carries all three. Otherwise the failure would be about the harness, not SUI.
BASE_CARDS = [
    {"id": "card-1", "text": "a", "x": 0.0, "y": 0.0},
    {"id": "card-2", "text": "b", "x": 1.0, "y": 1.0},
]
BASE_ISLANDS = [{"id": "island-1", "cardIds": ["card-1"]}]


def document_for(kind, record):
    """Wrap one projected record in the artifact shape SUI's consumer expects."""
    element = {
        "document": {"id": "doc-1", "title": "Oracle"},
        "cards": [dict(card) for card in BASE_CARDS],
        "islands": [dict(island) for island in BASE_ISLANDS],
    }
    if kind == "document":
        element["document"] = record
        element["document"].setdefault("id", "doc-1")
    elif kind == "cards":
        element["cards"] = [record] + [card for card in BASE_CARDS if card["id"] != record.get("id")]
    elif kind == "islands":
        element["islands"] = [record] + [island for island in BASE_ISLANDS if island["id"] != record.get("id")]
    else:
        element[kind] = [record]
    return element


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    src = Path(args.sui_repo) / "03_Implement/backend/src"
    workdir = Path(tempfile.mkdtemp(prefix="tei-oracle-", dir=os.environ.get("GOTMPDIR") or None))

    results = []
    built_ok = True
    for contract, (kind, strategy) in CONTRACTS.items():
        binary, error = build(args.tei_repo, workspace / "candidates" / contract / "contract.json",
                              strategy, workdir / contract)
        if binary is None:
            built_ok = False
            results.append({"contract": contract, "case": None, "projected": False, "error": error})
            continue
        fixtures = json.loads((workspace / "candidates" / contract / "fixtures.json").read_text(encoding="utf-8"))
        for case in fixtures["cases"]:
            if case.get("want", {}).get("state") != "present":
                continue
            completed = run([binary], cwd=workdir / contract, stdin_text=json.dumps(case["input"]))
            body = json.loads(completed.stdout) if completed.returncode == 0 and completed.stdout.strip().startswith("{") else {}
            if body.get("state") != "present":
                results.append({"contract": contract, "case": case["id"], "projected": False, "error": body.get("state")})
                continue
            record = json.loads(body["text"])
            artifact = {
                "schema": "tai.reference.tei-documentv1-projection/v0",
                "contract": {"id": "sui.documentv1.projection", "version": "1"},
                "source": {"teiCommit": "oracle"},
                "document": document_for(kind, record),
            }
            artifact_path = workdir / f"{contract}-{case['id']}.json"
            artifact_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            probe = subprocess.run(
                [sys.executable, "-c", PROBE, str(artifact_path)],
                env={**os.environ, "PYTHONPATH": str(src)},
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            lines = (probe.stdout or "").strip().splitlines()
            verdict = json.loads(lines[-1]) if lines else {"valid": False, "reason": "no output"}
            results.append(
                {
                    "contract": contract,
                    "case": case["id"],
                    "projected": True,
                    "validInSuiModel": verdict["valid"],
                    "reason": verdict["reason"],
                }
            )

    projected = [item for item in results if item.get("projected")]
    valid = [item for item in projected if item.get("validInSuiModel")]
    invalid = [
        f"{item['contract']}:{item['case']}"
        for item in results
        if item.get("projected") and not item.get("validInSuiModel")
    ]
    checks = {
        "casesConsidered": len(results),
        "casesProjected": len(projected),
        "casesValidInSuiModel": len(valid),
        "invalidInSui": invalid,
        "knownInvalidInSui": KNOWN_INVALID,
        "unexpectedInvalid": [name for name in invalid if name not in KNOWN_INVALID],
        "knownMismatchesStillReproduce": all(name in invalid for name in KNOWN_INVALID),
        "failures": [item for item in results if not item.get("validInSuiModel")],
        "everyProjectedCaseIsValidInSui": bool(projected) and len(valid) == len(projected),
        "results": results,
    }
    # The measurement passes when the only failures are the recorded mismatch;
    # a new failure, or the known one disappearing, needs a fresh look.
    passed = (
        built_ok
        and bool(projected)
        and not checks["unexpectedInvalid"]
        and checks["knownMismatchesStillReproduce"]
    )
    receipt = {
        "schema": "tai.reference.tei-independent-oracle/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the TEI reference generator and SUI's DocumentV1 model",
        "command": f"python integrations/tools/tei_independent_oracle_check.py --tei-repo {args.tei_repo} --workspace integrations/pilot-sui-document --sui-repo <SUI> --artifact {args.artifact} --out evaluations/records/TEI-independent-oracle-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Wraps each present projection in an artifact and validates it with SUI's DocumentV1 model, which is not derived from the TEI contract, so this is an outside check rather than the contract's own expectations. Three kind-less edge cases are refused by SUI's consumer; that mismatch is recorded by name instead of being ignored. It covers only the fields SUI's model knows, and it does not prove the meaning is right.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "considered": checks["casesConsidered"],
        "projected": checks["casesProjected"],
        "validInSui": checks["casesValidInSuiModel"],
        "knownInvalidInSui": checks["knownInvalidInSui"],
        "unexpectedInvalid": checks["unexpectedInvalid"],
        "failures": [(item.get("contract"), item.get("case"), item.get("reason")) for item in checks["failures"]],
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
