"""Compose a SUI DocumentV1 from flat TEI projection records.

The TEI projection contracts are flat. This module is the application-side
composition step: it checks identifier uniqueness, resolves edge endpoints
against cards or islands according to fromKind/toKind, and checks that each
affiliation points at an existing card and island.

SUI allows Edge.fromKind/toKind to be absent. When they are, the endpoint id
itself decides the kind, and an id that names no known card or island -- or that
names both -- is refused rather than assumed to be a card.
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
            kind = edge.get(f"{side}Kind")
            endpoint = edge.get(f"{side}Id")
            if kind is None:
                # SUI allows the endpoint kind to be absent. Resolve it from the
                # endpoint itself instead of assuming a card: an id that names an
                # island must not be looked up as a card, and an id that names
                # both is ambiguous rather than silently a card.
                matches = [name for name, ids in known.items() if endpoint in ids]
                if len(matches) != 1:
                    detail = "no such endpoint" if not matches else "ambiguous endpoint"
                    raise AssemblyError(
                        f"edge {edge_id} has no {side}Kind and {endpoint} is {detail}"
                    )
                kind = matches[0]
            elif kind not in KINDS:
                raise AssemblyError(f"edge {edge_id} has unknown {side}Kind {kind}")
            if endpoint not in known[kind]:
                raise AssemblyError(f"edge {edge_id} references unknown {kind} {endpoint}")

    for island in islands:
        for card_id in island.get("cardIds", []):
            if card_id not in card_ids:
                raise AssemblyError(f"island {island['id']} references unknown card {card_id}")

    containment = {
        (card_id, island["id"])
        for island in islands
        for card_id in island.get("cardIds", [])
    }

    for affiliation in affiliations:
        if affiliation.get("cardId") not in card_ids:
            raise AssemblyError(
                f"affiliation {affiliation['id']} references unknown card {affiliation.get('cardId')}"
            )
        if affiliation.get("islandId") not in island_ids:
            raise AssemblyError(
                f"affiliation {affiliation['id']} references unknown island {affiliation.get('islandId')}"
            )
        if (affiliation.get("cardId"), affiliation.get("islandId")) in containment:
            raise AssemblyError(
                f"affiliation {affiliation['id']} duplicates visual containment"
            )

    return {
        "document": dict(document),
        "cards": [dict(card) for card in cards],
        "islands": [dict(island) for island in islands],
        "edges": [dict(edge) for edge in edges],
        "affiliations": [dict(affiliation) for affiliation in affiliations],
    }
