import unittest

from validate_artifact import validate

VALID = {
    "schema": "tai.reference.tei-documentv1-projection/v0",
    "contract": {"id": "sui.documentv1.projection", "version": "1"},
    "source": {"teiCommit": "abc", "contracts": {"card-record": {"cases": 5}}},
    "document": {
        "document": {"id": "doc-1", "title": "Notes"},
        "cards": [{"id": "card-1", "text": "hello", "x": 1, "y": 2}],
        "islands": [{"id": "island-1", "title": "A", "cardIds": ["card-1"]}],
        "edges": [
            {
                "id": "edge-1",
                "fromId": "card-1",
                "toId": "island-1",
                "type": "contains",
                "fromKind": "card",
                "toKind": "island",
            }
        ],
        "affiliations": [{"id": "aff-1", "cardId": "card-1", "islandId": "island-1"}],
    },
}


class ValidateArtifactTest(unittest.TestCase):
    def test_accepts_valid_artifact(self):
        self.assertEqual(validate(VALID), [])

    def test_rejects_wrong_schema(self):
        payload = dict(VALID, schema="other")
        self.assertIn("schema must be tai.reference.tei-documentv1-projection/v0", validate(payload))

    def test_rejects_empty_cards(self):
        document = dict(VALID["document"], cards=[])
        payload = dict(VALID, document=document)
        self.assertIn("document.cards must not be empty", validate(payload))

    def test_rejects_numeric_coordinate_as_string(self):
        document = dict(VALID["document"], cards=[{"id": "card-1", "text": "t", "x": "1", "y": 2}])
        payload = dict(VALID, document=document)
        self.assertIn("card.x must be a number", validate(payload))


if __name__ == "__main__":
    unittest.main()
