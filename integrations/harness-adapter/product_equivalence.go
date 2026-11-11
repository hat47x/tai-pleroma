package harnessadapter

import (
	"encoding/json"
	"fmt"
	"sort"
	"strconv"
	"strings"
)

// ProductEnvelope is the subset of a product CLI/MCP result that two routes can
// be compared on. It is deliberately small: the point of E2 is to check that the
// same product operation, reached by a typed tool and by a direct CLI run,
// reports the same identity and outcome 遯ｶ繝ｻnot to compare every payload byte.
//
// Fields a product does not report stay absent. Absent is never equal to present
// and never equal to empty: `evidenced=false` on both sides means the comparison
// did not cover that field, which is different from "the two agreed".
type ProductEnvelope struct {
	// SchemaVersion is the product's declared result schema, when it has one.
	SchemaVersion string `json:"schemaVersion,omitempty"`
	// EnvelopeOK is the product's own success flag. Nil means the product did
	// not report one.
	EnvelopeOK *bool `json:"ok,omitempty"`
	// ErrorCode is the product's stable string failure code.
	ErrorCode string `json:"errorCode,omitempty"`
	// WorldFingerprint names the product's derived world identity.
	WorldFingerprint string `json:"worldFingerprint,omitempty"`
	// SourceIndexFingerprint names the product's source index identity.
	SourceIndexFingerprint string `json:"sourceIndexFingerprint,omitempty"`
	// ModelRevision is TEI's model revision. It is product-specific vocabulary,
	// so it is captured as an opaque extra rather than as a contract field.
	ModelRevision string `json:"modelRevision,omitempty"`
	// ValidationOK is the product's validation verdict, when it evaluated one.
	ValidationOK *bool `json:"validationOk,omitempty"`
	// Identity holds the product's own identity fields under the product's own
	// names. Products do not share a vocabulary here: TEI says
	// `worldFingerprint`, SEI says `snapshot_digest`. Forcing one name would make
	// the contract lie about products it does not own.
	//
	// The contract compares the INTERSECTION of identity keys, so two products
	// with no shared key are not silently claimed to agree.
	Identity map[string]string `json:"identity,omitempty"`
	// RawText is the payload exactly as the route returned it. It is kept so a
	// reader can re-derive anything this struct does not model.
	RawText string `json:"-"`
}

// productDoc is the wire shape this contract reads. Fields a product does not
// send stay empty.
type productDoc struct {
	SchemaVersion          string          `json:"schemaVersion"`
	OK                     *bool           `json:"ok"`
	Error                  json.RawMessage `json:"error"`
	Failure                json.RawMessage `json:"failure"`
	Result                 json.RawMessage `json:"result"`
	WorldFingerprint       string          `json:"worldFingerprint"`
	SourceIndexFingerprint string          `json:"sourceIndexFingerprint"`
	ModelRevision          string          `json:"modelRevision"`
	SnapshotDigest         string          `json:"snapshot_digest"`
	BundleID               string          `json:"bundle_id"`
	RecordCount            *int            `json:"record_count"`
	Validation             *struct {
		OK bool `json:"ok"`
	} `json:"validation"`
}

// ParseProductEnvelope reads a product result from either route. Both TEI routes
// return the same JSON object; an MCP route wraps it in `content[0].text`, which
// this function unwraps when the payload looks like an MCP tool result.
func ParseProductEnvelope(payload []byte) (ProductEnvelope, error) {
	text := strings.TrimSpace(string(payload))
	if text == "" {
		return ProductEnvelope{}, fmt.Errorf("empty product payload")
	}
	// MCP tool results carry the product JSON inside content[0].text. Unwrap only
	// when the shape is unmistakable, so a product that legitimately returns
	// `content` is not rewritten.
	if strings.HasPrefix(text, `{`) {
		var probe struct {
			Content []struct {
				Type string `json:"type"`
				Text string `json:"text"`
			} `json:"content"`
			MCPSchemaVersion string `json:"schemaVersion"`
		}
		if json.Unmarshal([]byte(text), &probe) == nil &&
			probe.MCPSchemaVersion == "" && len(probe.Content) > 0 && probe.Content[0].Type == "text" {
			text = strings.TrimSpace(probe.Content[0].Text)
		}
	}
	env := ProductEnvelope{RawText: text}

	var doc productDoc
	if err := json.Unmarshal([]byte(text), &doc); err != nil {
		return env, fmt.Errorf("product payload is not JSON: %w", err)
	}
	env.SchemaVersion = doc.SchemaVersion
	env.EnvelopeOK = doc.OK
	env.ErrorCode = errorCodeOf(doc.Error)
	if env.ErrorCode == "" {
		env.ErrorCode = errorCodeOf(doc.Failure)
	}
	if doc.Validation != nil {
		v := doc.Validation.OK
		env.ValidationOK = &v
	}
	// Identity: the product's own identity names, read from the top level and
	// from `result`. A product that reports none leaves the map empty, which the
	// comparison treats as "not shown", never as agreement.
	env.Identity = doc.IdentityCandidates()
	// The catalog/validate operations nest identity inside `result`.
	if len(doc.Result) > 0 {
		var nested productDoc
		if json.Unmarshal(doc.Result, &nested) == nil {
			if env.SchemaVersion == "" {
				env.SchemaVersion = nested.SchemaVersion
			}
			if env.ValidationOK == nil && nested.Validation != nil {
				v := nested.Validation.OK
				env.ValidationOK = &v
			}
			for k, v := range nested.IdentityCandidates() {
				if _, exists := env.Identity[k]; !exists {
					env.Identity[k] = v
				}
			}
		}
	}
	return env, nil
}

// IdentityCandidates returns the product-specific identity fields this
// contract can read, under the product's own names. A product that reports none
// returns an empty map; the comparison then says "not shown" rather than
// inventing agreement.
func (d *productDoc) IdentityCandidates() map[string]string {
	out := map[string]string{}
	if d.WorldFingerprint != "" {
		out["worldFingerprint"] = d.WorldFingerprint
	}
	if d.SourceIndexFingerprint != "" {
		out["sourceIndexFingerprint"] = d.SourceIndexFingerprint
	}
	if d.ModelRevision != "" {
		out["modelRevision"] = d.ModelRevision
	}
	if d.SnapshotDigest != "" {
		out["snapshot_digest"] = d.SnapshotDigest
	}
	if d.BundleID != "" {
		out["bundle_id"] = d.BundleID
	}
	if d.RecordCount != nil {
		out["record_count"] = strconv.Itoa(*d.RecordCount)
	}
	return out
}

// errorCodeOf reads a product failure code from either the `error` or `failure`
// shape. TEI uses `error.code` on some operations and `failure.code` on others.
func errorCodeOf(raw json.RawMessage) string {
	if len(raw) == 0 {
		return ""
	}
	var obj struct {
		Code    string `json:"code"`
		Message string `json:"message"`
	}
	if json.Unmarshal(raw, &obj) == nil && obj.Code != "" {
		return obj.Code
	}
	// Tolerate the field being carried as a bare string.
	var s string
	if json.Unmarshal(raw, &s) == nil {
		return s
	}
	return ""
}

// ---------------------------------------------------------------------------
// Equivalence: a comparison that reports coverage instead of a verdict.
// ---------------------------------------------------------------------------

// FieldComparison is one compared field. Evidenced=false means at least one side
// did not report it, so the comparison says nothing about it.
type FieldComparison struct {
	Field     string `json:"field"`
	Left      string `json:"left,omitempty"`
	Right     string `json:"right,omitempty"`
	Evidenced bool   `json:"evidenced"`
	Equal     bool   `json:"equal"`
}

// EquivalenceResult is the outcome of comparing two product routes.
//
// Agreement is a per-field fact, never a single boolean. `Agreed=false` with an
// unevidenced field means "these two routes were not shown to agree", which is
// weaker than "they disagree" and is recorded as such.
type EquivalenceResult struct {
	// LeftName and RightName identify the routes, e.g. "mcp" and "cli-direct".
	LeftName  string            `json:"leftName"`
	RightName string            `json:"rightName"`
	Fields    []FieldComparison `json:"fields"`
	// Agreed is true only when every compared field was evidenced on both sides
	// AND agreed. It is false when any field was unevidenced, by design.
	Agreed bool `json:"agreed"`
	// Notes carries the reason agreement could not be shown.
	Notes []string `json:"notes,omitempty"`
}

// CompareProductEnvelopes compares two routes on the fields both products
// report. It never promotes an unevidenced field to agreement.
//
// Identity is compared on the INTERSECTION of the two products' own identity
// keys. Two products that share no identity key contribute no identity
// comparison, and the report says so instead of claiming a match.
func CompareProductEnvelopes(leftName string, left ProductEnvelope, rightName string, right ProductEnvelope) EquivalenceResult {
	res := EquivalenceResult{LeftName: leftName, RightName: rightName}

	booleans := func(p *bool) string {
		if p == nil {
			return ""
		}
		if *p {
			return "true"
		}
		return "false"
	}
	fields := []FieldComparison{
		{Field: "schemaVersion", Left: left.SchemaVersion, Right: right.SchemaVersion},
		{Field: "ok", Left: booleans(left.EnvelopeOK), Right: booleans(right.EnvelopeOK)},
		{Field: "errorCode", Left: left.ErrorCode, Right: right.ErrorCode},
		{Field: "validationOk", Left: booleans(left.ValidationOK), Right: booleans(right.ValidationOK)},
	}
	// Identity keys present on both sides, compared under the product's own names.
	keys := make([]string, 0, len(left.Identity))
	for k := range left.Identity {
		if _, ok := right.Identity[k]; ok {
			keys = append(keys, k)
		}
	}
	sort.Strings(keys)
	for _, k := range keys {
		fields = append(fields, FieldComparison{
			Field: "identity:" + k, Left: left.Identity[k], Right: right.Identity[k],
		})
	}
	if len(keys) == 0 {
		res.Notes = append(res.Notes,
			"the two routes reported no shared identity key, so identity was not compared")
	}
	for _, f := range fields {
		if f.Field == "errorCode" {
			continue
		}
		// Evidenced requires BOTH routes to have said something. An empty value
		// on both sides is unevidenced, not agreement.
		f.Evidenced = f.Left != "" && f.Right != ""
		f.Equal = f.Evidenced && f.Left == f.Right
		res.Fields = append(res.Fields, f)
	}
	// errorCode is comparable only when both routes actually reported a verdict.
	// Two empty codes prove nothing on their own 遯ｶ繝ｻan unparsed or silent route
	// looks identical to a successful one. But when both sides reported `ok`,
	// "no failure code on either side" is a real observation: both said the
	// operation succeeded and neither named a failure.
	ec := FieldComparison{Field: "errorCode", Left: left.ErrorCode, Right: right.ErrorCode}
	if left.ErrorCode != "" || right.ErrorCode != "" {
		ec.Evidenced = true
		ec.Equal = left.ErrorCode == right.ErrorCode
	} else if left.EnvelopeOK != nil && right.EnvelopeOK != nil {
		ec.Evidenced = true
		ec.Equal = true
	}
	res.Fields = append(res.Fields, ec)
	sort.SliceStable(res.Fields, func(i, j int) bool { return res.Fields[i].Field < res.Fields[j].Field })

	allEvidenced := true
	allEqual := true
	var unevidenced, disagreed []string
	for _, f := range res.Fields {
		if !f.Evidenced {
			allEvidenced = false
			unevidenced = append(unevidenced, f.Field)
			continue
		}
		if !f.Equal {
			allEqual = false
			disagreed = append(disagreed, f.Field)
		}
	}
	res.Agreed = allEvidenced && allEqual
	if len(unevidenced) > 0 {
		res.Notes = append(res.Notes,
			"fields not reported by both routes (agreement not shown): "+strings.Join(unevidenced, ", "))
	}
	if len(disagreed) > 0 {
		res.Notes = append(res.Notes,
			"fields the two routes disagree on: "+strings.Join(disagreed, ", "))
	}
	if res.Agreed {
		res.Notes = append(res.Notes,
			"agreement is limited to the compared fields on this exact workspace and product build; it is not a whole-product equivalence or an acceptance")
	}
	return res
}

// Summary renders the comparison for an evidence log.
func (e EquivalenceResult) Summary() string {
	return fmt.Sprintf("%s vs %s: agreed=%v (%d fields, %d unevidenced)",
		e.LeftName, e.RightName, e.Agreed, len(e.Fields), countUnevidenced(e.Fields))
}

func countUnevidenced(fields []FieldComparison) int {
	n := 0
	for _, f := range fields {
		if !f.Evidenced {
			n++
		}
	}
	return n
}
