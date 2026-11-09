"""Tests for a PUBLIC SYNTHETIC RQ7 stimulus tool, not Product qualification."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import rq7_pilot as rq7


class PublicPilotChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stimuli, cls.gold = rq7.load()

    def test_public_fixture_status_and_size(self):
        result = rq7.validate(self.stimuli, self.gold)
        self.assertEqual(result["status"], "PUBLIC_SYNTHETIC_FIXTURE_CHECK_ONLY")
        self.assertEqual(result["experiment_run_status"], "NOT_RUN")
        self.assertIs(result["independent_holdout"], False)
        self.assertEqual(result["cases"], 10)
        self.assertEqual(result["gold_entries"], 10)

    def test_all_forty_render_paths(self):
        for case in self.stimuli["cases"]:
            for arm in rq7.ARMS:
                with self.subTest(case=case["id"], arm=arm):
                    output = rq7.render(case, arm)
                    self.assertIn(case["claim"], output)
                    self.assertIn("PUBLIC SYNTHETIC STIMULUS", output)
                    self.assertIn("NOT an independent holdout", output)
                    self.assertIn("**Answer**: supported / refuted / undetermined", output)
                    self.assertNotIn(self._gold_for(case["id"])["reason"], output)
                    self.assertEqual("Additional stipulated evidence" in output, arm in ("V2", "V3"))
                    self.assertEqual("```mermaid" in output, arm in ("V1", "V3"))

    def test_graph_and_text_have_same_declared_nodes_edges(self):
        for case in self.stimuli["cases"]:
            text = rq7.declared_text(case)
            graph = rq7.declared_graph(case)
            for node in case["declared"]["nodes"]:
                self.assertIn(f"Node `{node['id']}`: {node['label']}", text)
                self.assertIn(f'{node["id"]}["{node["label"]}"]', graph)
            for src, dest in case["declared"]["edges"]:
                self.assertIn(f"Edge: `{src}` → `{dest}`", text)
                self.assertIn(f"{src} --> {dest}", graph)

    def test_evidence_body_identical_for_v2_v3(self):
        for case in self.stimuli["cases"]:
            body = rq7.evidence(case)
            self.assertIn(body, rq7.render(case, "V2"))
            self.assertIn(body, rq7.render(case, "V3"))
            self.assertNotIn(body, rq7.render(case, "V0"))
            self.assertNotIn(body, rq7.render(case, "V1"))

    def test_gold_is_same_for_equivalent_information(self):
        for item in self.gold["cases"]:
            self.assertEqual(item["expected"]["V0"], item["expected"]["V1"])
            self.assertEqual(item["expected"]["V2"], item["expected"]["V3"])

    def test_declared_positive_prevents_all_unknown_strategy(self):
        for case_id in ("B-D01", "F-D01"):
            expected = self._gold_for(case_id)["expected"]
            self.assertEqual(expected["V0"], "supported")
            self.assertEqual(expected["V1"], "supported")

    def test_unknown_observer_is_not_nonexecution(self):
        for case_id in ("B-N03", "F-N02", "X-N01"):
            expected = self._gold_for(case_id)["expected"]
            self.assertEqual(expected["V2"], "undetermined")
            self.assertEqual(expected["V3"], "undetermined")

    def test_duplicate_case_rejected(self):
        fixture = copy.deepcopy(self.stimuli)
        fixture["cases"].append(copy.deepcopy(fixture["cases"][0]))
        with self.assertRaisesRegex(ValueError, "case IDs"):
            rq7.validate(fixture, self.gold)

    def test_dangling_edge_rejected(self):
        fixture = copy.deepcopy(self.stimuli)
        fixture["cases"][0]["declared"]["edges"].append(["src", "missing-node"])
        with self.assertRaisesRegex(ValueError, "dangling"):
            rq7.validate(fixture, self.gold)

    def test_valid_skip_cannot_be_required(self):
        fixture = copy.deepcopy(self.stimuli)
        fixture["cases"][0]["resolved"]["required"].append("test")
        with self.assertRaisesRegex(ValueError, "required or skipped"):
            rq7.validate(fixture, self.gold)

    def test_unsupported_observer_coverage_rejected(self):
        fixture = copy.deepcopy(self.stimuli)
        fixture["cases"][0]["observed"]["observer_coverage"] = "globally-complete"
        with self.assertRaisesRegex(ValueError, "observer coverage"):
            rq7.validate(fixture, self.gold)

    def test_gold_leak_and_holdout_label_rejected(self):
        fixture = copy.deepcopy(self.stimuli)
        fixture["cases"][0]["expected"] = "supported"
        with self.assertRaisesRegex(ValueError, "Gold leaked"):
            rq7.validate(fixture, self.gold)
        fixture = copy.deepcopy(self.stimuli)
        fixture["holdout"] = True
        with self.assertRaisesRegex(ValueError, "holdout"):
            rq7.validate(fixture, self.gold)

    def test_wrong_gold_or_arm_equivalence_rejected(self):
        gold = copy.deepcopy(self.gold)
        gold["cases"][0]["expected"]["V1"] = "supported"
        with self.assertRaisesRegex(ValueError, "unequal Gold"):
            rq7.validate(self.stimuli, gold)
        gold = copy.deepcopy(self.gold)
        gold["cases"][0]["expected"]["V0"] = "arbitrary"
        with self.assertRaisesRegex(ValueError, "invalid verdict"):
            rq7.validate(self.stimuli, gold)

    def test_cli_fixture_check_and_render(self):
        tool = Path(rq7.__file__).resolve()
        check = subprocess.run([sys.executable, str(tool), "--check"], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(check.stdout)["cases"], 10)
        render = subprocess.run([sys.executable, str(tool), "--case", "B-N01", "--arm", "V3"], capture_output=True, text=True, check=True)
        self.assertIn("hook", render.stdout)
        self.assertIn("```mermaid", render.stdout)

    @classmethod
    def _gold_for(cls, case_id: str) -> dict:
        return next(g for g in cls.gold["cases"] if g["id"] == case_id)


if __name__ == "__main__":
    unittest.main()
