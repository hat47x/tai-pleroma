#!/usr/bin/env python3
"""Render read-only PUBLIC RQ7 declared DAG as self-contained SVG.

Only the *declared* nodes/edges of a synthetic fixture are visualized.
No Product Source/Policy/Result is fetched; no real execution is claimed.
A structural XML comparison is NOT browser, visual, accessibility, or
human/AI cognitive equivalence.
"""
from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import rq7_pilot

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
SAFE_ID = re.compile(r"^[a-z][a-z0-9_]*$")


def tag(name: str) -> str:
    return f"{{{SVG_NS}}}{name}"


def graph_layout(case: dict) -> tuple[dict, dict, int, int]:
    graph = case["declared"]
    labels = {node["id"]: node["label"] for node in graph["nodes"]}
    if not labels or len(labels) != len(graph["nodes"]):
        raise ValueError("empty or duplicate nodes")
    if any(not SAFE_ID.fullmatch(n) for n in labels):
        raise ValueError("unsafe node ID")
    if any(not isinstance(label, str) or not label.strip() for label in labels.values()):
        raise ValueError("empty node label")

    indegree = dict.fromkeys(labels, 0)
    outgoing: dict[str, list[str]] = defaultdict(list)
    edges = [tuple(edge) for edge in graph["edges"]]
    if len(set(edges)) != len(edges):
        raise ValueError("duplicate declared edge")
    for src, dst in edges:
        if src not in labels or dst not in labels:
            raise ValueError("dangling edge")
        indegree[dst] += 1
        outgoing[src].append(dst)

    depth = dict.fromkeys(labels, 0)
    pending = sorted(n for n, d in indegree.items() if d == 0)
    seen = 0
    while pending:
        node = pending.pop(0)
        seen += 1
        for dest in outgoing[node]:
            depth[dest] = max(depth[dest], depth[node] + 1)
            indegree[dest] -= 1
            if indegree[dest] == 0:
                pending.append(dest)
                pending.sort()
    if seen != len(labels):
        raise ValueError("cyclic graph: this fixed static DAG renderer cannot visualize it")

    layer: dict[int, list[str]] = defaultdict(list)
    for node in labels:
        layer[depth[node]].append(node)
    rows = max(len(x) for x in layer.values())
    width, height = 90 + 230 * (max(depth.values()) + 1), 80 + 110 * rows
    positions: dict[str, tuple[int, int]] = {}
    for rank, nodes in sorted(layer.items()):
        for index, node in enumerate(nodes):
            positions[node] = (30 + 230 * rank, 30 + 110 * index + 55 * (rows - len(nodes)))
    return labels, positions, width, height


def render_svg(case: dict) -> str:
    labels, pos, width, height = graph_layout(case)
    root = ET.Element(tag("svg"), {
        "version": "1.1", "viewBox": f"0 0 {width} {height}",
        "width": str(width), "height": str(height), "role": "img",
        "aria-labelledby": "graph-title graph-description",
    })
    ET.SubElement(root, tag("title"), {"id": "graph-title"}).text = (
        f"Declared graph for {case['id']}"
    )
    ET.SubElement(root, tag("desc"), {"id": "graph-description"}).text = (
        "Public synthetic declaration only. Nodes are labelled with their IDs and names; "
        "arrows show all declared directed edges. No actual runtime observation is depicted."
    )
    defs = ET.SubElement(root, tag("defs"))
    marker = ET.SubElement(defs, tag("marker"), {
        "id": "arrowhead", "viewBox": "0 0 10 10",
        "refX": "9", "refY": "5", "markerWidth": "8",
        "markerHeight": "8", "orient": "auto-start-reverse",
    })
    ET.SubElement(marker, tag("path"), {
        "d": "M 0 0 L 10 5 L 0 10 z", "fill": "#333333"
    })
    for src, dst in case["declared"]["edges"]:
        x1, y1 = pos[src]
        x2, y2 = pos[dst]
        elem = ET.SubElement(root, tag("line"), {
            "class": "declared-edge", "data-from": src, "data-to": dst,
            "x1": str(x1 + 180), "y1": str(y1 + 30),
            "x2": str(x2 - 9), "y2": str(y2 + 30),
            "stroke": "#333333", "stroke-width": "2",
            "marker-end": "url(#arrowhead)",
        })
        ET.SubElement(elem, tag("title")).text = f"{src} to {dst}"
    for node, label in labels.items():
        x, y = pos[node]
        elem = ET.SubElement(root, tag("g"), {
            "class": "declared-node", "data-id": node,
            "data-label": label, "transform": f"translate({x},{y})",
        })
        ET.SubElement(elem, tag("rect"), {
            "width": "180", "height": "60", "rx": "7",
            "fill": "#ffffff", "stroke": "#333333", "stroke-width": "2",
        })
        ET.SubElement(elem, tag("title")).text = f"{node}: {label}"
        ET.SubElement(elem, tag("text"), {
            "x": "10", "y": "23", "font-family": "sans-serif",
            "font-size": "14", "font-weight": "bold", "fill": "#111111",
        }).text = node
        ET.SubElement(elem, tag("text"), {
            "x": "10", "y": "44", "font-family": "sans-serif",
            "font-size": "13", "fill": "#111111",
        }).text = label
    return ET.tostring(root, encoding="unicode", xml_declaration=True) + "\n"


def svg_semantics(payload: str) -> tuple[dict[str, str], set[tuple[str, str]]]:
    root = ET.fromstring(payload)
    if root.tag != tag("svg"):
        raise ValueError("not SVG")
    nodes: dict[str, str] = {}
    edges: set[tuple[str, str]] = set()
    for g in root.findall(tag("g")):
        if g.get("class") != "declared-node":
            continue
        node, label = g.get("data-id"), g.get("data-label")
        if node in nodes or node is None or label is None:
            raise ValueError("duplicate or missing node identity")
        visible = [t.text for t in g.findall(tag("text"))]
        if visible != [node, label]:
            raise ValueError("SVG visible text does not match node ID and label")
        nodes[node] = label
    for line in root.findall(tag("line")):
        if line.get("class") != "declared-edge":
            continue
        key = line.get("data-from"), line.get("data-to")
        if None in key or key in edges:
            raise ValueError("duplicate or unidentified SVG edge")
        edges.add(key)
    return nodes, edges


def text_semantics(text: str) -> tuple[dict[str, str], set[tuple[str, str]]]:
    nodes: dict[str, str] = {}
    edges: set[tuple[str, str]] = set()
    for line in text.splitlines():
        if line.startswith("- Node "):
            match = re.fullmatch(r"- Node `([^`]+)`: (.+)", line)
            if match is None or match[1] in nodes:
                raise ValueError("invalid/duplicate text node")
            nodes[match[1]] = match[2]
        if line.startswith("- Edge: "):
            match = re.fullmatch(r"- Edge: `([^`]+)` → `([^`]+)`", line)
            if match is None or (match[1], match[2]) in edges:
                raise ValueError("invalid/duplicate text edge")
            edges.add((match[1], match[2]))
    return nodes, edges



def check_svg_geometry(case: dict, payload: str) -> None:
    """Check edge endpoints/node placement, not just XML data attributes.

    Still NOT a browser pixel review: layout and oracle share a fixed DAG
    placement model, and actual font/viewport/assistive technology is untested.
    """
    root = ET.fromstring(payload)
    labels, positions, width, height = graph_layout(case)
    if root.get("viewBox") != f"0 0 {width} {height}" or root.get("role") != "img":
        raise ValueError("SVG viewport or role mismatch")
    if root.get("aria-labelledby") != "graph-title graph-description":
        raise ValueError("SVG accessible name missing")
    if root.find(tag("title")) is None or root.find(tag("desc")) is None:
        raise ValueError("SVG title or description missing")
    groups = [g for g in root.findall(tag("g")) if g.get("class") == "declared-node"]
    lines = [g for g in root.findall(tag("line")) if g.get("class") == "declared-edge"]
    if len(groups) != len(labels) or len(lines) != len(case["declared"]["edges"]):
        raise ValueError("SVG visual object count mismatch")
    for g in groups:
        node = g.get("data-id")
        if node not in positions:
            raise ValueError("SVG unknown visual node")
        x, y = positions[node]
        if g.get("transform") != f"translate({x},{y})":
            raise ValueError("SVG node moved without identity change")
        rect = g.find(tag("rect"))
        if rect is None or rect.get("width") != "180" or rect.get("height") != "60":
            raise ValueError("SVG node outline altered")
        texts = g.findall(tag("text"))
        if len(texts) != 2 or texts[0].get("fill") != "#111111" or texts[1].get("fill") != "#111111":
            raise ValueError("SVG visible text contrast/arity changed")
    for line in lines:
        src, dst = line.get("data-from"), line.get("data-to")
        if src not in positions or dst not in positions:
            raise ValueError("SVG edge endpoints unidentified")
        x1, y1 = positions[src]
        x2, y2 = positions[dst]
        expected = {
            "x1": str(x1 + 180), "y1": str(y1 + 30),
            "x2": str(x2 - 9), "y2": str(y2 + 30),
            "marker-end": "url(#arrowhead)",
            "stroke": "#333333",
            "stroke-width": "2",
        }
        if any(line.get(key) != value for key, value in expected.items()):
            raise ValueError("SVG arrow geometry changed without edge identity change")


def check_public_pair(case: dict) -> None:
    nodes = {n["id"]: n["label"] for n in case["declared"]["nodes"]}
    edges = {tuple(e) for e in case["declared"]["edges"]}
    expected = (nodes, edges)
    svg = render_svg(case)
    if svg_semantics(svg) != expected:
        raise ValueError(f"{case['id']}: SVG semantic mismatch")
    check_svg_geometry(case, svg)
    if text_semantics(rq7_pilot.declared_text(case)) != expected:
        raise ValueError(f"{case['id']}: text semantic mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=tuple(rq7_pilot.PUBLIC_DATASETS), default="v1")
    parser.add_argument("--case", help="public synthetic case ID; emits SVG to stdout")
    parser.add_argument("--check", action="store_true", help="parse public SVG and Markdown semantics for every case")
    args = parser.parse_args()
    if (args.case is None) == (not args.check):
        parser.error("specify exactly one of --case or --check")
    data, gold = rq7_pilot.load(args.dataset)
    rq7_pilot.validate(data, gold)
    if args.check:
        for case in data["cases"]:
            check_public_pair(case)
        print(json.dumps({
            "status": "PUBLIC_SYNTHETIC_SVG_TEXT_STRUCTURAL_PARITY_ONLY",
            "dataset": args.dataset, "cases": len(data["cases"]),
            "browser_visual_review": "NOT_RUN",
            "human_ai_cognition": "NOT_RUN",
            "product_execution": "NOT_RUN",
            "independent_holdout": False,
        }, indent=2))
        return
    selected = [c for c in data["cases"] if c["id"] == args.case]
    if len(selected) != 1:
        parser.error("unknown case")
    check_public_pair(selected[0])
    print(render_svg(selected[0]), end="")


if __name__ == "__main__":
    main()
