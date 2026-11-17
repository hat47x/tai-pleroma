"""Check that EKI refuses a public disclosure profile when private input is required.

So far the P stage has been examined in TEI and SUI. EKI has a different shape: a
relying party states `RequirePrivateInputProof`, and the acceptance path refuses a
proof whose disclosure profile is `public-io`. That is a recipient-side refusal made
by the product itself, not a selection of what to show.

This runs the two tests that pin the refusal and the acceptance, so the asymmetry is
observed rather than read from the source.
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

PACKAGE = "./spikes/verifiable-computation-contract"
PATTERN = "^Test(OrdinaryProofDoesNotSatisfyPrivateInputRequirement|PrivateInputProfileCanSatisfyPrivateInputRequirement)$"
TESTS = (
    "TestOrdinaryProofDoesNotSatisfyPrivateInputRequirement",
    "TestPrivateInputProfileCanSatisfyPrivateInputRequirement",
)
VERDICT = re.compile(r"^\s*---\s+(PASS|FAIL|SKIP):\s+(\S+)", re.M)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--eki-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    repo = Path(args.eki_repo).resolve()
    module = "spikes/verifiable-computation-contract"
    if not (repo / module / "go.mod").exists():
        print(f"not an EKI checkout: {repo}", file=sys.stderr)
        return 1

    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], cwd=repo,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"], cwd=repo,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()
    go_version = subprocess.run(
        ["go", "version"], cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    ).stdout.strip()

    module_dir = repo / module
    completed = subprocess.run(
        ["go", "test", ".", "-run", PATTERN, "-count=1", "-v"],
        cwd=module_dir, capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ},
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    verdicts = {name: verdict for verdict, name in VERDICT.findall(output)}
    failed = [name for name, value in verdicts.items() if value == "FAIL"]
    skipped = [name for name, value in verdicts.items() if value == "SKIP"]
    absent = [name for name in TESTS if name not in verdicts]

    checks = {
        "ekiCommit": head,
        "checkoutClean": dirty == "",
        "goVersion": go_version,
        "package": PACKAGE,
        "module": module,
        "tests": list(TESTS),
        "verdicts": verdicts,
        "failed": failed,
        "skipped": skipped,
        "testsWithoutVerdict": absent,
        "refusalAndAcceptanceBothHold": (
            not failed and not absent
            and all(verdicts.get(name) == "PASS" for name in TESTS)
        ),
        "whatItDecides": "a relying party refuses a public-io proof when private input is required",
        "whatItDoesNotDecide": "which recipient may receive which content",
        "finding": (
            "EKIの`Accept`は、`RequirePrivateInputProof`が真のとき"
            "`DisclosurePublicIO`の証明を拒否し、`DisclosurePrivateInput`の証明を受理する。"
            "これは**受取側が自分で出す拒否**であり、Pの形を持つ。"
            "ただし判定しているのは証明の開示Profileであって、"
            "「この受信者にこの内容を渡してよいか」ではない。"
        ),
    }
    passed = checks["refusalAndAcceptanceBothHold"] and checks["checkoutClean"]

    receipt = {
        "schema": "tai.reference.yic-eki-private-input/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Go, running the EKI contract tests",
        "command": (
            "python integrations/tools/yic_eki_private_input.py "
            f"--eki-repo <EKI checkout at {head[:12]}> "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-eki-private-input-2026-11-17.json"
        ),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Runs two EKI contract tests: one that a public-io proof is refused when private input "
            "is required, one that a private-input proof is accepted. Both are Go tests over a "
            "fixture, and the refusal is made by the relying party's own acceptance check. It does "
            "not show a recipient- or audience-specific disclosure permission, a real proof system, "
            "or any external delivery."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "commit": head[:12],
        "clean": checks["checkoutClean"],
        "verdicts": verdicts,
        "absent": absent,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
