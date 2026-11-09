import copy
import unittest

from putback_check import evaluate_putback

ARTIFACT = {
    "schema": "tai.reference.tei-documentv1-projection/v0",
    "contract": {"id": "sui.documentv1.projection", "version": "1"},
    "source": {"teiCommit": "abc", "contracts": {}},
    "document": {
        "document": {"id": "doc-1", "title": "Notes"},
        "cards": [
            {"id": "card-1", "text": "hello", "x": 1.0, "y": 2.0, "holdState": "held"},
        ],
        "islands": [{"id": "island-1", "title": "A", "cardIds": ["card-1"]}],
        "edges": [],
        "affiliations": [],
    },
}

EXISTING = {
    "id": "doc-1",
    "title": "Notes",
    "cards": [
        {"id": "card-1", "text": "hello", "x": 1.0, "y": 2.0, "holdState": "held"},
    ],
    "islands": [{"id": "island-1", "title": "A", "cardIds": ["card-1"]}],
    "edges": [],
    "affiliations": [],
}


def pair():
    return copy.deepcopy(ARTIFACT), copy.deepcopy(EXISTING)


class PutbackCheckTest(unittest.TestCase):
    def test_identical_projection_is_a_no_op(self):
        artifact, existing = pair()
        result = evaluate_putback(artifact, existing)
        self.assertEqual(result["decision"], "no-op")
        self.assertEqual(result["changes"], [])
        self.assertEqual(result["ambiguous"], [])

    def test_exact_text_edit_is_safe(self):
        artifact, existing = pair()
        artifact["document"]["cards"][0]["text"] = "updated"
        result = evaluate_putback(artifact, existing)
        self.assertEqual(result["decision"], "safe")
        self.assertEqual(result["changes"], [{"kind": "edit-text", "target": "card-1"}])

    def test_numeric_approximation_refuses_the_putback(self):
        artifact, existing = pair()
        artifact["document"]["cards"][0]["x"] = 1.0000000000000002
        result = evaluate_putback(artifact, existing)
        self.assertEqual(result["decision"], "refused")
        self.assertEqual(result["ambiguous"][0]["kind"], "numeric-approximation")

    def test_real_coordinate_change_is_safe(self):
        artifact, existing = pair()
        artifact["document"]["cards"][0]["x"] = 5.0
        result = evaluate_putback(artifact, existing)
        self.assertEqual(result["decision"], "safe")
        self.assertEqual(result["changes"], [{"kind": "edit-coordinate", "target": "card-1.x"}])

    def test_optional_omission_is_not_a_clear(self):
        artifact, existing = pair()
        del artifact["document"]["cards"][0]["holdState"]
        result = evaluate_putback(artifact, existing)
        self.assertEqual(result["decision"], "refused")
        self.assertEqual(result["ambiguous"][0]["kind"], "ambiguous-optional-absence")

    def test_empty_optional_list_is_not_a_clear(self):
        artifact, existing = pair()
        existing["cards"][0]["sources"] = ["source-1"]
        artifact["document"]["cards"][0]["sources"] = []
        result = evaluate_putback(artifact, existing)
        self.assertEqual(result["decision"], "refused")
        self.assertEqual(result["ambiguous"][0]["kind"], "ambiguous-optional-absence")

    def test_exact_optional_edit_is_safe(self):
        artifact, existing = pair()
        artifact["document"]["cards"][0]["holdState"] = "open"
        result = evaluate_putback(artifact, existing)
        self.assertEqual(result["decision"], "safe")
        self.assertEqual(result["changes"], [{"kind": "edit-optional", "target": "card-1.holdState"}])

    def test_card_missing_from_the_projection_is_ambiguous(self):
        artifact, existing = pair()
        existing["cards"].append({"id": "card-2", "text": "kept", "x": 0.0, "y": 0.0})
        result = evaluate_putback(artifact, existing)
        self.assertEqual(result["decision"], "refused")
        self.assertEqual(result["ambiguous"][0]["kind"], "ambiguous-absence")
        self.assertEqual(result["ambiguous"][0]["target"], "card-2")

    def test_card_added_by_the_projection_is_safe(self):
        artifact, existing = pair()
        artifact["document"]["cards"].append({"id": "card-2", "text": "new", "x": 0.0, "y": 0.0})
        result = evaluate_putback(artifact, existing)
        self.assertEqual(result["decision"], "safe")
        self.assertEqual(result["changes"], [{"kind": "add-card", "target": "card-2"}])

    def test_document_title_omission_is_ambiguous(self):
        artifact, existing = pair()
        del artifact["document"]["document"]["title"]
        result = evaluate_putback(artifact, existing)
        self.assertEqual(result["decision"], "refused")
        self.assertEqual(result["ambiguous"][0]["kind"], "ambiguous-document-field")

    def test_island_member_order_is_ambiguous(self):
        artifact, existing = pair()
        both = [
            {"id": "card-1", "text": "hello", "x": 1.0, "y": 2.0},
            {"id": "card-2", "text": "second", "x": 0.0, "y": 0.0},
        ]
        artifact["document"]["cards"] = copy.deepcopy(both)
        existing["cards"] = copy.deepcopy(both)
        artifact["document"]["islands"][0]["cardIds"] = ["card-2", "card-1"]
        existing["islands"][0]["cardIds"] = ["card-1", "card-2"]
        result = evaluate_putback(artifact, existing)
        self.assertEqual(result["decision"], "refused")
        self.assertEqual(result["ambiguous"][0]["kind"], "ambiguous-order")

    def test_document_mismatch_is_refused(self):
        artifact, existing = pair()
        existing["id"] = "doc-2"
        result = evaluate_putback(artifact, existing)
        self.assertEqual(result["decision"], "refused")
        self.assertEqual(result["ambiguous"][0]["kind"], "document-id-mismatch")


if __name__ == "__main__":
    unittest.main()
