"""Compose a SUI DocumentV1 from flat TEI projection records.

The TEI projection contracts are flat. This module is the application-side
composition step: it checks identifier uniqueness, resolves edge endpoints
against cards or islands according to fromKind/toKind, and checks that each
affiliation points at an existing card and island.
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


def assemble(document, cards, islands, edges, affiliations=()):
    if not document.get("id"):
        raise AssemblyError("document.id is required")

    card_ids = _unique(cards, "card")
    island_ids = _unique(islands, "island")
    _unique(edges, "edge")
    _unique(affiliations, "affiliation")

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

    for affiliation in affiliations:
        if affiliation.get("cardId") not in card_ids:
            raise AssemblyError(
                f"affiliation {affiliation['id']} references unknown card {affiliation.get('cardId')}"
            )
        if affiliation.get("islandId") not in island_ids:
            raise AssemblyError(
                f"affiliation {affiliation['id']} references unknown island {affiliation.get('islandId')}"
            )

    return {
        "document": dict(document),
        "cards": [dict(card) for card in cards],
        "islands": [dict(island) for island in islands],
        "edges": [dict(edge) for edge in edges],
        "affiliations": [dict(affiliation) for affiliation in affiliations],
    }
