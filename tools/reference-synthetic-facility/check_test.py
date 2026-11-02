import pathlib
import shutil
import tempfile
import unittest

from check import check

ROOT = pathlib.Path(__file__).resolve().parents[2] / "scenarios" / "SCN-001-synthetic-facility"


class CheckTest(unittest.TestCase):
    def test_synthetic_corpus_detects_defects(self):
        receipt = check(ROOT)
        self.assertTrue(receipt["passed"])
        self.assertTrue(receipt["synthetic"])
        self.assertFalse(receipt["publicationAllowed"])
        self.assertEqual(len(receipt["findings"]), 5)
        self.assertIn("原本を取得できていない", " ".join(receipt["detectedDefects"]))

    def test_reintroduced_meeting_room_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            for path in ROOT.glob("*.md"):
                shutil.copy(path, root / path.name)
            v11 = root / "distribution-2026-11.md"
            v11.write_text(v11.read_text(encoding="utf-8") + "\n会議室は事前予約制です。\n", encoding="utf-8")
            receipt = check(root)
            self.assertFalse(receipt["passed"])


if __name__ == "__main__":
    unittest.main()
