import unittest

from document_assembler import AssemblyError, assemble

DOCUMENT = {"id": "doc-1", "title": "Notes"}
CARDS = [{"id": "card-1", "text": "hello"}, {"id": "card-2", "text": "world"}]
ISLANDS = [{"id": "island-1", "title": "Group A"}]
EDGES = [
    {
        "id": "edge-1",
        "fromId": "card-1",
        "toId": "card-2",
        "type": "supports",
        "fromKind": "card",
        "toKind": "card",
    }
]


class AssembleTest(unittest.TestCase):
    def test_composes_one_document(self):
        composed = assemble(DOCUMENT, CARDS, ISLANDS, EDGES)
        self.assertEqual(composed["document"]["id"], "doc-1")
        self.assertEqual(len(composed["cards"]), 2)
        self.assertEqual(len(composed["edges"]), 1)

    def test_accepts_card_to_island_edge(self):
        edges = [
            {
                "id": "edge-2",
                "fromId": "card-1",
                "toId": "island-1",
                "type": "contains",
                "fromKind": "card",
                "toKind": "island",
            }
        ]
        composed = assemble(DOCUMENT, CARDS, ISLANDS, edges)
        self.assertEqual(composed["edges"][0]["toKind"], "island")

    def test_rejects_unknown_edge_endpoint(self):
        edges = [dict(EDGES[0], toId="card-9")]
        with self.assertRaises(AssemblyError):
            assemble(DOCUMENT, CARDS, ISLANDS, edges)

    def test_rejects_unknown_kind(self):
        edges = [dict(EDGES[0], toKind="narrative")]
        with self.assertRaises(AssemblyError):
            assemble(DOCUMENT, CARDS, ISLANDS, edges)

    def test_rejects_duplicate_card(self):
        with self.assertRaises(AssemblyError):
            assemble(DOCUMENT, [CARDS[0], CARDS[0]], ISLANDS, [])

    def test_rejects_missing_document_id(self):
        with self.assertRaises(AssemblyError):
            assemble({}, CARDS, ISLANDS, [])

    def test_accepts_affiliation(self):
        affiliations = [{"id": "aff-1", "cardId": "card-1", "islandId": "island-1"}]
        composed = assemble(DOCUMENT, CARDS, ISLANDS, EDGES, affiliations)
        self.assertEqual(len(composed["affiliations"]), 1)

    def test_rejects_island_card_id_unknown(self):
        islands = [dict(ISLANDS[0], cardIds=['card-9'])]
        with self.assertRaises(AssemblyError):
            assemble(DOCUMENT, CARDS, islands, EDGES)

    def test_rejects_affiliation_to_unknown_island(self):
        affiliations = [{"id": "aff-1", "cardId": "card-1", "islandId": "island-9"}]
        with self.assertRaises(AssemblyError):
            assemble(DOCUMENT, CARDS, ISLANDS, EDGES, affiliations)


if __name__ == "__main__":
    unittest.main()
