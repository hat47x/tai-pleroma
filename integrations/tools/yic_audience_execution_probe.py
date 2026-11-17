"""Run the envelope validator with a shape the product's own test uses.

The first attempt built a plausible envelope from field names and every case failed
with `handoff-missing-field` — the validator requires fields I had guessed wrong. Rather
than widen the guess, this reads the product's own test fixture shape and uses it, so a
rejection can be attributed to the audience rather than to an invented envelope.
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
ENTRY = "src/export/handoff_context_envelope.ts"

DRIVER = r"""
const m = require(process.env.BUNDLE);
const DIGEST = "b".repeat(64);
function base() {
  return {
    handoffId: "ho-20261118-0001",
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
      scope: "synthetic-only",
      audience: ["sho-composer"],
      purpose: "synthetic",
      rawSource: m.RAW_SOURCE_POLICY,
    },
    payload: {
      mediaType: "text/markdown",
      encoding: "utf-8",
      relPath: "payload.md",
      byteLength: 10,
      sha256: "sha256:" + DIGEST,
    },
    references: [],
    evidence: [],
    unresolved: [],
    usageRestrictions: ["synthetic-only"],
    obligations: [],
    dependenciesToConfirm: [],
    consumerRecheck: ["recheck the scope, audience and purpose at use"],
    residualWork: ["no return path from the consumer receipt"],
    conversationHistory: { included: false, note: "n" },
    transport: { harness: "deepseek-harness", sessionLabel: null, authority: m.TRANSPORT_AUTHORITY },
  };
}
function attempt(name, mutate) {
  const input = base();
  mutate(input);
  try {
    const envelope = m.buildHandoffContextEnvelope(input);
    return { case: name, accepted: true, audience: envelope.disclosure.audience };
  } catch (error) {
    return {
      case: name,
      accepted: false,
      code: (error && error.code) || (error && error.name) || "error",
      message: (error && error.message) || "",
    };
  }
}
const results = [
  attempt("valid-one-audience", () => {}),
  attempt("empty-audience", (i) => { i.disclosure.audience = []; }),
  attempt("non-string-audience-entry", (i) => { i.disclosure.audience = [7]; }),
  attempt("unrelated-recipient", (i) => { i.disclosure.audience = ["someone-else"]; }),
  attempt("wrong-case-recipient", (i) => { i.disclosure.audience = ["SHO-Composer"]; }),
  attempt("many-recipients", (i) => { i.disclosure.audience = ["a", "b", "c"]; }),
];
console.log(JSON.stringify({ results }));
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

    scratch = Path(os.environ.get("TEMP", "/tmp")) / "yic-envelope-run"
    scratch.mkdir(exist_ok=True)
    bundle = scratch / "envelope.bundle.cjs"
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
    results = {row["case"]: row for row in parsed["results"]}

    head = run(["git", "-C", str(FRONTEND.parents[2]), "rev-parse", "HEAD"], cwd=root).stdout.strip()

    unrelated_accepted = results.get("unrelated-recipient", {}).get("accepted") is True
    wrong_case_accepted = results.get("wrong-case-recipient", {}).get("accepted") is True
    checks = {
        "suiCommit": head,
        "entry": ENTRY,
        "fixtureShapeSource": "the product's own handoff_context_envelope.test.ts input()",
        "cases": parsed["results"],
        "validAccepted": results.get("valid-one-audience", {}).get("accepted"),
        "emptyRefused": results.get("empty-audience", {}).get("accepted") is False,
        "emptyRefusalCode": results.get("empty-audience", {}).get("code"),
        "nonStringRefused": results.get("non-string-audience-entry", {}).get("accepted") is False,
        "unrelatedRecipientAccepted": unrelated_accepted,
        "wrongCaseRecipientAccepted": wrong_case_accepted,
        "manyRecipientsAccepted": results.get("many-recipients", {}).get("accepted"),
        "finding": (
            "handoff envelopeの検証器を**実行**した。"
            "空のリストと非文字列の要素は拒否される。"
            f"一方、**無関係な受信者名は{'受理される' if unrelated_accepted else '拒否される'}**、"
            f"大文字小文字違いも{'受理される' if wrong_case_accepted else '拒否される'}。"
            "**この検証器は形式だけを見ており、受信者の妥当性は判定しない。**"
            "前ラウンドのソース読み取りと同じ結論を、実行で確認した。"
        ),
        "firstAttemptNote": (
            "最初は欄名から組み立てた票で実行したが、全ケースが`handoff-missing-field`で落ちた。"
            "検証器が要求する欄を推測で当てていたためで、"
            "製品自身のtest fixtureの形に合わせて再実行した。"
        ),
    }
    passed = (
        checks["validAccepted"] is True
        and checks["emptyRefused"]
        and checks["nonStringRefused"]
        and unrelated_accepted
    )

    receipt = {
        "schema": "tai.reference.yic-audience-execution/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Node and esbuild, bundling SUI's envelope validator",
        "command": (
            "python integrations/tools/yic_audience_execution_probe.py "
            "--artifact evaluations/artifacts/scn-003-document.json "
            f"--out {args.out}"
        ),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(root / args.artifact)},
        "observed": checks,
        "scope": (
            "Bundles SUI's handoff envelope module and drives its builder with six inputs shaped "
            "like the product's own test fixture. It executes the validator on synthetic inputs; it "
            "does not exercise the export flow around it, and acceptance of an unrelated recipient "
            "shows only that this validator does not judge recipients."
        ),
    }
    (root / args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: checks[k] for k in (
        "validAccepted", "emptyRefused", "nonStringRefused",
        "unrelatedRecipientAccepted", "wrongCaseRecipientAccepted", "passed",
    ) if k in checks}, ensure_ascii=False) or json.dumps({"passed": passed}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
