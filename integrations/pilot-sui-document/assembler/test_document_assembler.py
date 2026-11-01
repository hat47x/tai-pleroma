import unittest

from document_assembler import AssemblyError, assemble

DOCUMENT = {"documentId": "doc-1", "title": "Notes", "digest": "sha256:abc"}
CARDS = [
    {"cardId": "card-1", "documentId": "doc-1", "text": "hello"},
    {"cardId": "card-2", "documentId": "doc-1", "text": "world"},
]
ISLANDS = [{"islandId": "island-1", "documentId": "doc-1"}]
EDGES = [
    {"edgeId": "edge-1", "fromCard": "card-1", "toCard": "card-2", "relation": "supports"}
]


class AssembleTest(unittest.TestCase):
    def test_composes_one_document(self):
        composed = assemble(DOCUMENT, CARDS, ISLANDS, EDGES)
        self.assertEqual(composed["document"]["documentId"], "doc-1")
        self.assertEqual(len(composed["cards"]), 2)
        self.assertEqual(len(composed["edges"]), 1)

    def test_rejects_card_from_another_document(self):
        cards = [dict(CARDS[0], documentId="doc-2")]
        with self.assertRaises(AssemblyError):
            assemble(DOCUMENT, cards, ISLANDS, [])

    def test_rejects_island_from_another_document(self):
        islands = [dict(ISLANDS[0], documentId="doc-2")]
        with self.assertRaises(AssemblyError):
            assemble(DOCUMENT, CARDS, islands, [])

    def test_rejects_edge_to_unknown_card(self):
        edges = [dict(EDGES[0], toCard="card-9")]
        with self.assertRaises(AssemblyError):
            assemble(DOCUMENT, CARDS, ISLANDS, edges)

    def test_rejects_duplicate_card(self):
        with self.assertRaises(AssemblyError):
            assemble(DOCUMENT, [CARDS[0], CARDS[0]], ISLANDS, [])

    def test_rejects_missing_document_id(self):
        with self.assertRaises(AssemblyError):
            assemble({}, CARDS, ISLANDS, [])


if __name__ == "__main__":
    unittest.main()
