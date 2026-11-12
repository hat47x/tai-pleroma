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
        self.assertEqual(
            len(root.findall(rq7_svg.tag("line"))) + len(root.findall(rq7_svg.tag("path"))),
            len(case["declared"]["edges"]),
        )
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

    def test_accessible_description_contains_every_node_and_directed_edge(self):
        for dataset, cases in self.cases.items():
            for case in cases:
                with self.subTest(dataset=dataset, case=case["id"]):
                    svg = rq7_svg.render_svg(case)
                    root = ET.fromstring(svg)
                    self.assertEqual(root.get("aria-labelledby"), "graph-title")
                    self.assertEqual(root.get("aria-describedby"), "graph-description")
                    desc = root.find(rq7_svg.tag("desc")).text
                    self.assertEqual(desc, rq7_svg.accessible_graph_description(case))
                    for src, dst in case["declared"]["edges"]:
                        self.assertIn(f"{src} to {dst}", desc)
                    for node in case["declared"]["nodes"]:
                        self.assertIn(f'{node["id"]} ({node["label"]})', desc)
                    rq7_svg.check_accessible_graph_description(case, svg)

    def test_accessible_description_mutations_are_rejected(self):
        case = self.cases["v1"][0]
        original = rq7_svg.render_svg(case)
        root = ET.fromstring(original)
        desc = root.find(rq7_svg.tag("desc"))
        source, target = case["declared"]["edges"][0]
        desc.text = desc.text.replace(f"{source} to {target}", "missing edge", 1)
        with self.assertRaisesRegex(ValueError, "topology description mismatch"):
            rq7_svg.check_accessible_graph_description(case, ET.tostring(root, encoding="unicode"))
        root = ET.fromstring(original)
        root.attrib["aria-labelledby"] = "graph-title graph-description"
        with self.assertRaisesRegex(ValueError, "short name"):
            rq7_svg.check_accessible_graph_description(case, ET.tostring(root, encoding="unicode"))
        root = ET.fromstring(original)
        root.attrib.pop("aria-describedby")
        with self.assertRaisesRegex(ValueError, "reference missing"):
            rq7_svg.check_accessible_graph_description(case, ET.tostring(root, encoding="unicode"))

    def test_accessible_description_escapes_untrusted_node_label(self):
        case = copy.deepcopy(self.cases["v1"][0])
        case["declared"]["nodes"][0]["label"] = '<script>alert("x")</script>'
        svg = rq7_svg.render_svg(case)
        self.assertNotIn("<script", svg)
        root = ET.fromstring(svg)
        self.assertIn('<script>alert("x")</script>', root.find(rq7_svg.tag("desc")).text)
        rq7_svg.check_accessible_graph_description(case, svg)

    def test_long_english_label_gets_full_width_without_abbreviation(self):
        case = copy.deepcopy(self.cases["v1"][0])
        label = "A deliberately long synthetic label that should stay fully visible in Chromium"
        case["declared"]["nodes"][0]["label"] = label
        nodes = {n["id"]: n["label"] for n in case["declared"]["nodes"]}
        card_width = rq7_svg.node_panel_width(nodes)
        self.assertGreater(card_width, rq7_svg.NODE_MIN_WIDTH)
        root = ET.fromstring(rq7_svg.render_svg(case))
        self.assertTrue(all(g.find(rq7_svg.tag("rect")).get("width") == str(card_width)
                            for g in root.findall(rq7_svg.tag("g"))))
        self.assertEqual(
            rq7_svg.svg_semantics(ET.tostring(root, encoding="unicode"))[0][case["declared"]["nodes"][0]["id"]],
            label,
        )
        rq7_svg.check_public_pair(case)

    def test_japanese_label_expands_width_and_preserves_exact_text(self):
        case = copy.deepcopy(self.cases["v1"][0])
        label = "業務期間確定と訂正イベントの参照関係を表示する長いラベル"
        case["declared"]["nodes"][0]["label"] = label
        nodes, pos, _, _ = rq7_svg.graph_layout(case)
        width = rq7_svg.node_panel_width(nodes)
        self.assertGreater(width, rq7_svg.NODE_MIN_WIDTH)
        self.assertGreater(pos["test"][0], pos["compile"][0] + width)
        rq7_svg.check_public_pair(case)
        self.assertIn(label, rq7_svg.accessible_graph_description(case))

    def test_label_beyond_supported_single_line_width_fails_closed(self):
        case = copy.deepcopy(self.cases["v1"][0])
        case["declared"]["nodes"][0]["label"] = "漢" * 150
        with self.assertRaisesRegex(ValueError, "exceeds supported single-line SVG width"):
            rq7_svg.render_svg(case)

    def test_long_label_does_not_hide_edges_or_corrupt_ports(self):
        case = copy.deepcopy(self.cases["v1"][0])
        case["declared"]["nodes"][0]["label"] = "A very long declared node that causes the entire rank spacing to expand safely"
        labels, pos, _, _ = rq7_svg.graph_layout(case)
        card_width = rq7_svg.node_panel_width(labels)
        routed = rq7_svg.route_points(pos, "compile", "package", card_width)
        self.assertEqual(routed[0][0], pos["compile"][0] + card_width)
        self.assertEqual(routed[-1][0], pos["package"][0] - 9)
        rq7_svg.check_route_clearance(case, pos, card_width)
        rq7_svg.check_svg_geometry(case, rq7_svg.render_svg(case))

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

    def test_long_edge_no_longer_crosses_middle_node(self):
        case = self.cases["v1"][0]
        labels, positions, _, _ = rq7_svg.graph_layout(case)
        card_width = rq7_svg.node_panel_width(labels)
        self.assertIn("test", labels)
        self.assertTrue(rq7_svg.intersects_interior(
            (positions["compile"][0] + card_width, positions["compile"][1] + 30),
            (positions["package"][0] - 9, positions["package"][1] + 30),
            *positions["test"],
        ), "pre-fix straight line should cross test node")
        routed = rq7_svg.route_points(positions, "compile", "package", card_width)
        adjacent = rq7_svg.route_points(positions, "test", "package", card_width)
        self.assertEqual(len(routed), 6)
        self.assertEqual(len(adjacent), 2)
        self.assertEqual(routed[-1][0], adjacent[-1][0])
        self.assertNotEqual(routed[-1][1], adjacent[-1][1],
                            "two different incoming arrows must not merge at one port")
        self.assertNotEqual(routed[0][1], rq7_svg.route_points(positions, "compile", "test", card_width)[0][1],
                            "long and adjacent outgoing edges must have different ports")
        for a, b in zip(routed, routed[1:]):
            self.assertFalse(rq7_svg.intersects_interior(a, b, *positions["test"], w=card_width))
        svg = ET.fromstring(rq7_svg.render_svg(case))
        matches = [p for p in svg.findall(rq7_svg.tag("path"))
                   if p.get("class") == "declared-edge"
                   and p.get("data-from") == "compile"
                   and p.get("data-to") == "package"]
        self.assertEqual(len(matches), 1)
        self.assertTrue(matches[0].get("d").startswith("M "))
        rq7_svg.check_route_clearance(case, positions, card_width)

    def test_old_straight_shortcut_is_rejected_as_visual_wrong_connection(self):
        case = self.cases["v1"][0]
        root = ET.fromstring(rq7_svg.render_svg(case))
        long_edge = next(p for p in root.findall(rq7_svg.tag("path"))
                         if p.get("data-from") == "compile"
                         and p.get("data-to") == "package")
        root.remove(long_edge)
        labels, pos, _, _ = rq7_svg.graph_layout(case)
        card_width = rq7_svg.node_panel_width(labels)
        # Data IDs remain exactly right; only routing is visually misleading.
        ET.SubElement(root, rq7_svg.tag("line"), {
            "class": "declared-edge", "data-from": "compile", "data-to": "package",
            "x1": str(pos["compile"][0] + card_width), "y1": str(pos["compile"][1] + 30),
            "x2": str(pos["package"][0] - 9), "y2": str(pos["package"][1] + 30),
            "stroke": "#333333", "stroke-width": "2",
            "marker-end": "url(#arrowhead)",
        })
        mutated = ET.tostring(root, encoding="unicode")
        self.assertEqual(rq7_svg.svg_semantics(mutated)[1], {tuple(e) for e in case["declared"]["edges"]})
        with self.assertRaisesRegex(ValueError, "long edge requires"):
            rq7_svg.check_svg_geometry(case, mutated)

    def test_tampered_arrow_geometry_rejected_even_when_edge_metadata_matches(self):
        case = self.cases["v1"][0]
        root = ET.fromstring(rq7_svg.render_svg(case))
        line = root.find(rq7_svg.tag("line"))
        self.assertIsNotNone(line)
        line.set("x2", str(int(line.get("x2")) + 110))
        modified = ET.tostring(root, encoding="unicode")
        # The old metadata-only check still sees the same edge IDs.
        self.assertEqual(
            rq7_svg.svg_semantics(modified)[1],
            {tuple(e) for e in case["declared"]["edges"]},
        )
        with self.assertRaisesRegex(ValueError, "arrow geometry"):
            rq7_svg.check_svg_geometry(case, modified)

    def test_tampered_node_position_rejected(self):
        case = self.cases["v1"][0]
        root = ET.fromstring(rq7_svg.render_svg(case))
        node = root.find(rq7_svg.tag("g"))
        node.set("transform", "translate(0,0)")
        with self.assertRaisesRegex(ValueError, "node moved"):
            rq7_svg.check_svg_geometry(case, ET.tostring(root, encoding="unicode"))

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
