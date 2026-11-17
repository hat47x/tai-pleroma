"""Ask whether the Producer's receipt review looks at the audience at all.

`reviewHandoffReceipt` decides whether a Consumer's receipt may be accepted for a
Producer's ticket. Every round so far examined the ticket and the consumer. This checks
the review itself: what it compares, and whether the declared audience participates.

It bundles the module with the project's esbuild and drives it with receipts that differ
only in the audience the Consumer carried forward.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

FRONTEND = Path(r"D:\GIT\hat47x\sui-sensemaking\03_Implement\frontend")
ENTRY = "src/export/handoff_receipt_review.ts"

DRIVER = r"""
const m = require(process.env.BUNDLE);
const TICKET = "sha256:" + "a".repeat(64);
const R = "sha256:" + "b".repeat(64);
const D = "sha256:" + "c".repeat(64);

const ALL_CLAIMS = {
  independentReread: true,
  payloadMatchesTicket: true,
  conversationHistoryIncluded: false,
  authorityCarried: false,
  sourceRevisionCurrent: false,
  originalSourcesRead: false,
  meaningAccepted: false,
  writerInvoked: false,
  externalSourcesAcquired: false,
  externalDisclosure: false,
  sessionInheritedAuthority: false,
};

function receipt(audience) {
  return {
    schema: "yi.handoff.receipt/v1",
    status: "received",
    receivedAt: "2026-11-18T00:00:00.000Z",
    consumer: { product: "sho-composer", session: "s-1" },
    ticket: {
      sha256: TICKET,
      disclosure: { scope: "synthetic-only", audience, purpose: "synthetic" },
    },
    payload: { sha256: D, byteLength: 10, observedByteLength: 10 },
    checks: {},
    carriedForward: {},
    claims: ALL_CLAIMS,
  };
}

function review(name, audience) {
  try {
    const r = m.reviewHandoffReceipt(receipt(audience), TICKET);
    return { case: name, audience, status: r.status, reason: r.reason };
  } catch (error) {
    return { case: name, audience, threw: (error && error.code) || (error && error.name) };
  }
}

const results = [
  review("declared-recipient", ["sho-composer"]),
  review("unrelated-recipient", ["someone-else"]),
  review("empty-audience", []),
];
console.log(JSON.stringify({ exports: Object.keys(m), results }));
"""


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(cmd, cwd, env=None):
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
        errors="replace", env={**os.environ, **(env or {})}, timeout=1800,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]

    scratch = Path(os.environ.get("TEMP", "/tmp")) / "yic-receipt-review"
    scratch.mkdir(exist_ok=True)
    bundle = scratch / "review.bundle.cjs"
    driver = scratch / "driver.cjs"

    built = run(
        [str(FRONTEND / "node_modules" / ".bin" / "esbuild.cmd"),
         str(FRONTEND / ENTRY), "--bundle", "--platform=node",
         "--format=cjs", f"--outfile={bundle}"],
        cwd=FRONTEND,
    )
    if not bundle.exists():
        print((built.stderr or "")[:400], file=sys.stderr)
        return 1

    driver.write_text(DRIVER, encoding="utf-8")
    node = run(["node", str(driver)], cwd=FRONTEND, env={"BUNDLE": str(bundle)})
    body = (node.stdout or "").strip()
    if not body.startswith("{"):
        print((node.stderr or body)[:500], file=sys.stderr)
        return 1
    parsed = json.loads(body)
    rows = {row["case"]: row for row in parsed["results"]}

    unrelated = rows.get("unrelated-recipient", {})
    empty = rows.get("empty-audience", {})
    head = run(["git", "-C", str(FRONTEND.parents[3]), "rev-parse", "HEAD"], cwd=root).stdout.strip()

    checks = {
        "suiCommit": head,
        "entry": ENTRY,
        "exports": parsed["exports"],
        "cases": parsed["results"],
        "declaredRecipientStatus": rows.get("declared-recipient", {}).get("status"),
        "unrelatedRecipientStatus": unrelated.get("status"),
        "emptyAudienceStatus": empty.get("status"),
        "reviewIsBlindToAudience": (
            unrelated.get("status") == rows.get("declared-recipient", {}).get("status")
            == empty.get("status")
        ),
        "finding": (
            "ProducerのReceipt照合（`reviewHandoffReceipt`）を実行した。"
            "票のdigestとclaimsしか見ておらず、"
            f"**`audience`だけを変えた3つのReceiptがすべて"
            f"`{rows.get('declared-recipient', {}).get('status')}`になる**。"
            "つまり**Producerも受信者を判定していない**。"
            "これは前ラウンドまでの「宣言は判定ではない」を、"
            "3つ目の側（Producer）から確認したものである。"
        ),
    }
    passed = checks["reviewIsBlindToAudience"] and bool(checks["declaredRecipientStatus"])

    receipt = {
        "schema": "tai.reference.yic-receipt-review-audience/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Node and esbuild, bundling SUI's receipt review",
        "command": (
            "python integrations/tools/yic_receipt_review_probe.py "
            "--artifact evaluations/artifacts/scn-003-document.json "
            f"--out {args.out}"
        ),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(root / args.artifact)},
        "observed": checks,
        "scope": (
            "Bundles SUI's receipt review and drives it with three receipts differing only in the "
            "audience the Consumer carried forward. It executes the review on synthetic receipts; it "
            "does not cover the receipt write-back (which the module says is not implemented)."
        ),
    }
    (root / args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "declared": checks["declaredRecipientStatus"],
        "unrelated": checks["unrelatedRecipientStatus"],
        "empty": checks["emptyAudienceStatus"],
        "blind": checks["reviewIsBlindToAudience"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
