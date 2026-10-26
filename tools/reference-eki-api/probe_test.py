import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from probe import probe


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/v1/tasks":
            self.send_response(404)
            self.end_headers()
            return
        if self.headers.get("Authorization") == "Bearer valid-token":
            self.send_response(405)
        else:
            self.send_response(401)
        self.end_headers()

    def log_message(self, *args):
        pass


class ProbeTest(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def test_valid_token_authenticates(self):
        receipt = probe(self.base_url, "valid-token")
        self.assertTrue(receipt["passed"])
        self.assertTrue(receipt["authenticated"])
        self.assertTrue(receipt["readOnly"])
        self.assertFalse(receipt["taskDelegated"])
        self.assertEqual(receipt["tasksStatus"], 405)

    def test_invalid_token_is_rejected(self):
        receipt = probe(self.base_url, "wrong-token")
        self.assertFalse(receipt["passed"])
        self.assertFalse(receipt["authenticated"])


if __name__ == "__main__":
    unittest.main()
