package harnessadapter

import (
	"encoding/json"
	"fmt"
	"sort"
	"strings"
)

// ProductEnvelope is the subset of a product CLI/MCP result that two routes can
// be compared on. It is deliberately small: the point of E2 is to check that the
// same product operation, reached by a typed tool and by a direct CLI run,
// reports the same identity and outcome — not to compare every payload byte.
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
	// RawText is the payload exactly as the route returned it. It is kept so a
	// reader can re-derive anything this struct does not model.
	RawText string `json:"-"`
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

	var doc struct {
		SchemaVersion string          `json:"schemaVersion"`
		OK            *bool           `json:"ok"`
		Error         json.RawMessage `json:"error"`
		Failure       json.RawMessage `json:"failure"`
		Result        json.RawMessage `json:"result"`
		// validate returns these at the top level rather than inside `result`.
		WorldFingerprint       string `json:"worldFingerprint"`
		SourceIndexFingerprint string `json:"sourceIndexFingerprint"`
		ModelRevision          string `json:"modelRevision"`
		Validation             *struct {
			OK bool `json:"ok"`
		} `json:"validation"`
	}
	if err := json.Unmarshal([]byte(text), &doc); err != nil {
		return env, fmt.Errorf("product payload is not JSON: %w", err)
	}
	env.SchemaVersion = doc.SchemaVersion
	env.EnvelopeOK = doc.OK
	env.ErrorCode = errorCodeOf(doc.Error)
	if env.ErrorCode == "" {
		env.ErrorCode = errorCodeOf(doc.Failure)
	}
	env.WorldFingerprint = doc.WorldFingerprint
	env.SourceIndexFingerprint = doc.SourceIndexFingerprint
	env.ModelRevision = doc.ModelRevision
	if doc.Validation != nil {
		v := doc.Validation.OK
		env.ValidationOK = &v
	}
	// The catalog/validate operations nest these inside `result`.
	if len(doc.Result) > 0 {
		var nested struct {
			SchemaVersion          string `json:"schemaVersion"`
			WorldFingerprint       string `json:"worldFingerprint"`
			SourceIndexFingerprint string `json:"sourceIndexFingerprint"`
			ModelRevision          string `json:"modelRevision"`
			Validation             *struct {
				OK bool `json:"ok"`
			} `json:"validation"`
		}
		if json.Unmarshal(doc.Result, &nested) == nil {
			if env.SchemaVersion == "" {
				env.SchemaVersion = nested.SchemaVersion
			}
			if env.WorldFingerprint == "" {
				env.WorldFingerprint = nested.WorldFingerprint
			}
			if env.SourceIndexFingerprint == "" {
				env.SourceIndexFingerprint = nested.SourceIndexFingerprint
			}
			if env.ModelRevision == "" {
				env.ModelRevision = nested.ModelRevision
			}
			if env.ValidationOK == nil && nested.Validation != nil {
				v := nested.Validation.OK
				env.ValidationOK = &v
			}
		}
	}
	return env, nil
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
		{Field: "worldFingerprint", Left: left.WorldFingerprint, Right: right.WorldFingerprint},
		{Field: "sourceIndexFingerprint", Left: left.SourceIndexFingerprint, Right: right.SourceIndexFingerprint},
		{Field: "modelRevision", Left: left.ModelRevision, Right: right.ModelRevision},
		{Field: "validationOk", Left: booleans(left.ValidationOK), Right: booleans(right.ValidationOK)},
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
	// Two empty codes prove nothing on their own — an unparsed or silent route
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
