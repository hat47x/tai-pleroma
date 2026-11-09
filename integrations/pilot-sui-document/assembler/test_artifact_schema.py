import copy
import json
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = json.loads((ROOT.parent.parent / "evaluations/artifacts/documentv1-projection.json").read_text(encoding="utf-8"))
SCHEMA = json.loads((ROOT / "artifact.schema.json").read_text(encoding="utf-8"))


def errors_for(payload):
    validator = jsonschema.Draft202012Validator(SCHEMA)
    return list(validator.iter_errors(payload))


class ArtifactSchemaTest(unittest.TestCase):
    def test_current_artifact_is_valid(self):
        self.assertEqual(errors_for(ARTIFACT), [])

    def test_missing_card_text_is_rejected(self):
        payload = copy.deepcopy(ARTIFACT)
        del payload["document"]["cards"][0]["text"]
        self.assertTrue(errors_for(payload))

    def test_unknown_edge_kind_is_rejected(self):
        payload = copy.deepcopy(ARTIFACT)
        payload["document"]["edges"][0]["fromKind"] = "note"
        self.assertTrue(errors_for(payload))

    def test_bad_contract_digest_is_rejected(self):
        payload = copy.deepcopy(ARTIFACT)
        name = next(iter(payload["source"]["contracts"]))
        payload["source"]["contracts"][name]["contractDigest"] = "md5:abc"
        self.assertTrue(errors_for(payload))

    def test_empty_cards_are_rejected(self):
        payload = copy.deepcopy(ARTIFACT)
        payload["document"]["cards"] = []
        self.assertTrue(errors_for(payload))


if __name__ == "__main__":
    unittest.main()
