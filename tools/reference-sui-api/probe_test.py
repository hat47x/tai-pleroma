import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from probe import probe


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            payload = {"status": "ok"}
        elif self.path == "/openapi.json":
            payload = {"openapi": "3.1.0", "paths": {"/healthz": {}, "/docs/{doc_id}": {}}}
        else:
            self.send_response(404)
            self.end_headers()
            return
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

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

    def test_probe_reads_health_and_openapi(self):
        receipt = probe(self.base_url)
        self.assertTrue(receipt["passed"])
        self.assertTrue(receipt["readOnly"])
        self.assertTrue(receipt["realProductConnected"])
        self.assertEqual(receipt["pathCount"], 2)

    def test_probe_reports_unreachable(self):
        receipt = probe("http://127.0.0.1:1", timeout=1)
        self.assertFalse(receipt["passed"])
        self.assertFalse(receipt["realProductConnected"])
        self.assertIn("reason", receipt)


if __name__ == "__main__":
    unittest.main()
