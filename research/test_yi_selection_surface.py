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

    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "duplicate.json"
            path.write_text('{"synthetic":false,"synthetic":true}', encoding="utf-8")
            r = check_file(path)
            self.assertFalse(r["passed"])
            self.assertIn("duplicate JSON key", r["errors"][0])


if __name__ == "__main__":
    unittest.main()
