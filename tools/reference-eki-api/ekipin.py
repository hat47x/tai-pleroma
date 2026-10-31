"""Optional binding of the answering Control Plane process to an expected binary.

Shared by probe.py, submit.py and cancel.py of this tool only. It does not touch the
EKI checkout and starts nothing. Without an expectation it only records what was
given; with --expect-control-sha256 the run is "pinned" and no request is sent
unless the process named by --control-pid

  1. runs an executable whose sha256 equals the expectation (/proc/PID/exe),
  2. listens on the port of --base-url (/proc/net/tcp + /proc/PID/fd),

and the executable digest is the same again after the last request. Linux only:
elsewhere the pinned run is "unavailable" and fails closed. A match shows which
executable answered, not that the EKI is correct or that the Task was processed.
Receipts never carry a path, a PID or an error text of the OS.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
ENV_EXPECT = "TAI_EKI_EXPECT_CONTROL_SHA256"


def _expectation(value: str) -> str:
    value = (value or "").strip().lower()
    if value and not _DIGEST.match(value):
        raise argparse.ArgumentTypeError("expected sha256:<64 hex digits>")
    return value


def _pid(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("PID must be a positive integer") from None
    if number <= 0:
        raise argparse.ArgumentTypeError("PID must be a positive integer")
    return number


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--control-binary", default="", help="path of the Control Plane binary (an operator's claim, not a binding)")
    parser.add_argument("--control-pid", type=_pid, default=0, help="PID of the Control Plane process answering --base-url (Linux)")
    parser.add_argument(
        "--expect-control-sha256",
        type=_expectation,
        default=os.environ.get(ENV_EXPECT, ""),
        help="pin: sha256:<hex> of the executable that must answer (env " + ENV_EXPECT + ")",
    )


@dataclass
class Binding:
    expect: str = ""
    pid: int = 0
    binary: str = ""
    proc: str = "/proc"  # replaced by tests only

    @property
    def pinned(self) -> bool:
        return self.expect != ""

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Binding":
        return cls(expect=args.expect_control_sha256, pid=args.control_pid, binary=args.control_binary)


def sha256_file(path: str) -> str:
    """sha256:<hex> of a file, or "" when it cannot be read."""
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                digest.update(block)
    except OSError:
        return ""
    return "sha256:" + digest.hexdigest()


def process_image_digest(pid: int, proc: str = "/proc") -> str:
    """sha256 of the executable a process runs, or "" (not Linux, gone, not readable)."""
    return sha256_file(os.path.join(proc, str(pid), "exe"))


def parse_proc_net_tcp(text: str) -> list[tuple[str, int, str, str]]:
    """(local address hex, port, state, inode) of every row of /proc/net/tcp."""
    rows = []
    for line in text.splitlines()[1:]:
        fields = line.split()
        if len(fields) < 10 or ":" not in fields[1]:
            continue
        address, _, port = fields[1].partition(":")
        try:
            rows.append((address.upper(), int(port, 16), fields[3].upper(), fields[9]))
        except ValueError:
            continue
    return rows


_LOOPBACK_V4 = {"0100007F", "00000000"}


def listens_on(pid: int, host: str, port: int, proc: str = "/proc") -> bool | None:
    """True/False when the process owns a LISTEN socket on port (IPv4 loopback or any),
    None when that cannot be told (other host, no /proc, no right to read fd).
    An IPv6 listener is not found: that is False, which fails a pinned run closed."""
    if host not in ("127.0.0.1", "localhost") or port <= 0:
        return None
    try:
        with open(os.path.join(proc, "net", "tcp"), encoding="ascii") as handle:
            rows = parse_proc_net_tcp(handle.read())
        fd_dir = os.path.join(proc, str(pid), "fd")
        names = os.listdir(fd_dir)
        sockets = set()
        for name in names:
            try:
                target = os.readlink(os.path.join(fd_dir, name))
            except OSError:
                continue
            if target.startswith("socket:[") and target.endswith("]"):
                sockets.add(target[len("socket:["):-1])
    except OSError:
        return None
    return any(state == "0A" and address in _LOOPBACK_V4 and number == port and inode in sockets for address, number, state, inode in rows)


def _port_of(base_url: str) -> tuple[str, int]:
    try:
        parsed = urllib.parse.urlparse(base_url)
        return parsed.hostname or "", parsed.port or (443 if parsed.scheme == "https" else 80)
    except ValueError:
        return "", 0


def _proxied(base_url: str) -> bool:
    """True when urllib would send a request to base-url through a proxy (http_proxy,
    https_proxy, all_proxy, unless no_proxy names the host). A proxy, not the process
    named by --control-pid, would then answer, so a pinned run refuses to start."""
    host, _ = _port_of(base_url)
    scheme = urllib.parse.urlparse(base_url).scheme or "http"
    proxies = urllib.request.getproxies()
    if not (proxies.get(scheme) or proxies.get("all")):
        return False
    return not urllib.request.proxy_bypass(host)


class Guard:
    """Fills the additive receipt fields and enforces the pin around one run."""

    def __init__(self, binding: Binding | None = None):
        self.binding = binding or Binding()

    def before(self, receipt: dict[str, Any], base_url: str) -> bool:
        """Adds controlBinary/pin to the receipt. False means: send no request."""
        b = self.binding
        file_digest = sha256_file(b.binary) if b.binary else ""
        process_digest = process_image_digest(b.pid, b.proc) if b.pid else ""
        host, port = _port_of(base_url)
        bound = listens_on(b.pid, host, port, b.proc) if b.pid else None
        if b.pid:
            binding, source = ("process" if process_digest else "unavailable"), "pid"
        elif b.binary:
            binding, source = ("file" if file_digest else "unavailable"), "file"
        else:
            binding, source = "not-provided", "not-provided"
        receipt["controlBinary"] = {
            "binding": binding, "sha256": file_digest, "processSha256": process_digest,
            "listenerBound": bound, "source": source,
        }
        receipt["pin"] = {
            "checked": False, "result": "not-checked",
            "controlBinary": {"status": "not-checked", "expected": b.expect, "actual": process_digest},
        }
        notes = receipt["notes"]
        if binding == "file":
            notes.append("--control-binaryは操作者の申告であり、応答したサーバプロセスの束縛ではない。")
        if binding == "process":
            notes.append("プロセスの実行ファイルとLISTENを確認しただけで、そのプロセスがTaskを処理したこと、EKIの正しさ、Authorityは示さない。")
        if not b.pinned:
            return True
        pin = receipt["pin"]
        pin["checked"] = True
        item = pin["controlBinary"]
        notes.append("版固定の一致が示すのは、応答プロセスの実行ファイルのsha256が期待と合ったことだけである。実行前後の2回の確認の間の差し替えは完全には防げない。")
        reason = ""
        if not b.pid:
            result, reason = "unavailable", "pin unavailable: --control-pid is required for a pinned run"
        elif not process_digest:
            result, reason = "unavailable", "pin unavailable: process image could not be read"
        elif process_digest != b.expect:
            result, reason = "mismatch", "pin mismatch: control binary digest differs from the expectation"
        elif b.binary and file_digest != b.expect:
            result, reason = "mismatch", "pin mismatch: --control-binary digest differs from the expectation"
        elif _proxied(base_url):
            result, reason = "unavailable", "pin unavailable: an HTTP proxy is configured for base-url, so the request would not reach the process"
        elif bound is None:
            result, reason = "unavailable", "pin unavailable: listener of the process could not be checked"
        elif not bound:
            result, reason = "mismatch", "pin mismatch: pid does not listen on base-url port"
        else:
            result = "match"
        pin["result"] = result
        item["status"] = result
        if result != "match":
            receipt["passed"] = False
            receipt["reason"] = reason
            return False
        return True

    def after(self, receipt: dict[str, Any]) -> dict[str, Any]:
        """A pinned run fails when the executable is not the same after the last request."""
        b = self.binding
        if not b.pinned or receipt.get("pin", {}).get("result") != "match":
            return receipt
        if process_image_digest(b.pid, b.proc) != b.expect:
            receipt["pin"]["result"] = "mismatch"
            receipt["pin"]["controlBinary"]["status"] = "mismatch"
            receipt["passed"] = False
            reason = "pin mismatch: control process changed during the run"
            receipt["reason"] = receipt["reason"] + "; " + reason if receipt.get("reason") else reason
        return receipt
