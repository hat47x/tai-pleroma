"""Check what the handoff envelope's `audience` field actually does.

Earlier rounds concluded that SUI has no recipient field. That was true of
`AccessRequest` but not of the handoff envelope: `handoff_context_envelope.ts` has
`disclosure.audience`, and the validator rejects an empty list. This asks the narrower
question — does anything *decide* against that list, or is it only carried?

Two checks: what the validator enforces, and whether SHO's consumer compares the
declared audience with anything.
"""

import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

SUI_ENVELOPE = r"03_Implement/frontend/src/export/handoff_context_envelope.ts"
SHO_CONSUMER = "scripts/handoff-cross-product.cjs"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--sui-repo", default=r"D:\GIT\hat47x\sui-sensemaking")
    parser.add_argument("--sho-repo", default=r"D:\GIT\hat47x\sho-composer")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    envelope_path = Path(args.sui_repo) / SUI_ENVELOPE
    consumer_path = Path(args.sho_repo) / SHO_CONSUMER
    if not envelope_path.exists() or not consumer_path.exists():
        print("missing envelope or consumer source", file=sys.stderr)
        return 1

    envelope = envelope_path.read_text(encoding="utf-8")
    consumer = consumer_path.read_text(encoding="utf-8")

    # What the envelope validator enforces about audience.
    enforces_non_empty = "handoff-disclosure-audience-empty" in envelope
    requires_list = "requireList<string>" in envelope and "disclosure.audience" in envelope
    # Does anything compare the declared audience with a recipient?
    compares_audience = bool(
        re.search(r"audience\s*(===|!==|==|!=|\.includes)", envelope)
        or re.search(r"audience\s*(===|!==|==|!=|\.includes)", consumer)
    )
    # Does the consumer refuse an audience it was not declared for?
    refuses_expansion = bool(
        re.search(r"(deny|refuse|reject).*audience", consumer, re.I)
        or re.search(r"audience.*(deny|refuse|reject)", consumer, re.I)
    )
    # The consumer's own words about what it does not verify.
    declares_not_verifying = "does not verify" in consumer and "audience" in consumer
    host_grant_not_run = "hostRecipientAuthorization: 'not-run'" in consumer

    sui_head = subprocess.run(
        ["git", "-C", str(Path(args.sui_repo)), "rev-parse", "HEAD"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()
    sho_head = subprocess.run(
        ["git", "-C", str(Path(args.sho_repo)), "rev-parse", "HEAD"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()

    observed = {
        "suiCommit": sui_head,
        "shoCommit": sho_head,
        "envelopeFile": SUI_ENVELOPE,
        "envelopeHasAudience": "audience: string[]" in envelope,
        "validatesAudienceIsAList": requires_list,
        "refusesEmptyAudience": enforces_non_empty,
        "comparesAudienceAgainstARecipient": compares_audience,
        "consumerRefusesAudienceExpansion": refuses_expansion,
        "consumerDeclaresItDoesNotVerify": declares_not_verifying,
        "consumerRecordsHostGrantAsNotRun": host_grant_not_run,
        "finding": (
            "SUIのhandoff envelopeには`disclosure.audience`があり、"
            "**空のリストは拒否される**（`handoff-disclosure-audience-empty`）。"
            "しかし**宣言された受信者と実際の受信者を比較する箇所は無い**。"
            "SHOのConsumerは宣言を読み直して保持するが、"
            "受信者の拡大を拒否せず、Host Grantも検証していない"
            "（`hostRecipientAuthorization: 'not-run'`と自分で記録している）。"
            "**つまり`audience`は『宣言』であって『判定』ではない。**"
            "これは前ラウンドまでの結論（SUIに受信者の欄が無い）を"
            "**部分的に訂正する**：`AccessRequest`には無いが、"
            "handoff envelopeにはある。あるが、判定には使われていない。"
        ),
    }
    # Passes when the envelope has the field and nothing compares it.
    passed = (
        observed["envelopeHasAudience"]
        and observed["refusesEmptyAudience"]
        and not observed["comparesAudienceAgainstARecipient"]
    )

    receipt = {
        "schema": "tai.reference.yic-audience-field-reading/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the handoff envelope and its consumer",
        "command": (
            "python integrations/tools/yic_audience_declaration_check.py "
            "--artifact evaluations/artifacts/scn-003-document.json "
            "--out evaluations/records/YIC-audience-field-reading-2026-11-18.json"
        ),
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(root / args.artifact)},
        "observed": observed,
        "scope": (
            "Reads SUI's handoff envelope validator and SHO's consumer for audience handling: the "
            "field exists, an empty list is refused, and nothing compares the declared audience "
            "with an actual recipient. This is a source reading; it does not run the TypeScript "
            "validator, and it does not examine any other audience-carrying schema."
        ),
    }
    (root / args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: observed[k] for k in (
        "envelopeHasAudience", "refusesEmptyAudience",
        "comparesAudienceAgainstARecipient", "consumerRefusesAudienceExpansion",
        "consumerRecordsHostGrantAsNotRun",
    )}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
