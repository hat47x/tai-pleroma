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


if __name__ == "__main__":
    unittest.main()
