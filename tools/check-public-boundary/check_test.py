import unittest

from check import scan_text


class ScanTextTest(unittest.TestCase):
    def test_private_resource_name_is_rejected(self):
        pattern = "tei-platform-" + "private-resources"
        self.assertTrue(scan_text(f"see {pattern}"))

    def test_private_key_marker_is_rejected(self):
        self.assertTrue(scan_text("BEGIN " + "PRIVATE KEY"))

    def test_clean_text_passes(self):
        self.assertEqual(scan_text("公開してよい合成fixtureです。"), [])


if __name__ == "__main__":
    unittest.main()
