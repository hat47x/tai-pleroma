package main

import (
	"crypto/sha256"
	"fmt"
	"reflect"
	"strings"
	"testing"
)

// withoutBasis returns the bundle with every Decision's basis_refs emptied.
func withoutBasis(t *testing.T, raw []byte) []byte {
	t.Helper()
	bundle := decodeJSON(t, raw)
	for _, rec := range bundle["records"].([]any) {
		if decision, ok := rec.(map[string]any)["payload"].(map[string]any)["decision"].(map[string]any); ok {
			decision["basis_refs"] = []any{}
		}
	}
	return encodeJSON(t, bundle)
}

// A named Decision that cannot be compared with the current target (no ExactBinding in its basis, which is
// the shape the SEI CLI's `add decision` writes) must not read as "reacceptance required": the check does not
// know, so both flags stay unconfirmed and the reason is a blocking item.
func TestValidityNamedDecisionWithoutExactBasisLeavesFlagsUnconfirmed(t *testing.T) {
	for name, raw := range map[string][]byte{
		"logical basis only": fixture(t, "t-logical-basis-only"),
		"no basis at all":    withoutBasis(t, fixture(t, "t-a")),
	} {
		for label, tgt := range map[string][]byte{"A": tgtA(), "A-prime": tgtAPrime()} {
			r := must(t, raw, tgt, nameD1)
			var d DecisionValidity
			for _, candidate := range r.Decisions {
				d = candidate
			}
			if d.State != "no-exact-basis" || !d.Named || d.StructurallyBoundToCurrentTarget {
				t.Fatalf("%s/%s: %+v", name, label, d)
			}
			if !hasCode(r, "named-decision-has-no-exact-basis", true) || r.StructurallyBoundToCurrentTarget != nil || r.ReacceptanceRequired != nil {
				t.Fatalf("%s/%s: a named Decision that cannot be compared must leave both flags unconfirmed: %+v", name, label, r)
			}
		}
	}

	// naming a comparable bound Decision next to one that cannot be compared stays unconfirmed (the check does not
	// pick the one that counts), like a named Decision that is missing from the bundle
	bundle := decodeJSON(t, fixture(t, "t-ap-scope-reaccepted"))
	oldDecision := recordByID(t, bundle, "rec-d1")["payload"].(map[string]any)["decision"].(map[string]any)
	oldDecision["basis_refs"] = []any{map[string]any{"kind": "artifact", "id": "guidance-draft", "scope": "source-v1"}}
	r := must(t, encodeJSON(t, bundle), tgtAPrime(), nameD1, nameD3)
	if !hasCode(r, "named-decision-has-no-exact-basis", true) || r.StructurallyBoundToCurrentTarget != nil || r.ReacceptanceRequired != nil ||
		!reflect.DeepEqual(r.BoundDecisionRecordIDs, []string{"rec-d3"}) {
		t.Fatalf("%+v", r)
	}

	// controls: only a Decision that is named counts, and a comparable Decision is never reported this way
	if r := must(t, fixture(t, "t-logical-basis-only"), tgtA()); hasCode(r, "named-decision-has-no-exact-basis", true) || !hasCode(r, "no-decision-named", true) {
		t.Fatalf("an unnamed Decision must not be reported as the acceptance in question: %+v", r.Unresolved)
	}
	other := decodeJSON(t, fixture(t, "t-logical-basis-only"))["records"].([]any)[0].(map[string]any)
	other["record_id"] = "rec-other"
	other["logical_ref"].(map[string]any)["id"] = "dec-other"
	other["payload"].(map[string]any)["decision"].(map[string]any)["ref"].(map[string]any)["id"] = "dec-other"
	bundle = decodeJSON(t, fixture(t, "t-a"))
	bundle["records"] = append(bundle["records"].([]any), other)
	r = must(t, encodeJSON(t, bundle), tgtA(), nameD1)
	if byID(t, r, "rec-other").State != "no-exact-basis" || hasCode(r, "named-decision-has-no-exact-basis", true) ||
		!isTrue(r.StructurallyBoundToCurrentTarget) {
		t.Fatalf("an unnamed Decision that cannot be compared must not block the named bound Decision: %+v", r)
	}
	for _, tgt := range [][]byte{tgtA(), tgtAPrime()} {
		for _, name := range []string{"t-a", "t-b-embedded-supersedes", "t-ap-scope-reaccepted"} {
			if r := must(t, fixture(t, name), tgt, nameD1); hasCode(r, "named-decision-has-no-exact-basis", true) {
				t.Fatalf("%s: a Decision with an ExactBinding basis is comparable: %+v", name, r.Unresolved)
			}
		}
	}
}

// A named Decision whose ExactBindings all name another artifact than the current target does not concern the
// target at all. The flags keep their documented meaning (nothing named is bound, so reacceptanceRequired=true),
// but the output says that the target is another artifact instead of leaving the unresolved list empty.
func TestValidityNamedDecisionOfAnotherArtifactIsReported(t *testing.T) {
	for name, tgt := range map[string][]byte{
		"another id":   target("artifact", "totally-unrelated", "source-v1", digA, "sei.raw-bytes+sha256"),
		"another kind": target("document", "guidance-draft", "source-v1", digA, "sei.raw-bytes+sha256"),
	} {
		r := must(t, fixture(t, "t-a"), tgt, nameD1)
		if d1 := byID(t, r, "rec-d1"); d1.State != "basis-differs" || d1.StructurallyBoundToCurrentTarget {
			t.Fatalf("%s: %+v", name, d1)
		}
		if !hasCode(r, "named-decision-basis-other-identity", false) || hasAnyBlocking(r) || !isFalse(r.StructurallyBoundToCurrentTarget) || !isTrue(r.ReacceptanceRequired) {
			t.Fatalf("%s: %+v", name, r)
		}
	}
	// controls: the same logical identity under another scope, digest, profile or an unspecified scope is the
	// ordinary "the ExactBinding differs" case and is not reported as another artifact
	for name, tgt := range map[string][]byte{
		"another scope":       target("artifact", "guidance-draft", "source-v9", digA, "sei.raw-bytes+sha256"),
		"scope unspecified":   target("artifact", "guidance-draft", "", digA, "sei.raw-bytes+sha256"),
		"another digest":      target("artifact", "guidance-draft", "source-v1", digB, "sei.raw-bytes+sha256"),
		"another profile":     target("artifact", "guidance-draft", "source-v1", digA, "sei.jcs+sha256"),
		"another version too": targetWithVersion("artifact", "guidance-draft", "source-v1", digA, "sei.raw-bytes+sha256", "v2"),
	} {
		r := must(t, fixture(t, "t-a"), tgt, nameD1)
		if d1 := byID(t, r, "rec-d1"); d1.State != "basis-differs" || hasCode(r, "named-decision-basis-other-identity", false) || !isTrue(r.ReacceptanceRequired) {
			t.Fatalf("%s: %+v", name, r)
		}
	}
	// only a named Decision is reported
	if r := must(t, fixture(t, "t-a"), target("artifact", "totally-unrelated", "source-v1", digA, "sei.raw-bytes+sha256")); hasCode(r, "named-decision-basis-other-identity", false) {
		t.Fatalf("%+v", r.Unresolved)
	}
}

// The comparison is Go string equality: no case folding and no trimming, in any of the six components
// and in the identity match of a lineage endpoint.
func TestValidityComparisonDoesNotFoldCaseOrTrim(t *testing.T) {
	base := map[string]string{"kind": "artifact", "id": "guidance-draft", "scope": "source-v1", "digest": digA, "profile": "sei.raw-bytes+sha256", "version": "v1alpha1"}
	want := map[string]string{"kind": "logical_ref.kind", "id": "logical_ref.id", "scope": "logical_ref.scope", "digest": "content_digest",
		"profile": "representation_profile.profile_id", "version": "representation_profile.version"}
	for key, field := range want {
		for variant, value := range map[string]string{"upper": strings.ToUpper(base[key]), "trailing space": base[key] + " ", "leading space": " " + base[key]} {
			p := map[string]string{}
			for k, v := range base {
				p[k] = v
			}
			p[key] = value
			tgt := targetWithVersion(p["kind"], p["id"], p["scope"], p["digest"], p["profile"], p["version"])
			r := must(t, fixture(t, "t-a"), tgt, nameD1)
			if d1 := byID(t, r, "rec-d1"); d1.State != "basis-differs" || !reflect.DeepEqual(basis(t, d1).DifferingFields, []string{field}) {
				t.Fatalf("%s/%s: %+v", key, variant, d1)
			}
		}
	}

	raw := fixture(t, "x-artifact-supersedes-exact")
	endpoints := func(r ValidityInspection) (same, otherScope int) {
		for _, l := range r.Lineage {
			for _, side := range []string{l.FromCurrentTarget, l.ToCurrentTarget} {
				switch side {
				case identitySame:
					same++
				case identityOtherScope:
					otherScope++
				}
			}
		}
		return
	}
	if same, _ := endpoints(must(t, raw, tgtA(), nameD1)); same != 1 {
		t.Fatalf("control: the exact target must be the lineage endpoint once, got %d", same)
	}
	for name, tgt := range map[string][]byte{
		"kind case":      target("Artifact", "guidance-draft", "source-v1", digA, "sei.raw-bytes+sha256"),
		"id case":        target("artifact", "Guidance-Draft", "source-v1", digA, "sei.raw-bytes+sha256"),
		"id trailing":    target("artifact", "guidance-draft ", "source-v1", digA, "sei.raw-bytes+sha256"),
		"scope case":     target("artifact", "guidance-draft", "SOURCE-V1", digA, "sei.raw-bytes+sha256"),
		"scope trailing": target("artifact", "guidance-draft", "source-v1 ", digA, "sei.raw-bytes+sha256"),
	} {
		r := must(t, raw, tgt, nameD1)
		same, otherScope := endpoints(r)
		kindOrID := strings.HasPrefix(name, "kind") || strings.HasPrefix(name, "id")
		if same != 0 || (kindOrID && otherScope != 0) || (!kindOrID && (otherScope == 0 || !hasCode(r, "closing-lineage-endpoint-other-scope", false))) {
			t.Fatalf("%s: a case or whitespace variant must not be the same identity (same=%d otherScope=%d): %+v", name, same, otherScope, r.Lineage)
		}
		if d1 := byID(t, r, "rec-d1"); d1.State != "basis-differs" || d1.ClosingLineageReferenced {
			t.Fatalf("%s: %+v", name, d1)
		}
	}

	// a Decision endpoint is matched exactly too: another letter case is another Decision (reported as having no record)
	bundle := decodeJSON(t, fixture(t, "t-b-embedded-supersedes"))
	eachLineage(bundle, func(lineage map[string]any) {
		for _, side := range []string{"from", "to"} {
			if ref, ok := lineage[side].(map[string]any); ok && ref["id"] == "dec-accept-1" {
				ref["id"] = "DEC-ACCEPT-1"
			}
		}
	})
	r := must(t, encodeJSON(t, bundle), tgtA(), nameD1)
	if d1 := byID(t, r, "rec-d1"); d1.ClosingLineageReferenced || !hasCode(r, "lineage-endpoint-has-no-decision-record", false) {
		t.Fatalf("%+v", r)
	}
}

// A re-acceptance recorded as a Decision that supersedes or withdraws the old one is closed by the same rule
// as the old Decision, because the check never assumes a lineage direction. This pins the current limit: it is
// a false positive of reacceptanceRequired=true, not a statement that re-acceptance is missing. Change it on purpose
// when SEI defines the direction.
func TestValidityReacceptanceThatSupersedesTheOldDecisionIsClosedToo(t *testing.T) {
	bundle := decodeJSON(t, fixture(t, "t-ap-scope-reaccepted"))
	recordByID(t, bundle, "rec-d3")["payload"].(map[string]any)["decision"].(map[string]any)["lineage"] = map[string]any{"relation": "supersedes",
		"from": map[string]string{"kind": "decision", "id": "dec-accept-2"}, "to": map[string]string{"kind": "decision", "id": "dec-accept-1"}}
	raw := encodeJSON(t, bundle)
	r := must(t, raw, tgtAPrime(), nameD1, nameD3)
	if d3 := byID(t, r, "rec-d3"); d3.State != "closing-lineage-referenced" || d3.StructurallyBoundToCurrentTarget || !d3.ClosingLineageReferenced {
		t.Fatalf("D3: %+v", d3)
	}
	if len(r.BoundDecisionRecordIDs) != 0 || !isFalse(r.StructurallyBoundToCurrentTarget) || !isTrue(r.ReacceptanceRequired) || hasAnyBlocking(r) {
		t.Fatalf("%+v", r)
	}
	// the same re-acceptance recorded with revises is the only recorded form that stays bound (TAI's provisional assumption)
	if r := must(t, fixture(t, "t-ap-scope-reaccepted"), tgtAPrime(), nameD1, nameD3); !isTrue(r.StructurallyBoundToCurrentTarget) {
		t.Fatalf("%+v", r)
	}
}

// Defences of the pure extraction that the SEI path never reaches (SEI verify rejects these first).
func TestValidityRejectsUnsupportedOrDuplicateRecords(t *testing.T) {
	mutate := func(fn func(bundle map[string]any)) []byte {
		bundle := decodeJSON(t, fixture(t, "t-ap-scope-reaccepted"))
		fn(bundle)
		return encodeJSON(t, bundle)
	}
	records := func(bundle map[string]any) []any { return bundle["records"].([]any) }
	for name, raw := range map[string][]byte{
		"another interchange contract": mutate(func(b map[string]any) { b["contract"] = "sei.semantic-interchange/v2" }),
		"empty bundle id":              mutate(func(b map[string]any) { b["bundle_id"] = "" }),
		"missing bundle id":            mutate(func(b map[string]any) { delete(b, "bundle_id") }),
		"empty record id":              mutate(func(b map[string]any) { records(b)[0].(map[string]any)["record_id"] = "" }),
		"duplicate record id": mutate(func(b map[string]any) {
			records(b)[1].(map[string]any)["record_id"] = records(b)[0].(map[string]any)["record_id"]
		}),
	} {
		if _, err := validityFromSnapshot(raw, tgtA(), []string{nameD1}); err == nil {
			t.Fatalf("%s accepted", name)
		}
	}
	if _, err := validityFromSnapshot(mutate(func(b map[string]any) {}), tgtA(), []string{nameD1}); err != nil {
		t.Fatalf("control: %v", err)
	}
}

// The pure extraction accepts what SEI alone rejects, so it must keep such a lineage visible and blocking.
func TestValidityPureExtractionKeepsMalformedLineageBlocking(t *testing.T) {
	r := must(t, fixture(t, "bad-relation"), tgtA(), nameD1)
	if !hasCode(r, "lineage-relation-unknown", true) || r.StructurallyBoundToCurrentTarget != nil || r.ReacceptanceRequired != nil {
		t.Fatalf("an unknown lineage relation must block: %+v", r)
	}
	// a lineage endpoint that is neither a logical nor a complete exact reference
	bundle := decodeJSON(t, fixture(t, "t-b-embedded-supersedes"))
	eachLineage(bundle, func(lineage map[string]any) { lineage["to"] = map[string]any{"kind": "decision"} })
	r = must(t, encodeJSON(t, bundle), tgtA(), nameD1)
	if !hasCode(r, "invalid-reference", true) || r.StructurallyBoundToCurrentTarget != nil || r.ReacceptanceRequired != nil {
		t.Fatalf("an incomplete lineage endpoint must block: %+v", r)
	}
}

// A Decision whose other basis is a logical reference is closed through that reference too.
func TestValidityLogicalOtherBasisIsClosedByLineage(t *testing.T) {
	bundle := decodeJSON(t, fixture(t, "x-other-basis-closed"))
	basisRefs := recordByID(t, bundle, "rec-d1")["payload"].(map[string]any)["decision"].(map[string]any)["basis_refs"].([]any)
	basisRefs[1] = map[string]any{"kind": "artifact", "id": "annex", "scope": "x1"}
	r := must(t, encodeJSON(t, bundle), tgtA(), nameD1)
	d1 := byID(t, r, "rec-d1")
	if d1.State != "closing-lineage-referenced" || len(d1.LineageReferences) != 1 || d1.LineageReferences[0].Via != "other-basis" || !isTrue(r.ReacceptanceRequired) {
		t.Fatalf("%+v", r)
	}
}

// What the report says about its own origin and its shape.
func TestValidityReportProvenanceAndShape(t *testing.T) {
	raw := fixture(t, "t-b-standalone-withdraws")
	r := must(t, raw, tgtA(), nameD1)
	if want := fmt.Sprintf("sha256:%x", sha256.Sum256(raw)); r.SourceDigest != want {
		t.Fatalf("sourceDigest %s, want the SHA-256 of the input bytes %s", r.SourceDigest, want)
	}
	if r.CurrentTargetSource != "caller-supplied" || r.BundleID == "" || r.RecordCount != 3 {
		t.Fatalf("%+v", r)
	}
	if !isFalse(r.StructurallyBoundToCurrentTarget) || !isTrue(r.ReacceptanceRequired) {
		t.Fatalf("this fixture is meant to be unbound so that no flag is null: %+v", r)
	}
	// nothing that has no value is encoded as null, so a reader can tell "empty" from "unconfirmed"
	enc := string(encodeJSON(t, r))
	if strings.Contains(enc, ":null") || !strings.Contains(enc, `"unresolvedRefs":[]`) || !strings.Contains(enc, `"uninterpretedRecordIds":[]`) {
		t.Fatalf("%s", enc)
	}
}
