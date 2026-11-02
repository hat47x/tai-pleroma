import contextlib
import io
import json
import os
import shutil
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock

from probe import _document_digest, build_parser, main, probe
from suipin import Binding


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
                "edges": [{"id": "E-1", "fromId": "I-1", "toId": "I-2", "type": "related"}],
                "islands": [{"id": "I-1", "cardIds": []}],
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
        self.assertEqual(document["documentIslandCount"], 1)
        self.assertEqual(document["documentEdgeCount"], 1)
        self.assertEqual(document["documentEdges"][0]["type"], "related")

    def test_probe_reports_unreachable(self):
        receipt = probe("http://127.0.0.1:1", timeout=1)
        self.assertFalse(receipt["passed"])
        self.assertFalse(receipt["realProductConnected"])
        self.assertIn("reason", receipt)


HEX_A = "a" * 40
HEX_B = "b" * 40
DOC = {
    "version": 1, "id": "doc-1", "title": "SCN-001 demo", "createdAt": "2026-10-26T00:00:00Z",
    "updatedAt": "2026-10-26T00:00:00Z", "transform": {"panX": 0, "panY": 0, "zoom": 1},
    "cards": [], "edges": [], "islands": [],
}
EXISTING_KEYS = {
    "schema", "baseUrl", "readOnly", "realProductConnected", "synthetic", "evidenceKind", "passed",
    "notes", "health", "documentCount", "documentIds", "openapiVersion", "pathCount", "paths",
}
PROXY_VARS = ("http_proxy", "HTTP_PROXY", "https_proxy", "HTTPS_PROXY", "all_proxy", "ALL_PROXY",
              "no_proxy", "NO_PROXY")


class FakeSUI:
    """A fake SUI API that logs every request path. versions: successive GET /version bodies."""

    def __init__(self, versions=None, doc=None, on_docs=None, redirect=None, version_raw=None):
        self.log = []
        self.versions = list(versions) if versions is not None else [{"revision": HEX_A, "runtimeProfile": "evaluation"}]
        self.doc = doc if doc is not None else DOC
        fake = self

        class H(BaseHTTPRequestHandler):
            def do_GET(self):
                fake.log.append(self.path)
                if redirect and self.path in redirect:
                    self.send_response(302)
                    self.send_header("Location", redirect[self.path] + self.path)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                if self.path == "/version":
                    if version_raw is not None:
                        body = version_raw
                    elif not fake.versions:
                        self.send_response(404)
                        self.end_headers()
                        return
                    else:
                        item = fake.versions.pop(0) if len(fake.versions) > 1 else fake.versions[0]
                        body = json.dumps(item).encode("utf-8")
                    return self._send(body)
                if self.path == "/healthz":
                    payload = {"status": "ok"}
                elif self.path == "/openapi.json":
                    payload = {"openapi": "3.1.0", "info": {"title": "x", "version": "0.1.0"}, "paths": {"/healthz": {}}}
                elif self.path == "/docs":
                    payload = [{"id": "doc-1"}]
                elif self.path == "/docs/doc-1":
                    if on_docs:
                        on_docs()
                    payload = fake.doc
                else:
                    self.send_response(404)
                    self.end_headers()
                    return
                self._send(json.dumps(payload).encode("utf-8"))

            def _send(self, body):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


class PinTestCase(unittest.TestCase):
    def fake(self, **kwargs):
        fake = FakeSUI(**kwargs)
        self.addCleanup(fake.close)
        return fake

    def run_probe(self, fake, binding=None, doc_id=None):
        with mock.patch.dict(os.environ, {"no_proxy": "127.0.0.1"}):
            for name in PROXY_VARS[:-2]:
                os.environ.pop(name, None)
            return probe(fake.url, timeout=5, doc_id=doc_id, binding=binding)


class RecordOnlyTest(PinTestCase):
    def test_default_records_and_keeps_existing_fields(self):
        fake = self.fake()
        receipt = self.run_probe(fake, doc_id="doc-1")
        self.assertTrue(receipt["passed"])
        self.assertTrue(EXISTING_KEYS <= set(receipt))
        self.assertEqual(receipt["schema"], "tai.reference.sui-api-probe/v0")
        self.assertNotIn("reason", receipt)
        self.assertFalse(receipt["pin"]["checked"])
        self.assertEqual(receipt["pin"]["result"], "not-checked")
        identity = receipt["serverIdentity"]
        self.assertEqual((identity["status"], identity["revision"], identity["runtimeProfile"]), ("reported", HEX_A, "evaluation"))
        self.assertTrue(identity["revisionKnown"])
        self.assertEqual(identity["openapiInfoVersion"], "0.1.0")
        self.assertIsNone(identity["consistent"])
        self.assertEqual(receipt["checkout"], {"status": "not-provided"})
        self.assertEqual(fake.log, ["/version", "/healthz", "/openapi.json", "/docs", "/docs/doc-1"])
        self.assertEqual(receipt["pin"]["serverRevision"]["actual"], receipt["serverIdentity"]["revision"])

    def test_default_survives_missing_or_broken_version(self):
        for kwargs in ({"versions": []}, {"version_raw": b"not json"}, {"version_raw": b"x" * 200000},
                       {"version_raw": json.dumps({"revision": HEX_A, "runtimeProfile": "p", "pad": "x" * 200000}).encode()},
                       {"version_raw": b"[]"}, {"version_raw": b'{"revision":"a b","runtimeProfile":"p"}'}):
            with self.subTest(kwargs=kwargs):
                receipt = self.run_probe(self.fake(**kwargs))
                self.assertTrue(receipt["passed"])
                self.assertNotIn("reason", receipt)
                self.assertIn(receipt["serverIdentity"]["status"], ("unavailable", "invalid"))
                self.assertEqual(receipt["serverIdentity"]["revision"], "")
                self.assertFalse(receipt["serverIdentity"]["revisionKnown"])

    def test_default_unknown_revision_is_recorded_but_not_known(self):
        receipt = self.run_probe(self.fake(versions=[{"revision": "unknown", "runtimeProfile": "local-dev"}]))
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["serverIdentity"]["revision"], "unknown")
        self.assertFalse(receipt["serverIdentity"]["revisionKnown"])

    def test_server_text_is_not_copied_unless_it_passes_the_pattern(self):
        for bad in ("evil\nline", "a/b", "x" * 65, "", "../../etc"):
            with self.subTest(bad=bad):
                receipt = self.run_probe(self.fake(versions=[{"revision": bad, "runtimeProfile": "p"}]))
                self.assertEqual(receipt["serverIdentity"]["revision"], "")
                if bad:
                    self.assertNotIn(json.dumps(bad)[1:-1], json.dumps(receipt))
        receipt = self.run_probe(self.fake(versions=[{"revision": HEX_A, "runtimeProfile": "p q<script>"}]))
        self.assertEqual(receipt["serverIdentity"]["runtimeProfile"], "")
        self.assertNotIn("script", json.dumps(receipt))

    def test_unreachable_default_reason_is_unchanged(self):
        receipt = probe("http://127.0.0.1:1", timeout=1)
        self.assertFalse(receipt["passed"])
        self.assertIn("reason", receipt)
        self.assertEqual(receipt["serverIdentity"]["status"], "unavailable")


class PinnedRevisionTest(PinTestCase):
    def test_match_orders_version_first_and_last(self):
        fake = self.fake()
        receipt = self.run_probe(fake, Binding(expect_revision=HEX_A))
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["pin"]["result"], "match")
        self.assertTrue(receipt["pin"]["checked"])
        self.assertTrue(receipt["serverIdentity"]["consistent"])
        self.assertEqual(fake.log, ["/version", "/healthz", "/openapi.json", "/docs", "/version"])

    def test_mismatch_sends_nothing_more(self):
        fake = self.fake()
        receipt = self.run_probe(fake, Binding(expect_revision=HEX_B))
        self.assertFalse(receipt["passed"])
        self.assertFalse(receipt["realProductConnected"])
        self.assertEqual(receipt["pin"]["result"], "mismatch")
        self.assertEqual(receipt["reason"], "pin mismatch: server revision differs from the expectation")
        self.assertEqual(fake.log, ["/version"])
        self.assertEqual(receipt["pin"]["serverRevision"], {"status": "mismatch", "expected": HEX_B, "actual": HEX_A})
        self.assertEqual(receipt["serverIdentity"]["revision"], receipt["pin"]["serverRevision"]["actual"])

    def test_prefix_and_case_are_not_a_match(self):
        for expected in (HEX_A[:12], HEX_A.upper(), "a" * 41):
            with self.subTest(expected=expected):
                fake = self.fake()
                receipt = self.run_probe(fake, Binding(expect_revision=expected))
                self.assertFalse(receipt["passed"])
                self.assertEqual(receipt["pin"]["result"], "mismatch")
                self.assertEqual(fake.log, ["/version"])

    def test_switch_during_run_is_caught(self):
        fake = self.fake(versions=[{"revision": HEX_A, "runtimeProfile": "p"}, {"revision": HEX_B, "runtimeProfile": "p"}])
        receipt = self.run_probe(fake, Binding(expect_revision=HEX_A))
        self.assertFalse(receipt["passed"])
        self.assertIs(receipt["serverIdentity"]["consistent"], False)
        self.assertEqual(receipt["pin"]["result"], "mismatch")

    def test_unusable_revisions_fail_closed_and_send_nothing(self):
        cases = [{"revision": "unknown", "runtimeProfile": "p"}, {"revision": "a\nb", "runtimeProfile": "p"},
                 {"revision": "x" * 65, "runtimeProfile": "p"}, {"revision": "", "runtimeProfile": "p"}, {"runtimeProfile": "p"}]
        for body in cases:
            with self.subTest(body=body):
                fake = self.fake(versions=[body])
                receipt = self.run_probe(fake, Binding(expect_revision="unknown" if body.get("revision") == "unknown" else HEX_A))
                self.assertFalse(receipt["passed"])
                self.assertEqual(receipt["pin"]["result"], "unavailable")
                self.assertEqual(fake.log, ["/version"])
                self.assertEqual(receipt["pin"]["serverRevision"]["actual"], "" if body.get("revision") != "unknown" else "unknown")
                self.assertNotIn("a\\nb", json.dumps(receipt))

    def test_missing_version_endpoint_fails_closed(self):
        fake = self.fake(versions=[])
        receipt = self.run_probe(fake, Binding(expect_revision=HEX_A))
        self.assertFalse(receipt["passed"])
        self.assertEqual(receipt["pin"]["result"], "unavailable")
        self.assertEqual(fake.log, ["/version"])

    def test_file_scheme_is_refused_without_opening_anything(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            receipt = probe("file://" + tmp.replace("\\", "/"), binding=Binding(expect_revision=HEX_A))
        self.assertFalse(receipt["passed"])
        self.assertEqual(receipt["pin"]["result"], "unavailable")
        self.assertEqual(receipt["reason"], "pin unavailable: base-url must be http or https")
        self.assertNotIn(tmp.replace("\\", "/"), receipt["reason"])

    def test_proxy_environment_stops_a_pinned_run_only(self):
        fake = self.fake()
        with mock.patch.dict(os.environ):
            for name in PROXY_VARS:  # env names are case-insensitive on Windows: clear first, set after
                os.environ.pop(name, None)
            os.environ["http_proxy"] = "http://127.0.0.1:9"
            receipt = probe(fake.url, timeout=3, binding=Binding(expect_revision=HEX_A))
            self.assertFalse(receipt["passed"])
            self.assertEqual(receipt["pin"]["result"], "unavailable")
            self.assertIn("proxy", receipt["reason"])
            self.assertEqual(fake.log, [])
            os.environ["no_proxy"] = "127.0.0.1"
            self.assertTrue(probe(fake.url, timeout=3, binding=Binding(expect_revision=HEX_A))["passed"])

    def test_pinned_run_refuses_redirects_default_follows(self):
        for path in ("/version", "/healthz"):
            with self.subTest(path=path):
                target = self.fake()
                source = self.fake(redirect={path: target.url})
                receipt = self.run_probe(source, Binding(expect_revision=HEX_A))
                self.assertFalse(receipt["passed"])
                self.assertEqual(target.log, [])
                self.assertNotIn(target.url, receipt.get("reason", ""))
                if path == "/healthz":
                    self.assertEqual(receipt["reason"], "request failed: HTTP 302")
        target = self.fake()
        source = self.fake(redirect={"/version": target.url})
        self.assertTrue(self.run_probe(source)["passed"])
        self.assertEqual(target.log, ["/version"])

    def test_pinned_failure_reason_is_fixed_text(self):
        receipt = probe("http://127.0.0.1:1", timeout=1, binding=Binding(expect_revision=HEX_A))
        self.assertFalse(receipt["passed"])
        self.assertNotIn("Errno", json.dumps(receipt))
        self.assertEqual(receipt["pin"]["result"], "unavailable")


class PinnedDigestTest(PinTestCase):
    def test_digest_match_and_mismatch(self):
        good = _document_digest(DOC)
        receipt = self.run_probe(self.fake(), Binding(expect_digest=good), doc_id="doc-1")
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["pin"]["documentDigest"]["status"], "match")
        bad = good[:-1] + ("0" if good[-1] != "0" else "1")
        receipt = self.run_probe(self.fake(), Binding(expect_digest=bad), doc_id="doc-1")
        self.assertFalse(receipt["passed"])
        self.assertEqual(receipt["pin"]["documentDigest"]["status"], "mismatch")
        self.assertEqual(receipt["documentDigest"], good)
        changed = dict(DOC, title="changed")
        receipt = self.run_probe(self.fake(doc=changed), Binding(expect_digest=good), doc_id="doc-1")
        self.assertFalse(receipt["passed"])

    def test_one_failing_item_fails_the_whole_run(self):
        good = _document_digest(DOC)
        receipt = self.run_probe(self.fake(), Binding(expect_revision=HEX_A, expect_digest=good[:-1] + "0" if not good.endswith("0") else good[:-1] + "1"), doc_id="doc-1")
        self.assertFalse(receipt["passed"])
        self.assertEqual(receipt["pin"]["result"], "mismatch")
        self.assertEqual(receipt["pin"]["serverRevision"]["status"], "match")

    def test_digest_without_doc_id_sends_nothing(self):
        fake = self.fake()
        receipt = self.run_probe(fake, Binding(expect_digest=_document_digest(DOC)))
        self.assertFalse(receipt["passed"])
        self.assertEqual(receipt["pin"]["result"], "unavailable")
        self.assertEqual(fake.log, [])

    def test_digest_only_pin_does_not_need_a_known_revision(self):
        fake = self.fake(versions=[{"revision": "unknown", "runtimeProfile": "p"}])
        receipt = self.run_probe(fake, Binding(expect_digest=_document_digest(DOC)), doc_id="doc-1")
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["pin"]["serverRevision"]["status"], "not-checked")


class ArgumentTest(unittest.TestCase):
    def parse(self, argv, env=None):
        with mock.patch.dict(os.environ, env or {}):
            for name in ("TAI_SUI_EXPECT_REVISION", "TAI_SUI_EXPECT_DOCUMENT_DIGEST"):
                if not env or name not in env:
                    os.environ.pop(name, None)
            return build_parser().parse_args(argv)

    def assertRejected(self, argv, env=None):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            self.parse(argv, env)
        self.assertEqual(caught.exception.code, 2)

    def test_invalid_expectations_exit_2(self):
        self.assertRejected(["--expect-revision", "unknown"])
        self.assertRejected(["--expect-revision", "a b"])
        self.assertRejected(["--expect-revision", "x" * 65])
        self.assertRejected(["--expect-document-digest", "sha256:xyz"])
        self.assertRejected([], {"TAI_SUI_EXPECT_REVISION": "unknown"})
        self.assertRejected([], {"TAI_SUI_EXPECT_DOCUMENT_DIGEST": "nope"})

    def test_flag_beats_env_and_env_is_used(self):
        self.assertEqual(self.parse([], {"TAI_SUI_EXPECT_REVISION": HEX_A}).expect_revision, HEX_A)
        self.assertEqual(self.parse(["--expect-revision", HEX_B], {"TAI_SUI_EXPECT_REVISION": HEX_A}).expect_revision, HEX_B)

    def test_main_needs_doc_id_for_digest_and_prints_no_receipt(self):
        out = io.StringIO()
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as caught:
            main(["--expect-document-digest", _document_digest(DOC)])
        self.assertEqual(caught.exception.code, 2)
        self.assertEqual(out.getvalue(), "")


GIT_AVAILABLE = shutil.which("git") is not None


def run_git(cwd, *args):
    env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    for name in ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE"):
        env.pop(name, None)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "core.autocrlf=false", *args],
                   cwd=cwd, env=env, check=True, capture_output=True)


def make_repo(root):
    os.makedirs(root)
    run_git(root, "init", "-q")
    with open(os.path.join(root, "tracked.txt"), "w", encoding="utf-8", newline="") as handle:
        handle.write("aaaa\n")
    run_git(root, "add", "tracked.txt")
    run_git(root, "commit", "-q", "-m", "one")
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True)
    return out.stdout.strip()


@unittest.skipUnless(GIT_AVAILABLE, "git is not available")
class CheckoutTest(PinTestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(tmp.cleanup)
        self.root = os.path.realpath(os.path.join(tmp.name, "sui"))
        self.head = make_repo(self.root)
        self.versions = [{"revision": self.head, "runtimeProfile": "evaluation"}]

    def write(self, text="bbbb\n", name="tracked.txt"):
        with open(os.path.join(self.root, name), "w", encoding="utf-8", newline="") as handle:
            handle.write(text)

    def go(self, binding, fake=None):
        fake = fake or self.fake(versions=self.versions)
        return fake, self.run_probe(fake, binding, doc_id="doc-1")

    def test_clean_checkout_is_recorded_and_pin_matches(self):
        fake, receipt = self.go(Binding(expect_revision=self.head, checkout=self.root))
        self.assertTrue(receipt["passed"], receipt)
        checkout = receipt["checkout"]
        self.assertEqual((checkout["status"], checkout["head"], checkout["treeStatus"], checkout["trackedChanges"]),
                         ("recorded", self.head, "clean", 0))
        self.assertEqual(receipt["pin"]["checkout"]["status"], "match")
        self.assertEqual(receipt["checkout"]["after"]["head"], self.head)

    def test_record_only_checkout_without_expectation(self):
        fake, receipt = self.go(Binding(checkout=self.root))
        self.assertTrue(receipt["passed"])
        self.assertFalse(receipt["pin"]["checked"])
        self.assertEqual(receipt["checkout"]["head"], self.head)

    def test_git_environment_cannot_redirect_the_queries(self):
        other = os.path.join(os.path.dirname(self.root), "other")
        make_repo(other)
        with mock.patch.dict(os.environ, {"GIT_DIR": os.path.join(other, ".git"), "GIT_INDEX_FILE": os.path.join(other, ".git", "index"),
                                          "GIT_WORK_TREE": other, "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.bare", "GIT_CONFIG_VALUE_0": "true"}):
            fake, receipt = self.go(Binding(expect_revision=self.head, checkout=self.root))
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["checkout"]["head"], self.head)

    def test_head_mismatch_sends_nothing(self):
        fake = self.fake(versions=[{"revision": HEX_A, "runtimeProfile": "p"}])
        _, receipt = self.go(Binding(expect_revision=HEX_A, checkout=self.root), fake)
        self.assertFalse(receipt["passed"])
        self.assertEqual(receipt["pin"]["checkout"]["status"], "mismatch")
        self.assertEqual(fake.log, [])

    def test_tag_expectation_cannot_be_checked_against_a_checkout(self):
        fake = self.fake(versions=[{"revision": "v1.2.3", "runtimeProfile": "p"}])
        _, receipt = self.go(Binding(expect_revision="v1.2.3", checkout=self.root), fake)
        self.assertFalse(receipt["passed"])
        self.assertEqual(receipt["pin"]["checkout"]["status"], "unavailable")
        self.assertEqual(fake.log, [])
        _, receipt = self.go(Binding(expect_revision="v1.2.3"), self.fake(versions=[{"revision": "v1.2.3", "runtimeProfile": "p"}]))
        self.assertTrue(receipt["passed"])

    def test_same_size_same_second_edit_is_a_tracked_change(self):
        self.write("bbbb\n")
        fake, receipt = self.go(Binding(expect_revision=self.head, checkout=self.root))
        self.assertGreaterEqual(receipt["checkout"]["trackedChanges"], 1)
        self.assertFalse(receipt["passed"])
        self.assertEqual(receipt["pin"]["checkout"]["status"], "mismatch")
        self.assertEqual(fake.log, [])

    def test_untracked_files_are_recorded_but_do_not_fail(self):
        self.write("x\n", "new.db")
        fake, receipt = self.go(Binding(expect_revision=self.head, checkout=self.root))
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["checkout"]["untrackedFiles"], 1)

    def test_hidden_flags_close_a_pinned_run(self):
        for flag in ("--assume-unchanged", "--skip-worktree"):
            with self.subTest(flag=flag):
                run_git(self.root, "update-index", flag, "tracked.txt")
                self.write("zzzz\n")
                fake, receipt = self.go(Binding(expect_revision=self.head, checkout=self.root))
                self.assertGreaterEqual(receipt["checkout"]["hiddenFlaggedFiles"], 1)
                self.assertFalse(receipt["passed"])
                self.assertEqual(receipt["pin"]["checkout"]["status"], "unavailable")
                self.assertEqual(fake.log, [])
                _, record = self.go(Binding(checkout=self.root))
                self.assertTrue(record["passed"])
                self.assertGreaterEqual(record["checkout"]["hiddenFlaggedFiles"], 1)
                run_git(self.root, "update-index", "--no-assume-unchanged" if "assume" in flag else "--no-skip-worktree", "tracked.txt")
                self.write("aaaa\n")

    def test_subdirectory_and_missing_git_are_unavailable(self):
        sub = os.path.join(self.root, "sub")
        os.makedirs(sub)
        fake, receipt = self.go(Binding(expect_revision=self.head, checkout=sub))
        self.assertFalse(receipt["passed"])
        self.assertEqual(receipt["checkout"]["status"], "unavailable")
        self.assertEqual(fake.log, [])
        with mock.patch.dict(os.environ, {"PATH": ""}):
            fake, receipt = self.go(Binding(expect_revision=self.head, checkout=self.root))
            self.assertFalse(receipt["passed"])
            self.assertEqual(fake.log, [])
            _, record = self.go(Binding(checkout=self.root))
            self.assertTrue(record["passed"])
            self.assertEqual(record["checkout"]["status"], "unavailable")

    def test_product_writing_a_tracked_file_during_the_run_fails(self):
        fake = self.fake(versions=self.versions, on_docs=lambda: self.write("cccc\n"))
        _, receipt = self.go(Binding(expect_revision=self.head, checkout=self.root), fake)
        self.assertFalse(receipt["passed"])
        self.assertEqual(receipt["pin"]["checkout"]["status"], "mismatch")
        self.assertEqual(receipt["reason"], "pin mismatch: checkout changed during the run")

    def test_untracked_file_created_during_the_run_is_only_recorded(self):
        fake = self.fake(versions=self.versions, on_docs=lambda: self.write("db\n", "run.sqlite"))
        _, receipt = self.go(Binding(expect_revision=self.head, checkout=self.root), fake)
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual((receipt["checkout"]["untrackedFiles"], receipt["checkout"]["after"]["untrackedFiles"]), (0, 1))

    def test_the_checkout_index_is_never_touched(self):
        index = os.path.join(self.root, ".git", "index")
        def snapshot():
            with open(index, "rb") as handle:
                return handle.read(), os.stat(index).st_mtime_ns

        before = snapshot()
        self.write("dddd\n")
        self.go(Binding(expect_revision=self.head, checkout=self.root))
        self.go(Binding(checkout=self.root))
        self.assertEqual(snapshot(), before)

    def test_receipts_carry_no_path_pid_or_environment(self):
        for binding in (Binding(expect_revision=self.head, checkout=self.root), Binding(expect_revision=HEX_B, checkout=self.root)):
            with mock.patch.dict(os.environ, {"GOFLAGS": "-modcacherw=" + self.root}):
                _, receipt = self.go(binding)
            text = json.dumps(receipt)
            for leaked in (self.root, self.root.replace("\\", "\\\\"), os.path.dirname(self.root), "GOFLAGS", "Errno", "tai-sui-index", f'"{os.getpid()}"'):
                self.assertNotIn(leaked, text)


class RealSUITest(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("TAI_SUI_BASE_URL"), "TAI_SUI_BASE_URL is not set: no real SUI to probe")
    def test_real_sui_with_expectations_from_the_environment_only(self):
        binding = Binding(os.environ.get("TAI_SUI_EXPECT_REVISION", ""), os.environ.get("TAI_SUI_EXPECT_DOCUMENT_DIGEST", ""))
        receipt = probe(os.environ["TAI_SUI_BASE_URL"], doc_id=os.environ.get("TAI_SUI_DOC_ID") or None, binding=binding)
        self.assertTrue(receipt["passed"], receipt.get("reason"))


if __name__ == "__main__":
    unittest.main()
