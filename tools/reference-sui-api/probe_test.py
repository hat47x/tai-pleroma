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
        elif self.path == "/docs":
            payload = [{"id": "doc-1", "updated_at": "2026-10-26T00:00:00Z"}]
        elif self.path == "/docs/doc-1":
            payload = {
                "version": 1,
                "id": "doc-1",
                "title": "SCN-001 demo",
                "createdAt": "2026-10-26T00:00:00Z",
                "updatedAt": "2026-10-26T00:00:00Z",
                "transform": {"panX": 0, "panY": 0, "zoom": 1},
                "cards": [],
                "edges": [],
                "islands": [],
            }
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
        self.assertEqual(receipt["documentCount"], 1)
        self.assertEqual(receipt["documentIds"], ["doc-1"])
        document = probe(self.base_url, doc_id="doc-1")
        self.assertTrue(document["documentRead"])
        self.assertEqual(document["documentTitle"], "SCN-001 demo")
        self.assertEqual(document["documentCardCount"], 0)
        self.assertTrue(document["documentDigest"].startswith("sha256:"))
        self.assertEqual(document["documentCards"], [])

    def test_probe_reports_unreachable(self):
        receipt = probe("http://127.0.0.1:1", timeout=1)
        self.assertFalse(receipt["passed"])
        self.assertFalse(receipt["realProductConnected"])
        self.assertIn("reason", receipt)


if __name__ == "__main__":
    unittest.main()
