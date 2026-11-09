"""Regression checks for robotics audit receipt output paths."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class OutputPathTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        (self.root / "evaluations").mkdir(parents=True)
        shutil.copy2(ROOT / "evaluations/audit-robotics-records.py", self.root / "evaluations")
        for relative in ("evaluations/fixtures/ad", "evaluations/fixtures/robotics", "docs/yi-constellation/schemas"):
            shutil.copytree(ROOT / relative, self.root / relative)

    def run_audit(self, path):
        return subprocess.run(
            [sys.executable, "evaluations/audit-robotics-records.py", "--json", str(path)],
            cwd=self.root, capture_output=True, text=True, encoding="utf-8", check=False,
        )

    def test_relative_receipt_path(self):
        result = self.run_audit(Path("output/relative.json"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads((self.root / "output/relative.json").read_text(encoding="utf-8"))["passed"])
        self.assertIn("record: output/relative.json", result.stdout)

    def test_absolute_path_outside_repo(self):
        target = Path(self.tmp.name) / "outside.json"
        result = self.run_audit(target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(target.read_text(encoding="utf-8"))["passed"])
        self.assertIn(target.as_posix(), result.stdout)

    def test_invalid_fixture_returns_failure_and_writes_receipt(self):
        fixture = self.root / "evaluations/fixtures/ad/incident-event.json"
        record = json.loads(fixture.read_text(encoding="utf-8"))
        record["record_type"] = "invalid"
        fixture.write_text(json.dumps(record), encoding="utf-8")
        target = Path(self.tmp.name) / "failed.json"
        result = self.run_audit(target)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse(json.loads(target.read_text(encoding="utf-8"))["passed"])
        self.assertIn("FAILED:", result.stdout)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
