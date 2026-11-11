"""Tests for the optional producer declarations.

Two properties matter most and are pinned here:

1. An artifact that declares nothing stays valid and still leaves `status`
   absent. Absence must not become `active`.
2. A declared lifecycle / disclosure is accepted by both the JSON Schema and the
   structural validator, and an out-of-vocabulary value is rejected by both.
"""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import jsonschema

from producer_declaration import (
    DeclarationError,
    apply_declarations,
    disclosure_declaration,
    source_declaration,
)
from validate_artifact import validate

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = json.loads(
    (ROOT.parent.parent / "evaluations/artifacts/documentv1-projection.json").read_text(
        encoding="utf-8"
    )
)
SCHEMA = json.loads((ROOT / "artifact.schema.json").read_text(encoding="utf-8"))


def schema_errors(payload):
    return list(jsonschema.Draft202012Validator(SCHEMA).iter_errors(payload))


class UndeclaredArtifactTest(unittest.TestCase):
    def test_existing_artifact_stays_valid_and_declares_no_status(self):
        self.assertEqual(schema_errors(ARTIFACT), [])
        self.assertEqual(validate(ARTIFACT), [])
        # The absence is the point: a consumer must read it as unknown.
        self.assertNotIn("status", ARTIFACT["source"])
        self.assertNotIn("disclosure", ARTIFACT)

    def test_absent_status_is_not_rewritten_to_active(self):
        written = apply_declarations(ARTIFACT)
        self.assertNotIn("status", written["source"])
        self.assertNotIn("disclosure", written)


class DeclaredArtifactTest(unittest.TestCase):
    def test_active_lifecycle_is_accepted_by_schema_and_validator(self):
        payload = apply_declarations(
            ARTIFACT,
            source=source_declaration(
                status="active",
                document_revision="rev-1",
                observed_at="2026-11-12T00:00:00Z",
            ),
        )
        self.assertEqual(schema_errors(payload), [])
        self.assertEqual(validate(payload), [])
        self.assertEqual(payload["source"]["status"], "active")
        self.assertEqual(payload["source"]["documentRevision"], "rev-1")

    def test_revoked_lifecycle_is_accepted_structurally(self):
        payload = apply_declarations(
            ARTIFACT, source=source_declaration(status="revoked", status_reason="operator")
        )
        self.assertEqual(schema_errors(payload), [])
        self.assertEqual(validate(payload), [])

    def test_restricted_disclosure_is_accepted_structurally(self):
        payload = apply_declarations(
            ARTIFACT, disclosure=disclosure_declaration(scope="restricted")
        )
        self.assertEqual(schema_errors(payload), [])
        self.assertEqual(validate(payload), [])
        self.assertEqual(payload["disclosure"]["scope"], "restricted")

    def test_unknown_status_value_is_rejected(self):
        with self.assertRaises(DeclarationError):
            source_declaration(status="gone")

    def test_unknown_disclosure_value_is_rejected(self):
        with self.assertRaises(DeclarationError):
            disclosure_declaration(scope="secret")

    def test_schema_rejects_unknown_status_value(self):
        payload = copy.deepcopy(ARTIFACT)
        payload["source"]["status"] = "gone"
        self.assertTrue(schema_errors(payload))
        self.assertTrue(validate(payload))

    def test_validator_rejects_unknown_disclosure_value(self):
        payload = copy.deepcopy(ARTIFACT)
        payload["disclosure"] = {"scope": "secret"}
        self.assertTrue(validate(payload))

    def test_apply_does_not_mutate_the_input(self):
        original = copy.deepcopy(ARTIFACT)
        apply_declarations(ARTIFACT, source=source_declaration(status="expired"))
        self.assertEqual(ARTIFACT, original)


if __name__ == "__main__":
    unittest.main()
