"""Producer-side declarations for the M1 producer contract.

The artifact schema accepts `source.status` / `source.statusReason` /
`source.documentRevision` / `source.observedAt` and a top-level `disclosure.scope`
as **optional** keys. This module writes only what the caller supplies: it never
invents `active`, and it never invents a disclosure scope. Absent keys stay
absent so that a consumer reads them as `unknown` instead of `active`.
"""

from __future__ import annotations

#: Allowed source lifecycle values. Mirrors the artifact schema.
SOURCE_STATUSES = ("active", "revoked", "expired")
#: Allowed document-level disclosure values. Mirrors the artifact schema.
DISCLOSURE_SCOPES = ("public", "internal", "restricted")


class DeclarationError(ValueError):
    """Raised when a declaration is outside the allowed vocabulary."""


def source_declaration(
    *,
    status: str | None = None,
    status_reason: str | None = None,
    document_revision: str | None = None,
    observed_at: str | None = None,
) -> dict[str, str]:
    """Build the optional `source` keys.

    Omitted arguments produce no key. `active` is written only when the caller
    says so; a producer must not default to it, because a consumer that sees
    `active` may treat a stale artifact as current.
    """
    if status is not None and status not in SOURCE_STATUSES:
        raise DeclarationError(f"status must be one of {', '.join(SOURCE_STATUSES)}")
    declaration: dict[str, str] = {}
    if status is not None:
        declaration["status"] = status
    if status_reason is not None:
        if not status_reason:
            raise DeclarationError("statusReason must not be empty")
        declaration["statusReason"] = status_reason
    if document_revision is not None:
        if not document_revision:
            raise DeclarationError("documentRevision must not be empty")
        declaration["documentRevision"] = document_revision
    if observed_at is not None:
        if not observed_at:
            raise DeclarationError("observedAt must not be empty")
        declaration["observedAt"] = observed_at
    return declaration


def disclosure_declaration(
    *, scope: str | None = None, policy_ref: str | None = None
) -> dict[str, str]:
    """Build the optional top-level `disclosure` object.

    Omitted arguments produce an empty object, which the caller should omit
    entirely rather than write as `{}`; an absent key means "no document-level
    restriction", while an explicit scope is a claim the producer must own.
    """
    if scope is not None and scope not in DISCLOSURE_SCOPES:
        raise DeclarationError(f"scope must be one of {', '.join(DISCLOSURE_SCOPES)}")
    declaration: dict[str, str] = {}
    if scope is not None:
        declaration["scope"] = scope
    if policy_ref is not None:
        if not policy_ref:
            raise DeclarationError("policyRef must not be empty")
        declaration["policyRef"] = policy_ref
    return declaration


def apply_declarations(
    artifact: dict,
    *,
    source: dict[str, str] | None = None,
    disclosure: dict[str, str] | None = None,
) -> dict:
    """Return a copy of `artifact` with the declarations merged in.

    Only non-empty maps are written. The input is not mutated, so a caller can
    keep the undeclared artifact and write the declared one separately.
    """
    if not isinstance(artifact, dict):
        raise DeclarationError("artifact must be a JSON object")
    copy = {
        key: value for key, value in artifact.items() if key not in {"source", "disclosure"}
    }
    merged_source = dict(artifact.get("source") or {})
    if source:
        merged_source.update(source)
    copy["source"] = merged_source
    if disclosure:
        merged_disclosure = dict(artifact.get("disclosure") or {})
        merged_disclosure.update(disclosure)
        copy["disclosure"] = merged_disclosure
    elif "disclosure" in artifact:
        copy["disclosure"] = artifact["disclosure"]
    return copy
