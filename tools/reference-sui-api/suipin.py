"""Optional binding of "who answered" for the SUI API probe.

Used by probe.py of this tool only (copy it, do not import it from another tool).
Nothing is built here: SUI answers over HTTP. Without an expectation the probe only
records what GET /version reported (revision is the label an operator passed as
SUI_APP_REVISION, not something the server derives from git) and, with
--sui-checkout, the HEAD and the tracked-file state of a checkout. With
--expect-revision and/or --expect-document-digest the run is "pinned":

  1. before any HTTP request: a given --sui-checkout must be clean (tracked files, no
     assume-unchanged/skip-worktree flags) and its HEAD must equal the expectation;
     the URL must be http(s) and no proxy may apply;
  2. GET /version first: the reported revision must equal the expectation, else
     nothing else is sent;
  3. redirects are refused; /version is read again at the end and must report the
     same revision, the checkout must be unchanged, the DocumentV1 digest must match.

A match shows that the answering server reported the expected revision label and the
document bytes matched the expected digest. It does not show that the code is that
commit, that SUI is correct or that anything is authorised. The window between the
two /version reads is not closed. Receipts never carry a path, an OS error text or
server text that did not pass the revision pattern.
"""

from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

ENV_REVISION = "TAI_SUI_EXPECT_REVISION"
ENV_DIGEST = "TAI_SUI_EXPECT_DOCUMENT_DIGEST"
MAX_BODY = 64 * 1024

_REVISION = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_COMMIT = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_RANK = {"not-checked": 0, "match": 1, "unavailable": 2, "mismatch": 3}

# Variables that make git read another repository, index, object store or
# configuration than the checkout directory (a git hook sets some of them).
_GIT_STRIP = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_CONFIG_COUNT", "GIT_CONFIG_PARAMETERS",
    "GIT_NAMESPACE", "GIT_REPLACE_REF_BASE", "GIT_EXTERNAL_DIFF", "GIT_DIFF_OPTS",
    "GIT_CEILING_DIRECTORIES", "GIT_CONFIG", "GIT_ASKPASS",
)


def valid_revision(value: Any) -> str:
    """The value when it is a plain revision label, else "". Server text goes through here."""
    return value if isinstance(value, str) and _REVISION.match(value) else ""


def _expect_revision(value: str) -> str:
    value = (value or "").strip()
    if value and (not _REVISION.match(value) or value == "unknown"):
        raise argparse.ArgumentTypeError("expected 1-64 characters of A-Za-z0-9._- (not 'unknown')")
    return value


def _expect_digest(value: str) -> str:
    value = (value or "").strip().lower()
    if value and not _DIGEST.match(value):
        raise argparse.ArgumentTypeError("expected sha256:<64 hex digits>")
    return value


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--expect-revision", type=_expect_revision, default=os.environ.get(ENV_REVISION, ""),
        help="pin: revision GET /version must report, exact match (env " + ENV_REVISION + ")",
    )
    parser.add_argument(
        "--expect-document-digest", type=_expect_digest, default=os.environ.get(ENV_DIGEST, ""),
        help="pin: sha256:<hex> the DocumentV1 digest must have; needs --doc-id (env " + ENV_DIGEST + ")",
    )
    parser.add_argument(
        "--sui-checkout", default="",
        help="optional SUI checkout (its top level) whose HEAD and tracked state are recorded",
    )


@dataclass
class Binding:
    expect_revision: str = ""
    expect_digest: str = ""
    checkout: str = ""

    @property
    def pinned(self) -> bool:
        return bool(self.expect_revision or self.expect_digest)

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Binding":
        return cls(args.expect_revision, args.expect_document_digest, args.sui_checkout)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):  # type: ignore[override]
        return None


def build_opener(pinned: bool) -> urllib.request.OpenerDirector | None:
    return urllib.request.build_opener(_NoRedirect) if pinned else None


def _proxied(base_url: str) -> bool:
    """True when urllib would send a request to base-url through a proxy."""
    try:
        parsed = urllib.parse.urlparse(base_url)
        host = parsed.hostname or ""
    except ValueError:
        return False
    scheme = parsed.scheme or "http"
    proxies = urllib.request.getproxies()
    if not (proxies.get(scheme) or proxies.get("all")):
        return False
    return not urllib.request.proxy_bypass(host)


def fetch_version(base_url: str, timeout: float, opener: Any = None) -> Any:
    """Parsed GET /version, or None for any failure (never raises, bounded body)."""
    opening = opener.open if opener is not None else urllib.request.urlopen
    try:
        with opening(base_url.rstrip("/") + "/version", timeout=timeout) as response:
            if response.status != 200:
                return None
            body = response.read(MAX_BODY + 1)
        if len(body) > MAX_BODY:
            return None
        return json.loads(body.decode("utf-8"))
    except (OSError, http.client.HTTPException, ValueError):
        return None


def parse_identity(document: Any) -> dict[str, Any]:
    if document is None:
        return {"status": "unavailable", "revision": "", "runtimeProfile": ""}
    if isinstance(document, dict):
        revision = valid_revision(document.get("revision"))
        profile = valid_revision(document.get("runtimeProfile"))
        if revision and profile:
            return {"status": "reported", "revision": revision, "runtimeProfile": profile}
    return {"status": "invalid", "revision": "", "runtimeProfile": ""}


# --- checkout facts -------------------------------------------------------------


def _git(args: list[str], cwd: str, index: str = "") -> bytes | None:
    env = {k: v for k, v in os.environ.items() if k not in _GIT_STRIP}
    env["GIT_TERMINAL_PROMPT"] = "0"
    if index:
        env["GIT_INDEX_FILE"] = index
    command = ["git", "--no-replace-objects", "--no-optional-locks", "-c", "core.fsmonitor=false"] + args
    try:
        done = subprocess.run(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout if done.returncode == 0 else None


def _count(output: bytes) -> int:
    return sum(1 for entry in output.split(b"\0") if entry)


def _hidden(output: bytes) -> int:
    # `ls-files -v`: lower case tag = assume-unchanged, S = skip-worktree.
    return sum(1 for e in output.split(b"\0") if len(e) > 1 and (e[:1] == b"S" or e[:1].islower()))


def checkout_facts(path: str) -> dict[str, Any] | None:
    """HEAD and tracked state of a checkout, or None when it cannot be told.

    The index is copied (with its original mtime, so racy-git still compares content)
    and every index-reading query runs on the copy: the checkout's .git stays untouched."""
    top = _git(["rev-parse", "--show-toplevel"], path)
    if top is None:
        return None
    try:
        if not os.path.samefile(top.decode("utf-8", "replace").strip(), path):
            return None
    except OSError:
        return None
    head = _git(["rev-parse", "HEAD"], path)
    source = _git(["rev-parse", "--git-path", "index"], path)
    if head is None or source is None:
        return None
    head_id = head.decode("ascii", "replace").strip()
    if not _COMMIT.match(head_id):
        return None
    index = os.path.join(path, source.decode("utf-8", "replace").strip())
    try:
        stat = os.stat(index)
        with tempfile.TemporaryDirectory(prefix="tai-sui-index-") as tmp:
            copy = os.path.join(tmp, "index")
            shutil.copyfile(index, copy)
            os.utime(copy, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            changed = _git(["diff", "--name-only", "-z", "HEAD", "--"], path, copy)
            untracked = _git(["ls-files", "--others", "--exclude-standard", "-z"], path, copy)
            flagged = _git(["ls-files", "-v", "-z"], path, copy)
    except OSError:
        return None
    if changed is None or untracked is None or flagged is None:
        return None
    tracked, hidden = _count(changed), _hidden(flagged)
    status = "tracked-changes" if tracked else ("unavailable" if hidden else "clean")
    return {"head": head_id, "treeStatus": status, "trackedChanges": tracked,
            "untrackedFiles": _count(untracked), "hiddenFlaggedFiles": hidden}


# --- guard ------------------------------------------------------------------------


def _item(expected: str = "") -> dict[str, str]:
    return {"status": "not-checked", "expected": expected, "actual": ""}


class Guard:
    """Fills the additive receipt fields (serverIdentity, pin, checkout) and enforces the pin."""

    def __init__(self, binding: Binding | None = None):
        self.binding = binding or Binding()
        self.facts: dict[str, Any] | None = None

    def opener(self):
        return build_opener(self.binding.pinned)

    def _fail(self, receipt: dict[str, Any], names: list[str], status: str, reason: str) -> None:
        pin = receipt["pin"]
        for name in names:
            pin[name]["status"] = status
        if _RANK[status] > _RANK[pin["result"]]:
            pin["result"] = status
        receipt["passed"] = False
        receipt["realProductConnected"] = False
        if not receipt.get("reason"):
            receipt["reason"] = reason

    def before(self, receipt: dict[str, Any], base_url: str, doc_id: str | None) -> bool:
        """Adds serverIdentity/pin/checkout. False means: send no request."""
        b = self.binding
        receipt["serverIdentity"] = {
            "status": "unavailable", "revision": "", "runtimeProfile": "",
            "revisionKnown": False, "openapiInfoVersion": "", "consistent": None,
        }
        receipt["pin"] = {
            "checked": False, "result": "not-checked",
            "serverRevision": _item(b.expect_revision),
            "documentDigest": _item(b.expect_digest),
            "checkout": _item(b.expect_revision if b.checkout else ""),
        }
        receipt["checkout"] = {"status": "not-provided"}
        if b.checkout:
            self.facts = checkout_facts(b.checkout)
            receipt["checkout"] = (
                {"status": "unavailable", "head": "", "treeStatus": "unavailable", "trackedChanges": 0,
                 "untrackedFiles": 0, "hiddenFlaggedFiles": 0}
                if self.facts is None else {"status": "recorded", **self.facts}
            )
            receipt["notes"].append("--sui-checkoutのHEADは記録であり、応答したサーバがそのチェックアウトから起動したことは示さない。")
        if not b.pinned:
            return True
        pin = receipt["pin"]
        pin["checked"], pin["result"] = True, "match"
        receipt["notes"].append(
            "版固定の一致が示すのは、応答サーバが申告したrevisionとDocumentV1のdigestが期待と合ったことだけで、"
            "SUIの正しさ・コードの同一性・認可は示さない。実行前後の/versionの間の差し替えは完全には防げない。"
        )
        names = [n for n, v in (("serverRevision", b.expect_revision), ("documentDigest", b.expect_digest)) if v]
        try:
            scheme = urllib.parse.urlparse(base_url).scheme.lower()
        except ValueError:
            scheme = ""
        if b.expect_digest and not doc_id:
            self._fail(receipt, names, "unavailable", "pin unavailable: --doc-id is required to check the document digest")
        elif scheme not in ("http", "https"):
            self._fail(receipt, names, "unavailable", "pin unavailable: base-url must be http or https")
        elif _proxied(base_url):
            self._fail(receipt, names, "unavailable", "pin unavailable: an HTTP proxy is configured for base-url, so the request would not reach the server")
        elif b.checkout and b.expect_revision:
            facts = self.facts
            if not _COMMIT.match(b.expect_revision):
                self._fail(receipt, ["checkout"], "unavailable", "pin unavailable: checking --sui-checkout needs a 40 or 64 hex commit as the expected revision")
            elif facts is None:
                self._fail(receipt, ["checkout"], "unavailable", "pin unavailable: checkout state could not be determined")
            elif facts["head"] != b.expect_revision:
                pin["checkout"]["actual"] = facts["head"]
                self._fail(receipt, ["checkout"], "mismatch", "pin mismatch: checkout HEAD differs from the expectation")
            elif facts["trackedChanges"] > 0:
                pin["checkout"]["actual"] = facts["head"]
                self._fail(receipt, ["checkout"], "mismatch", "pin mismatch: checkout has tracked changes")
            elif facts["hiddenFlaggedFiles"] > 0:
                pin["checkout"]["actual"] = facts["head"]
                self._fail(receipt, ["checkout"], "unavailable", "pin unavailable: tracked files are marked assume-unchanged or skip-worktree, so edits to them cannot be seen")
            else:
                pin["checkout"]["status"], pin["checkout"]["actual"] = "match", facts["head"]
        return pin["result"] == "match" if pin["checked"] else True

    def read_identity(self, receipt: dict[str, Any], base_url: str, timeout: float) -> bool:
        """GET /version once, before /healthz. False means: a pinned run stops here."""
        b = self.binding
        identity = parse_identity(fetch_version(base_url, timeout, self.opener()))
        known = identity["revision"] not in ("", "unknown")
        receipt["serverIdentity"].update(identity, revisionKnown=known)
        item = receipt["pin"]["serverRevision"]
        item["actual"] = identity["revision"]
        if not b.expect_revision:
            return True
        if identity["status"] != "reported" or not known:
            self._fail(receipt, ["serverRevision"], "unavailable", "pin unavailable: /version could not be read")
        elif identity["revision"] != b.expect_revision:
            self._fail(receipt, ["serverRevision"], "mismatch", "pin mismatch: server revision differs from the expectation")
        else:
            item["status"] = "match"
        return item["status"] == "match"

    def note_openapi(self, receipt: dict[str, Any], openapi: Any) -> None:
        info = openapi.get("info") if isinstance(openapi, dict) else None
        if isinstance(info, dict):
            receipt["serverIdentity"]["openapiInfoVersion"] = valid_revision(info.get("version"))

    def finish(self, receipt: dict[str, Any], base_url: str, timeout: float) -> None:
        """After the last request: digest, same revision again, checkout unchanged."""
        b = self.binding
        pin = receipt["pin"]
        digest = receipt.get("documentDigest")
        pin["documentDigest"]["actual"] = digest if isinstance(digest, str) else ""
        if not b.pinned:
            return
        if b.expect_digest:
            if not pin["documentDigest"]["actual"]:
                self._fail(receipt, ["documentDigest"], "unavailable", "pin unavailable: document digest was not read")
            elif pin["documentDigest"]["actual"] != b.expect_digest:
                self._fail(receipt, ["documentDigest"], "mismatch", "pin mismatch: document digest differs from the expectation")
            else:
                pin["documentDigest"]["status"] = "match"
        if b.expect_revision:
            again = parse_identity(fetch_version(base_url, timeout, self.opener()))
            same = again["status"] == "reported" and again["revision"] == b.expect_revision
            receipt["serverIdentity"]["consistent"] = same
            if not same:
                self._fail(receipt, ["serverRevision"], "mismatch", "pin mismatch: server revision changed during the run")
            if b.checkout and pin["checkout"]["status"] == "match":
                after = checkout_facts(b.checkout)
                receipt["checkout"]["after"] = (
                    {k: after[k] for k in ("head", "trackedChanges", "untrackedFiles", "hiddenFlaggedFiles")}
                    if after else {"status": "unavailable"}
                )
                before = self.facts or {}
                if after is None or any(after[k] != before.get(k) for k in ("head", "trackedChanges", "hiddenFlaggedFiles")):
                    self._fail(receipt, ["checkout"], "mismatch", "pin mismatch: checkout changed during the run")


def error_text(error: BaseException, pinned: bool) -> str:
    """Default runs keep str(error); a pinned run never copies tool or OS error text."""
    if not pinned:
        return str(error)
    if isinstance(error, urllib.error.HTTPError):
        return "request failed: HTTP " + str(error.code)
    if isinstance(error, (OSError, http.client.HTTPException)):
        return "request failed"
    return "response could not be decoded"
