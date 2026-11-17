"""Run SHO's consumer against a ticket whose audience names a third party.

Last round showed SUI's validator accepts an unrelated recipient. The next question is
whether SHO's consumer notices: it is the party that would actually receive the payload,
so if anyone refuses a wrong audience, it is here.

This drives the real consumer CLI with three tickets that differ only in `audience`
(`['sho-composer']`, `['someone-else']`, `['sho-composer', 'someone-else']`) and records
what each returns. It is an execution against the real CLI, not a source reading.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SHO = Path(r"D:\GIT\hat47x\sho-composer")
SUI_FRONTEND = Path(r"D:\GIT\hat47x\sui-sensemaking\03_Implement\frontend")

# Build tickets with SUI's own builder, then let SHO read them.
BUILD = r"""
const m = require(process.env.BUNDLE);
const fs = require("fs");
const path = require("path");
const out = process.env.OUTDIR;
const crypto = require("crypto");
const PAYLOAD = "0123456789";
const PAYLOAD_DIGEST = crypto.createHash("sha256").update(PAYLOAD, "utf8").digest("hex");
const DIGEST = PAYLOAD_DIGEST;
function input(audience) {
  return {
    handoffId: "ho-20261118-0100",
    emittedAt: "2026-11-18T00:00:00.000Z",
    producer: {
      product: "sui-sensemaking",
      entrypoint: "03_Implement/frontend/src/export/handoff_context_envelope.ts",
      version: "sui-sensemaking@main",
      productSkill: null,
    },
    consumer: { product: "sho-composer", entrypoint: "bin/sho-inspect.cjs handoff" },
    purpose: "synthetic",
    task: { statement: "s", completionDefinition: "c" },
    target: { product: "sui-sensemaking", kind: "document", id: "doc-1" },
    revision: {
      kind: "context-projection.baseDocSignature",
      value: "v-1",
      digest: "sha256:" + DIGEST,
      observedAt: "2026-11-18T00:00:00.000Z",
    },
    disclosure: {
      scope: "synthetic-only", audience, purpose: "synthetic", rawSource: m.RAW_SOURCE_POLICY,
    },
    payload: {
      mediaType: "text/markdown", encoding: "utf-8", relPath: "payload.md",
      byteLength: 10, sha256: "sha256:" + DIGEST,
    },
    references: [],
    evidence: [],
    unresolved: [],
    usageRestrictions: ["synthetic-only"],
    obligations: [],
    dependenciesToConfirm: [],
    consumerRecheck: ["recheck the scope, audience and purpose at use"],
    residualWork: ["no return path"],
    conversationHistory: { included: false, note: "n" },
    transport: { harness: "deepseek-harness", sessionLabel: null, authority: m.TRANSPORT_AUTHORITY },
  };
}
const cases = {
  "declared-recipient": ["sho-composer"],
  "unrelated-recipient": ["someone-else"],
  "both": ["sho-composer", "someone-else"],
};
fs.mkdirSync(out, { recursive: true });
fs.writeFileSync(path.join(out, "payload.md"), PAYLOAD);
const manifest = {};
for (const [name, audience] of Object.entries(cases)) {
  const envelope = m.buildHandoffContextEnvelope(input(audience));
  fs.writeFileSync(path.join(out, name + ".json"), m.serializeHandoffContextEnvelope(envelope));
  manifest[name] = audience;
}
console.log(JSON.stringify(manifest));
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

    scratch = Path(tempfile.mkdtemp(prefix="yic-audience-consumer-"))
    bundle = scratch / "envelope.bundle.cjs"
    builder = scratch / "build.cjs"
    tickets = scratch / "tickets"

    built = run(
        [str(SUI_FRONTEND / "node_modules" / ".bin" / "esbuild.cmd"),
         str(SUI_FRONTEND / "src/export/handoff_context_envelope.ts"),
         "--bundle", "--platform=node", "--format=cjs", f"--outfile={bundle}"],
        cwd=SUI_FRONTEND,
    )
    if not bundle.exists():
        print((built.stderr or "")[:400], file=sys.stderr)
        return 1
    builder.write_text(BUILD, encoding="utf-8")
    made = run(["node", str(builder)], cwd=SHO,
               env={"BUNDLE": str(bundle), "OUTDIR": str(tickets)})
    if not (tickets / "declared-recipient.json").exists():
        print((made.stderr or made.stdout or "")[:400], file=sys.stderr)
        return 1

    results = []
    for name in ("declared-recipient", "unrelated-recipient", "both"):
        completed = run(
            ["node", "bin/sho-inspect.cjs", "handoff",
             str(tickets / f"{name}.json")],
            cwd=SHO,
        )
        body = (completed.stdout or "").strip()
        parsed = json.loads(body) if body.startswith("{") else None
        results.append({
            "case": name,
            "exit": completed.returncode,
            "parsed": parsed is not None,
            "acceptedTicket": None if parsed is None else parsed.get("ticket") is not None,
            "claims": None if parsed is None else sorted((parsed.get("claims") or {}).keys()),
            "authorityCarried": (
                None if parsed is None
                else (parsed.get("claims") or {}).get("authorityCarried")
            ),
            "externalDisclosure": (
                None if parsed is None
                else (parsed.get("claims") or {}).get("externalDisclosure")
            ),
            "consumerStatus": None if parsed is None else parsed.get("status"),
            "carriedAudience": (
                None if parsed is None
                else ((parsed.get("receipt") or {}).get("ticket") or {}).get("disclosure", {}).get("audience")
            ),
            "stderrTail": (completed.stderr or "").strip().splitlines()[-2:],
        })

    by_case = {row["case"]: row for row in results}
    unrelated_ok = by_case["unrelated-recipient"]["exit"] == 0
    head = run(["git", "-C", str(SHO), "rev-parse", "HEAD"], cwd=root).stdout.strip()
    sui_head = run(["git", "-C", str(SUI_FRONTEND.parents[3]), "rev-parse", "HEAD"], cwd=root).stdout.strip()

    checks = {
        "shoCommit": head,
        "suiCommit": sui_head,
        "cases": results,
        "consumerAcceptsUnrelatedRecipient": unrelated_ok,
        "consumerNeverClaimsAuthority": all(
            row["authorityCarried"] is False and row["externalDisclosure"] is False
            for row in results if row["parsed"]
        ),
        "firstAttemptNote": (
            "最初はpayloadのdigestを固定値`sha256:bbbb…`として組んだため、"
            "全ケースが`handoff-payload-digest-mismatch`で落ちた。"
            "これはConsumerの性質ではなく、こちらのfixtureの誤りである。"
            "実際に書くバイトのdigestを計算して再実行した。"
        ),
        "finding": (
            "SHOのConsumer CLIへ、`audience`だけが異なる3つの票を実際に読ませた。"
            f"`['someone-else']`のような**無関係な受信者を宣言した票も"
            f"{'受理される' if unrelated_ok else '拒否される'}**。"
            "Consumerは票を読み直して保持するが、"
            "**受信者の妥当性は判定しない**。"
            "Consumerのreceiptは`authorityCarried: false`と`externalDisclosure: false`を主張するが、"
            "これは権限を持たないという意味であって、"
            "受信者が正しいと確認したという意味ではない。"
            "**宣言は受信者を制限しない。**"
        ),
    }
    passed = unrelated_ok and checks["consumerNeverClaimsAuthority"]

    receipt = {
        "schema": "tai.reference.yic-audience-consumer/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Node, driving SHO's consumer CLI on three tickets",
        "command": (
            "python integrations/tools/yic_audience_consumer_probe.py "
            "--artifact evaluations/artifacts/scn-003-document.json "
            f"--out {args.out}"
        ),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(root / args.artifact)},
        "observed": checks,
        "scope": (
            "Builds three tickets with SUI's own envelope builder, differing only in audience, and "
            "runs SHO's consumer CLI on each. It executes the real consumer but with synthetic "
            "tickets; acceptance of an unrelated recipient shows this consumer does not judge "
            "recipients, not that no deployment would."
        ),
    }
    (root / args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "cases": len(results),
        "unrelatedAccepted": unrelated_ok,
        "neverClaimsAuthority": checks["consumerNeverClaimsAuthority"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
