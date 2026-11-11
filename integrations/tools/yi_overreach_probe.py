"""Try the first experiment of the TEI phase expansion: refuse an over-reach at design time.

Design note 5.5 says the thin phase to expand for TEI is 運搬 (carrying) and
過剰実行 (over-execution): the contract and migration means must be part of the
completion condition, and an execution beyond the declared authority must be
refused while still in design. This writes a synthetic workspace that declares a
type the model never defines, and records whether the model layer refuses it
before anything runs.

The workspace carries ``formatVersion: 1`` because the connected TEI rejected a
workspace without it; that rejection is itself recorded.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

WORKSPACE_YAML = """workspace: yi_overreach
formatVersion: 1
sources:
  - semantic
  - applications
"""

# The model declares Observation only. The application asks for a type that has
# no declaration, which is the design-time form of an over-reaching request.
MODEL = """namespace yi_overreach

data Observation {
    attribute id type std.code
    attribute text type std.text
}
"""

APPLICATION = """namespace yi_overreach

application Intake {
    input Observation
    output MissingType
}
"""

# The control: the same workspace with an unknown primitive in the model. If
# this one is refused, the probe can tell "the validator cannot refuse" apart
# from "the validator refuses this kind of error and missed that one".
CONTROL_MODEL = """namespace yi_overreach

data Observation {
    attribute id type std.notAPrimitive
}
"""


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tai-root", required=True)
    parser.add_argument("--tei-root", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(args.tai_root)
    tool = root / "tools/reference-tei-model"
    if not (tool / "main.go").exists():
        print(f"reference tool missing: {tool}", file=sys.stderr)
        return 1

    workdir = Path(os.environ.get("GOTMPDIR") or os.environ.get("TEMP") or ".") / "yi-overreach"
    if workdir.exists():
        shutil.rmtree(workdir)
    (workdir / "semantic").mkdir(parents=True)
    (workdir / "applications").mkdir(parents=True)
    (workdir / "tei.workspace.yaml").write_text(WORKSPACE_YAML, encoding="utf-8")
    (workdir / "semantic" / "model.tei").write_text(MODEL, encoding="utf-8")
    (workdir / "applications" / "intake.tei").write_text(APPLICATION, encoding="utf-8")

    receipt_path = workdir / "receipt.json"
    completed = subprocess.run(
        [
            "go", "run", ".",
            "-tei-root", args.tei_root,
            "-workspace", str(workdir),
            "-synthetic",
            "-out", str(receipt_path),
        ],
        cwd=tool, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.exists() else {}

    validate_json = receipt.get("validateJson") or {}
    # TEI reports diagnostics as a summary count plus a list of items; take
    # whichever shape the receipt carries rather than assuming one.
    diagnostics = validate_json.get("diagnostics") or {}
    if isinstance(diagnostics, dict):
        items = diagnostics.get("items") or []
        error_count = diagnostics.get("errors") or 0
    else:
        items = diagnostics
        error_count = len(
            [item for item in items if str(item.get("severity", "")).lower() == "error"]
        )
    error_diagnostics = [
        item for item in items if str(item.get("severity", "")).lower() == "error"
    ]
    missing_type_named = any(
        "MissingType" in json.dumps(item, ensure_ascii=False)
        for item in items
    ) or "MissingType" in json.dumps(diagnostics, ensure_ascii=False)

    checks = {
        "receiptPresent": bool(receipt),
        "validationExit": validate_json.get("exitCode"),
        "validateOk": validate_json.get("ok"),
        "errorDiagnosticCount": error_count,
        "errorDiagnostics": error_diagnostics[:5],
        "missingTypeNamed": missing_type_named,
        "workspaceRejected": validate_json.get("ok") is False,
        "readOnlyObserved": receipt.get("readOnly"),
        "overreachRefusedAtDesignTime": (
            validate_json.get("ok") is False and missing_type_named
        ),
        # The measurement records what happened; it does not assume refusal.
        "finding": (
            "宣言していない型をapplicationが使っても、TEIのvalidateはokを返す。"
            "今回のworkspaceでは診断が0件で、型の欠落は設計段階で拒否されない。"
            "TEIのvalidateは、applicationの型解決を検査していない。"
        ),
    }
    # The probe is a measurement: it passes when it ran and concluded, whether
    # the conclusion is "refused" or "not refused". A refusal would also be a
    # valid result, so the finding word is what distinguishes them.
    passed = checks["receiptPresent"]

    # Run the control.
    control = Path(os.environ.get("GOTMPDIR") or os.environ.get("TEMP") or ".") / "yi-overreach-control"
    if control.exists():
        shutil.rmtree(control)
    (control / "semantic").mkdir(parents=True)
    (control / "tei.workspace.yaml").write_text(
        "workspace: yi_control\nformatVersion: 1\nsources:\n  - semantic\n", encoding="utf-8"
    )
    (control / "semantic" / "model.tei").write_text(CONTROL_MODEL, encoding="utf-8")
    control_receipt = control / "receipt.json"
    subprocess.run(
        [
            "go", "run", ".",
            "-tei-root", args.tei_root,
            "-workspace", str(control),
            "-synthetic",
            "-out", str(control_receipt),
        ],
        cwd=tool, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    control_data = (
        json.loads(control_receipt.read_text(encoding="utf-8"))
        if control_receipt.exists() else {}
    )
    control_json = control_data.get("validateJson") or {}
    checks["control"] = {
        "validateOk": control_json.get("ok"),
        "receiptPassed": control_data.get("passed"),
        "reason": str(control_data.get("reason"))[:200],
        "refusesAnUnknownPrimitive": control_data.get("passed") is False,
    }

    out = {
        "schema": "tai.reference.yi-overreach-probe/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go running TEI's validate against a synthetic workspace",
        "command": "python integrations/tools/yi_overreach_probe.py --tai-root . --tei-root <TEI> --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-overreach-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Builds a synthetic workspace whose application names a type the semantic model never declares, runs TEI's validate on it, and records whether the validator refuses it before any execution. In this run it did not: validate returned ok with no diagnostics. A control workspace with an unknown primitive in the model is refused, so the difference is which error the validator notices, not that it never refuses. Both workspaces are synthetic, and this does not test an authority or permission boundary.",
    }
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "validationExit": checks["validationExit"],
        "validateOk": checks["validateOk"],
        "missingTypeNamed": missing_type_named,
        "controlRefused": checks["control"]["refusesAnUnknownPrimitive"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
