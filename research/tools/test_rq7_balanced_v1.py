"""Public RQ7 v1 prepilot checks; this is NOT an independent effectiveness evaluation."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

import rq7_pilot as rq7


class BalancedPublicPrepilotV1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases, cls.gold = rq7.load("v1")
        cls.by_id = {c["id"]: c for c in cls.cases["cases"]}
        cls.gold_id = {g["id"]: g for g in cls.gold["cases"]}

    def test_public_preflight(self):
        meta = rq7.validate(self.cases, self.gold)
        self.assertEqual(meta["cases"], 12)
        self.assertFalse(meta["independent_holdout"])
        self.assertEqual(meta["experiment_run_status"], "NOT_RUN")
        self.assertEqual(self.cases["experiment_set"], self.gold["experiment_set"])
        self.assertEqual(self.cases["experiment_set"], "public-prepilot-v1-gold-balance")

    def test_declared_only_verdicts_are_balanced(self):
        for arm in ("V0", "V1"):
            counts = Counter(c["expected"][arm] for c in self.gold["cases"])
            self.assertEqual(dict(counts), {
                "supported": 4, "refuted": 4, "undetermined": 4
            })

    def test_evidence_assisted_verdicts_have_all_categories(self):
        for arm in ("V2", "V3"):
            counts = Counter(c["expected"][arm] for c in self.gold["cases"])
            self.assertEqual(dict(counts), {
                "supported": 5, "refuted": 5, "undetermined": 2
            })

    def test_eight_declarative_cases_and_four_evidence_cases(self):
        self.assertEqual(
            sum(c["study_case_stage"] == "declared-only" for c in self.cases["cases"]),
            8
        )
        self.assertEqual(
            sum(c["study_case_stage"] == "evidence-dependent" for c in self.cases["cases"]),
            4
        )

    def test_declared_queries_independent_of_observed_events(self):
        for case in self.cases["cases"]:
            if case["study_case_stage"] != "declared-only":
                continue
            expected = self.gold_id[case["id"]]["expected"]
            self.assertEqual(expected["V0"], expected["V2"])

    def test_undetermined_requires_missing_execution_evidence(self):
        for case_id in ("F-EU01", "X-EU01"):
            self.assertEqual(self.gold_id[case_id]["expected"]["V3"], "undetermined")
            self.assertEqual(self.by_id[case_id]["observed"]["observer_coverage"], "partial")

    def test_direct_edge_is_not_indirect_reachability(self):
        self.assertEqual(
            self.gold_id["B-DR01"]["expected"]["V0"], "refuted"
        )
        self.assertEqual(
            self.gold_id["B-DP02"]["expected"]["V0"], "supported"
        )
        self.assertIn(
            ("src", "compile"),
            [tuple(edge) for edge in self.by_id["B-DP02"]["declared"]["edges"]],
        )

    def test_no_gold_reason_in_any_render(self):
        for case in self.cases["cases"]:
            reason = self.gold_id[case["id"]]["reason"]
            for arm in rq7.ARMS:
                with self.subTest(case=case["id"], arm=arm):
                    text = rq7.render(case, arm)
                    self.assertNotIn(reason, text)
                    self.assertIn(case["claim"], text)
                    self.assertEqual("```mermaid" in text, arm in ("V1", "V3"))
                    self.assertEqual("Additional stipulated evidence" in text, arm in ("V2", "V3"))

    def test_v0_unchanged_and_separate(self):
        old, old_gold = rq7.load()
        self.assertEqual(len(old["cases"]), 10)
        self.assertEqual(len(old_gold["cases"]), 10)
        self.assertFalse("experiment_set" in old)
        self.assertNotEqual(set(self.by_id), {c["id"] for c in old["cases"]})

    def test_cli_can_select_v1(self):
        script = Path(rq7.__file__).resolve()
        r = subprocess.run(
            [sys.executable, str(script), "--dataset", "v1", "--check"],
            capture_output=True, text=True, check=True
        )
        self.assertEqual(json.loads(r.stdout)["cases"], 12)
        r = subprocess.run(
            [sys.executable, str(script), "--dataset", "v1", "--case", "B-DR01", "--arm", "V1"],
            capture_output=True, text=True, check=True
        )
        self.assertIn("src --> compile", r.stdout)
        self.assertIn("direct edge from src to package", r.stdout)

    def test_unknown_dataset_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown public dataset"):
            rq7.load("holdout")


if __name__ == "__main__":
    unittest.main()
