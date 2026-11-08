"""Structural SVG/Text parity tests for *public synthetic* RQ7 DAGs only."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import rq7_pilot
import rq7_svg


class SvgTextStructuralParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {}
        for dataset in ("v0", "v1"):
            stimuli, gold = rq7_pilot.load(dataset)
            rq7_pilot.validate(stimuli, gold)
            cls.cases[dataset] = stimuli["cases"]

    def test_all_22_public_cases_have_semantic_pair(self):
        self.assertEqual(sum(map(len, self.cases.values())), 22)
        for dataset, cases in self.cases.items():
            for case in cases:
                with self.subTest(dataset=dataset, case=case["id"]):
                    rq7_svg.check_public_pair(case)

    def test_svg_is_real_self_contained_xml_with_declared_only(self):
        case = self.cases["v1"][0]
        svg = rq7_svg.render_svg(case)
        root = ET.fromstring(svg)
        self.assertEqual(root.tag, rq7_svg.tag("svg"))
        self.assertEqual(root.attrib["role"], "img")
        self.assertIn("graph-title", root.attrib["aria-labelledby"])
        self.assertEqual(len(root.findall(rq7_svg.tag("line"))), len(case["declared"]["edges"]))
        self.assertEqual(len(root.findall(rq7_svg.tag("g"))), len(case["declared"]["nodes"]))
        self.assertIn("<svg", svg)
        self.assertNotIn("<script", svg)
        self.assertNotIn("https://", svg)
        self.assertNotIn("Observed event steps:", svg)
        self.assertNotIn("**Answer**", svg)

    def test_svg_nodes_are_visible_as_id_and_label(self):
        for case in self.cases["v1"]:
            ns, es = rq7_svg.svg_semantics(rq7_svg.render_svg(case))
            self.assertEqual(ns, {n["id"]: n["label"] for n in case["declared"]["nodes"]})
            self.assertEqual(es, {tuple(e) for e in case["declared"]["edges"]})

    def test_escaping_untrusted_label_does_not_add_svg_elements(self):
        case = copy.deepcopy(self.cases["v1"][0])
        case["declared"]["nodes"][0]["label"] = '<script>alert("x")</script>'
        svg = rq7_svg.render_svg(case)
        root = ET.fromstring(svg)
        self.assertEqual(len(root.findall(".//" + rq7_svg.tag("script"))), 0)
        self.assertNotIn("<script", svg)
        ns, _ = rq7_svg.svg_semantics(svg)
        self.assertEqual(ns[case["declared"]["nodes"][0]["id"]], '<script>alert("x")</script>')

    def test_cycle_rejected_not_silently_drawn(self):
        case = copy.deepcopy(self.cases["v1"][0])
        case["declared"]["edges"].append(["package", "src"])
        with self.assertRaisesRegex(ValueError, "cyclic"):
            rq7_svg.render_svg(case)

    def test_dangling_and_duplicate_edges_rejected(self):
        case = copy.deepcopy(self.cases["v1"][0])
        case["declared"]["edges"].append(["src", "missing"])
        with self.assertRaisesRegex(ValueError, "dangling"):
            rq7_svg.render_svg(case)
        case = copy.deepcopy(self.cases["v1"][0])
        case["declared"]["edges"].append(case["declared"]["edges"][0].copy())
        with self.assertRaisesRegex(ValueError, "duplicate declared edge"):
            rq7_svg.render_svg(case)

    def test_removing_svg_edge_is_detected_by_independent_manifest(self):
        case = self.cases["v1"][0]
        svg = rq7_svg.render_svg(case)
        root = ET.fromstring(svg)
        line = root.find(rq7_svg.tag("line"))
        self.assertIsNotNone(line)
        root.remove(line)
        mutated = ET.tostring(root, encoding="unicode")
        graph_nodes, graph_edges = rq7_svg.svg_semantics(mutated)
        self.assertEqual(graph_nodes, {n["id"]: n["label"] for n in case["declared"]["nodes"]})
        self.assertNotEqual(graph_edges, {tuple(x) for x in case["declared"]["edges"]})

    def test_tampered_visible_text_rejected(self):
        case = self.cases["v1"][0]
        root = ET.fromstring(rq7_svg.render_svg(case))
        node = root.find(rq7_svg.tag("g"))
        visible = node.findall(rq7_svg.tag("text"))
        visible[1].text = "Unknown Source"
        with self.assertRaisesRegex(ValueError, "SVG visible text"):
            rq7_svg.svg_semantics(ET.tostring(root, encoding="unicode"))

    def test_text_mutation_rejected(self):
        case = self.cases["v1"][0]
        text = rq7_pilot.declared_text(case)
        altered = text.replace("- Edge:", "- DirectLink:", 1)
        self.assertNotEqual(
            rq7_svg.text_semantics(altered)[1],
            {tuple(edge) for edge in case["declared"]["edges"]},
        )
        with self.assertRaisesRegex(ValueError, "duplicate text node"):
            rq7_svg.text_semantics(text + "\n- Node `src`: Duplicate")

    def test_svg_cli_check_both_datasets(self):
        script = Path(rq7_svg.__file__).resolve()
        for dataset, expected in (("v0", 10), ("v1", 12)):
            with self.subTest(dataset=dataset):
                x = subprocess.run(
                    [sys.executable, str(script), "--dataset", dataset, "--check"],
                    capture_output=True, text=True, check=True,
                )
                result = json.loads(x.stdout)
                self.assertEqual(result["cases"], expected)
                self.assertEqual(result["status"], "PUBLIC_SYNTHETIC_SVG_TEXT_STRUCTURAL_PARITY_ONLY")
                self.assertEqual(result["browser_visual_review"], "NOT_RUN")

    def test_svg_cli_emits_parsable_xml(self):
        script = Path(rq7_svg.__file__).resolve()
        r = subprocess.run(
            [sys.executable, str(script), "--dataset", "v1", "--case", "B-DR01"],
            capture_output=True, text=True, check=True,
        )
        root = ET.fromstring(r.stdout)
        self.assertEqual(root.tag, rq7_svg.tag("svg"))


if __name__ == "__main__":
    unittest.main()
