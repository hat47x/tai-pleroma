package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"reflect"
	"strings"
	"testing"
)

var (
	digA = fmt.Sprintf("sha256:%x", sha256.Sum256([]byte("synthetic text A")))
	digB = fmt.Sprintf("sha256:%x", sha256.Sum256([]byte("synthetic text B")))
)

const (
	nameD1 = "decision:dec-accept-1"
	nameD3 = "decision:dec-accept-2"
)

func fixture(t *testing.T, name string) []byte {
	t.Helper()
	raw, err := os.ReadFile(filepath.Join("testdata", "validity", name+".json"))
	if err != nil {
		t.Fatal(err)
	}
	return raw
}

func target(kind, id, scope, digest, profile string) []byte {
	return targetWithVersion(kind, id, scope, digest, profile, "v1alpha1")
}

func targetWithVersion(kind, id, scope, digest, profile, version string) []byte {
	logical := map[string]string{"kind": kind, "id": id}
	if scope != "" {
		logical["scope"] = scope
	}
	raw, err := json.Marshal(map[string]any{"logical_ref": logical, "content_digest": digest,
		"representation_profile": map[string]string{"profile_id": profile, "version": version}})
	if err != nil {
		panic(err)
	}
	return raw
}

// tgtAPrime is the same text as D1's basis under another source/version scope (the TAI synthetic convention).
func tgtAPrime() []byte {
	return target("artifact", "guidance-draft", "source-v3", digA, "sei.raw-bytes+sha256")
}

// tgtA is the very same ExactBinding as D1's basis.
func tgtA() []byte {
	return target("artifact", "guidance-draft", "source-v1", digA, "sei.raw-bytes+sha256")
}

func hasCode(r ValidityInspection, code string, blocking bool) bool {
	for _, item := range r.Unresolved {
		if item.Code == code && item.Blocking == blocking {
			return true
		}
	}
	return false
}

func hasAnyBlocking(r ValidityInspection) bool {
	for _, item := range r.Unresolved {
		if item.Blocking {
			return true
		}
	}
	return false
}

// must runs the pure extraction and checks the invariants that hold for every report.
func must(t *testing.T, raw, tgt []byte, names ...string) ValidityInspection {
	t.Helper()
	r, err := validityFromSnapshot(raw, tgt, names)
	if err != nil {
		t.Fatal(err)
	}
	if r.RecordStructureChecked || r.ExactTargetsVerified || r.HumanReviewed || r.AuthorityVerified || r.PublicationApproved {
		t.Fatal("pure extraction overclaimed")
	}
	if r.ReacceptanceRequired != nil && !*r.ReacceptanceRequired {
		t.Fatalf("reacceptanceRequired=false would read as 'the acceptance continues': %+v", r)
	}
	if hasAnyBlocking(r) && (r.StructurallyBoundToCurrentTarget != nil || r.ReacceptanceRequired != nil) {
		t.Fatalf("a blocking item must leave both flags unconfirmed: %+v", r)
	}
	if isTrue(r.StructurallyBoundToCurrentTarget) && (r.ReacceptanceRequired != nil || !hasCode(r, "acceptance-validity-unconfirmed", false)) {
		t.Fatalf("a structural binding must stay unconfirmed as an acceptance: %+v", r)
	}
	return r
}

func byID(t *testing.T, r ValidityInspection, id string) DecisionValidity {
	t.Helper()
	for _, d := range r.Decisions {
		if d.RecordID == id {
			return d
		}
	}
	t.Fatalf("no decision record %s", id)
	return DecisionValidity{}
}

// basis returns the first basis comparison of a Decision, failing instead of panicking when there is none.
func basis(t *testing.T, d DecisionValidity) BasisComparison {
	t.Helper()
	if len(d.Basis) == 0 {
		t.Fatalf("decision %s has no basis comparison", d.RecordID)
	}
	return d.Basis[0]
}

// String keeps failure messages readable: the reports hold raw JSON fragments.
func (r ValidityInspection) String() string { return jsonString(r) }
func (d DecisionValidity) String() string   { return jsonString(d) }

func jsonString(v any) string {
	raw, err := json.Marshal(v)
	if err != nil {
		return err.Error()
	}
	return string(raw)
}

func isTrue(p *bool) bool  { return p != nil && *p }
func isFalse(p *bool) bool { return p != nil && !*p }

// naiveRevive is a comparison written independently of the implementation: it revives every Decision
// whose basis carries the same digest string, ignoring scope, profile and lineage.
func naiveRevive(t *testing.T, raw []byte, digest string) []string {
	t.Helper()
	var b struct {
		Records []struct {
			RecordID string `json:"record_id"`
			Payload  struct {
				Decision *struct {
					Basis []struct {
						ContentDigest string `json:"content_digest"`
					} `json:"basis_refs"`
				} `json:"decision"`
			} `json:"payload"`
		} `json:"records"`
	}
	if err := json.Unmarshal(raw, &b); err != nil {
		t.Fatal(err)
	}
	out := []string{}
	for _, r := range b.Records {
		if r.Payload.Decision == nil {
			continue
		}
		for _, ref := range r.Payload.Decision.Basis {
			if ref.ContentDigest == digest {
				out = append(out, r.RecordID)
				break
			}
		}
	}
	return out
}

func decodeJSON(t *testing.T, raw []byte) map[string]any {
	t.Helper()
	var m map[string]any
	if err := json.Unmarshal(raw, &m); err != nil {
		t.Fatal(err)
	}
	return m
}

// jsonEqual compares two JSON texts by value (the report keeps the source fragments, not their whitespace or key order).
func jsonEqual(t *testing.T, got []byte, want string) bool {
	t.Helper()
	var a, b any
	if err := json.Unmarshal(got, &a); err != nil {
		t.Fatal(err)
	}
	if err := json.Unmarshal([]byte(want), &b); err != nil {
		t.Fatal(err)
	}
	return reflect.DeepEqual(a, b)
}

func encodeJSON(t *testing.T, m any) []byte {
	t.Helper()
	raw, err := json.Marshal(m)
	if err != nil {
		t.Fatal(err)
	}
	return raw
}

func recordByID(t *testing.T, bundle map[string]any, id string) map[string]any {
	t.Helper()
	for _, rec := range bundle["records"].([]any) {
		if m := rec.(map[string]any); m["record_id"] == id {
			return m
		}
	}
	t.Fatalf("no record %s", id)
	return nil
}

// eachLineage visits every lineage object in a bundle (embedded in a Decision or a standalone semantic_lineage record).
func eachLineage(bundle map[string]any, fn func(lineage map[string]any)) {
	for _, rec := range bundle["records"].([]any) {
		payload, _ := rec.(map[string]any)["payload"].(map[string]any)
		if decision, ok := payload["decision"].(map[string]any); ok {
			if lineage, ok := decision["lineage"].(map[string]any); ok {
				fn(lineage)
			}
		}
		if lineage, ok := payload["semantic_lineage"].(map[string]any); ok {
			fn(lineage)
		}
	}
}

func swapLineageDirection(t *testing.T, raw []byte) []byte {
	t.Helper()
	bundle := decodeJSON(t, raw)
	swapped := 0
	eachLineage(bundle, func(lineage map[string]any) {
		lineage["from"], lineage["to"] = lineage["to"], lineage["from"]
		swapped++
	})
	if swapped == 0 {
		t.Fatal("fixture has no lineage to swap")
	}
	return encodeJSON(t, bundle)
}

func TestValidityScopeDiffersDigestEqualIsNotBound(t *testing.T) {
	raw := fixture(t, "t-b-embedded-supersedes")
	if got := naiveRevive(t, raw, digA); !reflect.DeepEqual(got, []string{"rec-d1"}) {
		t.Fatalf("a digest-only comparison would not revive D1, so this negative is meaningless: %v", got)
	}
	r := must(t, raw, tgtAPrime(), nameD1)
	d1 := byID(t, r, "rec-d1")
	if d1.State != "basis-differs" || d1.StructurallyBoundToCurrentTarget || !d1.DigestOnlyMatch ||
		!reflect.DeepEqual(basis(t, d1).DifferingFields, []string{"logical_ref.scope"}) || !basis(t, d1).DigestEqualsTarget {
		t.Fatalf("D1: %+v", d1)
	}
	if !reflect.DeepEqual(r.DigestOnlyMatchRecordIDs, []string{"rec-d1"}) || !reflect.DeepEqual(r.DigestOnlyMatchButNotBoundIDs, []string{"rec-d1"}) ||
		len(r.BoundDecisionRecordIDs) != 0 || !isFalse(r.StructurallyBoundToCurrentTarget) || !isTrue(r.ReacceptanceRequired) {
		t.Fatalf("report: %+v", r)
	}
}

// The scope difference alone keeps D1 unbound. A bundle that never recorded B gives the same result, so this
// is not a demonstration that A -> B -> A' was handled: it shows that the ExactBinding differs.
func TestValidityScopeMismatchDoesNotDependOnAnEarlierB(t *testing.T) {
	withB := must(t, fixture(t, "t-b-embedded-supersedes"), tgtAPrime(), nameD1)
	withoutB := must(t, fixture(t, "t-a"), tgtAPrime(), nameD1)
	b, a := byID(t, withB, "rec-d1"), byID(t, withoutB, "rec-d1")
	if !reflect.DeepEqual(b.Basis, a.Basis) || b.State != a.State || b.StructurallyBoundToCurrentTarget != a.StructurallyBoundToCurrentTarget ||
		!reflect.DeepEqual(withB.DigestOnlyMatchButNotBoundIDs, withoutB.DigestOnlyMatchButNotBoundIDs) ||
		!isTrue(withoutB.ReacceptanceRequired) || !isFalse(withoutB.StructurallyBoundToCurrentTarget) {
		t.Fatalf("with B: %+v\nwithout B: %+v", withB, withoutB)
	}
	if len(withoutB.Lineage) != 0 || len(withoutB.DigestOnlyMatchButNotBoundIDs) != 1 {
		t.Fatalf("the no-B bundle must carry no lineage yet still report D1 unbound: %+v", withoutB)
	}
}

func TestValidityNewDecisionIsBoundOnlyWhenNamed(t *testing.T) {
	raw := fixture(t, "t-ap-scope-reaccepted")
	r := must(t, raw, tgtAPrime(), nameD1, nameD3)
	if !reflect.DeepEqual(r.BoundDecisionRecordIDs, []string{"rec-d3"}) || !isTrue(r.StructurallyBoundToCurrentTarget) || r.ReacceptanceRequired != nil {
		t.Fatalf("report: %+v", r)
	}
	if !reflect.DeepEqual(r.DigestOnlyMatchButNotBoundIDs, []string{"rec-d1"}) {
		t.Fatalf("D1 must stay digest-only-matched but unbound: %v", r.DigestOnlyMatchButNotBoundIDs)
	}
	if !hasCode(r, "revises-referenced", false) || !hasCode(r, "acceptance-validity-unconfirmed", false) {
		t.Fatalf("the bound D3 is a revises endpoint and its acceptance stays unconfirmed: %+v", r.Unresolved)
	}
	// naming only the old decision keeps a new decision from counting, even though it is bound
	r = must(t, raw, tgtAPrime(), nameD1)
	if !isTrue(r.ReacceptanceRequired) || !isFalse(r.StructurallyBoundToCurrentTarget) {
		t.Fatalf("report: %+v", r)
	}
	if d3 := byID(t, r, "rec-d3"); d3.ClosingLineageReferenced || d3.State != "bound" || d3.Named {
		t.Fatalf("D3: %+v", d3)
	}
}

func TestValidityIdenticalBindingIsClosedByRecordedDecisionLineage(t *testing.T) {
	for _, name := range []string{"t-b-embedded-supersedes", "t-b-standalone-withdraws"} {
		t.Run(name, func(t *testing.T) {
			r := must(t, fixture(t, name), tgtA(), nameD1)
			d1 := byID(t, r, "rec-d1")
			if !d1.BasisEqualsCurrentTarget || !d1.ClosingLineageReferenced || d1.State != "closing-lineage-referenced" || d1.StructurallyBoundToCurrentTarget {
				t.Fatalf("D1: %+v", d1)
			}
			if !reflect.DeepEqual(r.DigestOnlyMatchButNotBoundIDs, []string{"rec-d1"}) || !isTrue(r.ReacceptanceRequired) || !isFalse(r.StructurallyBoundToCurrentTarget) {
				t.Fatalf("report: %+v", r)
			}
		})
	}
	r := must(t, fixture(t, "t-ap-identical-reaccepted"), tgtA(), nameD1, nameD3)
	if !reflect.DeepEqual(r.BoundDecisionRecordIDs, []string{"rec-d3x"}) || !isTrue(r.StructurallyBoundToCurrentTarget) || r.ReacceptanceRequired != nil {
		t.Fatalf("report: %+v", r)
	}
	if d1 := byID(t, r, "rec-d1"); d1.State != "closing-lineage-referenced" {
		t.Fatalf("D1: %+v", d1)
	}
}

// SEI defines lineage as a relation between Artifacts. A closing lineage whose endpoint is the current target
// must not leave a Decision bound to that target, whichever side the endpoint is on.
func TestValidityArtifactLevelClosingLineageClosesTheBinding(t *testing.T) {
	for _, name := range []string{"x-artifact-supersedes-exact", "x-artifact-withdraws-logical"} {
		for _, swapped := range []bool{false, true} {
			t.Run(fmt.Sprintf("%s/swapped=%v", name, swapped), func(t *testing.T) {
				raw := fixture(t, name)
				if swapped {
					raw = swapLineageDirection(t, raw)
				}
				r := must(t, raw, tgtA(), nameD1)
				d1 := byID(t, r, "rec-d1")
				if !d1.BasisEqualsCurrentTarget || !d1.ClosingLineageReferenced || d1.State != "closing-lineage-referenced" || d1.StructurallyBoundToCurrentTarget {
					t.Fatalf("D1 stayed bound to a target that a closing lineage names: %+v", d1)
				}
				if len(d1.LineageReferences) != 1 || d1.LineageReferences[0].Via != "basis-matching-current-target" || !d1.LineageReferences[0].Closing {
					t.Fatalf("the closing reference must be reported: %+v", d1.LineageReferences)
				}
				if !reflect.DeepEqual(r.DigestOnlyMatchButNotBoundIDs, []string{"rec-d1"}) || !isTrue(r.ReacceptanceRequired) || !isFalse(r.StructurallyBoundToCurrentTarget) {
					t.Fatalf("report: %+v", r)
				}
			})
		}
		t.Run(name+"/other scope target", func(t *testing.T) {
			// the lineage names source-v1 and source-v2; a source-v3 target is another scope: reported, not blocking
			r := must(t, fixture(t, name), tgtAPrime(), nameD1)
			if d1 := byID(t, r, "rec-d1"); d1.State != "basis-differs" || d1.ClosingLineageReferenced {
				t.Fatalf("D1: %+v", d1)
			}
			if !hasCode(r, "closing-lineage-endpoint-other-scope", false) || hasAnyBlocking(r) || !isTrue(r.ReacceptanceRequired) {
				t.Fatalf("report: %+v", r)
			}
		})
	}
}

// A Decision that rests on more than one basis is only bound if none of its other basis references is closed either.
func TestValidityClosingLineageOnAnotherBasisClosesTheBinding(t *testing.T) {
	for _, swapped := range []bool{false, true} {
		raw := fixture(t, "x-other-basis-closed")
		if swapped {
			raw = swapLineageDirection(t, raw)
		}
		r := must(t, raw, tgtA(), nameD1)
		d1 := byID(t, r, "rec-d1")
		if !d1.BasisEqualsCurrentTarget || !d1.ClosingLineageReferenced || d1.State != "closing-lineage-referenced" || d1.StructurallyBoundToCurrentTarget {
			t.Fatalf("swapped=%v: D1 stayed bound although a closing lineage names its annex basis: %+v", swapped, d1)
		}
		if len(d1.LineageReferences) != 1 || d1.LineageReferences[0].Via != "other-basis" || !isTrue(r.ReacceptanceRequired) {
			t.Fatalf("swapped=%v: %+v", swapped, r)
		}
	}
	rewrite := func(annexScope, annexID string) []byte {
		bundle := decodeJSON(t, fixture(t, "x-other-basis-closed"))
		basis := recordByID(t, bundle, "rec-d1")["payload"].(map[string]any)["decision"].(map[string]any)["basis_refs"].([]any)[1].(map[string]any)["logical_ref"].(map[string]any)
		basis["scope"], basis["id"] = annexScope, annexID
		return encodeJSON(t, bundle)
	}
	// controls: the lineage no longer touches the annex basis (another scope, another artifact)
	r := must(t, rewrite("x9", "annex"), tgtA(), nameD1)
	if d1 := byID(t, r, "rec-d1"); d1.State != "bound" || !hasCode(r, "closing-lineage-endpoint-other-scope", false) || hasAnyBlocking(r) {
		t.Fatalf("another scope of the annex is reported, not closed: %+v", r)
	}
	if r := must(t, rewrite("x1", "other-annex"), tgtA(), nameD1); byID(t, r, "rec-d1").State != "bound" || len(r.Unresolved) != 1 {
		t.Fatalf("a lineage on an unrelated artifact must not touch D1: %+v", r)
	}
	// an unscoped annex endpoint may cover every scope of the annex: unconfirmed, not silently ignored
	bundle := decodeJSON(t, fixture(t, "x-other-basis-closed"))
	recordByID(t, bundle, "rec-annex-l")["payload"].(map[string]any)["semantic_lineage"].(map[string]any)["to"] = map[string]any{"kind": "artifact", "id": "annex"}
	if r := must(t, encodeJSON(t, bundle), tgtA(), nameD1); !hasCode(r, "closing-lineage-endpoint-scope-unspecified", true) || r.StructurallyBoundToCurrentTarget != nil || r.ReacceptanceRequired != nil {
		t.Fatalf("an unscoped endpoint on another basis must block: %+v", r)
	}
}

func TestValidityClosingLineageEndpointWithUnspecifiedScopeBlocks(t *testing.T) {
	// decision:dec-accept-1 named under another scope: SEI accepts it, but it cannot be told apart from D1
	r := must(t, fixture(t, "x-decision-endpoint-other-scope"), tgtA(), nameD1)
	if !hasCode(r, "closing-lineage-endpoint-scope-unspecified", true) || r.StructurallyBoundToCurrentTarget != nil || r.ReacceptanceRequired != nil {
		t.Fatalf("report: %+v", r)
	}
	// an unscoped artifact endpoint may cover every scope of the artifact
	bundle := decodeJSON(t, fixture(t, "x-artifact-withdraws-logical"))
	recordByID(t, bundle, "rec-art-l2")["payload"].(map[string]any)["semantic_lineage"].(map[string]any)["to"] = map[string]any{"kind": "artifact", "id": "guidance-draft"}
	for _, tgt := range [][]byte{tgtA(), tgtAPrime()} {
		r := must(t, encodeJSON(t, bundle), tgt, nameD1)
		if !hasCode(r, "closing-lineage-endpoint-scope-unspecified", true) || r.StructurallyBoundToCurrentTarget != nil || r.ReacceptanceRequired != nil {
			t.Fatalf("report: %+v", r)
		}
	}
}

func TestValidityRevisesDoesNotCloseButIsSurfaced(t *testing.T) {
	r := must(t, fixture(t, "t-b-revises-only"), tgtA(), nameD1)
	d1 := byID(t, r, "rec-d1")
	if d1.ClosingLineageReferenced || d1.State != "bound" || !isTrue(r.StructurallyBoundToCurrentTarget) || r.ReacceptanceRequired != nil {
		t.Fatalf("revises must not close in this check: %+v", r)
	}
	if len(d1.LineageReferences) != 1 || d1.LineageReferences[0].Relation != "revises" || d1.LineageReferences[0].Closing {
		t.Fatalf("%+v", d1.LineageReferences)
	}
	// the effect of revises on an acceptance is not defined by SEI: say so instead of staying silent
	if !hasCode(r, "revises-referenced", false) {
		t.Fatalf("a bound Decision that a revises lineage names must be surfaced: %+v", r.Unresolved)
	}
}

func TestValidityUnresolvedRefsOfABoundDecisionAreSurfaced(t *testing.T) {
	bundle := decodeJSON(t, fixture(t, "t-a"))
	decision := recordByID(t, bundle, "rec-d1")["payload"].(map[string]any)["decision"].(map[string]any)
	decision["unresolved_refs"] = []any{map[string]string{"kind": "authority", "id": "unknown"}}
	r := must(t, encodeJSON(t, bundle), tgtA(), nameD1)
	if !isTrue(r.StructurallyBoundToCurrentTarget) || r.ReacceptanceRequired != nil {
		t.Fatalf("report: %+v", r)
	}
	if !hasCode(r, "named-decision-has-unresolved-refs", false) || !hasCode(r, "acceptance-validity-unconfirmed", false) {
		t.Fatalf("unresolved refs of the bound Decision must be surfaced: %+v", r.Unresolved)
	}
	d1 := byID(t, r, "rec-d1")
	if len(d1.UnresolvedRefs) != 1 || !jsonEqual(t, d1.UnresolvedRefs[0], `{"kind":"authority","id":"unknown"}`) {
		t.Fatalf("unresolved refs must pass through unchanged: %s", d1.UnresolvedRefs)
	}
}

// A bundle that anyone can write names the target as a basis. The structural binding says nothing about who
// wrote it, so it never turns into "re-acceptance is not required".
func TestValidityBindingNeverReportsReacceptanceNotRequired(t *testing.T) {
	entries, err := os.ReadDir(filepath.Join("testdata", "validity"))
	if err != nil {
		t.Fatal(err)
	}
	bound := 0
	for _, entry := range entries {
		name := strings.TrimSuffix(entry.Name(), ".json")
		if strings.HasPrefix(name, "target-") {
			continue
		}
		for _, tgt := range [][]byte{tgtA(), tgtAPrime()} {
			for _, names := range [][]string{nil, {nameD1}, {nameD3}, {nameD1, nameD3}, {"decision:dec-reconfirm"}} {
				r := must(t, fixture(t, name), tgt, names...)
				if isTrue(r.StructurallyBoundToCurrentTarget) {
					bound++
				}
			}
		}
	}
	if bound == 0 {
		t.Fatal("the matrix never produced a binding, so it checked nothing")
	}
}

func TestValidityUnrecordedExcursionIsNotDetected(t *testing.T) {
	// Documented limit: the same ExactBinding and no recorded closing lineage. The bundle cannot show that A left.
	r := must(t, fixture(t, "t-a"), tgtA(), nameD1)
	if !isTrue(r.StructurallyBoundToCurrentTarget) || r.ReacceptanceRequired != nil || !reflect.DeepEqual(r.BoundDecisionRecordIDs, []string{"rec-d1"}) {
		t.Fatalf("report: %+v", r)
	}
}

func TestValidityNeverAcceptedIsNotADemonstration(t *testing.T) {
	raw := fixture(t, "t-never-accepted")
	r := must(t, raw, tgtAPrime(), nameD1)
	if len(r.DigestOnlyMatchButNotBoundIDs) != 0 || len(r.DigestOnlyMatchRecordIDs) != 0 || r.ReacceptanceRequired != nil || r.StructurallyBoundToCurrentTarget != nil {
		t.Fatalf("a never-accepted bundle must not look like a demonstrated non-revival: %+v", r)
	}
	if !hasCode(r, "named-decision-not-found", true) {
		t.Fatalf("the missing named decision must stay unresolved: %+v", r.Unresolved)
	}
	if r = must(t, raw, tgtAPrime()); r.ReacceptanceRequired != nil || !hasCode(r, "no-decision-named", true) {
		t.Fatalf("no named decision must stay unresolved: %+v", r)
	}
}

func TestValidityEachExactBindingComponentIsCompared(t *testing.T) {
	raw := fixture(t, "t-a")
	base := map[string]any{"kind": "artifact", "id": "guidance-draft", "scope": "source-v1", "digest": digA, "profile": "sei.raw-bytes+sha256", "version": "v1alpha1"}
	for field, change := range map[string]struct{ key, value, want string }{
		"kind":            {"kind", "document", "logical_ref.kind"},
		"id":              {"id", "other-draft", "logical_ref.id"},
		"scope":           {"scope", "source-v9", "logical_ref.scope"},
		"digest":          {"digest", digB, "content_digest"},
		"profile id":      {"profile", "sei.jcs+sha256", "representation_profile.profile_id"},
		"profile version": {"version", "v2", "representation_profile.version"},
	} {
		t.Run(field, func(t *testing.T) {
			p := map[string]any{}
			for k, v := range base {
				p[k] = v
			}
			p[change.key] = change.value
			tgt := targetWithVersion(p["kind"].(string), p["id"].(string), p["scope"].(string), p["digest"].(string), p["profile"].(string), p["version"].(string))
			r := must(t, raw, tgt, nameD1)
			d1 := byID(t, r, "rec-d1")
			if d1.State != "basis-differs" || d1.StructurallyBoundToCurrentTarget || !reflect.DeepEqual(basis(t, d1).DifferingFields, []string{change.want}) {
				t.Fatalf("one differing component %s must be reported alone: %+v", change.want, d1)
			}
			if !isTrue(r.ReacceptanceRequired) {
				t.Fatalf("%+v", r)
			}
		})
	}
	// control: with no differing component the same binding is bound and nothing differs
	if d1 := byID(t, must(t, raw, tgtA(), nameD1), "rec-d1"); d1.State != "bound" || len(basis(t, d1).DifferingFields) != 0 {
		t.Fatalf("%+v", d1)
	}
}

func TestValidityAbsentScopeEqualsEmptyScopeLikeSEI(t *testing.T) {
	// SEI compares logical identities as Go strings, so an absent scope and an empty scope are the same.
	bundle := decodeJSON(t, fixture(t, "t-a"))
	logical := recordByID(t, bundle, "rec-d1")["payload"].(map[string]any)["decision"].(map[string]any)["basis_refs"].([]any)[0].(map[string]any)["logical_ref"].(map[string]any)
	logical["scope"] = ""
	emptyScope := encodeJSON(t, bundle)
	delete(logical, "scope")
	absentScope := encodeJSON(t, bundle)
	absentTarget := target("artifact", "guidance-draft", "", digA, "sei.raw-bytes+sha256")
	emptyTarget := []byte(`{"logical_ref":{"kind":"artifact","id":"guidance-draft","scope":""},"content_digest":"` + digA + `","representation_profile":{"profile_id":"sei.raw-bytes+sha256","version":"v1alpha1"}}`)
	for name, c := range map[string]struct{ bundle, target []byte }{
		"empty bundle scope, absent target scope": {emptyScope, absentTarget},
		"absent bundle scope, empty target scope": {absentScope, emptyTarget},
	} {
		if d1 := byID(t, must(t, c.bundle, c.target, nameD1), "rec-d1"); d1.State != "bound" || len(basis(t, d1).DifferingFields) != 0 {
			t.Fatalf("%s: %+v", name, d1)
		}
	}
	// but a scope is never invented from nothing
	if d1 := byID(t, must(t, absentScope, tgtA(), nameD1), "rec-d1"); d1.State != "basis-differs" {
		t.Fatalf("%+v", d1)
	}
}

func TestValidityNotComparableBases(t *testing.T) {
	r := must(t, fixture(t, "t-ap-different-profile"), tgtA(), nameD1)
	if d := byID(t, r, "rec-d1p"); d.State != "basis-differs" || !d.DigestOnlyMatch ||
		!reflect.DeepEqual(basis(t, d).DifferingFields, []string{"representation_profile.profile_id"}) {
		t.Fatalf("%+v", d)
	}
	r = must(t, fixture(t, "t-logical-basis-only"), tgtA(), nameD1)
	if d := byID(t, r, "rec-dl"); d.State != "no-exact-basis" || basis(t, d).Relation != "not-comparable" || d.StructurallyBoundToCurrentTarget {
		t.Fatalf("%+v", d)
	}
	// not comparable is not "unbound": both flags stay unconfirmed (the shape the SEI CLI's `add decision` writes)
	if !hasCode(r, "named-decision-has-no-exact-basis", true) || r.StructurallyBoundToCurrentTarget != nil || r.ReacceptanceRequired != nil {
		t.Fatalf("%+v", r)
	}
	// another artifact with the same digest (the SCN-001 O-02 vs O-07 shape)
	r = must(t, fixture(t, "t-a"), target("artifact", "other-draft", "source-v1", digA, "sei.raw-bytes+sha256"), nameD1)
	if d := byID(t, r, "rec-d1"); !reflect.DeepEqual(basis(t, d).DifferingFields, []string{"logical_ref.id"}) || d.StructurallyBoundToCurrentTarget || !d.DigestOnlyMatch {
		t.Fatalf("%+v", d)
	}
	// digest case is not folded
	r = must(t, fixture(t, "t-a"), target("artifact", "guidance-draft", "source-v1", strings.ToUpper(digA), "sei.raw-bytes+sha256"), nameD1)
	if d := byID(t, r, "rec-d1"); d.StructurallyBoundToCurrentTarget || d.DigestOnlyMatch {
		t.Fatalf("%+v", d)
	}
}

func TestValidityUninterpretedRecordBlocksBound(t *testing.T) {
	r := must(t, fixture(t, "ok-opaque-record"), tgtA(), "decision:dec-reconfirm")
	if r.ReacceptanceRequired != nil || r.StructurallyBoundToCurrentTarget != nil || !reflect.DeepEqual(r.UninterpretedRecordIDs, []string{"rec-opaque"}) || !hasCode(r, "uninterpreted-records", true) {
		t.Fatalf("%+v", r)
	}
}

func TestValidityDuplicateDecisionRefIsAmbiguous(t *testing.T) {
	r := must(t, fixture(t, "ok-duplicate-decision-ref"), tgtA(), nameD1)
	if r.ReacceptanceRequired != nil || len(r.NamedDecisions[0].RecordIDs) != 2 || !hasCode(r, "named-decision-ambiguous", true) {
		t.Fatalf("%+v", r)
	}
	for _, id := range []string{"rec-d1", "rec-d1b"} {
		if !byID(t, r, id).ClosingLineageReferenced {
			t.Fatalf("%s must be treated as referenced by the closing lineage", id)
		}
	}
	if !hasCode(r, "lineage-endpoint-ambiguous", false) {
		t.Fatalf("%+v", r.Unresolved)
	}
}

func TestValidityDanglingEndpointIsInformationOnly(t *testing.T) {
	r := must(t, fixture(t, "ok-dangling-endpoint"), tgtA(), nameD1)
	// from=dec-reconfirm (present), to=dec-not-in-bundle (absent); dec-accept-1 is no longer an endpoint
	if byID(t, r, "rec-d1").ClosingLineageReferenced || !hasCode(r, "lineage-endpoint-has-no-decision-record", false) {
		t.Fatalf("%+v", r)
	}
	if hasAnyBlocking(r) || !isTrue(r.StructurallyBoundToCurrentTarget) {
		t.Fatalf("a dangling endpoint is partial knowledge, not a verdict: %+v", r)
	}
}

func TestValidityCarrierOfEmbeddedLineageIsNotAnEndpoint(t *testing.T) {
	bundle := decodeJSON(t, fixture(t, "t-ap-scope-reaccepted"))
	recordByID(t, bundle, "rec-d3")["payload"].(map[string]any)["decision"].(map[string]any)["lineage"] = map[string]any{"relation": "supersedes",
		"from": map[string]string{"kind": "decision", "id": "dec-reconfirm"}, "to": map[string]string{"kind": "decision", "id": "dec-accept-1"}}
	r := must(t, encodeJSON(t, bundle), tgtAPrime(), nameD3)
	d3 := byID(t, r, "rec-d3")
	if d3.ClosingLineageReferenced || d3.State != "bound" || len(d3.LineageReferences) != 0 {
		t.Fatalf("%+v", d3)
	}
	if !byID(t, r, "rec-d1").ClosingLineageReferenced {
		t.Fatal("D1 is an endpoint of the closing lineage")
	}
}

func TestValidityLineageDirectionDoesNotChangeTheVerdict(t *testing.T) {
	for _, name := range []string{"t-b-embedded-supersedes", "t-b-standalone-withdraws", "x-artifact-supersedes-exact", "x-artifact-withdraws-logical"} {
		for label, tgt := range map[string][]byte{"A": tgtA(), "A-prime": tgtAPrime()} {
			base := must(t, fixture(t, name), tgt, nameD1)
			swapped := must(t, swapLineageDirection(t, fixture(t, name)), tgt, nameD1)
			for i := range base.Decisions {
				if base.Decisions[i].State != swapped.Decisions[i].State {
					t.Fatalf("%s/%s: direction changed the state of %s", name, label, base.Decisions[i].RecordID)
				}
			}
			if !reflect.DeepEqual(base.DigestOnlyMatchButNotBoundIDs, swapped.DigestOnlyMatchButNotBoundIDs) ||
				!reflect.DeepEqual(base.StructurallyBoundToCurrentTarget, swapped.StructurallyBoundToCurrentTarget) ||
				!reflect.DeepEqual(base.ReacceptanceRequired, swapped.ReacceptanceRequired) {
				t.Fatalf("%s/%s: direction changed the verdict: %+v vs %+v", name, label, base, swapped)
			}
		}
	}
}

func TestValidityMissingNamedDecisionBlocks(t *testing.T) {
	r := must(t, fixture(t, "t-ap-scope-reaccepted"), tgtAPrime(), nameD3, "decision:dec-missing")
	if r.ReacceptanceRequired != nil || r.StructurallyBoundToCurrentTarget != nil || !reflect.DeepEqual(r.BoundDecisionRecordIDs, []string{"rec-d3"}) || !hasCode(r, "named-decision-not-found", true) {
		t.Fatalf("%+v", r)
	}
}

func TestValidityRejectsAmbiguousJSON(t *testing.T) {
	raw := string(fixture(t, "t-b-embedded-supersedes"))
	cases := map[string]string{
		"duplicate relation": strings.Replace(raw, `"relation": "supersedes"`, `"relation": "supersedes", "relation": "revises"`, 1),
		"case alias":         strings.Replace(raw, `"relation": "supersedes"`, `"relation": "supersedes", "Relation": "revises"`, 1),
		"trailing":           raw + "{}",
		"invalid utf8":       strings.Replace(raw, "合成: 以前の", "合成: \xff以前の", 1),
	}
	for name, bad := range cases {
		if bad == raw {
			t.Fatalf("%s: no mutation", name)
		}
		if _, err := validityFromSnapshot([]byte(bad), tgtA(), []string{nameD1}); err == nil {
			t.Fatalf("%s accepted", name)
		}
	}
	for name, badTarget := range map[string]string{
		"missing profile": `{"logical_ref":{"kind":"artifact","id":"x"},"content_digest":"sha256:aa"}`,
		"logical only":    `{"kind":"artifact","id":"x"}`,
		"unknown field":   `{"logical_ref":{"kind":"artifact","id":"x"},"content_digest":"d","representation_profile":{"profile_id":"p","version":"v"},"note":"n"}`,
		"duplicate":       `{"logical_ref":{"kind":"artifact","id":"x","id":"y"},"content_digest":"d","representation_profile":{"profile_id":"p","version":"v"}}`,
	} {
		if _, err := validityFromSnapshot([]byte(raw), []byte(badTarget), nil); err == nil {
			t.Fatalf("target %s accepted", name)
		}
	}
	for _, names := range [][]string{{"no-colon"}, {"kind:"}, {nameD1, nameD1}} {
		if _, err := validityFromSnapshot([]byte(raw), tgtA(), names); err == nil {
			t.Fatalf("decision names %v accepted", names)
		}
	}
}

func TestValidityPointersFlagsAndPassThrough(t *testing.T) {
	r := must(t, fixture(t, "t-b-standalone-withdraws"), tgtA(), nameD1)
	if len(r.Lineage) != 1 || r.Lineage[0].JSONPointer != "/records/2/payload/semantic_lineage" || r.Lineage[0].Origin != "semantic_lineage" || !r.Lineage[0].Closing {
		t.Fatalf("%+v", r.Lineage)
	}
	if len(r.Decisions) == 0 || r.Decisions[0].JSONPointer != "/records/0/payload/decision" || basis(t, r.Decisions[0]).JSONPointer != "/records/0/payload/decision/basis_refs/0" {
		t.Fatalf("%+v", r.Decisions)
	}
	if got := r.Decisions[0].ResponsibilityRefs; len(got) != 1 || !jsonEqual(t, got[0], `{"kind":"role","id":"synthetic-reviewer"}`) {
		t.Fatalf("responsibility refs must be passed through unchanged and never read as authority: %s", got)
	}
	enc := string(encodeJSON(t, r))
	for _, want := range []string{`"exactTargetsVerified":false`, `"humanReviewed":false`, `"authorityVerified":false`, `"publicationApproved":false`, `"recordStructureChecked":false`} {
		if !strings.Contains(enc, want) {
			t.Fatalf("missing %s", want)
		}
	}
	if strings.Contains(enc, "statement") || strings.Contains(enc, "合成: Aの内部レビュー") {
		t.Fatal("the Decision statement must not be copied into the report")
	}
	notes := strings.Join(r.Notes, "\n")
	for _, want := range []string{"受理", "未確認", "向き"} {
		if !strings.Contains(notes, want) {
			t.Fatalf("notes must state the limits (%s): %s", want, notes)
		}
	}
}

func TestValidityCommittedTargetFixturesMatchTheInlineTargets(t *testing.T) {
	for name, want := range map[string][]byte{"target-ap-scope": tgtAPrime(), "target-a": tgtA()} {
		got, _, err := decodeCurrentTarget(fixture(t, name))
		if err != nil {
			t.Fatal(err)
		}
		expected, _, err := decodeCurrentTarget(want)
		if err != nil {
			t.Fatal(err)
		}
		if got != expected {
			t.Fatalf("%s: %+v != %+v", name, got, expected)
		}
	}
}

// The exit code only says whether a report was produced. It must not become an allow/deny gate.
func TestValidityExitCodeIsNotAGate(t *testing.T) {
	bound := must(t, fixture(t, "t-ap-scope-reaccepted"), tgtAPrime(), nameD1, nameD3)
	unbound := must(t, fixture(t, "t-b-embedded-supersedes"), tgtAPrime(), nameD1)
	unconfirmed := must(t, fixture(t, "t-never-accepted"), tgtAPrime(), nameD1)
	if !isTrue(bound.StructurallyBoundToCurrentTarget) || !isFalse(unbound.StructurallyBoundToCurrentTarget) || unconfirmed.StructurallyBoundToCurrentTarget != nil {
		t.Fatal("the three reports must differ in the binding they report")
	}
	for name, report := range map[string]ValidityInspection{"bound": bound, "unbound": unbound, "unconfirmed": unconfirmed} {
		var stdout, stderr bytes.Buffer
		if code := emitValidity(report, "", &stdout, &stderr); code != 0 || stdout.Len() == 0 {
			t.Fatalf("%s: a produced report must exit 0 (got %d): %s", name, code, stderr.String())
		}
	}
	// an existing -out file is never overwritten, and then no report is printed
	existing := filepath.Join(t.TempDir(), "report.json")
	if err := os.WriteFile(existing, []byte("keep"), 0600); err != nil {
		t.Fatal(err)
	}
	var stdout, stderr bytes.Buffer
	if code := emitValidity(bound, existing, &stdout, &stderr); code != 2 || stdout.Len() != 0 {
		t.Fatalf("write failure must exit 2 without a report (got %d)", code)
	}
	if after, err := os.ReadFile(existing); err != nil || string(after) != "keep" {
		t.Fatal("the existing file changed")
	}
	// an input that is rejected before SEI runs exits 1 and prints nothing
	dir := t.TempDir()
	badBundle, goodTarget := filepath.Join(dir, "bad.json"), filepath.Join(dir, "target.json")
	if err := os.WriteFile(badBundle, []byte(strings.Replace(string(fixture(t, "t-a")), "合成: Aの内部", "合成: \xffAの内部", 1)), 0600); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(goodTarget, tgtA(), 0600); err != nil {
		t.Fatal(err)
	}
	stdout.Reset()
	stderr.Reset()
	if code := runValidity(context.Background(), t.TempDir(), badBundle, goodTarget, []string{nameD1}, "", &stdout, &stderr); code != 1 || stdout.Len() != 0 || stderr.Len() == 0 {
		t.Fatalf("a rejected input must exit 1 without a report (got %d)", code)
	}
	if code := runValidity(context.Background(), t.TempDir(), filepath.Join(dir, "missing.json"), goodTarget, nil, "", &stdout, &stderr); code != 1 || stdout.Len() != 0 {
		t.Fatalf("an unreadable input must exit 1 (got %d)", code)
	}
}

// The flag wiring and exit codes are part of the interface, so they are checked on the built binary
// (go run does not pass the program's exit status through).
func TestValidityCLIFlagsAndExitCodes(t *testing.T) {
	if _, err := exec.LookPath("go"); err != nil {
		t.Skip("go is not available")
	}
	dir := t.TempDir()
	binary := filepath.Join(dir, "tool")
	if out, err := exec.Command("go", "build", "-o", binary, ".").CombinedOutput(); err != nil {
		t.Fatalf("build: %v: %s", err, out)
	}
	bundle := filepath.Join("testdata", "validity", "t-a.json")
	tgt := filepath.Join("testdata", "validity", "target-a.json")
	badBundle := filepath.Join(dir, "bad.json")
	if err := os.WriteFile(badBundle, append(fixture(t, "t-a"), '{', '}'), 0600); err != nil {
		t.Fatal(err)
	}
	for name, c := range map[string]struct {
		args []string
		want int
	}{
		"missing -current-target":                           {[]string{"-decision-validity", bundle}, 2},
		"-current-target without the mode":                  {[]string{"-current-target", tgt}, 2},
		"-decision without the mode":                        {[]string{"-decision", nameD1}, 2},
		"combined with -basis-bundle":                       {[]string{"-decision-validity", bundle, "-current-target", tgt, "-basis-bundle", bundle}, 2},
		"input rejected (trailing data)":                    {[]string{"-decision-validity", badBundle, "-current-target", tgt, "-decision", nameD1}, 1},
		"invalid decision name":                             {[]string{"-decision-validity", bundle, "-current-target", tgt, "-decision", "no-colon"}, 1},
		"SEI structural check cannot be run":                {[]string{"-sei-root", filepath.Join(dir, "no-sei"), "-decision-validity", bundle, "-current-target", tgt, "-decision", nameD1}, 1},
		"-out file is untouched when no report is produced": {[]string{"-sei-root", filepath.Join(dir, "no-sei"), "-decision-validity", bundle, "-current-target", tgt, "-decision", nameD1, "-out", badBundle}, 1},
	} {
		cmd := exec.Command(binary, c.args...)
		var stdout bytes.Buffer
		cmd.Stdout = &stdout
		err := cmd.Run()
		code := 0
		if exit, ok := err.(*exec.ExitError); ok {
			code = exit.ExitCode()
		} else if err != nil {
			t.Fatalf("%s: %v", name, err)
		}
		if code != c.want || stdout.Len() != 0 {
			t.Fatalf("%s: exit %d (want %d), stdout %q", name, code, c.want, stdout.String())
		}
	}
	if after, err := os.ReadFile(badBundle); err != nil || !bytes.HasSuffix(after, []byte("{}")) {
		t.Fatal("an existing file passed as -out changed")
	}
}

func TestValidityThroughSEIVerify(t *testing.T) {
	root := seiRootForTest(t)
	dir := filepath.Join("testdata", "validity")
	tgt := filepath.Join(t.TempDir(), "target.json")
	if err := os.WriteFile(tgt, tgtAPrime(), 0600); err != nil {
		t.Fatal(err)
	}
	// each case is one `go run ./cmd/sei` (about 25 s): keep the list short
	for name, notVerified := range map[string]int{"t-b-standalone-withdraws": 0, "t-ap-scope-reaccepted": 0, "x-artifact-supersedes-exact": 0, "x-decision-endpoint-other-scope": 0, "ok-opaque-record": 1} {
		r, err := inspectValidity(context.Background(), root, filepath.Join(dir, name+".json"), tgt, []string{nameD3})
		if err != nil {
			t.Fatalf("%s: %v", name, err)
		}
		if !r.RecordStructureChecked || r.SeiCommit == "" || r.NotVerifiedRecordCount != notVerified || r.ExactTargetsVerified || r.HumanReviewed || r.AuthorityVerified || r.PublicationApproved {
			t.Fatalf("%s: %+v", name, r)
		}
	}
}

func TestValidityMalformedLineageRejectedBySEIVerify(t *testing.T) {
	root := seiRootForTest(t)
	tgt := filepath.Join(t.TempDir(), "target.json")
	if err := os.WriteFile(tgt, tgtAPrime(), 0600); err != nil {
		t.Fatal(err)
	}
	for _, name := range []string{"bad-relation", "bad-same-logical-no-exact", "bad-partial-exact-endpoint"} {
		// the pure extraction does not reject these; only the SEI structural check does
		if _, err := validityFromSnapshot(fixture(t, name), tgtAPrime(), []string{nameD1}); err != nil {
			t.Fatalf("%s: the SEI-only rejection test needs a bundle the pure extraction accepts: %v", name, err)
		}
		if _, err := inspectValidity(context.Background(), root, filepath.Join("testdata", "validity", name+".json"), tgt, []string{nameD1}); err == nil {
			t.Fatalf("%s: SEI rejection must surface as an error without a report", name)
		}
	}
}
