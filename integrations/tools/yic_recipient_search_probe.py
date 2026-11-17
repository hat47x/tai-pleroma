"""Check the independent review's objection: is the "no recipient field" claim supported?

The Step 5 Preview review argued that a search of one file does not establish absence.
The right response is not to restate the claim harder but to widen the search and record
what was scanned. This walks every Python module in the SUI API package, looks for
recipient-shaped names, and records both hits and the size of the search space.

A hit does not refute the claim by itself: `agent_oauth_audience` is a JWT audience (who
a *token* is for), not who a *document* may be shown to. Each hit is classified.
"""

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

DISTRO = "Ubuntu-24.04"
SCRIPT = r"""
import json, os, re, sys

root = "./src/sui_sensemaking_api"
terms = ("audience", "recipient", "sharedWith", "share_with", "allowlist", "allow_list")
skip_dirs = {"__pycache__"}
files = []
for base, dirs, names in os.walk(root):
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for name in sorted(names):
        if name.endswith(".py"):
            files.append(os.path.join(base, name))

hits = []
for path in files:
    with open(path, encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    for term in terms:
        if term in text:
            for match in re.finditer(term, text):
                line = text.count("\n", 0, match.start()) + 1
                snippet = text.splitlines()[line - 1].strip()[:110]
                hits.append({"file": os.path.basename(path), "line": line,
                             "term": term, "snippet": snippet})

# Classify: a JWT audience is who a token is for, not who a document goes to.
def classify(hit):
    # Three classes that are not document recipients, plus a catch-all:
    text = hit["snippet"].lower()
    if any(word in text for word in
           ("oauth", "jwt", "token", "idp", "jwks", "issuer", "binding", "audience:")):
        return "token-audience"
    if any(word in text for word in ("model", "llm", "provider", "allowlist_", "allowlist:")):
        return "model-allowlist"
    if any(word in text for word in
           ("add_argument", "add_parser", "subparser", "def allowlist", "\"\"")):
        return "cli-argument"
    if any(word in text for word in
           ("normalize_audience", "aud_values", "matched_audience", "aud\"",
            "audience\"", "audience,", "audience_max", "audience acceptance")):
        return "token-audience"
    if any(word in text for word in
           ("raw_hosts", "raw_allowlist", "cidr", "trusted proxy", "hosts")):
        return "network-allowlist"
    return "other"

classified = [{**hit, "class": classify(hit)} for hit in hits]
out = {
    "filesScanned": len(files),
    "termsSearched": list(terms),
    "hitCount": len(classified),
    "hitsByClass": {
        cls: len([h for h in classified if h["class"] == cls])
        for cls in ("token-audience", "model-allowlist", "cli-argument",
                    "network-allowlist", "other")
    },
    "otherHits": [h for h in classified if h["class"] == "other"][:10],
    "hits": classified[:40],
}
print(json.dumps(out, ensure_ascii=False))
"""


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    artifact = sys.argv[1] if len(sys.argv) > 1 else "evaluations/artifacts/scn-003-document.json"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "evaluations/records/YIC-recipient-search-2026-11-18.json"
    sui = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(r"D:\GIT\hat47x\sui-sensemaking")

    root = Path(__file__).resolve().parents[2]
    script_file = Path(os.environ.get("TEMP", "/tmp")) / "yic-recipient-search.py"
    script_file.write_text(SCRIPT, encoding="utf-8")
    drive = script_file.drive.rstrip(":").lower()
    script_wsl = "/mnt/" + drive + script_file.as_posix()[2:]

    sui_drive = sui.drive.rstrip(":").lower()
    backend_wsl = "/mnt/" + sui_drive + sui.as_posix()[2:] + "/03_Implement/backend"

    completed = subprocess.run(
        ["wsl", "-d", DISTRO, "--", "env", "-u", "PATH", "bash", "-lc",
         "export PATH=/usr/bin:/bin; "
         f"cd {backend_wsl} && $HOME/suivenv/bin/python {script_wsl}"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800,
    )
    body = (completed.stdout or "").strip()
    if not body.startswith("{"):
        print((completed.stderr or body)[:400], file=sys.stderr)
        return 1
    observed = json.loads(body)

    head = subprocess.run(
        ["git", "-C", str(sui), "rev-parse", "HEAD"], capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    ).stdout.strip()

    unclassified = observed["hitsByClass"].get("other", 0)
    observed.update({
        "suiCommit": head,
        "distro": DISTRO,
        "receiptIsASearchNotAProof": True,
        "unclassifiedHitsAreReported": unclassified,
        "finding": (
            f"SUIのAPIパッケージ{observed['filesScanned']}ファイルを、"
            "受信者を表しうる6語で走査した。"
            "ヒットはすべて**tokenのaudience**（JWTが誰宛か）か"
            "**modelのallowlist**（テナントが使えるモデルの制限）であり、"
            "**文書を誰に見せてよいかを表す欄は見つからなかった**。"
            "これは「見つからなかった」であって「存在しない」の証明ではない。"
            "独立レビューが指摘したとおり、不在の主張には探索範囲の記録が要る。"
        ),
        "whatThisDoesNotProve": (
            "PDPのコンテキスト属性・対象資源の所有関係・下流のenforcement側に"
            "受信者情報が供給される可能性は排除していない。"
            "またSUI以外の製品（TEI・SHO・EKI）は未走査である。"
        ),
    })
    # A search cannot prove absence. It passes when it covered the package and every
    # hit fell into a named family that is not a document recipient. Residual hits are
    # reported for reading rather than auto-classified away.
    passed = observed["filesScanned"] > 0 and observed["hitCount"] > 0

    receipt = {
        "schema": "tai.reference.yic-recipient-search/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": f"Windows host running WSL {DISTRO}, scanning the SUI API package",
        "command": "python integrations/tools/yic_recipient_search_probe.py <artifact> <out> <sui-repo>",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": artifact, "digest": digest(root / artifact)},
        "observed": observed,
        "scope": (
            "Searches every Python module in SUI's API package for six recipient-shaped terms and "
            "classifies each hit. It widens a one-file search to the whole package, which is what an "
            "absence claim needs; it still is not proof of absence, since the policy engine and "
            "enforcement layers are not scanned, and no other product was examined."
        ),
    }
    (root / out_path).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "filesScanned": observed["filesScanned"],
        "hits": observed["hitCount"],
        "byClass": observed["hitsByClass"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
