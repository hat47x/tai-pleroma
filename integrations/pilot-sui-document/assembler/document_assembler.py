"""Compose a SUI DocumentV1 from flat TEI projection records.

The TEI projection contracts are flat. This module is the application-side
composition step: it checks that cards, islands and edges belong to the same
document and that edges point at existing cards.
"""


class AssemblyError(ValueError):
    """Raised when flat records cannot be composed into one document."""


def assemble(document, cards, islands, edges):
    document_id = document.get("documentId")
    if not document_id:
        raise AssemblyError("document.documentId is required")

    card_ids = set()
    for card in cards:
        if card.get("documentId") != document_id:
            raise AssemblyError(
                f"card {card.get('cardId')} belongs to {card.get('documentId')}, not {document_id}"
            )
        card_id = card.get("cardId")
        if not card_id:
            raise AssemblyError("card.cardId is required")
        if card_id in card_ids:
            raise AssemblyError(f"card {card_id} is duplicated")
        card_ids.add(card_id)

    island_ids = set()
    for island in islands:
        if island.get("documentId") != document_id:
            raise AssemblyError(
                f"island {island.get('islandId')} belongs to {island.get('documentId')}, not {document_id}"
            )
        island_id = island.get("islandId")
        if not island_id:
            raise AssemblyError("island.islandId is required")
        if island_id in island_ids:
            raise AssemblyError(f"island {island_id} is duplicated")
        island_ids.add(island_id)

    edge_ids = set()
    for edge in edges:
        edge_id = edge.get("edgeId")
        if not edge_id:
            raise AssemblyError("edge.edgeId is required")
        if edge_id in edge_ids:
            raise AssemblyError(f"edge {edge_id} is duplicated")
        edge_ids.add(edge_id)
        for side in ("fromCard", "toCard"):
            if edge.get(side) not in card_ids:
                raise AssemblyError(f"edge {edge_id} references unknown card {edge.get(side)}")

    return {
        "document": dict(document),
        "cards": [dict(card) for card in cards],
        "islands": [dict(island) for island in islands],
        "edges": [dict(edge) for edge in edges],
    }
