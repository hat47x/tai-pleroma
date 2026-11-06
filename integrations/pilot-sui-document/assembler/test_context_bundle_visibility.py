"""The SUI local-dev stub reference verifies *bounded selection*, not authority."""
import copy
import unittest

from context_bundle_check import observe_stub_visibility


def stub_response():
    return {
        "schemaVersion": "1.0.0",
        "selected": [
            {"id": "card-reviewed-01", "reviewed": True, "title": "Synthetic reviewed hypothesis"}
        ],
        "evidence": [
            {"cardId": "card-reviewed-01", "reviewed": True, "kind": "support"},
            {"cardId": "card-unreviewed-01", "reviewed": False, "kind": "counter_opinion"},
        ],
        "relations": [
            {"type": "supports", "from": "card-reviewed-01", "to": "card-unreviewed-01"}
        ],
        "reviewFlags": {"reviewed": 1, "unreviewed": 0},
        "excludedReason": ["unreviewed_filtered"],
        "truncationMeta": {
            "stubDatasetId": "A2-minimal-v1",
            "holdState": "hold:stub_dataset_contract_only",
        },
    }


class SuiContextReferenceVisibilityTests(unittest.TestCase):
    def test_synthetic_stub_selected_and_reference_only(self):
        actual = observe_stub_visibility(stub_response())
        self.assertTrue(actual["passed"], actual)
        self.assertEqual(actual["counts"], {
            "selected": 1, "referenceOnly": 1,
            "unreviewedReferenceOnly": 1, "counterOpinionReferenceOnly": 1,
        })
        self.assertEqual(actual["sourceRevisionMatched"], "not-checked")
        self.assertEqual(actual["disclosureAuthorization"], "not-checked")
        self.assertEqual(actual["candidateCompleteness"], "not-established")
        self.assertNotIn("card-unreviewed-01", repr(actual))  # aggregate only, no IDs

    def test_unreviewed_selected_is_rejected(self):
        b = stub_response()
        b["selected"][0]["reviewed"] = False
        self.assertFalse(observe_stub_visibility(b)["passed"])

    def test_counter_opinion_dropped_is_not_success(self):
        b = stub_response()
        b["evidence"] = b["evidence"][:1]
        b["relations"] = []
        r = observe_stub_visibility(b)
        self.assertFalse(r["passed"], r)
        self.assertEqual(r["counts"], {})

    def test_review_flag_mismatch_fails_closed(self):
        b = stub_response()
        b["reviewFlags"]["unreviewed"] = 1
        self.assertFalse(observe_stub_visibility(b)["passed"])

    def test_unreviewed_filtered_reason_required_for_fixed_stub(self):
        b = stub_response()
        b["excludedReason"] = []
        self.assertFalse(observe_stub_visibility(b)["passed"])

    def test_other_stub_not_accepted_as_same_universe(self):
        b = stub_response()
        b["truncationMeta"]["stubDatasetId"] = "new-dataset"
        self.assertFalse(observe_stub_visibility(b)["passed"])

    def test_bad_relation_endpoint_fails(self):
        b = stub_response()
        b["relations"][0].pop("to")
        self.assertFalse(observe_stub_visibility(b)["passed"])

    def test_duplicate_selected_fails(self):
        b = stub_response()
        b["selected"].append(copy.deepcopy(b["selected"][0]))
        self.assertFalse(observe_stub_visibility(b)["passed"])

    def test_malformed_response_never_produces_success_counts(self):
        b = stub_response()
        b["selected"] = "card-reviewed-01"
        r = observe_stub_visibility(b)
        self.assertFalse(r["passed"])
        self.assertEqual(r["counts"], {})


if __name__ == "__main__":
    unittest.main()
