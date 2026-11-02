"""ロボティクスと自動運転の四つの記録を、合成fixtureで検証する。

対象は docs/yi-constellation/schemas/ の event, handoff, decision, meaning の
四つのスキーマと、evaluations/fixtures/ad/ と evaluations/fixtures/robotics/ の
合成fixtureである。スキーマの構文と必須項目、型、列挙、パターンを確かめ、
記録の間の参照と、二つの領域の網羅を確かめる。

実車、実ロボット、実安全制御器、安全認証は対象外である。合成fixtureの
検証を、実システムの検証と同一視しない。

使い方:
    python evaluations/audit-robotics-records.py
    python evaluations/audit-robotics-records.py --json <path>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SCHEMA_DIR = BASE / "docs" / "yi-constellation" / "schemas"
FIXTURE_DIR = BASE / "evaluations" / "fixtures"
DEFAULT_RECORD = BASE / "evaluations" / "records" / "robotics-records-2026-11-02.json"
RECORD_TYPES = ("event", "handoff", "decision", "meaning")
DOMAINS = ("ad", "robotics")


def type_matches(value: object, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def validate(instance: object, schema: dict, path: str = "$") -> list[str]:
    errors: list[str] = []
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {instance!r}")
        return errors
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} is not in {schema['enum']}")
        return errors
    expected = schema.get("type")
    if expected and not type_matches(instance, expected):
        errors.append(f"{path}: expected {expected}, got {type(instance).__name__}")
        return errors
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required {key}")
        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key in properties:
                errors.extend(validate(value, properties[key], f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected property {key}")
    elif isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: {len(instance)} items < minItems {schema['minItems']}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: {len(instance)} items > maxItems {schema['maxItems']}")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                errors.extend(validate(item, item_schema, f"{path}[{index}]"))
    elif isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: length {len(instance)} < minLength {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: length {len(instance)} > maxLength {schema['maxLength']}")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}: {instance!r} does not match {schema['pattern']}")
    elif isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")
    return errors


def load_schemas() -> dict[str, dict]:
    schemas: dict[str, dict] = {}
    for name in RECORD_TYPES:
        path = SCHEMA_DIR / f"{name}.schema.json"
        schemas[name] = json.loads(path.read_text(encoding="utf-8"))
    return schemas


def load_fixtures() -> list[tuple[Path, dict]]:
    fixtures: list[tuple[Path, dict]] = []
    for domain in DOMAINS:
        for path in sorted((FIXTURE_DIR / domain).glob("*.json")):
            fixtures.append((path, json.loads(path.read_text(encoding="utf-8"))))
    return fixtures


def cross_record_checks(fixtures: list[tuple[Path, dict]]) -> list[str]:
    errors: list[str] = []
    handoff_ids = {
        record.get("handoff_id")
        for _, record in fixtures
        if record.get("record_type") == "handoff"
    }
    for path, record in fixtures:
        label = path.as_posix()
        record_type = record.get("record_type")
        domain = record.get("domain")
        if record_type in ("event", "handoff", "decision"):
            if not record.get("safety_envelope_ref"):
                errors.append(f"{label}: safety_envelope_ref is required for {record_type}")
        if record_type == "event" and "handoff_ref" in record:
            if record["handoff_ref"] not in handoff_ids:
                errors.append(f"{label}: handoff_ref {record['handoff_ref']} is not defined")
        if domain == "ad" and record_type in ("event", "handoff", "decision"):
            for field in ("vehicle_id", "automation_level"):
                if field not in record:
                    errors.append(f"{label}: ad {record_type} requires {field}")
        if domain == "robotics" and record_type in ("event", "handoff", "decision"):
            if "robot_id" not in record:
                errors.append(f"{label}: robotics {record_type} requires robot_id")
        if record_type == "handoff":
            if not record.get("sent"):
                errors.append(f"{label}: handoff requires at least one sent item")
            if record.get("from", {}).get("id") == record.get("to", {}).get("id"):
                errors.append(f"{label}: from and to must differ")
        if record_type == "decision":
            for field in ("options", "criteria", "assumptions", "safety_constraints", "evidence_refs"):
                if not record.get(field):
                    errors.append(f"{label}: decision requires non-empty {field}")
        if record_type == "meaning":
            if not record.get("safety_case_ref"):
                errors.append(f"{label}: meaning requires safety_case_ref")
            if record.get("status") not in ("same", "split", "merged", "dropped", "new"):
                errors.append(f"{label}: meaning status is invalid")
    for domain in DOMAINS:
        present = {
            record.get("record_type")
            for _, record in fixtures
            if record.get("domain") == domain
        }
        missing = set(RECORD_TYPES) - present
        if missing:
            errors.append(f"{domain}: missing record types {sorted(missing)}")
    return errors


def run_self_test(schemas: dict[str, dict], fixtures: list[tuple[Path, dict]]) -> list[str]:
    """検証器が失敗を検出できることを、負例で確かめる。"""
    errors: list[str] = []
    handoff = next((record for _, record in fixtures if record.get("record_type") == "handoff"), None)
    event = next((record for _, record in fixtures if record.get("record_type") == "event"), None)
    if handoff is None or event is None:
        return ["self-test: base fixture is missing"]
    missing = dict(handoff)
    missing.pop("safety_envelope_ref", None)
    if not validate(missing, schemas["handoff"]):
        errors.append("self-test: missing safety_envelope_ref was not detected")
    extra = dict(handoff)
    extra["unexpected"] = True
    if not validate(extra, schemas["handoff"]):
        errors.append("self-test: unexpected property was not detected")
    bad_ref = dict(event)
    bad_ref["handoff_ref"] = "hnd-missing"
    ref_errors = [
        message
        for message in cross_record_checks(
            [(Path("self-test-event.json"), bad_ref), (Path("self-test-handoff.json"), handoff)]
        )
        if "handoff_ref" in message
    ]
    if not ref_errors:
        errors.append("self-test: missing handoff_ref was not detected")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="ロボティクスと自動運転の四つの記録を検証する")
    parser.add_argument("--json", type=Path, default=DEFAULT_RECORD, help="検証結果のJSONの出力先")
    args = parser.parse_args()

    schemas = load_schemas()
    fixtures = load_fixtures()
    errors: list[str] = []
    for path, record in fixtures:
        record_type = record.get("record_type")
        schema = schemas.get(record_type)
        if schema is None:
            errors.append(f"{path.as_posix()}: unknown record_type {record_type!r}")
            continue
        errors.extend(
            f"{path.as_posix()}: {message}"
            for message in validate(record, schema)
        )
    errors.extend(cross_record_checks(fixtures))
    self_test_errors = run_self_test(schemas, fixtures)
    errors.extend(self_test_errors)

    receipt = {
        "schema": "tai.evaluation.robotics-records/v0",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "synthetic": True,
        "passed": not errors,
        "errors": errors,
        "self_test": {
            "passed": not self_test_errors,
            "errors": self_test_errors,
        },
        "fixtures": [path.relative_to(BASE).as_posix() for path, _ in fixtures],
        "schemas": [f"docs/yi-constellation/schemas/{name}.schema.json" for name in RECORD_TYPES],
        "checks": {
            "schema_validation": "required, type, enum, const, pattern, minLength, minItems, additionalProperties",
            "cross_record": "safety_envelope_ref, handoff_ref, domain fields, from/to, decision fields, meaning status",
            "coverage": "event, handoff, decision, meaning in ad and robotics",
        },
        "notes": [
            "合成fixtureのみ。実車、実ロボット、実安全制御器は未検証。",
            "安全エンベロープは参照のみで、安全認証の証拠ではない。",
            "意味の対応は移行の記録であり、移行の正しさを検証したものではない。",
        ],
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"fixtures: {len(fixtures)}")
    for path, record in fixtures:
        print(f"  {path.relative_to(BASE).as_posix()}: {record.get('record_type')}")
    print(f"self-test: {'PASSED' if not self_test_errors else 'FAILED'}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        for error in errors:
            print(f"  - {error}")
        print(f"record: {args.json.relative_to(BASE).as_posix()}")
        return 1
    print("PASSED: schemas, cross-record checks, and self-test")
    print(f"record: {args.json.relative_to(BASE).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
