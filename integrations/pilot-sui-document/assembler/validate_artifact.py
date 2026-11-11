"""Structural validation for the DocumentV1 projection artifact.

This checks the artifact's own envelope and element shapes. It does not
validate the meaning against SUI's DocumentV1 model.

The producer-side lifecycle / disclosure keys checked below are *optional*. A
SUI consumer that does not see them treats the source as `unknown` and applies
no document-level restriction, so an artifact written before this check existed
stays valid.
"""

SCHEMA = "tai.reference.tei-documentv1-projection/v0"
#: Allowed values for the optional source lifecycle declaration.
SOURCE_STATUSES = ("active", "revoked", "expired")
#: Allowed values for the optional document-level disclosure declaration.
DISCLOSURE_SCOPES = ("public", "internal", "restricted")


def _require(condition, message, errors):
    if not condition:
        errors.append(message)


def validate(payload):
    errors = []
    if not isinstance(payload, dict):
        return ["artifact must be a JSON object"]
    _require(payload.get("schema") == SCHEMA, f"schema must be {SCHEMA}", errors)
    contract = payload.get("contract") or {}
    _require(bool(contract.get("id")), "contract.id is required", errors)
    _require(bool(contract.get("version")), "contract.version is required", errors)
    source = payload.get("source") or {}
    _require(bool(source.get("teiCommit")), "source.teiCommit is required", errors)
    _require(isinstance(source.get("contracts"), dict), "source.contracts must be an object", errors)
    # Optional: an absent status is not `active`; the consumer reads it as unknown.
    if "status" in source:
        _require(
            source["status"] in SOURCE_STATUSES,
            f"source.status must be one of {', '.join(SOURCE_STATUSES)}",
            errors,
        )
    for key in ("statusReason", "documentRevision", "observedAt"):
        if key in source:
            _require(
                isinstance(source[key], str) and bool(source[key]),
                f"source.{key} must be a non-empty string when present",
                errors,
            )

    # Optional: an absent disclosure applies no document-level restriction.
    disclosure = payload.get("disclosure")
    if disclosure is not None:
        _require(isinstance(disclosure, dict), "disclosure must be an object when present", errors)
        if isinstance(disclosure, dict):
            scope = disclosure.get("scope")
            _require(
                scope in DISCLOSURE_SCOPES,
                f"disclosure.scope must be one of {', '.join(DISCLOSURE_SCOPES)}",
                errors,
            )

    document = payload.get("document") or {}
    _require(isinstance(document, dict), "document must be an object", errors)
    meta = document.get("document") or {}
    _require(bool(meta.get("id")), "document.document.id is required", errors)

    cards = document.get("cards") or []
    _require(isinstance(cards, list) and len(cards) > 0, "document.cards must not be empty", errors)
    for card in cards:
        _require(bool(card.get("id")), "card.id is required", errors)
        _require(isinstance(card.get("text"), str), "card.text must be a string", errors)
        _require(isinstance(card.get("x"), (int, float)), "card.x must be a number", errors)
        _require(isinstance(card.get("y"), (int, float)), "card.y must be a number", errors)

    for island in document.get("islands") or []:
        _require(bool(island.get("id")), "island.id is required", errors)
        _require(isinstance(island.get("cardIds"), list), "island.cardIds must be an array", errors)

    for edge in document.get("edges") or []:
        _require(bool(edge.get("id")), "edge.id is required", errors)
        for key in ("fromId", "toId", "type"):
            _require(bool(edge.get(key)), f"edge.{key} is required", errors)
        for key in ("fromKind", "toKind"):
            _require(edge.get(key) in ("card", "island"), f"edge.{key} must be card or island", errors)

    for affiliation in document.get("affiliations") or []:
        _require(bool(affiliation.get("id")), "affiliation.id is required", errors)
        _require(bool(affiliation.get("cardId")), "affiliation.cardId is required", errors)
        _require(bool(affiliation.get("islandId")), "affiliation.islandId is required", errors)

    return errors
