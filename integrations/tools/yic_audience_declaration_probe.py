"""Check what the cross-product handoff does with `disclosure.audience`.

The handoff envelope carries `disclosure.audience`, and the SHO consumer rereads the
ticket it is given. The consumer's own runner records
`hostRecipientAuthorization: 'not-run'`, which is the honest position: it can read the
declaration, not authorise it. This runs the consumer's handoff runner and records
that the broader audience is reread while authority stays unestablished.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

HANDOFF_SCRIPT = "handoff-cross-product.cjs"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sho-repo", required=True)
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    repo = Path(args.sho_repo).resolve()
    script_path = repo / "scripts" / HANDOFF_SCRIPT
    if not script_path.exists():
        candidate = next(repo.rglob(HANDOFF_SCRIPT), None)
        if candidate is None:
            print(f"missing {HANDOFF_SCRIPT} under {repo}", file=sys.stderr)
            return 1
        script_path = candidate
    sui_frontend = Path(args.sui_repo).resolve() / "03_Implement/frontend"
    if not sui_frontend.exists():
        print(f"missing SUI frontend: {sui_frontend}", file=sys.stderr)
        return 1

    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()
    node_version = subprocess.run(
        ["node", "--version"], capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    ).stdout.strip()

    completed = subprocess.run(
        ["node", str(script_path), "--sui-frontend", str(sui_frontend)],
        cwd=script_path.parent, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=1800,
    )
    output = (completed.stdout or "") + (completed.stderr or "")

    # The runner prints an observations array. Read it if it printed JSON.
    observations = []
    parsed_output = None
    try:
        parsed_output = json.loads(completed.stdout or "")
    except json.JSONDecodeError:
        # Fall back to a line-oriented read only if the whole body is not JSON.
        for line in (completed.stdout or "").splitlines():
            stripped = line.strip()
            if not stripped.startswith(("[", "{")):
                continue
            try:
                small = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            if isinstance(small, list):
                observations = small
            elif isinstance(small, dict) and isinstance(small.get("observations"), list):
                observations = small["observations"]
    if isinstance(parsed_output, dict) and isinstance(parsed_output.get("observations"), list):
        observations = parsed_output["observations"]
        receipt_claims = parsed_output.get("claims") or {}
    else:
        receipt_claims = {}

    audience_observation = next(
        (item for item in observations if item.get("id") == "g4-n2-current-audience"),
        None,
    )
    source = script_path.read_text(encoding="utf-8")
    declares_authorization_not_run = "hostRecipientAuthorization: 'not-run'" in source

    checks = {
        "shoCommit": head,
        "checkoutClean": dirty == "",
        "nodeVersion": node_version,
        "suiFrontend": str(sui_frontend),
        "scriptType": "node",
        "runnerExit": completed.returncode,
        "observationsCount": len(observations),
        "outputParsed": parsed_output is not None,
        "receiptClaims": receipt_claims,
        "audienceObservation": audience_observation,
        "declaresAuthorizationNotRun": declares_authorization_not_run,
        "broaderAudienceIsRereadNotAuthorised": bool(
            audience_observation
            and audience_observation.get("ok") is True
            and audience_observation.get("hostRecipientAuthorization") == "not-run"
        ),
        "runnerPassed": completed.returncode == 0,
        "finding": (
            "`yi.handoff.context/v1`の票は`disclosure.audience`を運び、"
            "SHOのConsumerは与えられた票を毎回読み直す。受信者を"
            "['sho-composer']から['sho-composer','other-consumer']へ広げても、"
            "Consumerは**現在の宣言をそのまま読む**。しかし、そのConsumerの"
            "runner自身が`hostRecipientAuthorization: 'not-run'`と記録しており、"
            "**拡大を拒否したことにも、開示を許可したことにもならない**。"
            "これはPの記録（誰に渡すと宣言したか）であり、Pの判定ではない。"
        ),
    }
    passed = checks["runnerPassed"] and checks["broaderAudienceIsRereadNotAuthorised"] and checks["checkoutClean"]

    receipt = {
        "schema": "tai.reference.yic-audience-declaration/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Node, running the SHO cross-product handoff runner",
        "command": (
            "python integrations/tools/yic_audience_declaration_probe.py "
            f"--sho-repo <SHO checkout at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-audience-declaration-2026-11-17.json"
        ),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs SHO's cross-product handoff runner and records how it treats a broadened "
            "`disclosure.audience`: it rereads the current declaration and carries no authority. This "
            "shows the declaration is transported and reread, not that the broadening was refused or "
            "permitted. Host recipient authorization remains not-run, and no external recipient was "
            "contacted."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": head[:12],
        "clean": checks["checkoutClean"],
        "runnerExit": checks["runnerExit"],
        "observations": len(observations),
        "audienceObservation": bool(audience_observation),
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
