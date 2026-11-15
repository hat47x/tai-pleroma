import json
import pathlib
import shutil
import tempfile
import unittest

from check import (REAL_RECORDS, RECORDS, REVIEW_STATUS,
                   SUI_CONSUMER_MAPPING_NEGATIVE, SUI_CONSUMER_MAPPING_ARTIFACT, check)

ROOT = pathlib.Path(__file__).resolve().parents[2]


class CheckTest(unittest.TestCase):
    def test_repository_receipts_are_synthetic(self):
        receipt = check(ROOT)
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["recordCount"], len(RECORDS))
        self.assertEqual(receipt["knownNegativeReceipts"], [SUI_CONSUMER_MAPPING_NEGATIVE])
        self.assertEqual(
            json.loads((ROOT / SUI_CONSUMER_MAPPING_NEGATIVE).read_text(encoding="utf-8"))["result"],
            "FAIL",  # This is a known historical field loss, not a successful SUI consumer.
        )

    def _copy_fixture(self, root):
        for relative in (*RECORDS, *REAL_RECORDS, REVIEW_STATUS, SUI_CONSUMER_MAPPING_ARTIFACT):
            source = ROOT / relative
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(source, destination)

    def test_missing_synthetic_label_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            self._copy_fixture(root)
            target = root / RECORDS[0]
            data = json.loads(target.read_text(encoding="utf-8"))
            data["synthetic"] = False
            target.write_text(json.dumps(data), encoding="utf-8")
            receipt = check(root)
            self.assertFalse(receipt["passed"])
            self.assertTrue(any("synthetic is not true" in error for error in receipt["errors"]))

    def test_conflicting_duplicate_review_id_is_rejected(self):
        # The former dict comprehension silently replaced the accepted row.
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            self._copy_fixture(root)
            path = root / REVIEW_STATUS
            data = json.loads(path.read_text(encoding="utf-8"))
            data["items"].insert(0, {"id": "R-01", "status": "accepted", "evidenceKind": "real"})
            path.write_text(json.dumps(data), encoding="utf-8")
            receipt = check(root)
            self.assertFalse(receipt["passed"])
            self.assertIn("duplicate review item: R-01", receipt["errors"])

    def test_duplicate_json_member_is_rejected_even_if_last_is_safe(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            self._copy_fixture(root)
            path = root / RECORDS[0]
            path.write_text('{"synthetic":false,"synthetic":true,"evidenceKind":"synthetic"}', encoding="utf-8")
            receipt = check(root)
            self.assertFalse(receipt["passed"])
            self.assertTrue(any("duplicate JSON key" in e for e in receipt["errors"]))

    def test_nested_duplicate_json_member_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            self._copy_fixture(root)
            path = root / REVIEW_STATUS
            source = path.read_text(encoding="utf-8")
            path.write_text(source.replace('"status": "pending"', '"status": "accepted", "status": "pending"', 1), encoding="utf-8")
            receipt = check(root)
            self.assertFalse(receipt["passed"])
            self.assertTrue(any("duplicate JSON key" in e for e in receipt["errors"]))

    def test_malformed_review_items_return_failed_receipt_not_exception(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            self._copy_fixture(root)
            path = root / REVIEW_STATUS
            data = json.loads(path.read_text(encoding="utf-8"))
            data["items"] = {"R-01": {"status": "pending"}}
            path.write_text(json.dumps(data), encoding="utf-8")
            receipt = check(root)
            self.assertFalse(receipt["passed"])
            self.assertTrue(any("review items must be an array" in e for e in receipt["errors"]))

    def test_malformed_receipt_returns_failed_receipt_not_exception(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            self._copy_fixture(root)
            (root / RECORDS[0]).write_text("{broken", encoding="utf-8")
            receipt = check(root)
            self.assertFalse(receipt["passed"])
            self.assertTrue(any("invalid JSON file" in e for e in receipt["errors"]))

    def test_no_evidence_review_cannot_have_hidden_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            self._copy_fixture(root)
            path = root / REVIEW_STATUS
            data = json.loads(path.read_text(encoding="utf-8"))
            next(r for r in data["items"] if r["id"] == "R-07")["evidence"] = "unexpected real item"
            path.write_text(json.dumps(data), encoding="utf-8")
            receipt = check(root)
            self.assertFalse(receipt["passed"])
            self.assertTrue(any("R-07 declares evidence" in e for e in receipt["errors"]))


    def test_archived_sui_consumer_loss_cannot_be_relabelled_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            self._copy_fixture(root)
            path = root / SUI_CONSUMER_MAPPING_NEGATIVE
            data = json.loads(path.read_text(encoding="utf-8"))
            data["result"] = "PASS"
            path.write_text(json.dumps(data), encoding="utf-8")
            result = check(root)
            self.assertFalse(result["passed"])
            self.assertEqual(result["knownNegativeReceipts"], [])
            self.assertTrue(any("archived SUI consumer negative" in e for e in result["errors"]))

    def test_archived_sui_consumer_loss_must_match_the_exact_negative(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            self._copy_fixture(root)
            path = root / SUI_CONSUMER_MAPPING_NEGATIVE
            data = json.loads(path.read_text(encoding="utf-8"))
            data["observed"]["documentDropped"] = []
            path.write_text(json.dumps(data), encoding="utf-8")
            result = check(root)
            self.assertFalse(result["passed"])
            self.assertEqual(result["knownNegativeReceipts"], [])

    def test_archived_sui_consumer_loss_is_tied_to_original_artifact_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            self._copy_fixture(root)
            artifact = root / SUI_CONSUMER_MAPPING_ARTIFACT
            artifact.write_bytes(artifact.read_bytes() + b" ")
            result = check(root)
            self.assertFalse(result["passed"])
            self.assertEqual(result["knownNegativeReceipts"], [])

    def test_other_real_receipt_failure_is_not_admitted_as_negative(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            self._copy_fixture(root)
            path = root / REAL_RECORDS[0]
            data = json.loads(path.read_text(encoding="utf-8"))
            data["result"] = "FAIL"
            path.write_text(json.dumps(data), encoding="utf-8")
            result = check(root)
            self.assertFalse(result["passed"])
            self.assertTrue(any("real-execution receipt is not PASS" in e for e in result["errors"]))
            self.assertEqual(result["knownNegativeReceipts"], [SUI_CONSUMER_MAPPING_NEGATIVE])

    def test_real_execution_receipt_claiming_synthetic_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            self._copy_fixture(root)
            target = root / REAL_RECORDS[0]
            data = json.loads(target.read_text(encoding="utf-8"))
            data["synthetic"] = True
            target.write_text(json.dumps(data), encoding="utf-8")
            receipt = check(root)
            self.assertFalse(receipt["passed"])
            self.assertTrue(any("claims synthetic" in error for error in receipt["errors"]))


if __name__ == "__main__":
    unittest.main()
