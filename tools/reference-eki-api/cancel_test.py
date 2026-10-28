import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from cancel import cancel


FIXTURE = {"schema": "eki.task-request/v1", "executor": {"id": "dev.example.transform"}}


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.headers.get("Authorization") != "Bearer valid-token":
            self.send_response(401)
            self.end_headers()
            return
        if self.path == "/v1/tasks":
            self._send(202, {"task_id": "tsk_test", "status": "queued"})
        elif self.path == "/v1/tasks/tsk_test/cancel":
            self._send(202, {"task_id": "tsk_test", "status": "cancellation-requested"})
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == "/v1/tasks/tsk_test/result":
            self.send_response(501)
            self.end_headers()
            return
        if self.path != "/v1/tasks/tsk_test":
            self.send_response(404)
            self.end_headers()
            return
        self._send(200, {"task_id": "tsk_test", "status": "cancelled", "terminal_code": "CANCELLED"})

    def log_message(self, *args):
        pass


class CancelTest(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def test_cancel_reaches_cancelled(self):
        receipt = cancel(self.base_url, "valid-token", FIXTURE, "key-1")
        self.assertTrue(receipt["passed"])
        self.assertTrue(receipt["cancelled"])
        self.assertEqual(receipt["taskStatus"], "cancelled")
        self.assertEqual(receipt["terminalCode"], "CANCELLED")
        self.assertFalse(receipt["taskExecuted"])
        self.assertFalse(receipt["workerResult"])
        self.assertFalse(receipt["resultAvailable"])
        self.assertEqual(receipt["resultStatus"], 501)

    def test_invalid_token_is_rejected(self):
        receipt = cancel(self.base_url, "wrong-token", FIXTURE, "key-1")
        self.assertFalse(receipt["passed"])
        self.assertFalse(receipt["taskSubmitted"])


# --- binding of the answering process (ekipin.py): the Task is not sent on a failed pin ---

import ekipin


class CountingCancelTest(unittest.TestCase):
    def test_unpinned_run_adds_fields_only(self):
        receipt = cancel(self.base_url, "valid-token", FIXTURE, "key-1")
        self.assertEqual(receipt["schema"], "tai.reference.eki-task-cancel/v0")
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["controlBinary"]["binding"], "not-provided")
        self.assertFalse(receipt["pin"]["checked"])

    def test_pinned_run_without_a_matching_process_sends_nothing(self):
        counted = []
        original = Handler.do_POST
        Handler.do_POST = lambda handler: (counted.append(1), original(handler))[1]
        try:
            receipt = cancel(self.base_url, "valid-token", FIXTURE, "key-1", ekipin.Binding(expect="sha256:" + "0" * 64))
        finally:
            Handler.do_POST = original
        self.assertFalse(receipt["passed"])
        self.assertFalse(receipt["taskSubmitted"])
        self.assertEqual(receipt["pin"]["result"], "unavailable")
        self.assertEqual(counted, [])


CountingCancelTest.setUp = CancelTest.setUp
CountingCancelTest.tearDown = CancelTest.tearDown


if __name__ == "__main__":
    unittest.main()
