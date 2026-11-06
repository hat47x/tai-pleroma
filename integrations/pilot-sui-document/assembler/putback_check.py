"""Evaluate whether a read-only projection can be turned back into an edit Intent.

PFC-12 (#2585): a projection is a read-only view. Turning it back into an edit
Intent is only safe when every difference is an exact, present-on-both value.
Three losses make the Putback ambiguous:

- a card or field that exists only in the Source of truth may have been
  "not projected" or may have been intended for deletion;
- an optional field that the projection omits may mean "absent" or "clear";
- a coordinate or decimal difference within floating-point tolerance is an
  approximation, not a business change.

The evaluator never guesses. Any ambiguity refuses the whole Putback.
"""

SCHEMA = "tai.reference.tei-documentv1-projection/v0"

CARD_OPTIONAL_FIELDS = ("claimType", "holdState", "textReviewed", "sources")
FLOAT_TOLERANCE = 1e-9


def _numbers_approximately_equal(left, right):
    if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
        return False
    return abs(float(left) - float(right)) <= FLOAT_TOLERANCE


def _is_present(value):
    return value is not None


def evaluate_putback(artifact, existing):
    """Return a Putback evaluation for one projection against one document.

    The result is a plain dict so a receipt can be written without importing a
    model layer.
    """
    changes = []
    ambiguous = []

    if not isinstance(artifact, dict) or not isinstance(existing, dict):
        return {
            "decision": "refused",
            "changes": [],
            "ambiguous": [{"kind": "invalid-input", "reason": "artifact and existing must be objects"}],
        }
    if artifact.get("schema") != SCHEMA:
        return {
            "decision": "refused",
            "changes": [],
            "ambiguous": [{"kind": "invalid-artifact", "reason": f"schema must be {SCHEMA}"}],
        }

    projected = artifact.get("document") or {}
    meta = projected.get("document") or {}
    if meta.get("id") != existing.get("id"):
        return {
            "decision": "refused",
            "changes": [],
            "ambiguous": [{
                "kind": "document-id-mismatch",
                "reason": "the projection and the source of truth are different documents",
            }],
        }

    # Document-level fields that the projection may omit.
    for field in ("title", "readingOrder"):
        projected_value = meta.get(field)
        existing_value = existing.get(field)
        if not _is_present(projected_value):
            if _is_present(existing_value) and existing_value != []:
                ambiguous.append({
                    "kind": "ambiguous-document-field",
                    "target": field,
                    "reason": "the projection omits the field; absence may mean not-projected or clear",
                })
        elif projected_value != existing_value:
            changes.append({"kind": "edit-document-field", "target": field})

    projected_cards = {card.get("id"): card for card in projected.get("cards") or []}
    existing_cards = {card.get("id"): card for card in existing.get("cards") or []}

    for card_id in sorted(set(projected_cards) - set(existing_cards)):
        changes.append({"kind": "add-card", "target": card_id})
    for card_id in sorted(set(existing_cards) - set(projected_cards)):
        ambiguous.append({
            "kind": "ambiguous-absence",
            "target": card_id,
            "reason": "the card exists only in the source of truth; the projection may not carry it",
        })

    for card_id in sorted(set(projected_cards) & set(existing_cards)):
        card = projected_cards[card_id]
        current = existing_cards[card_id]
        if card.get("text") != current.get("text"):
            changes.append({"kind": "edit-text", "target": card_id})
        for axis in ("x", "y"):
            if card.get(axis) == current.get(axis):
                continue
            if _numbers_approximately_equal(card.get(axis), current.get(axis)):
                ambiguous.append({
                    "kind": "numeric-approximation",
                    "target": f"{card_id}.{axis}",
                    "reason": "the values differ only within floating-point tolerance",
                })
            else:
                changes.append({"kind": "edit-coordinate", "target": f"{card_id}.{axis}"})
        for field in CARD_OPTIONAL_FIELDS:
            projected_value = card.get(field)
            existing_value = current.get(field)
            if not _is_present(projected_value) or projected_value == []:
                if _is_present(existing_value) and existing_value != []:
                    ambiguous.append({
                        "kind": "ambiguous-optional-absence",
                        "target": f"{card_id}.{field}",
                        "reason": "the projection omits the optional field; absence may mean not-projected or clear",
                    })
            elif projected_value != existing_value:
                changes.append({"kind": "edit-optional", "target": f"{card_id}.{field}"})

    projected_islands = {island.get("id"): island for island in projected.get("islands") or []}
    existing_islands = {island.get("id"): island for island in existing.get("islands") or []}
    for island_id in sorted(set(projected_islands) - set(existing_islands)):
        changes.append({"kind": "add-island", "target": island_id})
    for island_id in sorted(set(existing_islands) - set(projected_islands)):
        ambiguous.append({
            "kind": "ambiguous-absence",
            "target": island_id,
            "reason": "the island exists only in the source of truth; the projection may not carry it",
        })
    for island_id in sorted(set(projected_islands) & set(existing_islands)):
        projected_ids = list(projected_islands[island_id].get("cardIds") or [])
        existing_ids = list(existing_islands[island_id].get("cardIds") or [])
        if projected_ids == existing_ids:
            continue
        if sorted(projected_ids) == sorted(existing_ids):
            ambiguous.append({
                "kind": "ambiguous-order",
                "target": island_id,
                "reason": "the same members appear in a different order; order may not be meaningful",
            })
        else:
            changes.append({"kind": "edit-island-members", "target": island_id})
        projected_title = projected_islands[island_id].get("title")
        existing_title = existing_islands[island_id].get("title")
        if not _is_present(projected_title):
            if _is_present(existing_title):
                ambiguous.append({
                    "kind": "ambiguous-optional-absence",
                    "target": f"{island_id}.title",
                    "reason": "the projection omits the optional field",
                })
        elif projected_title != existing_title:
            changes.append({"kind": "edit-optional", "target": f"{island_id}.title"})

    for collection in ("edges", "affiliations"):
        projected_items = {item.get("id") for item in projected.get(collection) or []}
        existing_items = {item.get("id") for item in existing.get(collection) or []}
        for item_id in sorted(projected_items - existing_items):
            changes.append({"kind": f"add-{collection[:-1]}", "target": item_id})
        for item_id in sorted(existing_items - projected_items):
            ambiguous.append({
                "kind": "ambiguous-absence",
                "target": item_id,
                "reason": f"the {collection[:-1]} exists only in the source of truth",
            })

    if ambiguous:
        decision = "refused"
    elif changes:
        decision = "safe"
    else:
        decision = "no-op"
    return {"decision": decision, "changes": changes, "ambiguous": ambiguous}
