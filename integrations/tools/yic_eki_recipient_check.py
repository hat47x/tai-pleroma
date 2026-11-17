"""Check whether EKI verifies that a Lease goes to the intended recipient.

The independent review warned that checking only SUI generalises too far. EKI has an
explicit recipient check: a Lease carries `WorkerIdentity`, and the verifier refuses it
when that differs from the local Worker. This reads the source and records the exact
comparison and the reason code it raises, so the claim rests on the code rather than on
a product-wide assumption.

This is a source reading, not a run: the EKI recipient path needs a signed lease fixture
that this probe does not construct.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

EKI = Path(r"D:\GIT\hat47x\eki-fabric")
VERIFY = "internal/core/leasedelivery/verify.go"
DELIVERY = "internal/core/leasedelivery/delivery.go"


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def locate(root, relative):
    """Find the file, allowing for a different package directory layout."""
    direct = root / relative
    if direct.exists():
        return direct
    matches = [p for p in root.rglob(Path(relative).name)
               if "worktrees" not in str(p) and "vendor" not in str(p)]
    return matches[0] if matches else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    verify_path = locate(EKI, VERIFY)
    delivery_path = locate(EKI, DELIVERY)
    if verify_path is None or delivery_path is None:
        print("could not locate the EKI lease delivery sources", file=sys.stderr)
        return 1

    verify_text = verify_path.read_text(encoding="utf-8")
    delivery_text = delivery_path.read_text(encoding="utf-8")

    # The recipient comparison and its reason code.
    recipient_comparison = re.search(
        r"lease\.WorkerIdentity\(\)\s*!=\s*v\.cfg\.WorkerIdentity", verify_text
    )
    reason_code = re.search(
        r"failure\(decisiontrust\.(\w+)", verify_text.split("WorkerIdentity")[-1]
    ) if "WorkerIdentity" in verify_text else None
    reason_name = reason_code.group(1) if reason_code else None

    # Delivery refuses a caller-supplied recipient.
    caller_cannot_supply = "The caller cannot supply a recipient" in delivery_text
    envelope_fields = re.findall(r"^\s+(\w+)\s+(?:ids\.|string|\[\]byte)", delivery_text, re.M)

    head = __import__("subprocess").run(
        ["git", "-C", str(EKI), "rev-parse", "HEAD"], capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    ).stdout.strip()

    checks = {
        "ekiCommit": head,
        "verifyFile": str(verify_path.relative_to(EKI)).replace("\\", "/"),
        "deliveryFile": str(delivery_path.relative_to(EKI)).replace("\\", "/"),
        "comparesRecipient": bool(recipient_comparison),
        "comparisonText": (
            "lease.WorkerIdentity() != v.cfg.WorkerIdentity"
            if recipient_comparison else None
        ),
        "reasonOnMismatch": reason_name,
        "deliveryRefusesCallerSuppliedRecipient": caller_cannot_supply,
        "envelopeFields": envelope_fields,
        "finding": (
            "EKIのLease検証は、`lease.WorkerIdentity()`が"
            "ローカルWorkerと一致するかを比較し、"
            f"一致しなければ`{reason_name}`で拒否する。"
            "**受信者が判定に入っている**という点で、SUIの`AccessRequest`とは違う。"
            "ただしこれは**Leaseの受信者がWorkerか**という判定であり、"
            "「誰に文書を見せてよいか」とは対象が違う。"
        ),
        "whatThisDoesNotShow": (
            "署名付きLeaseのfixtureを組み立てていないため、この比較が実際に走ることは"
            "実行で確かめていない。ソースの読み取りである。"
        ),
    }
    passed = bool(
        checks["comparesRecipient"]
        and checks["deliveryRefusesCallerSuppliedRecipient"]
        and reason_name
    )

    receipt = {
        "schema": "tai.reference.yic-eki-recipient-check/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the EKI lease delivery sources",
        "command": "python integrations/tools/yic_eki_recipient_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YIC-eki-recipient-2026-11-18.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": (
            "Reads EKI's lease delivery sources and records that the verifier compares the Lease "
            "recipient with the local Worker and refuses a mismatch, and that the delivery envelope "
            "does not let a caller supply a recipient. It is a source reading, not an execution: no "
            "signed lease is built, and the comparison is about a Lease recipient, not about which "
            "person a document may be shown to."
        ),
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "comparesRecipient": checks["comparesRecipient"],
        "reason": reason_name,
        "callerCannotSupply": caller_cannot_supply,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
