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
import unicodedata
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import rq7_pilot

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
SAFE_ID = re.compile(r"^[a-z][a-z0-9_]*$")
NODE_MIN_WIDTH = 180
NODE_MAX_WIDTH = 2048
NODE_HEIGHT = 60
NODE_COLUMN_GAP = 50


def node_panel_width(labels: dict[str, str]) -> int:
    """Conservative one-line glyph budget, checked against actual Chromium bounds.

    Width is *never* used to cut or abbreviate the original label. Unsupported
    extreme strings fail closed; the structured text table remains a separate
    research alternative, not a license to truncate the visible Graph.
    """
    def estimate(label: str) -> int:
        total = 0
        for char in label:
            if unicodedata.combining(char):
                continue
            if char.isspace():
                total += 5
            elif unicodedata.east_asian_width(char) in ("W", "F"):
                total += 18
            elif ord(char) < 128 and char.isupper():
                total += 11
            elif ord(char) < 128 and char.islower():
                total += 9
            elif ord(char) < 128:
                total += 12
            else:
                total += 16
        return total + 28

    required = max((estimate(label) for label in labels.values()), default=NODE_MIN_WIDTH)
    if required > NODE_MAX_WIDTH:
        raise ValueError("label exceeds supported single-line SVG width")
    return max(NODE_MIN_WIDTH, required)



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
    card_width = node_panel_width(labels)
    step = card_width + NODE_COLUMN_GAP
    width, height = 90 + step * (max(depth.values()) + 1), 80 + 110 * rows
    positions: dict[str, tuple[int, int]] = {}
    for rank, nodes in sorted(layer.items()):
        for index, node in enumerate(nodes):
            positions[node] = (30 + step * rank, 30 + 110 * index + 55 * (rows - len(nodes)))
    return labels, positions, width, height



def route_points(positions: dict, source: str, target: str, card_width: int = NODE_MIN_WIDTH) -> list[tuple[int, int]]:
    """A narrow, explicit DAG-only route. Long edges use the upper corridor.

    This is not a general edge routing algorithm: the fixture currently has
    just three distinct small DAGs, and the geometry check must fail closed.
    """
    x1, y1 = positions[source]
    x2, y2 = positions[target]
    if x2 - x1 > card_width + NODE_COLUMN_GAP:
        # Separate this shortcut's arrow port from any adjacent edge that
        # enters the same target at its midline (avoids visually merged arrows).
        start, end = (x1 + card_width, y1 + 15), (x2 - 9, y2 + 15)
        corridor = min(y for _, y in positions.values()) - 18
        return [
            start,
            (start[0] + 18, start[1]),
            (start[0] + 18, corridor),
            (end[0] - 18, corridor),
            (end[0] - 18, end[1]),
            end,
        ]
    return [(x1 + card_width, y1 + 30), (x2 - 9, y2 + 30)]


def route_path_data(points: list[tuple[int, int]]) -> str:
    return " ".join(
        (f"M {x},{y}" if i == 0 else f"L {x},{y}")
        for i, (x, y) in enumerate(points)
    )


def intersects_interior(a: tuple[int, int], b: tuple[int, int],
                        x: int, y: int, w: int = 180, h: int = 60) -> bool:
    """Liang–Barsky segment/rectangle intersection, excluding the border."""
    x0, y0 = a
    dx, dy = b[0] - x0, b[1] - y0
    left, right, top, bottom = x + 1, x + w - 1, y + 1, y + h - 1
    lo, hi = 0.0, 1.0
    for p, q in (
        (-dx, x0 - left), (dx, right - x0),
        (-dy, y0 - top), (dy, bottom - y0),
    ):
        if p == 0:
            if q < 0:
                return False
        else:
            t = q / p
            if p < 0:
                lo = max(lo, t)
            else:
                hi = min(hi, t)
            if lo > hi:
                return False
    return True


def check_route_clearance(case: dict, positions: dict, card_width: int = NODE_MIN_WIDTH) -> None:
    """Reject any arrow segment cutting through unrelated rendered nodes."""
    for source, target in case["declared"]["edges"]:
        points = route_points(positions, source, target, card_width)
        for node, (x, y) in positions.items():
            if node in (source, target):
                continue
            for a, b in zip(points, points[1:]):
                if intersects_interior(a, b, x, y, w=card_width):
                    raise ValueError(
                        f"edge {source}->{target} crosses unrelated node {node}"
                    )


def accessible_graph_description(case: dict) -> str:
    """Textual alternative for the *declared* graph; no runtime or Gold claims.

    The image name remains short. This description exposes each directed
    edge (not transitive reachability), including the original node labels.
    Chromium AX-tree checks are not a substitute for screen-reader trials.
    """
    nodes = case["declared"]["nodes"]
    edges = case["declared"]["edges"]
    node_text = "; ".join(f'{n["id"]} ({n["label"]})' for n in nodes)
    edge_text = "; ".join(f"{src} to {dst}" for src, dst in edges)
    return (
        "Public synthetic declaration only. "
        f"Declared nodes ({len(nodes)}): {node_text}. "
        f"Declared directed edges ({len(edges)}): {edge_text}. "
        "No runtime observation, source closure, policy permission, or Owner acceptance is proven."
    )


def check_accessible_graph_description(case: dict, payload: str) -> None:
    """Fail if the image's textual topology omits or substitutes any relation."""
    root = ET.fromstring(payload)
    if root.get("role") != "img" or root.get("aria-labelledby") != "graph-title":
        raise ValueError("SVG accessible image role or short name missing")
    if root.get("aria-describedby") != "graph-description":
        raise ValueError("SVG accessible description reference missing")
    title = root.find(tag("title"))
    desc = root.find(tag("desc"))
    if title is None or title.get("id") != "graph-title" or title.text != f"Declared graph for {case['id']}":
        raise ValueError("SVG accessible title mismatch")
    if desc is None or desc.get("id") != "graph-description":
        raise ValueError("SVG accessible description missing")
    if desc.text != accessible_graph_description(case):
        raise ValueError("SVG accessible topology description mismatch")


def render_svg(case: dict) -> str:
    labels, pos, width, height = graph_layout(case)
    card_width = node_panel_width(labels)
    root = ET.Element(tag("svg"), {
        "version": "1.1", "viewBox": f"0 0 {width} {height}",
        "width": str(width), "height": str(height), "role": "img",
        "aria-labelledby": "graph-title",
        "aria-describedby": "graph-description",
    })
    ET.SubElement(root, tag("title"), {"id": "graph-title"}).text = (
        f"Declared graph for {case['id']}"
    )
    ET.SubElement(root, tag("desc"), {"id": "graph-description"}).text = (
        accessible_graph_description(case)
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
    check_route_clearance(case, pos, card_width)
    for src, dst in case["declared"]["edges"]:
        points = route_points(pos, src, dst, card_width)
        attrs = {
            "class": "declared-edge", "data-from": src, "data-to": dst,
            "stroke": "#333333", "stroke-width": "2",
            "marker-end": "url(#arrowhead)",
        }
        if len(points) == 2:
            (x1, y1), (x2, y2) = points
            attrs.update(x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2))
            elem = ET.SubElement(root, tag("line"), attrs)
        else:
            attrs["d"] = route_path_data(points)
            elem = ET.SubElement(root, tag("path"), attrs)
        ET.SubElement(elem, tag("title")).text = f"{src} to {dst}"
    for node, label in labels.items():
        x, y = pos[node]
        elem = ET.SubElement(root, tag("g"), {
            "class": "declared-node", "data-id": node,
            "data-label": label, "transform": f"translate({x},{y})",
        })
        ET.SubElement(elem, tag("rect"), {
            "width": str(card_width), "height": str(NODE_HEIGHT), "rx": "7",
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
    for edge in root.findall(tag("line")) + root.findall(tag("path")):
        if edge.get("class") != "declared-edge":
            continue
        key = edge.get("data-from"), edge.get("data-to")
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
    card_width = node_panel_width(labels)
    if root.get("viewBox") != f"0 0 {width} {height}" or root.get("role") != "img":
        raise ValueError("SVG viewport or role mismatch")
    if root.get("aria-labelledby") != "graph-title" or root.get("aria-describedby") != "graph-description":
        raise ValueError("SVG accessible name or description reference missing")
    if root.find(tag("title")) is None or root.find(tag("desc")) is None:
        raise ValueError("SVG title or description missing")
    groups = [g for g in root.findall(tag("g")) if g.get("class") == "declared-node"]
    lines = [g for g in root.findall(tag("line")) if g.get("class") == "declared-edge"]
    paths = [g for g in root.findall(tag("path")) if g.get("class") == "declared-edge"]
    if len(groups) != len(labels) or len(lines) + len(paths) != len(case["declared"]["edges"]):
        raise ValueError("SVG visual object count mismatch")
    for g in groups:
        node = g.get("data-id")
        if node not in positions:
            raise ValueError("SVG unknown visual node")
        x, y = positions[node]
        if g.get("transform") != f"translate({x},{y})":
            raise ValueError("SVG node moved without identity change")
        rect = g.find(tag("rect"))
        if rect is None or rect.get("width") != str(card_width) or rect.get("height") != str(NODE_HEIGHT):
            raise ValueError("SVG node outline altered")
        texts = g.findall(tag("text"))
        if len(texts) != 2 or texts[0].get("fill") != "#111111" or texts[1].get("fill") != "#111111":
            raise ValueError("SVG visible text contrast/arity changed")
    for edge in lines + paths:
        src, dst = edge.get("data-from"), edge.get("data-to")
        if src not in positions or dst not in positions:
            raise ValueError("SVG edge endpoints unidentified")
        points = route_points(positions, src, dst, card_width)
        expected = {
            "marker-end": "url(#arrowhead)",
            "stroke": "#333333",
            "stroke-width": "2",
        }
        if len(points) == 2:
            if edge.tag != tag("line"):
                raise ValueError("unexpected path for adjacent edge")
            (x1, y1), (x2, y2) = points
            expected.update(x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2))
        else:
            if edge.tag != tag("path"):
                raise ValueError("long edge requires a routed path")
            expected["d"] = route_path_data(points)
        if any(edge.get(key) != value for key, value in expected.items()):
            raise ValueError("SVG arrow geometry changed without edge identity change")
    check_route_clearance(case, positions, card_width)


def check_public_pair(case: dict) -> None:
    nodes = {n["id"]: n["label"] for n in case["declared"]["nodes"]}
    edges = {tuple(e) for e in case["declared"]["edges"]}
    expected = (nodes, edges)
    svg = render_svg(case)
    if svg_semantics(svg) != expected:
        raise ValueError(f"{case['id']}: SVG semantic mismatch")
    check_svg_geometry(case, svg)
    check_accessible_graph_description(case, svg)
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
