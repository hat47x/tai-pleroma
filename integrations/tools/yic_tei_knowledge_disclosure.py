"""Measure whether TEI can answer "may this be disclosed" as a Product decision.

The I/R/P/T/C/H table stopped at R because none of the five cards named a
recipient. `knowledge-context -disclose` is the closest thing the Product has to a
P step, so this runs it three ways: with one section, with every section, and with
a name it does not support. What it establishes is narrower than a disclosure
grant, and the command's own `authorityLimits` says so; this records that too.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

WORKSPACE = "reference/workspace"
SUBJECT = ("-subject-kind", "semantic-data", "-subject-id", "sales.order")
SECTIONS = ["data-design", "definition", "dependencies", "source"]

# The limits the command declares that bear on whether this is a P step at all.
RELEVANT_LIMITS = (
    "selective-disclosure-is-not-access-control-or-redaction",
    "selective-disclosure-is-derived-not-authority",
    "omitted-knowledge-is-not-negative-evidence",
    "disclosure-fingerprint-is-cache-identity-not-semantic-proof",
)


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
    return {"exit": completed.returncode, "json": parsed}


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

    one = run(repo, ["knowledge-context", "-workspace", WORKSPACE, *SUBJECT,
                     "-disclose", "definition"])
    every = run(repo, ["knowledge-context", "-workspace", WORKSPACE, *SUBJECT,
                       "-disclose", ",".join(SECTIONS)])
    bad = run(repo, ["knowledge-context", "-workspace", WORKSPACE, *SUBJECT,
                     "-disclose", "unknown"])

    one_result = (one["json"] or {}).get("result") or {}
    every_result = (every["json"] or {}).get("result") or {}
    bad_error = (bad["json"] or {}).get("error") or {}
    limits = one_result.get("authorityLimits") or []

    checks = {
        "teiCommit": head,
        "checkoutClean": dirty == "",
        "workspace": WORKSPACE,
        "oneSection": {
            "exit": one["exit"],
            "ok": (one["json"] or {}).get("ok"),
            "mode": (one["json"] or {}).get("mode"),
            "status": one_result.get("status"),
            "selected": one_result.get("selectedSections"),
            "disclosed": one_result.get("disclosedSections"),
            "omitted": one_result.get("omittedAvailableSections"),
            "available": one_result.get("availableSections"),
            "fingerprint": one_result.get("fingerprint"),
        },
        "everySection": {
            "exit": every["exit"],
            "ok": (every["json"] or {}).get("ok"),
            "status": every_result.get("status"),
            "disclosed": every_result.get("disclosedSections"),
            "omitted": every_result.get("omittedAvailableSections"),
        },
        "unknownSection": {
            "exit": bad["exit"],
            "ok": (bad["json"] or {}).get("ok"),
            "code": bad_error.get("code"),
            "messageListsSupported": all(section in (bad_error.get("message") or "")
                                         for section in SECTIONS),
        },
        "authorityLimits": limits,
        "declaredLimitsThatBlockAPReading": [
            limit for limit in RELEVANT_LIMITS if limit in limits
        ],
        "declaresItIsNotAccessControl": (
            "selective-disclosure-is-not-access-control-or-redaction" in limits
        ),
        "selectiveDisclosureWorks": (
            one["exit"] == 0
            and (one["json"] or {}).get("ok") is True
            and one_result.get("disclosedSections") == ["definition"]
            and set(one_result.get("omittedAvailableSections") or []) == set(SECTIONS) - {"definition"}
        ),
        "allSectionsDiscloseEverything": (
            every["exit"] == 0
            and set(every_result.get("disclosedSections") or []) == set(SECTIONS)
            and not (every_result.get("omittedAvailableSections") or [])
        ),
        "unknownSectionIsRefused": (
            bad["exit"] != 0 and bad_error.get("code") == "KNOWLEDGE_BUILD_FAILED"
        ),
        "finding": (
            "TEIの`knowledge-context -disclose`は、Subjectに対して開示するSectionを選ばせ、"
            "選んだものだけを`disclosedSections`に、残りを`omittedAvailableSections`に分ける。"
            "これは**P（開示）の形を作れる**が、Pの判定主体ではない。"
            "コマンド自身が`selective-disclosure-is-not-access-control-or-redaction`と"
            "`selective-disclosure-is-derived-not-authority`を返しており、"
            "受信者・Audience別の許可判定ではない。"
        ),
    }
    passed = (
        checks["selectiveDisclosureWorks"]
        and checks["allSectionsDiscloseEverything"]
        and checks["unknownSectionIsRefused"]
        and checks["checkoutClean"]
    )

    receipt = {
        "schema": "tai.reference.yic-tei-knowledge-disclosure/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go, running the real TEI CLI against reference/workspace",
        "command": (
            "python integrations/tools/yic_tei_knowledge_disclosure.py "
            f"--tei-repo <clean TEI clone at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-tei-knowledge-disclosure-2026-11-16.json"
        ),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs TEI's knowledge-context disclosure with one section, with all four, and with an "
            "unsupported name, and records what each returns. It shows the Product can select and "
            "report disclosed versus omitted sections for a subject. It does **not** show a recipient "
            "or audience-specific permission decision: the command itself declares it is not access "
            "control or redaction, and that selective disclosure is derived rather than authority. No "
            "external recipient was contacted and no Owner acceptance was sought."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": head[:12],
        "clean": checks["checkoutClean"],
        "selective": checks["selectiveDisclosureWorks"],
        "allSections": checks["allSectionsDiscloseEverything"],
        "refusesUnknown": checks["unknownSectionIsRefused"],
        "notAccessControl": checks["declaresItIsNotAccessControl"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
