"""Public synthetic structured graph alternatives; not human or AT acceptance."""
from __future__ import annotations

import copy
import unittest
import xml.etree.ElementTree as ET

import rq7_pilot
import rq7_structured_alt as alt


class StructuredGraphAlternative(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = []
        for dataset in ("v0", "v1"):
            inputs, gold = rq7_pilot.load(dataset)
            rq7_pilot.validate(inputs, gold)
            cls.cases += inputs["cases"]

    def test_all_22_public_cases_preserve_node_and_direct_edge_meanings(self):
        self.assertEqual(len(self.cases), 22)
        for case in self.cases:
            with self.subTest(case=case["id"]):
                text = alt.structured_graph_html(case)
                alt.check_structured_graph(case, text)
                nodes, edges = alt.structured_graph_semantics(text)
                self.assertEqual(nodes, [(n["id"], n["label"]) for n in case["declared"]["nodes"]])
                self.assertEqual(edges, [tuple(e) for e in case["declared"]["edges"]])

    def test_native_disclosure_and_table_structure(self):
        root = ET.fromstring(alt.structured_graph_html(self.cases[0]))
        self.assertEqual(root.tag, "details")
        self.assertEqual(root.attrib, {"id": "graph-data"})
        self.assertIsNotNone(root.find("summary"))
        self.assertEqual(len(root.findall("table")), 2)
        for table in root.findall("table"):
            self.assertIsNotNone(table.find("caption"))
            self.assertEqual([h.get("scope") for h in table.findall("./thead/tr/th")],
                             ["col", "col"])
            self.assertTrue(all(t.get("scope") == "row" for t in table.findall("./tbody/tr/th")))

    def test_same_number_of_edges_but_different_relation_is_rejected(self):
        case = self.cases[0]
        root = ET.fromstring(alt.structured_graph_html(case))
        first_row = root.find("./table[@id='declared-direct-edges']/tbody/tr")
        self.assertIsNotNone(first_row)
        first_row.find("td").text = "another_valid_label"
        mutated = ET.tostring(root, encoding="unicode")
        _, before = alt.structured_graph_semantics(alt.structured_graph_html(case))
        _, after = alt.structured_graph_semantics(mutated)
        self.assertEqual(len(before), len(after))
        self.assertNotEqual(before, after)
        with self.assertRaisesRegex(ValueError, "direct-edge identities"):
            alt.check_structured_graph(case, mutated)

    def test_missing_node_row_detected(self):
        case = self.cases[0]
        root = ET.fromstring(alt.structured_graph_html(case))
        tbody = root.find("./table[@id='declared-nodes']/tbody")
        tbody.remove(tbody.find("tr"))
        with self.assertRaisesRegex(ValueError, "node identities"):
            alt.check_structured_graph(case, ET.tostring(root, encoding="unicode"))

    def test_escaped_label_is_not_executable_markup(self):
        case = copy.deepcopy(self.cases[0])
        case["declared"]["nodes"][0]["label"] = '<script src="evil">A & B</script>'
        html = alt.structured_graph_html(case)
        self.assertNotIn("<script", html)
        self.assertNotIn('src="evil"', html)
        alt.check_structured_graph(case, html)

    def test_table_caption_not_optional(self):
        root = ET.fromstring(alt.structured_graph_html(self.cases[0]))
        table = root.find("table")
        table.remove(table.find("caption"))
        with self.assertRaisesRegex(ValueError, "named structured table"):
            alt.structured_graph_semantics(ET.tostring(root, encoding="unicode"))

    def test_missing_row_header_rejected(self):
        root = ET.fromstring(alt.structured_graph_html(self.cases[0]))
        th = root.find("./table[@id='declared-nodes']/tbody/tr/th")
        th.set("scope", "col")
        with self.assertRaisesRegex(ValueError, "row header"):
            alt.structured_graph_semantics(ET.tostring(root, encoding="unicode"))

    def test_no_gold_or_runtime_evidence_leaked(self):
        for case in self.cases:
            text = alt.structured_graph_html(case)
            self.assertNotIn("Expected verdict:", text)
            self.assertNotIn("Observed event steps:", text)
            self.assertNotIn("question_selector", text)
            self.assertIn("not evidence of runtime execution", text)


if __name__ == "__main__":
    unittest.main()
