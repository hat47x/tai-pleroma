import json
import pathlib
import shutil
import tempfile
import unittest

from check import RECORDS, check

ROOT = pathlib.Path(__file__).resolve().parents[2]


class CheckTest(unittest.TestCase):
    def test_cross_scenario_matrix_passes(self):
        receipt = check(ROOT)
        self.assertTrue(receipt["passed"], receipt)
        self.assertFalse(receipt["publicationAllowed"])

    def test_open_publication_gate_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            for relative in RECORDS.values():
                source = ROOT / relative
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(source, destination)
            target = root / RECORDS["scn002"]
            data = json.loads(target.read_text(encoding="utf-8"))
            data["publicationAllowed"] = True
            target.write_text(json.dumps(data), encoding="utf-8")
            self.assertFalse(check(root)["passed"])


if __name__ == "__main__":
    unittest.main()
