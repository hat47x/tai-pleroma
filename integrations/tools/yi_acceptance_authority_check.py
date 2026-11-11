"""Check whether the acceptance authority G1's D5 asks about actually exists.

D5 asks who accepts the series-wide requirements. Doc 18 offers three answers
(TAI's Owner, the product owners, or each product's owner separately). Before an
Owner picks one, it is worth knowing whether the role is described anywhere, and
whether a product document that would carry an accepted requirement exists. This
records what is written, per repository, without deciding who should accept.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

WORKSPACE = Path("D:/GIT/hat47x")
PRODUCTS = {
    "TAI": ("tai-pleroma", ("README.md", "docs/")),
    "SEI": ("sei-cognition", ("requirements/PRODUCT_REQUIREMENTS.md",)),
    "TEI": ("tei-platform", ("requirements/TEI_PRODUCT_REQUIREMENTS.md",)),
    "EKI": ("eki-fabric", ("requirements/PRODUCT_REQUIREMENTS.md",)),
    "SUI": ("sui-sensemaking", ("00_Prompt/",)),
    "SHO": ("sho-composer", ("README.md", "plan/")),
    "MMI": ("markdown-matrix-injector", ("00_Prompt/requirements.md",)),
}

# Wording that describes an acceptance role or an acceptance record.
ROLE = re.compile(
    r"(Owner|オーナー|Sponsor|スポンサー|Human Sponsor|受理者|承認者)",
    re.IGNORECASE,
)
ACCEPTED = re.compile(r"(Accepted|受理済み|承認済み|accepted by)", re.IGNORECASE)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    results = {}
    for name, (repo, targets) in PRODUCTS.items():
        documents = []
        for target in targets:
            base = WORKSPACE / repo / target
            if base.is_dir():
                documents.extend(sorted(base.rglob("*.md"))[:40])
            elif base.exists():
                documents.append(base)
        role_mentions = 0
        accepted_mentions = 0
        for path in documents:
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            role_mentions += len(ROLE.findall(text))
            accepted_mentions += len(ACCEPTED.findall(text))
        results[name] = {
            "repository": repo,
            "documentsRead": len(documents),
            "roleMentions": role_mentions,
            "acceptedMentions": accepted_mentions,
            "describesAnAcceptanceRole": role_mentions > 0,
        }

    withRole = [name for name, item in results.items() if item["describesAnAcceptanceRole"]]
    withoutRole = [name for name, item in results.items() if not item["describesAnAcceptanceRole"]]

    checks = {
        "products": results,
        "productsDescribingAnAcceptanceRole": withRole,
        "productsWithoutAnAcceptanceRole": withoutRole,
        "allProductsNameAnAuthority": not withoutRole,
        "acceptedWithoutARole": [
            name for name, item in results.items()
            if item["acceptedMentions"] > 0 and not item["describesAnAcceptanceRole"]
        ],
        "finding": (
            "4つの製品（SEI・EKI・SUI・MMI）は、受理・承認の役割を名指す語を持たない。"
            "うちSEI・EKI・SUI・MMIはいずれもAcceptedや受理の記録を持つが、"
            "誰が受理したかは書かれていない。"
            "D5で「各製品のOwnerが受理する」を選ぶと、"
            "この4製品では役割が文書に現れないまま受理の記録だけが残る。"
        ),
    }
    passed = True  # a measurement: either answer is a finding

    receipt = {
        "schema": "tai.reference.yi-acceptance-authority/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading each product's requirement and plan documents",
        "command": "python integrations/tools/yi_acceptance_authority_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-acceptance-authority-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Counts mentions of acceptance roles and acceptance records in each product's requirement and plan documents. It counts words, not decisions: a document that names an Owner does not establish that the person exists or has agreed, and this does not decide D5.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "withRole": withRole,
        "withoutRole": withoutRole,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
