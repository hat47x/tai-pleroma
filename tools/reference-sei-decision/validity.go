package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"unicode/utf8"
)

const (
	validitySchema              = "tai.reference.sei-decision-validity/v0"
	decisionMemoryContractID    = "sei.decision-memory"
	semanticReferenceContractID = "sei.semantic-reference"
	seiContractVersion          = "v1alpha1"
)

// Result of comparing a lineage endpoint's logical identity (kind, id, scope) with another identity.
const (
	identityNone             = "none"
	identitySame             = "same-identity"
	identityOtherScope       = "other-scope"
	identityScopeUnspecified = "scope-unspecified"
)

type logicalKey struct{ Kind, ID, Scope string }

type bindingKey struct {
	Logical        logicalKey
	Digest         string
	ProfileID      string
	ProfileVersion string
}

type wireLogical struct {
	Kind  string `json:"kind"`
	ID    string `json:"id"`
	Scope string `json:"scope"`
}

type wireProfile struct {
	ProfileID string `json:"profile_id"`
	Version   string `json:"version"`
}

// wireRef is SEI's Reference union: logical (kind/id/scope) or exact (logical_ref/content_digest/representation_profile).
type wireRef struct {
	Kind                  string       `json:"kind"`
	ID                    string       `json:"id"`
	Scope                 string       `json:"scope"`
	LogicalRef            *wireLogical `json:"logical_ref"`
	ContentDigest         string       `json:"content_digest"`
	RepresentationProfile *wireProfile `json:"representation_profile"`
}

type lineageWire struct {
	Relation string          `json:"relation"`
	From     json.RawMessage `json:"from"`
	To       json.RawMessage `json:"to"`
}

type BasisComparison struct {
	Index              int      `json:"index"`
	JSONPointer        string   `json:"jsonPointer"`
	Form               string   `json:"form"`     // exact | logical | invalid
	Relation           string   `json:"relation"` // equal | differs | not-comparable
	DifferingFields    []string `json:"differingFields"`
	DigestEqualsTarget bool     `json:"digestEqualsTarget"`
}

type LineageReference struct {
	JSONPointer string `json:"jsonPointer"`
	Relation    string `json:"relation"`
	Endpoint    string `json:"endpoint"` // from | to
	Closing     bool   `json:"closing"`
	Via         string `json:"via"` // decision-ref | basis-matching-current-target | other-basis
}

type DecisionValidity struct {
	RecordID                         string             `json:"recordId"`
	JSONPointer                      string             `json:"jsonPointer"`
	DecisionRef                      json.RawMessage    `json:"decisionRef"`
	Named                            bool               `json:"named"`
	Basis                            []BasisComparison  `json:"basis"`
	ResponsibilityRefs               []json.RawMessage  `json:"responsibilityRefs"`
	UnresolvedRefs                   []json.RawMessage  `json:"unresolvedRefs"`
	LineageReferences                []LineageReference `json:"lineageReferences"`
	DigestOnlyMatch                  bool               `json:"digestOnlyMatch"`
	BasisEqualsCurrentTarget         bool               `json:"basisEqualsCurrentTarget"`
	ClosingLineageReferenced         bool               `json:"closingLineageReferenced"`
	StructurallyBoundToCurrentTarget bool               `json:"structurallyBoundToCurrentTarget"`
	State                            string             `json:"state"` // bound | basis-differs | no-exact-basis | closing-lineage-referenced

	logical      logicalKey
	otherBasis   []logicalKey // logical identities of the basis references that are not the current target
	exactSeen    bool
	exactRelated bool // an ExactBinding basis names the current target's kind and id (under any scope)
}

type LineageEntry struct {
	RecordID              string          `json:"recordId"`
	JSONPointer           string          `json:"jsonPointer"`
	Origin                string          `json:"origin"` // decision.lineage | semantic_lineage
	Relation              string          `json:"relation"`
	Closing               bool            `json:"closing"`
	From                  json.RawMessage `json:"from"`
	To                    json.RawMessage `json:"to"`
	FromDecisionRecordIDs []string        `json:"fromDecisionRecordIds"`
	ToDecisionRecordIDs   []string        `json:"toDecisionRecordIds"`
	FromCurrentTarget     string          `json:"fromCurrentTarget"` // identityNone | identitySame | identityOtherScope | identityScopeUnspecified
	ToCurrentTarget       string          `json:"toCurrentTarget"`
}

type NamedDecision struct {
	Ref       string   `json:"ref"`
	RecordIDs []string `json:"recordIds"`
}

type UnresolvedItem struct {
	Code     string `json:"code"`
	Blocking bool   `json:"blocking"`
	Detail   string `json:"detail"`
}

// ValidityInspection is a structural diagnostic. It is not an acceptance, an approval or a new SEI Contract.
type ValidityInspection struct {
	Schema                           string             `json:"schema"`
	SourceDigest                     string             `json:"sourceDigest"`
	SeiCommit                        string             `json:"seiCommit,omitempty"`
	BundleID                         string             `json:"bundleId"`
	RecordCount                      int                `json:"recordCount"`
	NotVerifiedRecordCount           int                `json:"notVerifiedRecordCount"`
	CurrentTarget                    json.RawMessage    `json:"currentTarget"`
	CurrentTargetSource              string             `json:"currentTargetSource"`
	NamedDecisions                   []NamedDecision    `json:"namedDecisions"`
	Decisions                        []DecisionValidity `json:"decisions"`
	Lineage                          []LineageEntry     `json:"lineage"`
	UninterpretedRecordIDs           []string           `json:"uninterpretedRecordIds"`
	BoundDecisionRecordIDs           []string           `json:"boundDecisionRecordIds"`
	DigestOnlyMatchRecordIDs         []string           `json:"digestOnlyMatchRecordIds"`
	DigestOnlyMatchButNotBoundIDs    []string           `json:"digestOnlyMatchButNotBoundRecordIds"`
	StructurallyBoundToCurrentTarget *bool              `json:"structurallyBoundToCurrentTarget"`
	ReacceptanceRequired             *bool              `json:"reacceptanceRequired"`
	Unresolved                       []UnresolvedItem   `json:"unresolved"`
	Notes                            []string           `json:"notes"`
	RecordStructureChecked           bool               `json:"recordStructureChecked"`
	ExactTargetsVerified             bool               `json:"exactTargetsVerified"`
	HumanReviewed                    bool               `json:"humanReviewed"`
	AuthorityVerified                bool               `json:"authorityVerified"`
	PublicationApproved              bool               `json:"publicationApproved"`
}

// strictFrontDoor applies the acceptance of basisFromSnapshot: valid UTF-8, no duplicate or case-folded
// duplicate JSON names, no trailing data. It is stricter than SEI itself.
func strictFrontDoor(raw []byte, what string) error {
	if !utf8.Valid(raw) {
		return fmt.Errorf("%s is not valid UTF-8", what)
	}
	scanner := json.NewDecoder(bytes.NewReader(raw))
	scanner.UseNumber()
	if err := scanBasisJSON(scanner); err != nil {
		return err
	}
	if _, err := scanner.Token(); err != io.EOF {
		return fmt.Errorf("trailing JSON in %s", what)
	}
	return nil
}

// classifyRef mirrors semanticruntime.validateReference without importing SEI.
func classifyRef(raw json.RawMessage) (form string, logical logicalKey, binding bindingKey) {
	var ref wireRef
	if err := json.Unmarshal(raw, &ref); err != nil {
		return "invalid", logicalKey{}, bindingKey{}
	}
	hasSimple := ref.Kind != "" || ref.ID != "" || ref.Scope != ""
	hasExact := ref.LogicalRef != nil || ref.ContentDigest != "" || ref.RepresentationProfile != nil
	switch {
	case hasSimple && hasExact:
		return "invalid", logicalKey{}, bindingKey{}
	case hasExact:
		if ref.LogicalRef == nil || ref.LogicalRef.Kind == "" || ref.LogicalRef.ID == "" || ref.ContentDigest == "" ||
			ref.RepresentationProfile == nil || ref.RepresentationProfile.ProfileID == "" || ref.RepresentationProfile.Version == "" {
			return "invalid", logicalKey{}, bindingKey{}
		}
		l := logicalKey{ref.LogicalRef.Kind, ref.LogicalRef.ID, ref.LogicalRef.Scope}
		return "exact", l, bindingKey{l, ref.ContentDigest, ref.RepresentationProfile.ProfileID, ref.RepresentationProfile.Version}
	default:
		if ref.Kind == "" || ref.ID == "" {
			return "invalid", logicalKey{}, bindingKey{}
		}
		return "logical", logicalKey{ref.Kind, ref.ID, ref.Scope}, bindingKey{}
	}
}

// diffBinding lists the SEI sameExact components that differ. Go string equality only: no case folding,
// no Unicode normalization, an absent scope equals an empty scope (as in semanticruntime.sameLogical).
func diffBinding(a, b bindingKey) []string {
	out := []string{}
	if a.Logical.Kind != b.Logical.Kind {
		out = append(out, "logical_ref.kind")
	}
	if a.Logical.ID != b.Logical.ID {
		out = append(out, "logical_ref.id")
	}
	if a.Logical.Scope != b.Logical.Scope {
		out = append(out, "logical_ref.scope")
	}
	if a.Digest != b.Digest {
		out = append(out, "content_digest")
	}
	if a.ProfileID != b.ProfileID {
		out = append(out, "representation_profile.profile_id")
	}
	if a.ProfileVersion != b.ProfileVersion {
		out = append(out, "representation_profile.version")
	}
	return out
}

// matchIdentity compares a lineage endpoint with another logical identity. SEI does not say whether a reference
// without a scope covers every scope, so a missing scope on either side is reported as unspecified, not as a match.
func matchIdentity(endpoint, subject logicalKey) string {
	if endpoint.Kind != subject.Kind || endpoint.ID != subject.ID {
		return identityNone
	}
	switch {
	case endpoint.Scope == subject.Scope:
		return identitySame
	case endpoint.Scope != "" && subject.Scope != "":
		return identityOtherScope
	default:
		return identityScopeUnspecified
	}
}

func decodeCurrentTarget(raw []byte) (bindingKey, json.RawMessage, error) {
	if err := strictFrontDoor(raw, "current target"); err != nil {
		return bindingKey{}, nil, err
	}
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.DisallowUnknownFields()
	var probe wireRef
	if err := decoder.Decode(&probe); err != nil {
		return bindingKey{}, nil, err
	}
	form, _, binding := classifyRef(raw)
	if form != "exact" {
		return bindingKey{}, nil, fmt.Errorf("current target must be a complete ExactBinding (logical_ref, content_digest, representation_profile)")
	}
	compact := &bytes.Buffer{}
	if err := json.Compact(compact, raw); err != nil {
		return bindingKey{}, nil, err
	}
	return binding, json.RawMessage(compact.Bytes()), nil
}

func parseNamed(values []string) ([]logicalKey, error) {
	seen := map[logicalKey]bool{}
	out := []logicalKey{}
	for _, value := range values {
		kind, id, ok := strings.Cut(value, ":")
		if !ok || kind == "" || id == "" {
			return nil, fmt.Errorf("decision name %q must be written kind:id", value)
		}
		key := logicalKey{Kind: kind, ID: id}
		if seen[key] {
			return nil, fmt.Errorf("decision name %q given twice", value)
		}
		seen[key] = true
		out = append(out, key)
	}
	return out, nil
}

func isClosing(relation string) bool { return relation == "supersedes" || relation == "withdraws" }

func orEmpty(in []json.RawMessage) []json.RawMessage {
	if in == nil {
		return []json.RawMessage{}
	}
	return in
}

func newLineage(recordID, pointer, origin string, w lineageWire) LineageEntry {
	return LineageEntry{RecordID: recordID, JSONPointer: pointer, Origin: origin, Relation: w.Relation, Closing: isClosing(w.Relation),
		From: w.From, To: w.To, FromDecisionRecordIDs: []string{}, ToDecisionRecordIDs: []string{},
		FromCurrentTarget: identityNone, ToCurrentTarget: identityNone}
}

// validityFromSnapshot is pure and needs no SEI checkout. RecordStructureChecked stays false here.
func validityFromSnapshot(raw, targetRaw []byte, names []string) (ValidityInspection, error) {
	if err := strictFrontDoor(raw, "bundle snapshot"); err != nil {
		return ValidityInspection{}, err
	}
	var bundle struct {
		Contract string `json:"contract"`
		BundleID string `json:"bundle_id"`
		Records  []struct {
			RecordID string `json:"record_id"`
			Contract struct {
				ID      string `json:"contract_id"`
				Version string `json:"version"`
			} `json:"contract"`
			Payload json.RawMessage `json:"payload"`
		} `json:"records"`
	}
	if err := json.Unmarshal(raw, &bundle); err != nil {
		return ValidityInspection{}, err
	}
	if bundle.Contract != "sei.semantic-interchange/v1alpha1" || bundle.BundleID == "" {
		return ValidityInspection{}, fmt.Errorf("unsupported interchange")
	}
	target, targetNormalized, err := decodeCurrentTarget(targetRaw)
	if err != nil {
		return ValidityInspection{}, err
	}
	namedKeys, err := parseNamed(names)
	if err != nil {
		return ValidityInspection{}, err
	}

	out := ValidityInspection{
		Schema: validitySchema, SourceDigest: fmt.Sprintf("sha256:%x", sha256.Sum256(raw)), BundleID: bundle.BundleID,
		RecordCount: len(bundle.Records), CurrentTarget: targetNormalized, CurrentTargetSource: "caller-supplied",
		NamedDecisions: []NamedDecision{}, Decisions: []DecisionValidity{}, Lineage: []LineageEntry{},
		UninterpretedRecordIDs: []string{}, BoundDecisionRecordIDs: []string{}, DigestOnlyMatchRecordIDs: []string{},
		DigestOnlyMatchButNotBoundIDs: []string{}, Unresolved: []UnresolvedItem{}, Notes: validityNotes(),
	}
	seenItems := map[string]bool{}
	report := func(code string, blocking bool, detail string) {
		if key := fmt.Sprint(code, blocking, detail); !seenItems[key] {
			seenItems[key] = true
			out.Unresolved = append(out.Unresolved, UnresolvedItem{Code: code, Blocking: blocking, Detail: detail})
		}
	}

	seen := map[string]bool{}
	for i, record := range bundle.Records {
		if record.RecordID == "" || seen[record.RecordID] {
			return ValidityInspection{}, fmt.Errorf("missing or duplicate record ID")
		}
		seen[record.RecordID] = true
		interpreted := false
		switch {
		case record.Contract.ID == decisionMemoryContractID && record.Contract.Version == seiContractVersion:
			interpreted = true
			var doc struct {
				RecordType string `json:"record_type"`
				Decision   *struct {
					Ref            json.RawMessage   `json:"ref"`
					Basis          []json.RawMessage `json:"basis_refs"`
					Responsibility []json.RawMessage `json:"responsibility_refs"`
					Unresolved     []json.RawMessage `json:"unresolved_refs"`
					Lineage        *lineageWire      `json:"lineage"`
				} `json:"decision"`
			}
			if err := json.Unmarshal(record.Payload, &doc); err != nil {
				return ValidityInspection{}, err
			}
			if doc.RecordType != "decision" {
				break
			}
			if doc.Decision == nil {
				return ValidityInspection{}, fmt.Errorf("decision payload is missing")
			}
			base := fmt.Sprintf("/records/%d/payload/decision", i)
			form, logical, _ := classifyRef(doc.Decision.Ref)
			if form != "logical" {
				report("invalid-reference", true, base+"/refが論理参照ではない")
			}
			d := DecisionValidity{RecordID: record.RecordID, JSONPointer: base, DecisionRef: doc.Decision.Ref, logical: logical,
				Basis: []BasisComparison{}, LineageReferences: []LineageReference{},
				ResponsibilityRefs: orEmpty(doc.Decision.Responsibility), UnresolvedRefs: orEmpty(doc.Decision.Unresolved)}
			for j, basisRaw := range doc.Decision.Basis {
				comparison := BasisComparison{Index: j, JSONPointer: fmt.Sprintf("%s/basis_refs/%d", base, j), DifferingFields: []string{}}
				form, basisLogical, binding := classifyRef(basisRaw)
				comparison.Form = form
				switch form {
				case "exact":
					comparison.DigestEqualsTarget = binding.Digest == target.Digest
					if fields := diffBinding(binding, target); len(fields) == 0 {
						comparison.Relation = "equal"
					} else {
						comparison.Relation, comparison.DifferingFields = "differs", fields
					}
				case "logical":
					comparison.Relation = "not-comparable"
				default:
					comparison.Relation = "not-comparable"
					report("invalid-reference", true, comparison.JSONPointer+"は論理参照でも完全なExactBindingでもない")
				}
				d.Basis = append(d.Basis, comparison)
				switch {
				case form == "exact" && comparison.Relation == "equal":
					d.BasisEqualsCurrentTarget = true
				case form != "invalid":
					d.otherBasis = append(d.otherBasis, basisLogical)
				}
				d.exactSeen = d.exactSeen || form == "exact"
				d.exactRelated = d.exactRelated || (form == "exact" && matchIdentity(basisLogical, target.Logical) != identityNone)
				d.DigestOnlyMatch = d.DigestOnlyMatch || comparison.DigestEqualsTarget
			}
			out.Decisions = append(out.Decisions, d)
			if doc.Decision.Lineage != nil {
				out.Lineage = append(out.Lineage, newLineage(record.RecordID, base+"/lineage", "decision.lineage", *doc.Decision.Lineage))
			}
		case record.Contract.ID == semanticReferenceContractID && record.Contract.Version == seiContractVersion:
			interpreted = true
			var doc struct {
				RecordType      string       `json:"record_type"`
				SemanticLineage *lineageWire `json:"semantic_lineage"`
			}
			if err := json.Unmarshal(record.Payload, &doc); err != nil {
				return ValidityInspection{}, err
			}
			if doc.RecordType == "semantic_lineage" {
				if doc.SemanticLineage == nil {
					return ValidityInspection{}, fmt.Errorf("semantic_lineage payload is missing")
				}
				out.Lineage = append(out.Lineage, newLineage(record.RecordID, fmt.Sprintf("/records/%d/payload/semantic_lineage", i), "semantic_lineage", *doc.SemanticLineage))
			}
		}
		if !interpreted {
			out.UninterpretedRecordIDs = append(out.UninterpretedRecordIDs, record.RecordID)
		}
	}
	if len(out.UninterpretedRecordIDs) > 0 {
		report("uninterpreted-records", true, strings.Join(out.UninterpretedRecordIDs, ","))
	}

	// Resolve lineage endpoints by logical identity only. Direction (from/to) is never assumed. A closing
	// lineage reaches a Decision through the Decision's own identity, through the current target that its basis
	// names, or through its other basis references, because SEI defines lineage between Artifacts as well as
	// between Decisions.
	byLogical := map[logicalKey][]int{}
	for i, d := range out.Decisions {
		byLogical[d.logical] = append(byLogical[d.logical], i)
	}
	var targetReferences []LineageReference
	for li := range out.Lineage {
		l := &out.Lineage[li]
		if l.Relation != "revises" && !l.Closing {
			report("lineage-relation-unknown", true, fmt.Sprintf("%sのrelation %qは未知", l.JSONPointer, l.Relation))
		}
		for _, side := range []struct {
			name       string
			raw        json.RawMessage
			decisionID *[]string
			current    *string
		}{{"from", l.From, &l.FromDecisionRecordIDs, &l.FromCurrentTarget}, {"to", l.To, &l.ToDecisionRecordIDs, &l.ToCurrentTarget}} {
			where := l.JSONPointer + "/" + side.name
			form, endpoint, _ := classifyRef(side.raw)
			if form == "invalid" {
				report("invalid-reference", true, where)
				continue
			}
			same := 0
			for i := range out.Decisions {
				d := &out.Decisions[i]
				switch matchIdentity(endpoint, d.logical) {
				case identitySame:
					same++
					*side.decisionID = append(*side.decisionID, d.RecordID)
					d.LineageReferences = append(d.LineageReferences, LineageReference{JSONPointer: l.JSONPointer, Relation: l.Relation, Endpoint: side.name, Closing: l.Closing, Via: "decision-ref"})
					if l.Closing {
						d.ClosingLineageReferenced = true
					}
				case identityScopeUnspecified:
					if l.Closing {
						report("closing-lineage-endpoint-scope-unspecified", true, fmt.Sprintf("%sはdecision %s:%sをscopeの有無が食い違う形で指しており、%sと同じ対象か判断できない", where, endpoint.Kind, endpoint.ID, d.RecordID))
					}
				case identityOtherScope:
					if l.Closing {
						report("closing-lineage-endpoint-other-scope", false, fmt.Sprintf("%sは%s:%sを%sとは別のscopeで指す", where, endpoint.Kind, endpoint.ID, d.RecordID))
					}
				}
			}
			if same == 0 && endpoint.Kind == "decision" {
				report("lineage-endpoint-has-no-decision-record", false, where)
			}
			if same > 1 {
				report("lineage-endpoint-ambiguous", false, fmt.Sprintf("%sは%d件のDecision recordに当たる", where, same))
			}
			if l.Closing {
				// A Decision that would otherwise be bound also rests on its other basis references.
				for i := range out.Decisions {
					d := &out.Decisions[i]
					if !d.BasisEqualsCurrentTarget {
						continue
					}
					for _, basisLogical := range d.otherBasis {
						switch matchIdentity(endpoint, basisLogical) {
						case identitySame:
							d.LineageReferences = append(d.LineageReferences, LineageReference{JSONPointer: l.JSONPointer, Relation: l.Relation, Endpoint: side.name, Closing: true, Via: "other-basis"})
							d.ClosingLineageReferenced = true
						case identityScopeUnspecified:
							report("closing-lineage-endpoint-scope-unspecified", true, fmt.Sprintf("%sは%s:%sを、%sの他のbasisとscopeの有無が食い違う形で指しており、同じ対象か判断できない", where, endpoint.Kind, endpoint.ID, d.RecordID))
						case identityOtherScope:
							report("closing-lineage-endpoint-other-scope", false, fmt.Sprintf("%sは%s:%sを、%sの他のbasisとは別のscopeで指す", where, endpoint.Kind, endpoint.ID, d.RecordID))
						}
					}
				}
			}
			*side.current = matchIdentity(endpoint, target.Logical)
			switch *side.current {
			case identitySame:
				targetReferences = append(targetReferences, LineageReference{JSONPointer: l.JSONPointer, Relation: l.Relation, Endpoint: side.name, Closing: l.Closing, Via: "basis-matching-current-target"})
			case identityScopeUnspecified:
				if l.Closing {
					report("closing-lineage-endpoint-scope-unspecified", true, fmt.Sprintf("%sは%s:%sを、現行対象とscopeの有無が食い違う形で指しており、同じ対象か判断できない", where, endpoint.Kind, endpoint.ID))
				}
			case identityOtherScope:
				if l.Closing {
					report("closing-lineage-endpoint-other-scope", false, fmt.Sprintf("%sは%s:%sを現行対象とは別のscopeで指す", where, endpoint.Kind, endpoint.ID))
				}
			}
		}
	}

	namedSet := map[int]bool{}
	for _, key := range namedKeys {
		matches := byLogical[key]
		ids := []string{}
		for _, di := range matches {
			ids = append(ids, out.Decisions[di].RecordID)
			namedSet[di] = true
		}
		out.NamedDecisions = append(out.NamedDecisions, NamedDecision{Ref: key.Kind + ":" + key.ID, RecordIDs: ids})
		switch {
		case len(matches) == 0:
			report("named-decision-not-found", true, key.Kind+":"+key.ID)
		case len(matches) > 1:
			report("named-decision-ambiguous", true, key.Kind+":"+key.ID+" -> "+strings.Join(ids, ","))
		}
	}
	if len(namedKeys) == 0 {
		report("no-decision-named", true, "どのDecisionが受理かを検査は判断できない。-decisionでの指名が要る")
	}

	for i := range out.Decisions {
		d := &out.Decisions[i]
		d.Named = namedSet[i]
		if d.BasisEqualsCurrentTarget {
			for _, reference := range targetReferences {
				d.LineageReferences = append(d.LineageReferences, reference)
				d.ClosingLineageReferenced = d.ClosingLineageReferenced || reference.Closing
			}
		}
		switch {
		case !d.BasisEqualsCurrentTarget && !d.exactSeen:
			d.State = "no-exact-basis"
		case !d.BasisEqualsCurrentTarget:
			d.State = "basis-differs"
		case d.ClosingLineageReferenced:
			d.State = "closing-lineage-referenced"
		default:
			d.State = "bound"
			d.StructurallyBoundToCurrentTarget = true
			out.BoundDecisionRecordIDs = append(out.BoundDecisionRecordIDs, d.RecordID)
		}
		if d.Named {
			switch {
			case d.State == "no-exact-basis":
				// Not comparable is not "unbound": say that the check does not know, instead of reporting reacceptanceRequired=true.
				report("named-decision-has-no-exact-basis", true, d.RecordID+"はExactBindingのbasisを持たず、現行対象と比べられない（SEI CLIの`add decision`が作る形を含む）")
			case d.State == "basis-differs" && !d.exactRelated:
				report("named-decision-basis-other-identity", false, d.RecordID+"のExactBindingのbasisは、現行対象とkindまたはidが異なる対象を指す。同じ対象かどうかは判断しない")
			}
		}
		if d.DigestOnlyMatch {
			out.DigestOnlyMatchRecordIDs = append(out.DigestOnlyMatchRecordIDs, d.RecordID)
			if !d.StructurallyBoundToCurrentTarget {
				out.DigestOnlyMatchButNotBoundIDs = append(out.DigestOnlyMatchButNotBoundIDs, d.RecordID)
			}
		}
		if d.StructurallyBoundToCurrentTarget {
			// SEI does not define what revises does to an acceptance: surface it instead of staying silent.
			for _, reference := range d.LineageReferences {
				if reference.Relation == "revises" {
					report("revises-referenced", false, fmt.Sprintf("%sはrevises lineage（%s）の端点になっている", d.RecordID, reference.JSONPointer))
					break
				}
			}
			if d.Named && len(d.UnresolvedRefs) > 0 {
				report("named-decision-has-unresolved-refs", false, d.RecordID+"はunresolved_refsを持つ。解釈せず原値のまま通す")
			}
		}
	}

	// reacceptanceRequired is never false: a structural binding says nothing about the meaning, period,
	// authority or writer of an acceptance, so it stays unconfirmed (null) instead of reading as "still accepted".
	for _, item := range out.Unresolved {
		if item.Blocking {
			return out, nil
		}
	}
	namedBound := false
	for i, d := range out.Decisions {
		namedBound = namedBound || (namedSet[i] && d.StructurallyBoundToCurrentTarget)
	}
	out.StructurallyBoundToCurrentTarget = &namedBound
	if namedBound {
		report("acceptance-validity-unconfirmed", false, "指名したDecisionの意味・期間・権限・書込み主体は未確認")
	} else {
		required := true
		out.ReacceptanceRequired = &required
	}
	return out, nil
}

func validityNotes() []string {
	return []string{
		"構造検査の診断であり、Decisionの意味・受理・権限・公開を判定しない。structurallyBoundToCurrentTarget=trueは、現行対象のExactBindingがbasisに含まれ、閉じるlineageの端点でないという構造事実だけで、受理が有効であることを意味しない。",
		"reacceptanceRequired=trueは、指名したDecisionのいずれも構造上束縛されていないことだけを示し、Ownerの意味判断ではない。現行対象と別の対象を指すDecisionだけを指名した場合や、再受理Decision自身がsupersedes/withdrawsの端点になる場合も含み、再受理がないという断定ではない。比べられないDecision（ExactBindingのbasisがない）を指名したときは、trueにせずnullとする。束縛があっても、受理の有効性（意味・期間・権限・bundleへの書込み主体）は未確認のためnullとする。",
		"lineageのfrom/toの向きと、relationが受理へ及ぼす効果はSEI v1alpha1が定めていない。向きを仮定せず、supersedes/withdrawsが端点として参照するDecision・現行対象・Decisionの他のbasisの論理identityは、向きを問わず束縛扱いにしない。revisesは閉じない扱いとするが、これはTAIの暫定仮定でありOwner判断が必要。",
		"同一ExactBindingに戻り、閉じるlineageがbundleに記録されていない往復は検出できない。現行対象の実在・digestの再計算・参照先の内容は検証していない。",
	}
}

// inspectValidity = SEI verify of the same snapshot, then validityFromSnapshot.
func inspectValidity(ctx context.Context, seiRoot, path, targetPath string, names []string) (ValidityInspection, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return ValidityInspection{}, err
	}
	targetRaw, err := os.ReadFile(targetPath)
	if err != nil {
		return ValidityInspection{}, err
	}
	result, err := validityFromSnapshot(raw, targetRaw, names)
	if err != nil {
		return ValidityInspection{}, err
	}
	work, err := os.MkdirTemp("", "tai-sei-validity-")
	if err != nil {
		return ValidityInspection{}, err
	}
	defer os.RemoveAll(work)
	snapshot := filepath.Join(work, "bundle.json")
	if err := os.WriteFile(snapshot, raw, 0600); err != nil {
		return ValidityInspection{}, err
	}
	// Verify the same snapshot that was read, never re-read a changing input path.
	checked, err := run(ctx, filepath.Join(seiRoot, "runtime", "go"), "run", "./cmd/sei", "verify", "--input", snapshot)
	if err != nil {
		return ValidityInspection{}, err
	}
	var summary struct {
		BundleID         string `json:"bundle_id"`
		RecordCount      int    `json:"record_count"`
		ValidatedCount   int    `json:"validated_count"`
		NotVerifiedCount int    `json:"not_verified_count"`
	}
	if err := json.Unmarshal(checked, &summary); err != nil {
		return ValidityInspection{}, err
	}
	standalone := 0
	for _, l := range result.Lineage {
		if l.Origin == "semantic_lineage" {
			standalone++
		}
	}
	if summary.BundleID != result.BundleID || summary.RecordCount != result.RecordCount ||
		summary.ValidatedCount < 0 || summary.NotVerifiedCount < 0 || summary.ValidatedCount+summary.NotVerifiedCount != summary.RecordCount ||
		summary.ValidatedCount < len(result.Decisions)+standalone {
		return ValidityInspection{}, fmt.Errorf("SEI verification summary differs from the snapshot")
	}
	result.NotVerifiedRecordCount = summary.NotVerifiedCount
	result.RecordStructureChecked = true
	result.SeiCommit = output(ctx, seiRoot, "git", "rev-parse", "HEAD")
	return result, nil
}

// emitValidity writes the report and returns the exit code: 0 when a report was produced, 2 when it could not be written.
// The exit code is never a verdict: read the report fields.
func emitValidity(inspection ValidityInspection, outPath string, stdout, stderr io.Writer) int {
	encoded, err := json.MarshalIndent(inspection, "", "  ")
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 2
	}
	encoded = append(encoded, '\n')
	if outPath != "" {
		if err := writeBasisInspection(outPath, encoded); err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
	}
	if _, err := stdout.Write(encoded); err != nil {
		fmt.Fprintln(stderr, err)
		return 2
	}
	return 0
}

// runValidity returns 0 when a report was produced, 1 when the input was rejected (no report), 2 on output failure.
func runValidity(ctx context.Context, seiRoot, bundlePath, targetPath string, names []string, outPath string, stdout, stderr io.Writer) int {
	inspection, err := inspectValidity(ctx, seiRoot, bundlePath, targetPath, names)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	return emitValidity(inspection, outPath, stdout, stderr)
}
