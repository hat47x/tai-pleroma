"""Test the YI/CSW synthetic candidate-selection evidence boundary."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from check_yi_selection_surface import check, check_file

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "yi-selection-surface-synthetic.json"


class CandidateSelectionTests(unittest.TestCase):
    def setUp(self):
        self.base = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def assert_refused(self, data, fragment):
        result = check(data)
        self.assertFalse(result["passed"], result)
        self.assertTrue(any(fragment in error for error in result["errors"]), result["errors"])

    def test_bounded_example_passes_without_owner_acceptance(self):
        r = check_file(FIXTURE)
        self.assertTrue(r["passed"], r)
        self.assertEqual(r["observedCounts"],
                         dict(zip(("generated", "captured", "searched", "presented", "evaluated", "recommended"),
                                  (4, 4, 3, 2, 2, 1))))
        self.assertFalse(self.base["ownerAccepted"])

    def test_unobserved_candidate_cannot_be_presented(self):
        d = copy.deepcopy(self.base)
        d["stages"][3]["observedIds"].append("H04")
        self.assert_refused(d, "reappearance without trace")

    def test_absence_is_not_proved_by_an_open_stage(self):
        d = copy.deepcopy(self.base)
        d["stages"][3]["closedForRun"] = False
        self.assert_refused(d, "cannot infer absence")

    def test_omitted_candidate_is_not_globally_nonexistent(self):
        d = copy.deepcopy(self.base)
        d["claims"][1]["scope"] = "all_possible_hypotheses"
        self.assert_refused(d, "unbounded scope")

    def test_not_presented_cannot_be_mislabeled_as_rejected(self):
        d = copy.deepcopy(self.base)
        d["claims"][1]["kind"] = "owner_rejected"
        self.assert_refused(d, "unlicensed kind")

    def test_recommended_is_not_owner_accepted(self):
        d = copy.deepcopy(self.base)
        d["ownerAccepted"] = True
        self.assert_refused(d, "Owner acceptance")

    def test_claim_cannot_contradict_stage(self):
        d = copy.deepcopy(self.base)
        d["claims"][1]["candidate"] = "H01"
        self.assert_refused(d, "contradicts the observed stage")

    def test_retention_is_scoped_to_declared_closed_run(self):
        r = check(self.base)
        self.assertTrue(r["passed"], r)
        transitions = r["boundedTransitions"]
        self.assertEqual(len(transitions), 5)
        self.assertEqual(transitions[1]["retentionFraction"],
                         {"numerator": 3, "denominator": 4})
        self.assertEqual(transitions[2]["droppedObservedIds"], ["H02"])
        # A rate within an authored fixture is NOT completeness of all possible ideas.
        self.assertIn("no proof of exporter completeness", r["scope"])

    def test_open_stage_has_unknown_retention_not_zero_or_full(self):
        d = copy.deepcopy(self.base)
        d["stages"][2]["closedForRun"] = False
        d["claims"] = [c for c in d["claims"] if c["stage"] != "searched"]
        r = check(d)
        self.assertTrue(r["passed"], r)
        # captured -> searched and searched -> presented cannot claim denominators.
        self.assertIsNone(r["boundedTransitions"][1]["retentionFraction"])
        self.assertIsNone(r["boundedTransitions"][2]["retentionFraction"])
        self.assertEqual(r["boundedTransitions"][1]["closure"], "not_qualified")
        self.assertIsNone(r["boundedTransitions"][1]["droppedObservedIds"])

    def test_bad_trace_does_not_emit_success_like_summary(self):
        d = copy.deepcopy(self.base)
        d["stages"][3]["observedIds"].append("H04")
        r = check(d)
        self.assertFalse(r["passed"])
        self.assertEqual(r["boundedTransitions"], [])
        self.assertEqual(r["observedCounts"], {})

    def test_unobserved_internal_ideas_cannot_be_declared_absent(self):
        d = copy.deepcopy(self.base)
        d["claims"][0]["kind"] = "not_generated_anywhere"
        self.assert_refused(d, "unlicensed kind")

    def test_new_attempt_can_rereport_idea_without_cross_run_authority(self):
        # Monotone stage snapshots are scoped to ONE attempt, not a universal
        # prohibition on rediscovery or recombination in a later CSW/SUI attempt.
        d = copy.deepcopy(self.base)
        d["run"]["id"] = "YI-SEL-02-synthetic"
        self.assertTrue(check(d)["passed"])
        self.assertEqual(d["candidates"][1]["id"], "H02")

    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "duplicate.json"
            path.write_text('{"synthetic":false,"synthetic":true}', encoding="utf-8")
            r = check_file(path)
            self.assertFalse(r["passed"])
            self.assertIn("duplicate JSON key", r["errors"][0])


if __name__ == "__main__":
    unittest.main()
