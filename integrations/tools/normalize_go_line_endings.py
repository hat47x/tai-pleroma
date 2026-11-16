"""Normalise Go files committed with CRLF to LF.

Thirteen Go files were committed with CRLF line endings, so CI's
``test -z "$(gofmt -l .)"`` step fails on main regardless of branch content.
This rewrites only those files' line endings, leaving their Go source byte-for-byte
identical otherwise, and prints the list it changed or would change.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def go_files_with_index_crlf(root: Path):
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--eol"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if completed.returncode != 0:
        raise SystemExit(f"git ls-files failed: {completed.stderr.strip()}")
    found = []
    for line in completed.stdout.splitlines():
        if not line.strip():
            continue
        columns = line.split("\t")
        eol = columns[0]
        path = columns[-1]
        if "i/crlf" in eol and path.endswith(".go"):
            found.append(path)
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="TAI checkout root")
    parser.add_argument("--apply", action="store_true", help="rewrite the files (default: report only)")
    args = parser.parse_args()

    root = Path(args.repo).resolve()
    if not (root / ".git").exists():
        raise SystemExit(f"not a git checkout: {root}")

    targets = go_files_with_index_crlf(root)
    changed = []
    for relative in targets:
        path = root / relative
        raw = path.read_bytes()
        if b"\r\n" not in raw:
            continue
        normalised = raw.replace(b"\r\n", b"\n")
        if normalised == raw:
            continue
        changed.append(relative)
        if args.apply:
            path.write_bytes(normalised)

    print(f"{'rewrote' if args.apply else 'would rewrite'} {len(changed)} of {len(targets)} files")
    for relative in changed:
        print(f"  {relative}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
