import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from submit import submit


FIXTURE = {"schema": "eki.task-request/v1", "executor": {"id": "dev.example.transform"}}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/v1/tasks":
            self.send_response(404)
            self.end_headers()
            return
        if self.headers.get("Authorization") != "Bearer valid-token":
            self.send_response(401)
            self.end_headers()
            return
        if not self.headers.get("Idempotency-Key"):
            self.send_response(400)
            self.end_headers()
            return
        body = json.dumps({"task_id": "tsk_test", "status": "queued"}).encode()
        self.send_response(202)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/v1/tasks/tsk_test":
            self.send_response(404)
            self.end_headers()
            return
        body = json.dumps({"task_id": "tsk_test", "status": "queued"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class SubmitTest(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def test_submit_reads_queued_status(self):
        receipt = submit(self.base_url, "valid-token", FIXTURE, "key-1")
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["taskId"], "tsk_test")
        self.assertEqual(receipt["taskStatus"], "queued")
        self.assertTrue(receipt["idempotent"])
        self.assertFalse(receipt["taskExecuted"])
        self.assertFalse(receipt["workerResult"])
        self.assertFalse(receipt["readOnly"])

    def test_invalid_token_is_rejected(self):
        receipt = submit(self.base_url, "wrong-token", FIXTURE, "key-1")
        self.assertFalse(receipt["passed"])
        self.assertFalse(receipt["taskSubmitted"])


# --- binding of the answering process (ekipin.py): the Task is not sent on a failed pin ---

import ekipin


class CountingSubmitTest(unittest.TestCase):
    def test_unpinned_run_adds_fields_only(self):
        receipt = submit(self.base_url, "valid-token", FIXTURE, "key-1")
        self.assertEqual(receipt["schema"], "tai.reference.eki-task-submit/v0")
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["controlBinary"]["binding"], "not-provided")
        self.assertFalse(receipt["pin"]["checked"])

    def test_pinned_run_without_a_matching_process_sends_nothing(self):
        counted = []
        original = Handler.do_POST
        Handler.do_POST = lambda handler: (counted.append(1), original(handler))[1]
        try:
            expect = "sha256:" + "0" * 64
            for binding in (ekipin.Binding(expect=expect), ekipin.Binding(expect=expect, pid=424242, proc="/nonexistent-proc")):
                receipt = submit(self.base_url, "valid-token", FIXTURE, "key-1", binding)
                self.assertFalse(receipt["passed"])
                self.assertFalse(receipt["taskSubmitted"])
                self.assertEqual(receipt["pin"]["result"], "unavailable")
        finally:
            Handler.do_POST = original
        self.assertEqual(counted, [])


CountingSubmitTest.setUp = SubmitTest.setUp
CountingSubmitTest.tearDown = SubmitTest.tearDown


if __name__ == "__main__":
    unittest.main()
