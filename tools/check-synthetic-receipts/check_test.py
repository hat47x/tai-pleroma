import json
import pathlib
import shutil
import tempfile
import unittest

from check import REVIEW_STATUS, RECORDS, check

ROOT = pathlib.Path(__file__).resolve().parents[2]


class CheckTest(unittest.TestCase):
    def test_repository_receipts_are_synthetic(self):
        receipt = check(ROOT)
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["recordCount"], len(RECORDS))

    def test_missing_synthetic_label_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            for relative in (*RECORDS, REVIEW_STATUS):
                source = ROOT / relative
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(source, destination)
            target = root / RECORDS[0]
            data = json.loads(target.read_text(encoding="utf-8"))
            data["synthetic"] = False
            target.write_text(json.dumps(data), encoding="utf-8")
            receipt = check(root)
            self.assertFalse(receipt["passed"])
            self.assertTrue(any("synthetic is not true" in error for error in receipt["errors"]))


if __name__ == "__main__":
    unittest.main()
