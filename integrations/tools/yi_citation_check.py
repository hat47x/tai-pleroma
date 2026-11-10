"""Check that requirement IDs cited by the YI analysis exist in each product.

The G1 packet asks an Owner to accept candidates, and the acceptance rests on
citations like ``SEI REQ-0005`` or ``TEI RQ-028``. A citation to an ID that a
product never defined would make the packet's evidence unfalsifiable. This
resolves each cited ID against the product's own requirement document.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

WORKSPACE = Path("D:/GIT/hat47x")

# Where each product keeps the documents that define its requirement IDs.
PRODUCTS = {
    "SEI": ("sei-cognition", ["requirements/PRODUCT_REQUIREMENTS.md"]),
    "TEI": ("tei-platform", ["requirements/TEI_PRODUCT_REQUIREMENTS.md"]),
    "EKI": ("eki-fabric", ["requirements/PRODUCT_REQUIREMENTS.md"]),
    "MMI": ("markdown-matrix-injector", ["00_Prompt/requirements.md"]),
    "SUI": ("sui-sensemaking", ["00_Prompt/domain.md", "00_Prompt/qualitative_card_quality_requirements.md"]),
}

ID = re.compile(r"(?<![A-Za-z0-9-])(REQ-000\d|RQ-0\d\d|CQ-[A-Z]+-\d+|DOM-[A-Z]+-\d+)(?![0-9])")
# Japanese characters are word characters, so \b does not break "SEI"
# after a particle. Match the product names with ASCII lookarounds instead.
NAME = re.compile(r"(?<![A-Z])(SEI|TEI|EKI|MMI|SUI)(?![A-Z])")


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def attribute(line):
    """Assign each ID to the nearest product name that precedes it on the line."""
    names = [(m.start(), m.group(1)) for m in NAME.finditer(line)]
    found = []
    for match in ID.finditer(line):
        product = None
        for position, name in names:
            if position < match.start():
                product = name
            else:
                break
        found.append((product, match.group(1)))
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    analysis = root / "docs/yi-constellation/analysis"
    docs = ["14-既存要求との照合.md", "18-G1レビューパケット.md"]

    definitions = {}
    documents_read = {}
    for product, (repo, relatives) in PRODUCTS.items():
        ids = set()
        readable = True
        for relative in relatives:
            path = WORKSPACE / repo / relative
            if not path.exists():
                readable = False
                continue
            ids |= set(ID.findall(path.read_text(encoding="utf-8", errors="replace")))
        definitions[product] = ids if readable else None
        documents_read[product] = relatives

    cited = {}
    for doc in docs:
        text = (analysis / doc).read_text(encoding="utf-8")
        for line in text.splitlines():
            for product, found in attribute(line):
                if found.startswith(("REQ-", "RQ-")):
                    # ``RQ-002`` alone is ambiguous across products; without a
                    # product name it is not a resolvable citation.
                    if product is None:
                        cited.setdefault(found, {"products": set(), "docs": set(), "unattributed": True})
                        cited[found]["docs"].add(doc)
                        continue
                    cited.setdefault(found, {"products": set(), "docs": set(), "unattributed": False})
                    cited[found]["products"].add(product)
                    cited[found]["docs"].add(doc)
                else:
                    cited.setdefault(found, {"products": set(), "docs": set(), "unattributed": False})
                    if product:
                        cited[found]["products"].add(product)
                    cited[found]["docs"].add(doc)

    unresolved = []
    wrong_product = []
    for found, info in sorted(cited.items()):
        if not info["products"]:
            unresolved.append(f"{found} (no product named next to it in {sorted(info['docs'])})")
            continue
        for product in sorted(info["products"]):
            known = definitions.get(product)
            if known is None:
                unresolved.append(f"{found} (product {product} has no readable requirement document)")
            elif found not in known:
                wrong_product.append(f"{product} {found}")

    # The G1 packet must account for every candidate exactly once: the 22
    # candidates of doc 14 stay among the 15 kept as requirements (new plus
    # extension plus the 3 harness additions) or the 10 moved to existing
    # requirements.
    cross = (analysis / "14-既存要求との照合.md").read_text(encoding="utf-8")
    packet_text = (analysis / "18-G1レビューパケット.md").read_text(encoding="utf-8")
    classification = {}
    for line in cross.splitlines():
        row = re.match(r"\| 0(\d\d) ", line)
        if not row:
            continue
        cells = [cell.strip() for cell in line.split("|")]
        if len(cells) >= 5:
            classification.setdefault(row.group(1), set()).add(cells[3])

    kept_rows = set()
    for line in packet_text.splitlines():
        row = re.match(r"\| (0\d\d) \|", line)
        if row:
            kept_rows.add(row.group(1))
    moved_rows = set()
    for line in packet_text.splitlines():
        # The kept table is ``| 001 | 通塞…`` and the moved table is
        # ``| 003 輔相…``; the pipe right after the number separates them.
        row = re.match(r"\| (0\d\d) ([^|])", line)
        if row:
            moved_rows.add(row.group(1))
    split = sorted(kept_rows & moved_rows)
    requirement_candidates = {f"{number:03d}" for number in range(1, 23)}
    harness_additions = {"023", "024", "025"}
    covered = kept_rows | moved_rows
    unaccounted = sorted(requirement_candidates - covered)
    duplicated = sorted(kept_rows & moved_rows)
    extra = sorted(covered - requirement_candidates - harness_additions)
    counts = {}
    for values in classification.values():
        for value in values:
            counts[value] = counts.get(value, 0) + 1

    checks = {
        "documents": docs,
        "documentsRead": documents_read,
        "productsReadable": {name: value is not None for name, value in definitions.items()},
        "definedIdCounts": {name: len(value or ()) for name, value in definitions.items()},
        "citedIds": len(cited),
        "unresolved": unresolved,
        "notDefinedByProduct": wrong_product,
        "everyCitationResolves": not unresolved,
        "everyCitationIsDefined": not wrong_product,
        "crossCheckClassification": counts,
        "keptInPacket": len(kept_rows),
        "movedInPacket": len(moved_rows),
        "candidatesNotAccounted": unaccounted,
        "candidatesCountedTwice": duplicated,
        "candidatesOutsideTheKnownSet": extra,
        "everyCandidateIsAccountedOnce": not unaccounted and not duplicated and not extra,
    }
    passed = (
        checks["everyCitationResolves"]
        and checks["everyCitationIsDefined"]
        and checks["everyCandidateIsAccountedOnce"]
    )
    receipt = {
        "schema": "tai.reference.yi-citation-check/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 reading the product requirement documents",
        "command": "python integrations/tools/yi_citation_check.py --artifact evaluations/artifacts/scn-003-document.json --out evaluations/records/YI-citation-check-2026-11-11.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(Path(args.artifact).resolve())},
        "observed": checks,
        "scope": "Reads the requirement documents of SEI, TEI, EKI, MMI and SUI and checks that the IDs cited by the YI cross-check and G1 packet are defined there, and that the G1 packet accounts for every candidate exactly once. An ID is attributed to the product name written before it on the same line. This checks presence and bookkeeping only: a defined ID is not evidence that the candidate is a duplicate, that the requirement covers the reading, or that an Owner accepted anything.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "cited": len(cited),
        "unresolved": unresolved,
        "notDefined": wrong_product,
        "passed": passed,
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
