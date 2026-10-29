import json
import pathlib
import shutil
import tempfile
import unittest

from check import D04, RECORDS, check

ROOT = pathlib.Path(__file__).resolve().parents[2]


class CheckTest(unittest.TestCase):
    def test_repository_flow_passes(self):
        receipt = check(ROOT)
        self.assertTrue(receipt["passed"], receipt)
        self.assertFalse(receipt["publicationAllowed"])

    def test_open_publication_gate_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            for relative in (*RECORDS.values(), D04):
                source = ROOT / relative
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(source, destination)
            gate = root / RECORDS["gate"]
            data = json.loads(gate.read_text(encoding="utf-8"))
            data["allowed"] = True
            gate.write_text(json.dumps(data), encoding="utf-8")
            receipt = check(root)
            self.assertFalse(receipt["passed"])


if __name__ == "__main__":
    unittest.main()
