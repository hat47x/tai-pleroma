"""Reduce a real-connection pilot report for commit as an evidence record.

The full report stays in the trial directory outside the repository. What gets
committed keeps every structural field, every tool-call record, every digest and
every diagnostic verbatim, and replaces only oversized result bodies with their
digest and byte count. That keeps the record auditable without committing
hundreds of kilobytes of product output.

Usage:
    python reduce_pilot_report.py <in.json> <out.json> [max_body_bytes]
"""

import hashlib
import json
import sys


def reduce(value, limit, key=None):
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if k in ("resultText", "finalText") and isinstance(v, str) and len(v.encode()) > limit:
                digest = hashlib.sha256(v.encode()).hexdigest()
                out[k] = {
                    "_reduced": "body over %d bytes; full report kept in the trial directory" % limit,
                    "bytes": len(v.encode()),
                    "sha256": "sha256:" + digest,
                }
            else:
                out[k] = reduce(v, limit, k)
        return out
    if isinstance(value, list):
        return [reduce(v, limit, key) for v in value]
    return value


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 2048
    with open(sys.argv[1], encoding="utf-8") as fh:
        data = json.load(fh)
    reduced = reduce(data, limit)
    with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as fh:
        json.dump(reduced, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote %s (limit %d bytes)" % (sys.argv[2], limit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
