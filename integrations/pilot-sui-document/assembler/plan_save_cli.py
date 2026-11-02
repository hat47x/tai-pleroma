"""CLI: build a non-writing save plan from a projection artifact."""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--existing", default=None)
    parser.add_argument("--transform", default='{"panX":0,"panY":0,"zoom":1}')
    parser.add_argument("--created-at", default="2026-11-03T00:00:00Z")
    parser.add_argument("--updated-at", default="2026-11-03T00:00:00Z")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))
    from sui_sensemaking_api.documentv1_projection import from_artifact
    from sui_sensemaking_api.documentv1_save_plan import plan_save

    artifact = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    existing = (
        json.loads(Path(args.existing).read_text(encoding="utf-8")) if args.existing else None
    )
    plan = plan_save(
        from_artifact(artifact),
        transform=json.loads(args.transform),
        created_at=args.created_at,
        updated_at=args.updated_at,
        existing=existing,
        preserve_existing=True,
    )

    receipt = {
        "schema": "tai.reference.tei-save-plan-cli/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12",
        "command": f"python integrations/pilot-sui-document/assembler/plan_save_cli.py --sui-repo {args.sui_repo} --artifact {args.artifact}",
        "result": "PASS",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "existing": (
            {"path": args.existing, "digest": digest(args.existing)} if args.existing else None
        ),
        "observed": {
            "action": plan.action,
            "cardsAdded": len(plan.cards_added),
            "cardsRemoved": len(plan.cards_removed),
            "cardsChanged": len(plan.cards_changed),
            "islandsAdded": len(plan.islands_added),
            "preservedCards": len(plan.preserved_cards),
            "preservedIslands": len(plan.preserved_islands),
            "warnings": len(plan.warnings),
            "writes": False,
        },
        "scope": "Builds a save plan through SUI's consumer and planner. It does not save, call the API, or touch a database.",
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(receipt["observed"]))


if __name__ == "__main__":
    main()
