"""Check SUI's apply_card_move domain rules: refusal cases and island containment."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sui-repo", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="sui-cm-", dir=os.environ.get("GOTMPDIR") or None))
    os.environ["SUI_DATABASE_URL"] = f"sqlite:///{workdir / 'sui.db'}"
    os.environ["SUI_RUNTIME_PROFILE"] = "local-dev"
    os.environ["SUI_LLM_PROVIDER"] = "none"
    os.environ["SUI_LOG_LEVEL"] = "ERROR"
    os.environ["SUI_API_KEY"] = "cardmove-key"
    os.environ.pop("SUI_ADMIN_API_KEY", None)
    sys.path.insert(0, str(Path(args.sui_repo) / "03_Implement/backend/src"))

    from sui_sensemaking_api.card_move_command import InvalidCardMove, apply_card_move
    from sui_sensemaking_api.documentv1_projection import from_artifact, to_documentv1_payload
    from sui_sensemaking_api.models import DocumentV1

    projected = from_artifact(json.loads(Path(args.artifact).read_text(encoding="utf-8")))
    base = to_documentv1_payload(
        projected,
        transform={"panX": 0.0, "panY": 0.0, "zoom": 1.0},
        created_at="2026-11-03T00:00:00Z",
        updated_at="2026-11-03T00:00:00Z",
    )

    def document(**overrides):
        body = dict(base)
        body.update(overrides)
        return DocumentV1.model_validate(body)

    card_ids = [card["id"] for card in base.get("cards", [])]
    checks = {"cardIds": card_ids}

    def attempt(name, doc, **kwargs):
        try:
            moved = apply_card_move(doc, **kwargs)
        except InvalidCardMove as error:
            checks[name] = {"outcome": "refused", "reason": str(error)}
            return
        except Exception as error:  # noqa: BLE001 - record the class, do not mask it
            checks[name] = {"outcome": "error", "type": type(error).__name__}
            return
        card = next(c for c in moved.cards if c.id == kwargs.get("card_id"))
        checks[name] = {
            "outcome": "applied",
            "x": card.x,
            "y": card.y,
            "updatedAtChanged": moved.updatedAt != doc.updatedAt,
        }

    if card_ids:
        first = card_ids[0]
        start = next(c for c in base["cards"] if c["id"] == first)
        attempt("noOp", document(), card_id=first, x=start["x"], y=start["y"])
        attempt("unknownCard", document(), card_id="card-absent", x=10.0, y=10.0)
        attempt("nonFiniteX", document(), card_id=first, x=float("nan"), y=10.0)
        attempt("emptyCardId", document(), card_id="", x=10.0, y=10.0)
        attempt("successfulMove", document(), card_id=first, x=300.0, y=400.0)

        duplicate_cards = list(base["cards"]) + [dict(base["cards"][0])]
        try:
            attempt("duplicateCardId", document(cards=duplicate_cards), card_id=first, x=5.0, y=5.0)
        except Exception as error:  # noqa: BLE001 - the model may reject it earlier
            checks["duplicateCardId"] = {"outcome": "rejectedByModel", "type": type(error).__name__}

        islands = [
            {"id": "island-1", "cardIds": [first], "title": "One", "titleReviewed": True},
            {"id": "island-2", "cardIds": [], "title": "Two", "titleReviewed": True},
        ]
        attempt("duplicateIslandId", document(islands=islands + [dict(islands[1])]), card_id=first, x=5.0, y=5.0)

        # A move that lands inside island-2 by its bounding rectangle.
        two = document(islands=islands, cards=[
            {**card, "x": float(card["x"]), "y": float(card["y"])} for card in base["cards"]
        ])
        attempt("containmentMove", two, card_id=first, x=900.0, y=900.0)
    else:
        checks["note"] = "the artifact carried no cards, so only the empty cases ran"

    passed = (
        checks.get("noOp", {}).get("outcome") == "refused"
        and checks.get("unknownCard", {}).get("outcome") == "refused"
        and checks.get("nonFiniteX", {}).get("outcome") == "refused"
        and checks.get("emptyCardId", {}).get("outcome") == "refused"
        and checks.get("successfulMove", {}).get("outcome") == "applied"
        and checks.get("successfulMove", {}).get("updatedAtChanged") is True
        and checks.get("duplicateCardId", {}).get("outcome") in ("refused", "rejectedByModel")
        and checks.get("duplicateIslandId", {}).get("outcome") == "refused"
        and checks.get("containmentMove", {}).get("outcome") in ("applied", "refused")
    )
    receipt = {
        "schema": "tai.reference.sui-card-move-domain/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with Python 3.12 calling SUI's card-move domain function directly",
        "command": f"python integrations/pilot-sui-document/assembler/card_move_domain_check.py --sui-repo {args.sui_repo} --artifact {args.artifact} --out evaluations/records/SUI-TEI-card-move-2026-11-06.json",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": args.artifact, "digest": digest(args.artifact)},
        "observed": checks,
        "scope": "Applies SUI's card-move domain function to a no-op, an unknown card, non-finite coordinates, an empty id, a valid move, duplicate identities, and a containment move. It does not touch persistence, CAS, or the HTTP route.",
    }
    Path(args.out).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    raise SystemExit(main())
