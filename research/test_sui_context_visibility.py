"""Bounded SUI Context candidate visibility: selected is not all evidence."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from check_sui_context_visibility import observe, read

FIXTURE = Path(__file__).parent / "fixtures" / "sui-context-visibility.synthetic.json"


class SuiContextVisibilityTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_reference_only_counter_opinion_is_not_selected(self):
        r = observe(self.record)
        self.assertTrue(r["passed"], r)
        self.assertEqual(r["classes"]["selected"], ["card-reviewed-01"])
        self.assertEqual(r["classes"]["referencedOnly"], ["card-unreviewed-01"])
        self.assertEqual(r["counts"]["notObservedInBundle"], 0)
        self.assertEqual(r["comparisonQualification"], "UNVERIFIED_SAME_SOURCE_REVISION")
        self.assertEqual(r["observedExclusionReasons"], ["unreviewed_filtered"])
        # A generic exclusion reason does not attribute a specific decision to a card.
        self.assertNotIn("reasonByCandidate", r)

    def test_direct_only_candidate_is_not_called_nonexistent(self):
        d = copy.deepcopy(self.record)
        d["directSnapshot"]["candidateIds"].append("card-not-observed-01")
        r = observe(d)
        self.assertTrue(r["passed"], r)
        self.assertEqual(r["classes"]["notObservedInBundle"], ["card-not-observed-01"])
        self.assertIn("candidate absence", r["scope"])

    def test_bundle_only_reference_is_not_inferred_to_be_invalid(self):
        d = copy.deepcopy(self.record)
        d["bundle"]["evidence"].append({"cardId": "card-other-01", "kind": "unknown"})
        r = observe(d)
        self.assertTrue(r["passed"], r)
        self.assertEqual(r["classes"]["bundleOutsideDirectSnapshot"], ["card-other-01"])
        self.assertEqual(r["comparisonQualification"], "UNVERIFIED_SAME_SOURCE_REVISION")

    def test_strict_reviewed_only_selected_unreviewed_refused(self):
        d = copy.deepcopy(self.record)
        d["bundle"]["selected"][0]["reviewed"] = False
        r = observe(d)
        self.assertFalse(r["passed"])
        self.assertTrue(any("violates strict" in e for e in r["errors"]))

    def test_mismatch_flags_refused(self):
        d = copy.deepcopy(self.record)
        d["bundle"]["reviewFlags"]["unreviewed"] = 1
        r = observe(d)
        self.assertFalse(r["passed"])
        self.assertTrue(any("reviewFlags disagree" in e for e in r["errors"]))

    def test_missing_relation_endpoint_refused(self):
        d = copy.deepcopy(self.record)
        d["bundle"]["relations"][0].pop("to")
        r = observe(d)
        self.assertFalse(r["passed"])
        self.assertTrue(any("relations[0].to missing" in e for e in r["errors"]))

    def test_unapproved_real_capture_refused(self):
        d = copy.deepcopy(self.record)
        d["synthetic"] = False
        r = observe(d)
        self.assertFalse(r["passed"])
        self.assertTrue(any("explicitly synthetic" in e for e in r["errors"]))

    def test_bad_json_member_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "bad.json"
            p.write_text('{"synthetic":false,"synthetic":true}', encoding="utf-8")
            r = read(p)
        self.assertFalse(r["passed"])
        self.assertTrue(any("duplicate JSON key" in e for e in r["errors"]))

    def test_synthetic_unverified_hash_is_not_accepted_as_proof(self):
        d = copy.deepcopy(self.record)
        d["bundle"]["bundleHash"] = "made-up-hash"
        r = observe(d)
        self.assertTrue(r["passed"], r)
        self.assertEqual(r["comparisonQualification"], "UNVERIFIED_SAME_SOURCE_REVISION")
        self.assertNotIn("hashVerified", r)


if __name__ == "__main__":
    unittest.main()
