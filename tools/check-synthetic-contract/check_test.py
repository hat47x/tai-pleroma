import json
import pathlib
import shutil
import tempfile
import unittest

from check import RECORD, check

ROOT = pathlib.Path(__file__).resolve().parents[2]


class CheckTest(unittest.TestCase):
    def test_unknown_edge_is_preserved(self):
        receipt = check(ROOT)
        self.assertTrue(receipt["passed"], receipt)
        self.assertTrue(receipt["unknownEdgePreserved"])

    def test_changed_edge_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            target = root / RECORD
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / RECORD, target)
            data = json.loads(target.read_text(encoding="utf-8"))
            data["edgeType"] = "supports"
            target.write_text(json.dumps(data), encoding="utf-8")
            self.assertFalse(check(root)["passed"])


if __name__ == "__main__":
    unittest.main()
