"""Synthetic replay guards; actual SUI product execution is a separate qualification."""

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import consumer_mapping_coverage_check as replay


class ConsumerMappingReplayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sui = self.root / "sui"
        self.modules = self.sui / "03_Implement/backend/src/sui_sensemaking_api"
        self.modules.mkdir(parents=True)
        for name in ("documentv1_projection.py", "models.py"):
            (self.modules / name).write_text("# fixture " + name + "\n", encoding="utf-8")
        self.artifact = self.root / "artifact.json"
        self.artifact.write_text(json.dumps({
            "document": {
                "document": {"id": "doc", "readingOrder": ["card-1", "card-2"]},
                "cards": [
                    {"id": "card-1", "text": "a", "x": 0, "y": 0},
                    {"id": "card-2", "text": "b", "x": 1, "y": 1, "sources": ["src"]},
                ],
                "islands": [], "edges": [], "affiliations": [],
            }
        }), encoding="utf-8")
        self.out = self.root / "replay.json"

    def args(self, output=None):
        return ["--sui-repo", str(self.sui), "--artifact", str(self.artifact),
                "--out", str(output or self.out)]

    def response(self, reading_order=None, cards=None):
        return {
            "payloadTopLevel": ["id", "cards", "readingOrder", "islands", "edges", "affiliations"],
            "payloadKeys": {
                "cards": ["id", "sources", "text", "x", "y"],
                "islands": [], "edges": [], "affiliations": [],
            },
            "modelTopLevel": ["id", "cards", "readingOrder", "islands", "edges", "affiliations"],
            "modelKeys": {
                "cards": cards if cards is not None else ["id", "sources", "text", "x", "y"],
                "islands": [], "edges": [], "affiliations": [],
            },
            "modelAffiliations": 0,
            "modelReadingOrder": len(reading_order if reading_order is not None else
                                     ["card-1", "card-2"]),
            "modelReadingOrderValues": reading_order if reading_order is not None else
                                       ["card-1", "card-2"],
            "valid": True,
        }

    def execute(self, response=None, output=None):
        result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(response or self.response()))
        with patch.object(replay.subprocess, "run", return_value=result):
            return replay.main(self.args(output))

    def test_archived_negative_receipt_is_never_an_output(self):
        with patch.object(replay.subprocess, "run") as runner:
            self.assertEqual(replay.main(self.args(replay.HISTORICAL_RECEIPT)), 2)
            runner.assert_not_called()

    def test_existing_receipt_cannot_be_overwritten(self):
        self.out.write_text("ORIGINAL", encoding="utf-8")
        with patch.object(replay.subprocess, "run") as runner:
            self.assertEqual(replay.main(self.args()), 2)
            runner.assert_not_called()
        self.assertEqual(self.out.read_text(encoding="utf-8"), "ORIGINAL")

    def test_new_attempt_records_source_digests_and_full_card_keys(self):
        self.assertEqual(replay.element_keys([
            {"id": "a"}, {"id": "b", "sources": ["source-2"]}]), ["id", "sources"])
        self.assertEqual(self.execute(), 0)
        result = json.loads(self.out.read_text(encoding="utf-8"))
        self.assertEqual(result["result"], "PASS")
        self.assertTrue(result["observed"]["readingOrderKept"])
        self.assertEqual(result["observed"]["collections"]["cards"]["sourceKeys"],
                         ["id", "sources", "text", "x", "y"])
        self.assertEqual(result["observed"]["collections"]["cards"]["dropped"], [])
        self.assertEqual(result["artifact"]["digest"], replay.digest(self.artifact))
        self.assertEqual(result["replayProvenance"]["suiSourceModules"],
                         replay.consumer_source_digests(self.modules.parent))
        self.assertNotEqual(self.out.resolve(), replay.HISTORICAL_RECEIPT.resolve())
        original = self.out.read_bytes()
        with patch.object(replay.subprocess, "run") as runner:
            self.assertEqual(replay.main(self.args()), 2)
            runner.assert_not_called()
        self.assertEqual(self.out.read_bytes(), original)

    def test_reordered_reading_order_is_not_a_success_with_matching_count(self):
        self.assertEqual(self.execute(self.response(["card-2", "card-1"])), 1)
        receipt = json.loads(self.out.read_text(encoding="utf-8"))
        self.assertEqual(receipt["result"], "FAIL")
        self.assertEqual(receipt["observed"]["modelReadingOrder"], 2)
        self.assertFalse(receipt["observed"]["readingOrderKept"])

    def test_optional_field_only_on_later_card_must_survive(self):
        self.assertEqual(self.execute(self.response(cards=["id", "text", "x", "y"])), 1)
        receipt = json.loads(self.out.read_text(encoding="utf-8"))
        self.assertEqual(receipt["result"], "FAIL")
        self.assertEqual(receipt["observed"]["collectionsWithLoss"], ["cards"])
        self.assertEqual(receipt["observed"]["collections"]["cards"]["dropped"], ["sources"])

    def test_model_loss_after_payload_mapped_is_still_detected(self):
        observed = self.response(cards=["id", "text", "x", "y"])
        self.assertIn("sources", observed["payloadKeys"]["cards"])
        self.assertNotIn("sources", observed["modelKeys"]["cards"])
        self.assertEqual(self.execute(observed), 1)
        receipt = json.loads(self.out.read_text(encoding="utf-8"))
        self.assertEqual(receipt["result"], "FAIL")
        self.assertEqual(receipt["observed"]["collections"]["cards"]["payloadKeys"],
                         ["id", "sources", "text", "x", "y"])
        self.assertEqual(receipt["observed"]["collections"]["cards"]["dropped"], ["sources"])

    def test_source_change_during_consumer_call_prevents_receipt(self):
        def changed_source(*args, **kwargs):
            (self.modules / "models.py").write_text("# changed\n", encoding="utf-8")
            return subprocess.CompletedProcess(
                args=[], returncode=0, stdout=json.dumps(self.response()))
        with patch.object(replay.subprocess, "run", side_effect=changed_source):
            self.assertEqual(replay.main(self.args()), 1)
        self.assertFalse(self.out.exists())

    def test_artifact_change_during_consumer_call_prevents_receipt(self):
        def changed_artifact(*args, **kwargs):
            self.artifact.write_bytes(self.artifact.read_bytes() + b" ")
            return subprocess.CompletedProcess(
                args=[], returncode=0, stdout=json.dumps(self.response()))
        with patch.object(replay.subprocess, "run", side_effect=changed_artifact):
            self.assertEqual(replay.main(self.args()), 1)
        self.assertFalse(self.out.exists())


if __name__ == "__main__":
    unittest.main()
