"""Structured, keyboard-disclosable HTML text alternative for PUBLIC RQ7 DAGs.

This is a research-only display component, NOT a TEI Studio UI, semantic
Source Reader, current-policy Disclosure evaluator, or screen-reader test.
"""
from __future__ import annotations

from html import escape
import xml.etree.ElementTree as ET


def structured_graph_html(case: dict) -> str:
    """Render two native HTML tables, preserving direct edges and labels.

    No inferred transitive edges, runtime events, Gold, or privileged Source
    are read. HTML is also a well-formed XML fragment for deterministic tests.
    """
    nodes = case["declared"]["nodes"]
    edges = case["declared"]["edges"]
    node_rows = "\n".join(
        f'<tr><th scope="row">{escape(node["id"])}</th>'
        f'<td>{escape(node["label"])}</td></tr>'
        for node in nodes
    )
    edge_rows = "\n".join(
        f'<tr><th scope="row">{escape(src)}</th>'
        f'<td>{escape(dst)}</td></tr>'
        for src, dst in edges
    )
    return (
        '<details id="graph-data">'
        '<summary>Declared graph as navigable node and direct-edge tables</summary>'
        '<p>Public synthetic declaration only. This is not evidence of '
        'runtime execution, Source closure, current permissions, or Owner acceptance.</p>'
        '<table id="declared-nodes">'
        '<caption>Declared nodes</caption>'
        '<thead><tr><th scope="col">Node ID</th><th scope="col">Label</th></tr></thead>'
        f'<tbody>{node_rows}</tbody></table>'
        '<table id="declared-direct-edges">'
        '<caption>Declared directed edges, not transitive paths</caption>'
        '<thead><tr><th scope="col">From node</th><th scope="col">To node</th></tr></thead>'
        f'<tbody>{edge_rows}</tbody></table>'
        '</details>'
    )


def structured_graph_semantics(fragment: str) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Extract native table row meanings; do not trust row counts alone."""
    root = ET.fromstring(fragment)
    if root.tag != "details" or root.attrib != {"id": "graph-data"}:
        raise ValueError("missing native details disclosure")
    if root.find("summary") is None:
        raise ValueError("missing graph disclosure summary")
    result = []
    for table_id in ("declared-nodes", "declared-direct-edges"):
        table = root.find(f"./table[@id='{table_id}']")
        if table is None or table.find("caption") is None:
            raise ValueError("missing named structured table")
        rows = []
        for tr in table.findall("./tbody/tr"):
            th, td = tr.find("th"), tr.find("td")
            if th is None or td is None or th.get("scope") != "row":
                raise ValueError("missing row header or value")
            rows.append((th.text or "", td.text or ""))
        result.append(rows)
    return result[0], result[1]


def check_structured_graph(case: dict, fragment: str) -> None:
    actual_nodes, actual_edges = structured_graph_semantics(fragment)
    expected_nodes = [(node["id"], node["label"]) for node in case["declared"]["nodes"]]
    expected_edges = [tuple(edge) for edge in case["declared"]["edges"]]
    if actual_nodes != expected_nodes:
        raise ValueError("structured table node identities or labels differ from declared Graph")
    if actual_edges != expected_edges:
        raise ValueError("structured table direct-edge identities differ from declared Graph")
