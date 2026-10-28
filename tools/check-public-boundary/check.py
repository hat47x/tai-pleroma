#!/usr/bin/env python3
"""Fail when a public TAI checkout contains private-resource or credential markers.

The patterns are assembled from fragments so this checker does not match its own
source. This is a regression guard, not a replacement for GitHub secret scanning.
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

FORBIDDEN = (
    "tei-platform-" + "private-resources",
    "BEGIN " + "PRIVATE KEY",
    "ghp_",
    "github_pat_",
    "AKIA",
    "/mnt/d/GIT/",
    "D:\\GIT\\hat47x\\tei-platform-private-resources",
)
SKIP = {
    "tools/check-public-boundary/check.py",
    "tools/check-public-boundary/check_test.py",
}


def scan_text(text: str) -> list[str]:
    return [pattern for pattern in FORBIDDEN if pattern in text]


def tracked_files(root: pathlib.Path) -> list[str]:
    output = subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "-z"], stderr=subprocess.STDOUT
    )
    return [item for item in output.decode("utf-8").split("\0") if item]


def scan_repository(root: pathlib.Path) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    for relative in tracked_files(root):
        if relative in SKIP:
            continue
        path = root / relative
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for pattern in scan_text(text):
            findings.append((relative, pattern))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    findings = scan_repository(root)
    for relative, pattern in findings:
        print(f"{relative}: forbidden marker {pattern!r}", file=sys.stderr)
    if findings:
        return 1
    print("public boundary: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
