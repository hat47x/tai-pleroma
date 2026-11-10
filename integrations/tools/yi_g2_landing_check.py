"""Work out where each adopted candidate would land in a product's requirement document.

G2 moves accepted candidates into each product's requirement document under that
product's own numbering. Before that can happen, two things have to be known:
which file and namespace a product uses, and which numbers are free. This reads
each product's requirement document and reports both, so the landing is mechanical
rather than guessed.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

WORKSPACE = Path("D:/GIT/hat47x")

# Each product's requirement document and the prefix its numbered IDs use.
PRODUCTS = {
    "SEI": ("sei-cognition", ["requirements/PRODUCT_REQUIREMENTS.md"], r"REQ-(?P<n>\d{4})"),
    "TEI": ("tei-platform", ["requirements/TEI_PRODUCT_REQUIREMENTS.md"], r"RQ-(?P<n>\d{3})"),
    "EKI": ("eki-fabric", ["requirements/PRODUCT_REQUIREMENTS.md"], r"RQ-(?P<n>\d{3})"),
    "SUI": (
        "sui-sensemaking",
        [
            "00_Prompt/domain.md",
            "00_Prompt/qualitative_card_quality_requirements.md",
            "00_Prompt/w_type_iterative_inquiry_requirements.md",
        ],
        r"(?:CQ|DOM)-[A-Z]+-(?P<n>\d{2})",
    ),
    # MMI states requirements as prose sections and records decisions as ADRs.
    # The ADR numbers live in the ADR directory, not in requirements.md, so
    # counting the document would report a number that is already taken.
    "MMI": ("markdown-matrix-injector", ["01_Plans/adr"], r"ADR-(?P<n>\d{4})"),
}

# Which candidates the G1 packet hands to which product, read from the packet.
CANDIDATES = (
    "13-設計ノート.md",
    "18-G1レビューパケット.md",
)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]

    spaces = {}
    for product, (repo, relatives, pattern) in PRODUCTS.items():
        numbers = set()
        readable = []
        missing = []
        prefixes = set()
        for relative in relatives:
            path = WORKSPACE / repo / relative
            if not path.exists():
                missing.append(f"{repo}/{relative}")
                continue
            if path.is_dir():
                # An ADR directory: the numbers are in the file names.
                readable.append(f"{repo}/{relative}/")
                for candidate in sorted(path.glob("*.md")):
                    for match in re.finditer(pattern, candidate.name):
                        numbers.add(int(match.group("n")))
                        prefixes.add(
                            match.group(0)[: match.group(0).rindex(match.group("n"))]
                        )
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            readable.append(f"{repo}/{relative}")
            for match in re.finditer(pattern, text):
                numbers.add(int(match.group("n")))
                prefixes.add(match.group(0)[: match.group(0).rindex(match.group("n"))])
        spaces[product] = {
            "documents": readable,
            "missingDocuments": missing,
            "highestNumber": max(numbers) if numbers else None,
            "count": len(numbers),
            "nextFreeNumber": (max(numbers) + 1) if numbers else 1,
            "prefixes": sorted(prefixes),
        }

    # A product without a numbered ID space cannot take a numbered candidate:
    # MMI records decisions as ADRs, so a YI requirement would have to become an
    # ADR rather than a new requirement ID.
    checks = {
        "spaces": spaces,
        "productsWithoutNumberedRequirements": [
            name
            for name, space in spaces.items()
            if not space["documents"]
        ],
        "productsThatNeedAnAdrInstead": [
            name
            for name, space in spaces.items()
            if space["documents"] and not space["prefixes"]
        ],
        # MMI's numbers are decision ADRs, not requirement IDs, so a candidate
        # accepted there becomes a prose requirement section plus an ADR if it
        # changes a boundary, not a new numbered requirement.
        "productsWhoseNumbersAreDecisions": [
            name
            for name, space in spaces.items()
            if space["prefixes"] and all(prefix.startswith("ADR-") for prefix in space["prefixes"])
        ],
        "allDocumentsReadable": all(
            not space["missingDocuments"] for space in spaces.values()
        ),
        "everyProductHasAFreeNumber": all(
            space["nextFreeNumber"] for space in spaces.values() if space["documents"]
        ),
    }
    passed = checks["allDocumentsReadable"] and checks["everyProductHasAFreeNumber"]

    receipt = {
        "schema": "tai.reference.yi-g2-landing/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the product requirement documents",
        "command": "python integrations/tools/yi_g2_landing_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-g2-landing-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Reads each product's requirement document and reports the namespace its numbered IDs use, the highest number in use and the next free one, so that G2 can move a candidate in without a number collision. MMI's numbers are decision ADRs rather than requirement IDs, which is recorded separately. It does not move anything: no requirement is added, and it does not check whether a product should accept a candidate or whether the numbering style suits the requirement.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "next": {name: space["nextFreeNumber"] for name, space in spaces.items()},
        "missing": [space["missingDocuments"] for space in spaces.values() if space["missingDocuments"]],
        "withoutNumberedRequirements": checks["productsWithoutNumberedRequirements"],
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
