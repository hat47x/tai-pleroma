import json
import pathlib
import shutil
import tempfile
import unittest

from check import VARIANTS, check

ROOT = pathlib.Path(__file__).resolve().parents[2]


class CheckTest(unittest.TestCase):
    def test_repository_variants_pass(self):
        receipt = check(ROOT)
        self.assertTrue(receipt["passed"], receipt)
        self.assertFalse(receipt["publicationAllowed"])

    def test_broken_tei_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            for expected in VARIANTS.values():
                for relative in (expected["mmi"], expected["tei"], expected["sei"]):
                    source = ROOT / relative
                    destination = root / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(source, destination)
            target = root / VARIANTS["variant-b"]["tei"]
            data = json.loads(target.read_text(encoding="utf-8"))
            data["validation"] = "failed"
            target.write_text(json.dumps(data), encoding="utf-8")
            receipt = check(root)
            self.assertFalse(receipt["passed"])


if __name__ == "__main__":
    unittest.main()
