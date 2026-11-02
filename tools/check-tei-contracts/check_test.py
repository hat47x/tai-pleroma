import json
import pathlib
import shutil
import tempfile
import unittest

from check import RECORD, check

ROOT = pathlib.Path(__file__).resolve().parents[2]


class CheckTest(unittest.TestCase):
    def test_repository_chain_passes(self):
        receipt = check(ROOT)
        self.assertTrue(receipt["passed"], receipt)
        self.assertFalse(receipt["publicationAllowed"])

    def test_broken_chain_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            target = root / RECORD
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / RECORD, target)
            data = json.loads(target.read_text(encoding="utf-8"))
            data["capabilities"]["product_contracts.eki_attempt_execute"]["inputs"][0]["type"] = "product_contracts.other"
            target.write_text(json.dumps(data), encoding="utf-8")
            self.assertFalse(check(root)["passed"])

    def test_reordered_flow_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            target = root / RECORD
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / RECORD, target)
            data = json.loads(target.read_text(encoding="utf-8"))
            data["flowOrder"] = list(reversed(data["flowOrder"]))
            target.write_text(json.dumps(data), encoding="utf-8")
            self.assertFalse(check(root)["passed"])

    def test_order_evidence_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            target = root / RECORD
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / RECORD, target)
            data = json.loads(target.read_text(encoding="utf-8"))
            data["orderEvidence"]["order"] = list(reversed(data["orderEvidence"]["order"]))
            target.write_text(json.dumps(data), encoding="utf-8")
            self.assertFalse(check(root)["passed"])

    def test_order_evidence_without_negative_control_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            target = root / RECORD
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / RECORD, target)
            data = json.loads(target.read_text(encoding="utf-8"))
            data["orderEvidence"].pop("negativeResult", None)
            target.write_text(json.dumps(data), encoding="utf-8")
            self.assertFalse(check(root)["passed"])

    def test_missing_read_only_effect_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            target = root / RECORD
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / RECORD, target)
            data = json.loads(target.read_text(encoding="utf-8"))
            data["effects"]["product_contracts.mmi_observation_select"] = "create product_contracts.selection"
            target.write_text(json.dumps(data), encoding="utf-8")
            self.assertFalse(check(root)["passed"])

    def test_missing_http_binding_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            target = root / RECORD
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / RECORD, target)
            data = json.loads(target.read_text(encoding="utf-8"))
            data["bindingImplementations"]["product_contracts.eki_task_submit"] = ["EKITaskSubmit"]
            target.write_text(json.dumps(data), encoding="utf-8")
            self.assertFalse(check(root)["passed"])

    def test_synthetic_receipt_claiming_live_call_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            target = root / RECORD
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / RECORD, target)
            data = json.loads(target.read_text(encoding="utf-8"))
            data["httpBinding"]["liveCallExecuted"] = True
            target.write_text(json.dumps(data), encoding="utf-8")
            self.assertFalse(check(root)["passed"])


if __name__ == "__main__":
    unittest.main()
