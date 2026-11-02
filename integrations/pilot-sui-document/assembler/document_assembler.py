"""Compose a SUI DocumentV1 from flat TEI projection records.

The TEI projection contracts are flat. This module is the application-side
composition step: it checks identifier uniqueness and resolves edge endpoints
against cards or islands according to fromKind/toKind.
"""

KINDS = ("card", "island")


class AssemblyError(ValueError):
    """Raised when flat records cannot be composed into one document."""


def _unique(records, label):
    ids = set()
    for record in records:
        identifier = record.get("id")
        if not identifier:
            raise AssemblyError(f"{label}.id is required")
        if identifier in ids:
            raise AssemblyError(f"{label} {identifier} is duplicated")
        ids.add(identifier)
    return ids


def assemble(document, cards, islands, edges):
    if not document.get("id"):
        raise AssemblyError("document.id is required")

    card_ids = _unique(cards, "card")
    island_ids = _unique(islands, "island")
    _unique(edges, "edge")

    known = {"card": card_ids, "island": island_ids}
    for edge in edges:
        edge_id = edge["id"]
        for side in ("from", "to"):
            kind = edge.get(f"{side}Kind") or "card"
            if kind not in KINDS:
                raise AssemblyError(f"edge {edge_id} has unknown {side}Kind {kind}")
            endpoint = edge.get(f"{side}Id")
            if endpoint not in known[kind]:
                raise AssemblyError(f"edge {edge_id} references unknown {kind} {endpoint}")

    return {
        "document": dict(document),
        "cards": [dict(card) for card in cards],
        "islands": [dict(island) for island in islands],
        "edges": [dict(edge) for edge in edges],
    }
