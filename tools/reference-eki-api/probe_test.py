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


# --- binding of the answering process (ekipin.py) -------------------------------------
# CI runs this file from tools/reference-eki-api (python -m unittest -v probe_test.py ...),
# which is what makes `import ekipin` work; no EKI, network or fixed port is needed.

import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr
from unittest import mock

import ekipin

LINUX = sys.platform.startswith("linux")
PID = 424242
INODE = "777001"
TCP_HEADER = "  sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode\n"


def tcp_row(index, address, port, state, inode):
    return f"   {index}: {address}:{port:04X} 00000000:0000 {state} 00000000:00000000 00:00000000 00000000  1000        0 {inode} 1 0000000000000000 100 0 0 10 0\n"


def make_proc(root, pid, exe, port, inode=INODE, address="0100007F", state="0A", listen=True):
    """A directory shaped like /proc for one process. The exe entry is a plain file."""
    os.makedirs(os.path.join(root, "net"), exist_ok=True)
    with open(os.path.join(root, "net", "tcp"), "w", encoding="ascii") as handle:
        handle.write(TCP_HEADER + tcp_row(0, "0100007F", 22, "0A", "1") + tcp_row(1, address, port, state, inode))
    os.makedirs(os.path.join(root, str(pid), "fd"), exist_ok=True)
    with open(os.path.join(root, str(pid), "exe"), "wb") as handle:
        handle.write(exe)
    link = os.path.join(root, str(pid), "fd", "3")
    if os.path.lexists(link):
        os.remove(link)
    if listen:
        os.symlink(f"socket:[{inode}]", link)


def digest_of(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


class CountingHandler(BaseHTTPRequestHandler):
    count = 0
    hook = None

    def do_GET(self):
        type(self).count += 1
        if type(self).hook:
            type(self).hook()
        self.send_response(405 if self.headers.get("Authorization") == "Bearer valid-token" else 401)
        self.end_headers()

    def log_message(self, *args):
        pass


class PinnedBase(unittest.TestCase):
    def setUp(self):
        self.handler = type("H", (CountingHandler,), {"count": 0, "hook": None})
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), self.handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_port
        self.base_url = f"http://127.0.0.1:{self.port}"
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.proc = os.path.join(self.tmp.name, "proc")

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def binding(self, expect, pid=PID, binary=""):
        return ekipin.Binding(expect=expect, pid=pid, binary=binary, proc=self.proc)


class UnpinnedRecordTest(PinnedBase):
    def test_no_expectation_behaviour_is_unchanged(self):
        receipt = probe(self.base_url, "valid-token")
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["schema"], "tai.reference.eki-api-probe/v0")
        self.assertEqual(receipt["tasksStatus"], 405)
        self.assertEqual(self.handler.count, 1)
        self.assertEqual(receipt["controlBinary"]["binding"], "not-provided")
        self.assertEqual(receipt["controlBinary"]["source"], "not-provided")
        self.assertFalse(receipt["pin"]["checked"])
        self.assertEqual(receipt["pin"]["result"], "not-checked")

    def test_unreadable_process_is_recorded_not_failed(self):
        receipt = probe(self.base_url, "valid-token", binding=self.binding("", pid=PID))
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["controlBinary"]["binding"], "unavailable")
        self.assertIsNone(receipt["controlBinary"]["listenerBound"])

    def test_file_binding_is_not_called_process_binding(self):
        path = os.path.join(self.tmp.name, "eki-control")
        with open(path, "wb") as handle:
            handle.write(b"one")
        receipt = probe(self.base_url, "valid-token", binding=ekipin.Binding(binary=path))
        self.assertEqual(receipt["controlBinary"]["binding"], "file")
        self.assertEqual(receipt["controlBinary"]["source"], "file")
        self.assertEqual(receipt["controlBinary"]["sha256"], digest_of(b"one"))
        self.assertIsNone(receipt["controlBinary"]["listenerBound"])
        self.assertEqual(receipt["controlBinary"]["processSha256"], "")
        self.assertTrue(any("申告" in note for note in receipt["notes"]))
        self.assertNotIn(self.tmp.name, json.dumps(receipt))
        with open(path, "wb") as handle:
            handle.write(b"two")
        changed = probe(self.base_url, "valid-token", binding=ekipin.Binding(binary=path))
        self.assertEqual(changed["controlBinary"]["sha256"], digest_of(b"two"))
        missing = probe(self.base_url, "valid-token", binding=ekipin.Binding(binary=path + ".none"))
        self.assertEqual(missing["controlBinary"]["binding"], "unavailable")
        self.assertEqual(missing["controlBinary"]["sha256"], "")
        self.assertTrue(missing["passed"])


class PinnedRunTest(PinnedBase):
    EXE = b"control-binary"

    def test_pinned_run_requires_pid_and_sends_no_request(self):
        receipt = probe(self.base_url, "valid-token", binding=ekipin.Binding(expect=digest_of(self.EXE)))
        self.assertFalse(receipt["passed"])
        self.assertEqual(receipt["pin"]["result"], "unavailable")
        self.assertEqual(self.handler.count, 0)

    def test_declared_binary_alone_cannot_pin(self):
        path = os.path.join(self.tmp.name, "eki-control")
        with open(path, "wb") as handle:
            handle.write(self.EXE)
        receipt = probe(self.base_url, "valid-token", binding=ekipin.Binding(expect=digest_of(self.EXE), binary=path))
        self.assertFalse(receipt["passed"])
        self.assertEqual(receipt["pin"]["result"], "unavailable")
        self.assertEqual(self.handler.count, 0)

    def test_unavailable_platform_fails_closed(self):
        # self.proc does not exist: as on Windows or macOS.
        receipt = probe(self.base_url, "valid-token", binding=self.binding(digest_of(self.EXE)))
        self.assertFalse(receipt["passed"])
        self.assertEqual(receipt["pin"]["result"], "unavailable")
        self.assertEqual(self.handler.count, 0)

    def test_expectation_and_arguments_are_validated(self):
        parser = argparse.ArgumentParser()
        ekipin.add_arguments(parser)
        for bad in ("abc", "sha256:12", "sha256:" + "g" * 64):
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                parser.parse_args(["--expect-control-sha256", bad])
            self.assertEqual(raised.exception.code, 2)
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(["--control-pid", "0"])
        upper = parser.parse_args(["--expect-control-sha256", "SHA256:" + "A" * 64])
        self.assertEqual(upper.expect_control_sha256, "sha256:" + "a" * 64)

    @unittest.skipUnless(LINUX, "needs symlinks shaped like /proc/PID/fd")
    def test_match_with_a_process_that_listens(self):
        make_proc(self.proc, PID, self.EXE, self.port)
        receipt = probe(self.base_url, "valid-token", binding=self.binding(digest_of(self.EXE)))
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["pin"]["result"], "match")
        self.assertEqual(receipt["controlBinary"]["binding"], "process")
        self.assertIs(receipt["controlBinary"]["listenerBound"], True)
        self.assertEqual(self.handler.count, 1)
        text = json.dumps(receipt)
        for forbidden in (self.tmp.name, "/proc", str(PID), "valid-token"):
            self.assertNotIn(forbidden, text)

    @unittest.skipUnless(LINUX, "needs symlinks shaped like /proc/PID/fd")
    def test_proxy_environment_fails_a_pinned_run_closed(self):
        # With http_proxy set, urllib would send the request to the proxy, not to --control-pid.
        make_proc(self.proc, PID, self.EXE, self.port)
        proxy = type("P", (CountingHandler,), {"count": 0, "hook": None})
        proxy_server = ThreadingHTTPServer(("127.0.0.1", 0), proxy)
        thread = threading.Thread(target=proxy_server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 5)
        self.addCleanup(proxy_server.server_close)
        self.addCleanup(proxy_server.shutdown)
        environment = {"http_proxy": f"http://127.0.0.1:{proxy_server.server_port}", "HTTP_PROXY": "", "no_proxy": "", "NO_PROXY": ""}
        with mock.patch.dict(os.environ, environment):
            receipt = probe(self.base_url, "valid-token", binding=self.binding(digest_of(self.EXE)))
            self.assertFalse(receipt["passed"], receipt)
            self.assertEqual(receipt["pin"]["result"], "unavailable")
            self.assertIn("proxy", receipt["reason"])
            self.assertEqual((self.handler.count, proxy.count), (0, 0))
            # no_proxy naming the host keeps the request direct, so the pin can match.
            os.environ["no_proxy"] = "127.0.0.1"
            direct = probe(self.base_url, "valid-token", binding=self.binding(digest_of(self.EXE)))
            self.assertTrue(direct["passed"], direct)
            self.assertEqual((self.handler.count, proxy.count), (1, 0))
        # A run without an expectation is not changed by the environment.
        with mock.patch.dict(os.environ, environment):
            plain = probe(self.base_url, "valid-token")
            self.assertEqual(plain["pin"]["result"], "not-checked")

    @unittest.skipUnless(LINUX, "needs symlinks shaped like /proc/PID/fd")
    def test_digest_mismatch_sends_no_request(self):
        make_proc(self.proc, PID, self.EXE, self.port)
        receipt = probe(self.base_url, "valid-token", binding=self.binding(digest_of(b"other")))
        self.assertFalse(receipt["passed"])
        self.assertEqual(receipt["pin"]["result"], "mismatch")
        self.assertEqual(self.handler.count, 0)

    @unittest.skipUnless(LINUX, "needs symlinks shaped like /proc/PID/fd")
    def test_declared_binary_that_differs_is_not_accepted(self):
        make_proc(self.proc, PID, self.EXE, self.port)
        path = os.path.join(self.tmp.name, "claimed")
        with open(path, "wb") as handle:
            handle.write(b"another file")
        receipt = probe(self.base_url, "valid-token", binding=self.binding(digest_of(self.EXE), binary=path))
        self.assertFalse(receipt["passed"])
        self.assertEqual(self.handler.count, 0)

    @unittest.skipUnless(LINUX, "needs symlinks shaped like /proc/PID/fd")
    def test_process_that_listens_elsewhere_or_on_ipv6_fails_closed(self):
        make_proc(self.proc, PID, self.EXE, self.port + 1)
        other_port = probe(self.base_url, "valid-token", binding=self.binding(digest_of(self.EXE)))
        self.assertEqual(other_port["pin"]["result"], "mismatch")
        self.assertIs(other_port["controlBinary"]["listenerBound"], False)
        # An IPv6 (dual stack) listener is in tcp6 only, which is not read: not found, so closed.
        with open(os.path.join(self.proc, "net", "tcp"), "w", encoding="ascii") as handle:
            handle.write(TCP_HEADER)
        with open(os.path.join(self.proc, "net", "tcp6"), "w", encoding="ascii") as handle:
            handle.write(TCP_HEADER + tcp_row(0, "0000000000000000FFFF00000100007F", self.port, "0A", INODE))
        ipv6 = probe(self.base_url, "valid-token", binding=self.binding(digest_of(self.EXE)))
        self.assertFalse(ipv6["passed"])
        self.assertEqual(self.handler.count, 0)

    @unittest.skipUnless(LINUX, "needs symlinks shaped like /proc/PID/fd")
    def test_other_state_or_other_socket_is_not_a_listener(self):
        make_proc(self.proc, PID, self.EXE, self.port, address="0F02000A")  # 10.0.2.15, not the loopback of base-url
        self.assertEqual(probe(self.base_url, "valid-token", binding=self.binding(digest_of(self.EXE)))["pin"]["result"], "mismatch")
        make_proc(self.proc, PID, self.EXE, self.port, state="01")  # ESTABLISHED
        self.assertEqual(probe(self.base_url, "valid-token", binding=self.binding(digest_of(self.EXE)))["pin"]["result"], "mismatch")
        make_proc(self.proc, PID, self.EXE, self.port, inode="999")  # row of a socket the PID does not hold
        os.remove(os.path.join(self.proc, str(PID), "fd", "3"))
        os.symlink("socket:[123]", os.path.join(self.proc, str(PID), "fd", "3"))
        self.assertEqual(probe(self.base_url, "valid-token", binding=self.binding(digest_of(self.EXE)))["pin"]["result"], "mismatch")
        self.assertEqual(self.handler.count, 0)

    def test_fd_directory_that_cannot_be_read_is_unavailable(self):
        make_proc(self.proc, PID, self.EXE, self.port, listen=False)
        os.rmdir(os.path.join(self.proc, str(PID), "fd"))  # as for a PID of another user or namespace
        receipt = probe(self.base_url, "valid-token", binding=self.binding(digest_of(self.EXE)))
        self.assertFalse(receipt["passed"])
        self.assertEqual(receipt["pin"]["result"], "unavailable")
        self.assertEqual(self.handler.count, 0)

    @unittest.skipUnless(LINUX, "needs symlinks shaped like /proc/PID/fd")
    def test_process_replaced_or_gone_during_the_run_fails(self):
        make_proc(self.proc, PID, self.EXE, self.port)
        exe = os.path.join(self.proc, str(PID), "exe")

        def replace():
            with open(exe, "wb") as handle:
                handle.write(b"swapped")

        self.handler.hook = replace
        replaced = probe(self.base_url, "valid-token", binding=self.binding(digest_of(self.EXE)))
        self.assertFalse(replaced["passed"])
        self.assertEqual(replaced["pin"]["result"], "mismatch")
        self.assertIn("changed during the run", replaced["reason"])

        make_proc(self.proc, PID, self.EXE, self.port)
        self.handler.hook = lambda: os.remove(exe)
        gone = probe(self.base_url, "valid-token", binding=self.binding(digest_of(self.EXE)))
        self.assertFalse(gone["passed"])
        self.assertIn("changed during the run", gone["reason"])

    def test_proc_net_tcp_parsing(self):
        text = TCP_HEADER + tcp_row(0, "0100007F", 8080, "0A", "55") + tcp_row(1, "0100007F", 8081, "01", "56") + "garbage\n"
        self.assertEqual(
            ekipin.parse_proc_net_tcp(text),
            [("0100007F", 8080, "0A", "55"), ("0100007F", 8081, "01", "56")],
        )
        self.assertIsNone(ekipin.listens_on(1, "192.0.2.1", 80, self.proc))
        self.assertIsNone(ekipin.listens_on(1, "::1", 80, self.proc))


@unittest.skipUnless(LINUX, "reads the real /proc")
class RealProcessTest(PinnedBase):
    CHILD = (
        "from http.server import BaseHTTPRequestHandler, HTTPServer\n"
        "class H(BaseHTTPRequestHandler):\n"
        "    def do_GET(self):\n"
        "        self.send_response(405 if self.headers.get('Authorization') == 'Bearer valid-token' else 401)\n"
        "        self.end_headers()\n"
        "    def log_message(self, *a): pass\n"
        "s = HTTPServer(('127.0.0.1', 0), H)\n"
        "print(s.server_port, flush=True)\n"
        "s.serve_forever()\n"
    )

    def test_child_process_is_bound_by_its_executable_and_port(self):
        child = subprocess.Popen([sys.executable, "-c", self.CHILD], stdout=subprocess.PIPE, text=True)

        def reap():
            child.kill()
            child.wait(timeout=10)
            child.stdout.close()

        self.addCleanup(reap)
        port = int(child.stdout.readline())  # printed after bind+listen: no fixed port, no sleep
        base_url = f"http://127.0.0.1:{port}"
        with open(os.path.realpath(sys.executable), "rb") as handle:
            expected = digest_of(handle.read())
        receipt = probe(base_url, "valid-token", binding=ekipin.Binding(expect=expected, pid=child.pid))
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["pin"]["result"], "match")
        self.assertIs(receipt["controlBinary"]["listenerBound"], True)
        wrong = probe(base_url, "valid-token", binding=ekipin.Binding(expect="sha256:" + "0" * 64, pid=child.pid))
        self.assertEqual(wrong["pin"]["result"], "mismatch")
        # The parent (this test) does not listen on the child's port.
        parent = probe(base_url, "valid-token", binding=ekipin.Binding(expect=expected, pid=os.getpid()))
        self.assertFalse(parent["passed"])
        self.assertIs(parent["controlBinary"]["listenerBound"], False)


if __name__ == "__main__":
    unittest.main()
