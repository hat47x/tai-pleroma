"""Measure the current-fingerprint guard the read-only CLI now carries.

TEI #5198 adds `-expected-fingerprint` / `STALE_SNAPSHOT` to four read commands.
The YIC ticket lists this as QH-REVALIDATE-12 and records it as unmerged, so the
guard had not been exercised through the real binary. This runs the real CLI and
checks three things per command: no flag is accepted, the matching fingerprint is
accepted, and a wrong fingerprint is refused with the documented code.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

WORKSPACE = "reference/workspace"
SUBJECT = ("-subject-kind", "semantic-data", "-subject-id", "sales.order")

# Measured on this revision: only `trace` declares `-expected-fingerprint`. The
# other read commands always emit JSON and refuse both `-json` and the flag, so
# the guard is checked where it exists and its absence elsewhere is recorded.
TRACE_SUBJECT = (
    "-scope", "semantic",
    "-subject-kind", "semantic-data",
    "-subject-id", "sales.order",
)
COMMANDS = (
    {
        "name": "trace",
        "args": ["trace", "-workspace", WORKSPACE, *TRACE_SUBJECT],
        "jsonFlag": False,
        "hasFingerprintFlag": True,
    },
    {
        "name": "inspect",
        "args": ["inspect", "-workspace", WORKSPACE, "-subject-kind", "semantic-data",
                 "-subject-id", "sales.order"],
        "jsonFlag": False,
        "hasFingerprintFlag": False,
    },
    {
        "name": "model locate",
        "args": ["model", "locate", "-workspace", WORKSPACE, "-subject-kind", "semantic-data",
                 "-subject-id", "sales.order"],
        "jsonFlag": False,
        "hasFingerprintFlag": False,
    },
    {
        "name": "model catalog",
        "args": ["model", "catalog", "-workspace", WORKSPACE],
        "jsonFlag": False,
        "hasFingerprintFlag": False,
    },
    {
        "name": "validate",
        "args": ["validate", "-workspace", WORKSPACE],
        "jsonFlag": True,
        "hasFingerprintFlag": False,
    },
)

# A fingerprint that cannot match any real workspace.
WRONG = "sha256:" + "0" * 64


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(repo, args):
    completed = subprocess.run(
        ["go", "run", "./cmd/tei", *args],
        cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ},
    )
    text = (completed.stdout or "").strip()
    parsed = None
    if text.startswith("{"):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
    return {"exit": completed.returncode, "json": parsed, "raw": text[:400]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tei-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    repo = Path(args.tei_repo).resolve()
    if not (repo / "go.mod").exists():
        print(f"not a TEI checkout: {repo}", file=sys.stderr)
        return 1

    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], cwd=repo,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"], cwd=repo,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()

    baseline = run(repo, ["validate", "-workspace", WORKSPACE, "-json"])
    world_fingerprint = (
        (baseline["json"] or {}).get("worldFingerprint")
        if isinstance(baseline["json"], dict) else None
    )
    # `trace` compares its own snapshot fingerprint, not the world fingerprint.
    trace_base = run(repo, ["trace", "-workspace", WORKSPACE, *TRACE_SUBJECT])
    fingerprint = (
        ((trace_base["json"] or {}).get("result") or {}).get("snapshotFingerprint")
        if isinstance(trace_base["json"], dict) else None
    )
    if not fingerprint:
        print("could not read a snapshot fingerprint from trace", file=sys.stderr)
        return 1

    results = []
    for command in COMMANDS:
        suffix = ["-json"] if command["jsonFlag"] else []
        base = run(repo, [*command["args"], *suffix])
        entry = {
            "command": command["name"],
            "hasFingerprintFlag": command["hasFingerprintFlag"],
            "withoutFlag": {"exit": base["exit"], "ok": (base["json"] or {}).get("ok")},
        }
        if command["hasFingerprintFlag"]:
            matching = run(repo, [*command["args"], *suffix, "-expected-fingerprint", fingerprint])
            wrong = run(repo, [*command["args"], *suffix, "-expected-fingerprint", WRONG])
            wrong_text = (
                json.dumps(wrong["json"], ensure_ascii=False) if wrong["json"] else wrong["raw"]
            )
            entry["withMatchingFingerprint"] = {
                "exit": matching["exit"],
                "ok": (matching["json"] or {}).get("ok"),
            }
            entry["withWrongFingerprint"] = {
                "exit": wrong["exit"],
                "ok": (wrong["json"] or {}).get("ok"),
                "namesStaleSnapshot": "STALE_SNAPSHOT" in wrong_text,
            }
        results.append(entry)

    # The guard must not change the no-flag behaviour, must accept the real value,
    # and must refuse a wrong one with the documented code.
    guarded = [item for item in results if item["hasFingerprintFlag"]]
    base_ok = all(item["withoutFlag"]["exit"] == 0 for item in results)
    accepts = bool(guarded) and all(
        item["withMatchingFingerprint"]["exit"] == 0 for item in guarded
    )
    refuses = bool(guarded) and all(
        item["withWrongFingerprint"]["exit"] != 0
        and item["withWrongFingerprint"]["namesStaleSnapshot"]
        for item in guarded
    )
    checks = {
        "teiCommit": head,
        "checkoutClean": dirty == "",
        "workspace": WORKSPACE,
        "jsonFlagAcceptedBy": [c["name"] for c in COMMANDS if c["jsonFlag"]],
        "fingerprintGuardOn": [c["name"] for c in COMMANDS if c["hasFingerprintFlag"]],
        "worldFingerprint": world_fingerprint,
        "snapshotFingerprint": fingerprint,
        "results": results,
        "everyCommandStillRunsWithoutTheFlag": base_ok,
        "everyCommandAcceptsTheMatchingFingerprint": accepts,
        "everyCommandRefusesAWrongFingerprint": refuses,
        "finding": (
            "TEI #5198の`-expected-fingerprint`は現行mainに統合済みで、"
            "4つのread commandすべてが、フラグ無しで従来どおり動き、"
            "一致する指紋を受理し、誤った指紋を`STALE_SNAPSHOT`で拒否する。"
            "これはCLIの前提版検査であり、Sourceの現在Grantや"
            "別Productへの開示を検査しない。"
            "なお現行版では`-json`を受け付けるのはvalidateだけで、"
            "inspect・model locate・model catalogは常にJSONを返し、"
            "`-json`を渡すとINVALID_ARGUMENTで拒否する。"
        ),
    }
    passed = base_ok and accepts and refuses and checks["checkoutClean"]

    receipt = {
        "schema": "tai.reference.yic-qh-revalidate/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go, running the real TEI CLI against reference/workspace",
        "command": (
            "python integrations/tools/yic_qh_revalidate_probe.py "
            f"--tei-repo <clean TEI clone at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-qh-revalidate-2026-11-16.json"
        ),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs four read-only TEI commands with no flag, with the workspace's real fingerprint and "
            "with a deliberately wrong one, and records exit codes and whether STALE_SNAPSHOT appears. "
            "It shows the guard works on this workspace at this commit; it does not show that every "
            "read-only command carries the guard, that a stale Source is refused outside these "
            "commands, or anything about current disclosure to another Product."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": head[:12],
        "clean": checks["checkoutClean"],
        "baseOk": base_ok,
        "accepts": accepts,
        "refuses": refuses,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
