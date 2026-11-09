"""Regression checks for the YI hexagram audit (structure, not interpretation)."""

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("yi_structure_audit", ROOT / "audit-yi-constellation.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class YiStructureAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc01 = (audit.BASE / "01-64卦のシステム地図.md").read_text(encoding="utf-8")
        cls.doc09 = (audit.BASE / "09-変爻の分析.md").read_text(encoding="utf-8")

    def test_analysis_location_is_current(self):
        self.assertEqual(audit.BASE.name, "analysis")
        self.assertTrue((audit.BASE / "01-64卦のシステム地図.md").is_file())
        self.assertTrue((audit.BASE / "09-変爻の分析.md").is_file())

    def test_existing_structural_tables_and_fixture(self):
        checks = (
            audit.check_fixture_integrity(),
            audit.check_64_table(self.doc01),
            audit.check_matrix(self.doc01),
            audit.check_product_identity(self.doc09),
            audit.check_changes(self.doc09),
            audit.check_xiang(self.doc09),
            audit.check_pairs(),
            audit.check_one_line_neighborhood(),
        )
        self.assertEqual([], [e for group in checks for e in group])

    def test_stale_sui_identity_is_rejected(self):
        # Earlier prose used 隨(17), but the current series mapping is 萃(45).
        corrupted = self.doc09.replace("## 3. SUI 萃", "## 3. SUI 隨", 1)
        self.assertNotEqual(corrupted, self.doc09)
        self.assertTrue(any("identity SUI" in e for e in audit.check_product_identity(corrupted)))
        corrupted_summary = self.doc09.replace("| SUI 萃 |", "| SUI 隨 |", 1)
        self.assertNotEqual(corrupted_summary, self.doc09)
        self.assertTrue(any("identity SUI" in e for e in audit.check_product_identity(corrupted_summary)))

    def test_corrupted_changing_line_is_rejected(self):
        corrupted = self.doc09.replace("隨（隨）", "昇（升）", 1)
        self.assertNotEqual(corrupted, self.doc09)
        self.assertTrue(any("summary SUI line 1" in e for e in audit.check_changes(corrupted)))

    def test_product_pair_and_coverage_are_structural(self):
        self.assertEqual("萃", audit.PRODUCTS["SUI"])
        self.assertEqual(45, audit.BY_NAME[audit.PRODUCTS["SUI"]][0])
        self.assertEqual(46, audit.BY_BITS[audit.BY_NAME["萃"][1][::-1]][0])
        self.assertEqual([], audit.check_one_line_neighborhood())


if __name__ == "__main__":
    unittest.main()
