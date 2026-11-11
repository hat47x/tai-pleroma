"""Compare where a reference to an artifact could be added for the centre handoff.

The probe found no key joining SHO's provenance report to SEI's decision record.
Two places could carry it: SEI's ``decision.basis_refs`` (already a list of
references) and SEI's ``decision.extensions`` (open by design). This tests what
each can hold without breaking the schema, so the choice rests on what the
contract already permits rather than on guesswork.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

SEI = Path("D:/GIT/hat47x/sei-cognition")
SCHEMA = SEI / "contracts/schemas/v1alpha1/decision-memory.schema.json"
REFERENCE = SEI / "contracts/schemas/v1alpha1/semantic-reference.schema.json"

# What a handoff would need to carry on the SEI side.
NEEDED = ("artifactDigest", "source", "sheet", "range", "sourceDigest")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))

    logical = reference["$defs"]["logicalReference"]
    logical_fields = sorted((logical.get("properties") or {}).keys())
    exact = reference["$defs"]["exactBinding"]
    exact_fields = sorted((exact.get("properties") or {}).keys())

    decisions = schema["$defs"]["decision"]
    props = decisions.get("properties") or {}
    basis = props.get("basis_refs")
    extensions = props.get("extensions")

    # Can a basis_ref carry the five units as structured fields?
    basis_can_carry_units = False
    if basis and basis.get("items"):
        items = basis["items"]
        target = items.get("$ref", "")
        if target.endswith("exactBinding"):
            basis_can_carry_units = all(unit in exact_fields for unit in NEEDED)
    # An extension is open by design, so it can carry anything.
    extensions_can_carry_units = bool(extensions) and extensions.get(
        "additionalProperties"
    ) is True

    checks = {
        "schema": str(SCHEMA.relative_to(Path("D:/GIT/hat47x"))),
        "referenceSchema": str(REFERENCE.relative_to(Path("D:/GIT/hat47x"))),
        "logicalReferenceFields": logical_fields,
        "exactBindingFields": exact_fields,
        "neededUnits": list(NEEDED),
        "guidance": {
            "basis_refs": (
                "SEIの参照として型が決まっている。持てるのは "
                + ", ".join(exact_fields)
                + " だけなので、成果物のシート・範囲は入らない"
            ),
            "extensions": (
                "追加の項目を自由に持てる。ただし契約上は拡張であり、"
                "検証つきの第一級の項目ではない"
            ),
        },
        "basisRefsCanCarryTheUnits": basis_can_carry_units,
        "extensionsCanCarryTheUnits": extensions_can_carry_units,
        "exactlyOneTypedPlaceExists": basis_can_carry_units != extensions_can_carry_units,
        "neitherTypedNorOpen": not basis_can_carry_units and not extensions_can_carry_units,
    }
    passed = extensions_can_carry_units

    receipt = {
        "schema": "tai.reference.yi-centre-key-options/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading SEI's JSON Schema documents",
        "command": "python integrations/tools/yi_centre_key_options.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-centre-key-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Reads SEI's decision-memory and semantic-reference JSON Schemas and records what its basis_refs and extensions can hold, so that adding a key is a choice about permitted shape rather than an invention. It does not add anything, does not validate a real record, and does not decide which side should carry the key.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "logicalFields": logical_fields,
        "exactFields": exact_fields,
        "basisRefsCanCarryTheUnits": basis_can_carry_units,
        "extensionsCanCarryTheUnits": extensions_can_carry_units,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
