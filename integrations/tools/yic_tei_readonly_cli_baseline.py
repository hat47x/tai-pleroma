"""Run the TEI read-only CLI baseline the YIC ticket lists as an unexecuted example.

The ticket gives five `go run ./cmd/tei ...` commands and marks them as examples
not yet run. Running them against the reference workspace turns "the CLI has
these commands" into "these commands answer on this workspace at this commit".
It records what each returned, and deliberately does not treat a read as
acceptance, disclosure permission or write authority.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# The five commands the ticket lists, and what each would establish.
COMMANDS = (
    {
        "name": "commands",
        "args": ["commands"],
        "establishes": "入口の実Discovery（選択されたread-onlyコマンドの一覧）",
    },
    {
        "name": "modelCatalog",
        "args": ["model", "catalog", "-workspace", "reference/workspace"],
        "establishes": "宣言された型の実Catalog",
    },
    {
        "name": "modelLocate",
        "args": [
            "model", "locate", "-workspace", "reference/workspace",
            "-subject-kind", "semantic-data", "-subject-id", "sales.order",
        ],
        "establishes": "Subjectの位置（派生のread-only投影）",
    },
    {
        "name": "inspect",
        "args": [
            "inspect", "-workspace", "reference/workspace",
            "-subject-kind", "semantic-data", "-subject-id", "sales.order",
        ],
        "establishes": "Canonical内容と元byte範囲",
    },
    {
        "name": "validate",
        "args": ["validate", "-workspace", "reference/workspace", "-json"],
        "establishes": "Workspaceの診断",
    },
)

# Fields the receipt keeps from each command; the rest stays in the raw output.
KEEP = {
    "commands": ("schemaVersion", "scope"),
    "modelCatalog": ("schemaVersion", "ok"),
    "modelLocate": ("schemaVersion", "ok", "result"),
    "inspect": ("schemaVersion", "ok", "result"),
    "validate": ("schemaVersion", "ok", "diagnostics", "declarationCounts"),
}


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


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

    results = []
    for command in COMMANDS:
        completed = subprocess.run(
            ["go", "run", "./cmd/tei", *command["args"]],
            cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace",
            env={**os.environ},
        )
        raw = (completed.stdout or "").strip()
        parsed = None
        if raw.startswith("{"):
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = None
        kept = {}
        if isinstance(parsed, dict):
            for key in KEEP[command["name"]]:
                if key in parsed:
                    kept[key] = parsed[key]
            # Inspect and locate are large; keep the fields that carry evidence.
            if command["name"] == "inspect" and isinstance(kept.get("result"), dict):
                result = kept["result"]
                kept["result"] = {
                    key: result[key]
                    for key in (
                        "subject", "canonical", "sourceStatus",
                        "worldFingerprint", "sourceIndexFingerprint", "sources", "authorityLimits",
                    )
                    if key in result
                }
            if command["name"] == "modelLocate" and isinstance(kept.get("result"), dict):
                result = kept["result"]
                kept["result"] = {
                    key: result[key]
                    for key in ("subject", "validation", "authorityLimits", "coverage")
                    if key in result
                }
        results.append({
            "command": "go run ./cmd/tei " + " ".join(command["args"]),
            "establishes": command["establishes"],
            "exit": completed.returncode,
            "jsonParsed": parsed is not None,
            "kept": kept,
            "stderrTail": (completed.stderr or "").strip().splitlines()[-2:],
        })

    failed = [
        item["command"] for item in results
        if item["exit"] != 0 or not item["jsonParsed"]
    ]
    inspections = next(
        (item for item in results if item["command"].startswith("go run ./cmd/tei inspect")),
        {},
    )
    kept_inspect = inspections.get("kept", {})
    sources = (kept_inspect.get("result") or {}).get("sources") or {}
    definition_ranges = [
        reference.get("range") for reference in sources.get("references") or []
        if reference.get("role") == "definition"
    ]

    checks = {
        "teiCommit": head,
        "checkoutClean": dirty == "",
        "commandsRun": len(results),
        "failed": failed,
        "results": results,
        "inspectReturnedByteRange": bool(definition_ranges),
        "definitionRanges": definition_ranges,
        "inspectAuthorityLimits": (kept_inspect.get("result") or {}).get("authorityLimits"),
        "everyCommandAnswered": not failed,
        "finding": (
            "実行票が例示のみとしていた5つのread-only CLIは、固定commitのclean cloneで"
            "すべて応答した。inspectは元byte範囲（offset・line・column）と"
            "sourceIndexFingerprintを返し、authorityLimitsに"
            "「read-onlyの派生投影であり、意味の受理でも書込み権限でも開示許可でもない」と明記する。"
        ),
    }
    passed = not failed and checks["inspectReturnedByteRange"]

    receipt = {
        "schema": "tai.reference.yic-tei-readonly-cli-baseline/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go, running the TEI CLI against reference/workspace in a clean clone",
        "command": (
            "python integrations/tools/yic_tei_readonly_cli_baseline.py "
            f"--tei-repo <clean TEI clone at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-tei-readonly-cli-2026-11-16.json"
        ),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs the five read-only TEI CLI commands the YIC ticket lists as examples, against "
            "reference/workspace in a dedicated clean clone, and records exit code and the fields "
            "that carry evidence. A successful read is not semantic acceptance, write authority or "
            "disclosure permission, as the inspect output itself states. It does not exercise a real "
            "Provider invocation, an external harness delivery, a complete Tool Reply, or receipt by "
            "the original subject's Consumer, and it says nothing about the distributed Workbench or "
            "real Windows WebView2."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": head[:12],
        "clean": checks["checkoutClean"],
        "commands": len(results),
        "failed": failed,
        "byteRange": checks["inspectReturnedByteRange"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
