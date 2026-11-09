"""Research dataset discriminability, not participant or Product results."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

import rq7_calibrate as cal
import rq7_pilot


class PublicGoldBaselineCalibration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v0 = cal.calibrate("v0")
        cls.v1 = cal.calibrate("v1")

    def test_v0_old_gold_stays_unbalanced(self):
        for arm in ("V0", "V1"):
            self.assertEqual(self.v0["arms"][arm]["gold_distribution"], {
                "supported": 2, "refuted": 0, "undetermined": 8
            })

    def test_v1_declaration_gold_is_balanced(self):
        for arm in ("V0", "V1"):
            self.assertEqual(self.v1["arms"][arm]["gold_distribution"], {
                "supported": 4, "refuted": 4, "undetermined": 4
            })

    def test_v1_evidence_gold_is_distinct(self):
        for arm in ("V2", "V3"):
            self.assertEqual(self.v1["arms"][arm]["gold_distribution"], {
                "supported": 5, "refuted": 5, "undetermined": 2
            })

    def test_always_unknown_baseline_decreases_after_v1_balance(self):
        for arm in ("V0", "V1"):
            old = self.v0["arms"][arm]["baselines"]["always-undetermined"]["overall"]
            new = self.v1["arms"][arm]["baselines"]["always-undetermined"]["overall"]
            self.assertEqual((old["correct"], old["total"]), (8, 10))
            self.assertEqual((new["correct"], new["total"]), (4, 12))

    def test_privileged_selector_baseline_reveals_evidence_blind_spot(self):
        for arm in ("V2", "V3"):
            result = self.v1["arms"][arm]["baselines"]["typed-selector-else-undetermined"]
            self.assertEqual((result["overall"]["correct"], result["overall"]["total"]), (10, 12))
            self.assertEqual(result["overall"]["unnecessary_abstention"], 2)
            self.assertEqual(
                result["by_study_case_stage"]["evidence-dependent"]["score"]["correct"], 2
            )
            self.assertEqual(
                result["by_study_case_stage"]["evidence-dependent"]["score"]["total"], 4
            )

    def test_selector_baseline_answers_all_declared_only_cases(self):
        for arm in cal.ARMS:
            group = self.v1["arms"][arm]["baselines"]["typed-selector-else-undetermined"]["by_study_case_stage"]["declared-only"]["score"]
            self.assertEqual((group["correct"], group["total"]), (8, 8))

    def test_score_separates_confidence_from_wrong_direction(self):
        out = cal.score(
            ["undetermined", "supported", "refuted", "supported"],
            ["supported", "undetermined", "supported", "supported"],
        )
        self.assertEqual(out["correct"], 1)
        self.assertEqual(out["false_certainty"], 1)
        self.assertEqual(out["unnecessary_abstention"], 1)
        self.assertEqual(out["wrong_direction"], 1)

    def test_score_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            cal.score([], [])
        with self.assertRaises(ValueError):
            cal.score(["supported"], ["supported", "refuted"])
        with self.assertRaises(ValueError):
            cal.score(["supported"], ["accepted"])

    def test_selector_queries_are_explicit_and_do_not_use_gold(self):
        data, _ = rq7_pilot.load("v1")
        cases = data["cases"]
        for case in cases:
            result = cal.declared_query_verdict(case)
            if case["study_case_stage"] == "declared-only":
                self.assertIn(result, ("supported", "refuted"))
                self.assertIn("question_selector", case)
            else:
                self.assertEqual(result, "undetermined")

    def test_ci_cli_prints_no_participant_result(self):
        script = Path(cal.__file__).resolve()
        result = subprocess.run(
            [sys.executable, str(script), "--dataset", "v1"],
            check=True, capture_output=True, text=True,
        )
        self.assertIn('"status": "PUBLIC_SYNTHETIC_GOLD_CALIBRATION_ONLY"', result.stdout)
        self.assertIn('"human_or_ai_responses": "NONE"', result.stdout)
        self.assertIn('"product_execution": "NOT_RUN"', result.stdout)
        self.assertIn('"cases": 12', result.stdout)

    def test_not_holdout_by_contract(self):
        for report in (self.v0, self.v1):
            self.assertIs(report["holdout"], False)
            self.assertEqual(report["study_experiment_status"], "NOT_RUN")
            self.assertIn("hidden from", report["privileged_baseline_notice"])


if __name__ == "__main__":
    unittest.main()
