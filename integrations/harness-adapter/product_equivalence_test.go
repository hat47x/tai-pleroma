package harnessadapter

import (
	"strings"
	"testing"
)

// teiCatalogJSON is the shape `tei model catalog` returns (top-level result).
const teiCatalogJSON = `{"schemaVersion":"tei.cli.model/v0","ok":true,"result":{"schemaVersion":"tei.operations.model-catalog/v0","effect":"read-only","namespaceMatched":true,"worldFingerprint":"sha256:c92de09f","sourceIndexFingerprint":"sha256:1827f4b4","modelRevision":"sha256:f414e2b0","declarationCounts":{"total":79},"validation":{"ok":true,"errorCount":0,"warningCount":3}}}`

// teiValidateJSON is the shape `tei validate -json` returns (top-level fields).
const teiValidateJSON = `{"schemaVersion":"tei.cli.validate/v0","ok":true,"worldFingerprint":"sha256:c92de09f","sourceIndexFingerprint":"sha256:1827f4b4","declarationCounts":{"total":79},"validation":{"ok":false,"errorCount":2,"warningCount":0}}`

// teiMcpWrapped wraps a product payload the way an MCP tool result does.
func teiMcpWrapped(productJSON string) string {
	return `{"content":[{"type":"text","text":` + jsonQuote(productJSON) + `}],"isError":false}`
}

func jsonQuote(s string) string {
	// Minimal JSON string quoting sufficient for these fixtures.
	return `"` + strings.NewReplacer(`\`, `\\`, `"`, `\"`, "\n", `\n`).Replace(s) + `"`
}

// TestParseProductEnvelopeTopLevelAndNested covers both TEI result shapes: the
// catalog nests identity inside `result`, while validate reports it at the top.
func TestParseProductEnvelopeTopLevelAndNested(t *testing.T) {
	cat, err := ParseProductEnvelope([]byte(teiCatalogJSON))
	if err != nil {
		t.Fatalf("catalog: %v", err)
	}
	if cat.SchemaVersion != "tei.cli.model/v0" {
		t.Fatalf("catalog schemaVersion = %q", cat.SchemaVersion)
	}
	if cat.Identity["worldFingerprint"] != "sha256:c92de09f" || cat.Identity["sourceIndexFingerprint"] != "sha256:1827f4b4" {
		t.Fatalf("catalog fingerprints not found: %+v", cat)
	}
	if cat.Identity["modelRevision"] != "sha256:f414e2b0" {
		t.Fatalf("model revision = %q", cat.ModelRevision)
	}
	if cat.ValidationOK == nil || !*cat.ValidationOK {
		t.Fatalf("nested validation not read: %+v", cat.ValidationOK)
	}

	val, err := ParseProductEnvelope([]byte(teiValidateJSON))
	if err != nil {
		t.Fatalf("validate: %v", err)
	}
	if val.SchemaVersion != "tei.cli.validate/v0" {
		t.Fatalf("validate schemaVersion = %q", val.SchemaVersion)
	}
	if val.Identity["worldFingerprint"] != "sha256:c92de09f" {
		t.Fatalf("validate top-level fingerprint not read: %+v", val)
	}
	if val.ValidationOK == nil || *val.ValidationOK {
		t.Fatalf("validate validation verdict wrong: %+v", val.ValidationOK)
	}
}

// TestParseProductEnvelopeUnwrapsMCPResult is the route-agnostic read: an MCP
// tool result carries the same product JSON inside content[0].text.
func TestParseProductEnvelopeUnwrapsMCPResult(t *testing.T) {
	mcp, err := ParseProductEnvelope([]byte(teiMcpWrapped(teiCatalogJSON)))
	if err != nil {
		t.Fatalf("mcp: %v", err)
	}
	direct, err := ParseProductEnvelope([]byte(teiCatalogJSON))
	if err != nil {
		t.Fatalf("direct: %v", err)
	}
	if mcp.SchemaVersion != direct.SchemaVersion ||
		mcp.WorldFingerprint != direct.WorldFingerprint ||
		mcp.SourceIndexFingerprint != direct.SourceIndexFingerprint {
		t.Fatalf("unwrapping lost identity:\n mcp=%+v\n direct=%+v", mcp, direct)
	}
}

// TestParseProductEnvelopeDoesNotRewriteProductContent keeps a product that
// legitimately returns a `content` field from being mistaken for an MCP wrapper.
func TestParseProductEnvelopeDoesNotRewriteProductContent(t *testing.T) {
	payload := `{"schemaVersion":"product/v0","ok":true,"result":{"content":[{"type":"text","text":"x"}]}}`
	env, err := ParseProductEnvelope([]byte(payload))
	if err != nil {
		t.Fatalf("parse: %v", err)
	}
	if env.SchemaVersion != "product/v0" {
		t.Fatalf("payload was unwrapped: %+v", env)
	}
	if !strings.Contains(env.RawText, "result") {
		t.Fatalf("raw text was rewritten: %q", env.RawText)
	}
}

// TestCompareAgreementRequiresBothSides is the core rule: an empty value on one
// side is "not shown", never "equal".
func TestCompareAgreementRequiresBothSides(t *testing.T) {
	left := ProductEnvelope{SchemaVersion: "v0", Identity: map[string]string{"worldFingerprint": "sha256:a"}}
	right := ProductEnvelope{SchemaVersion: "v0"} // fingerprint not reported
	res := CompareProductEnvelopes("mcp", left, "cli-direct", right)
	if res.Agreed {
		t.Fatal("agreement was claimed with an unevidenced field")
	}
	byField := map[string]FieldComparison{}
	for _, f := range res.Fields {
		byField[f.Field] = f
	}
	if byField["identity:worldFingerprint"].Evidenced {
		t.Fatal("an unreported field was marked evidenced")
	}
	if byField["schemaVersion"].Evidenced != true || !byField["schemaVersion"].Equal {
		t.Fatalf("the evidenced field was not compared: %+v", byField["schemaVersion"])
	}
	if len(res.Notes) == 0 || !strings.Contains(strings.Join(res.Notes, " "), "not shown") {
		t.Fatalf("the gap was not explained: %v", res.Notes)
	}
}

// TestCompareDetectsDisagreement is the positive control: a real difference must
// be reported as a difference, not as a coverage gap.
func TestCompareDetectsDisagreement(t *testing.T) {
	left := ProductEnvelope{SchemaVersion: "v0", Identity: map[string]string{"worldFingerprint": "sha256:a", "sourceIndexFingerprint": "sha256:b"}}
	right := ProductEnvelope{SchemaVersion: "v0", Identity: map[string]string{"worldFingerprint": "sha256:DIFFERENT", "sourceIndexFingerprint": "sha256:b"}}
	res := CompareProductEnvelopes("mcp", left, "cli-direct", right)
	if res.Agreed {
		t.Fatal("disagreement was reported as agreement")
	}
	for _, f := range res.Fields {
		if f.Field == "identity:worldFingerprint" {
			if !f.Evidenced || f.Equal {
				t.Fatalf("fingerprint difference not recorded: %+v", f)
			}
		}
	}
	joined := strings.Join(res.Notes, " ")
	if !strings.Contains(joined, "disagree") {
		t.Fatalf("disagreement not named: %v", res.Notes)
	}
}

// TestCompareErrorCodeOnlyWhenBothSidesReported stops two silent routes from
// "agreeing" on an empty error code while still allowing two explicit successes
// to agree that neither named a failure.
func TestCompareErrorCodeOnlyWhenBothSidesReported(t *testing.T) {
	// Both sides reported ok and neither named a failure: comparable, equal.
	okTrue := true
	ok := ProductEnvelope{SchemaVersion: "v0", EnvelopeOK: &okTrue}
	res := CompareProductEnvelopes("mcp", ok, "cli-direct", ok)
	for _, f := range res.Fields {
		if f.Field == "errorCode" && !f.Evidenced {
			t.Fatalf("two explicit successes left errorCode unevidenced: %+v", f)
		}
	}
	// Neither side reported an ok flag: nothing was said, so nothing is compared.
	silent := ProductEnvelope{SchemaVersion: "v0"}
	res2 := CompareProductEnvelopes("mcp", silent, "cli-direct", silent)
	for _, f := range res2.Fields {
		if f.Field == "errorCode" && f.Evidenced {
			t.Fatalf("a silent route produced an evidenced errorCode: %+v", f)
		}
	}
	// One side failed: the codes are comparable and differ.
	failed := ProductEnvelope{ErrorCode: "INVALID_ARGUMENT"}
	res3 := CompareProductEnvelopes("mcp", ok, "cli-direct", failed)
	var ec *FieldComparison
	for i := range res3.Fields {
		if res3.Fields[i].Field == "errorCode" {
			ec = &res3.Fields[i]
		}
	}
	if ec == nil || !ec.Evidenced || ec.Equal {
		t.Fatalf("a failure code was not compared: %+v", ec)
	}
}

// TestCompareValidationVerdictSeparateFromOK keeps the operation/validation split
// visible in the comparison: a route can succeed while validation fails.
func TestCompareValidationVerdictSeparateFromOK(t *testing.T) {
	clienv, _ := ParseProductEnvelope([]byte(teiValidateJSON))
	res := CompareProductEnvelopes("mcp", clienv, "cli-direct", clienv)
	byField := map[string]FieldComparison{}
	for _, f := range res.Fields {
		byField[f.Field] = f
	}
	if !byField["ok"].Equal {
		t.Fatalf("ok not compared: %+v", byField["ok"])
	}
	// Both routes report ok=true while validation is false. They must agree on
	// both, with the two fields staying separate.
	if byField["validationOk"].Left != "false" || byField["validationOk"].Right != "false" {
		t.Fatalf("validation verdict not carried: %+v", byField["validationOk"])
	}
}

// TestCompareSummaryIsReadable keeps the evidence line stable.
func TestCompareSummaryIsReadable(t *testing.T) {
	left, _ := ParseProductEnvelope([]byte(teiCatalogJSON))
	res := CompareProductEnvelopes("mcp", left, "cli-direct", left)
	s := res.Summary()
	if !strings.Contains(s, "mcp vs cli-direct") || !strings.Contains(s, "agreed=true") {
		t.Fatalf("summary = %q", s)
	}
}

// TestCompareDoesNotPromote is the anti-promotion guard: agreement on the
// compared fields must carry its own limit note.
func TestCompareDoesNotPromote(t *testing.T) {
	left, _ := ParseProductEnvelope([]byte(teiCatalogJSON))
	res := CompareProductEnvelopes("mcp", left, "cli-direct", left)
	if !res.Agreed {
		// The fixture reports both sides fully, so this should agree; if it does
		// not, the test above already failed.
		t.Skip("agreement unexpectedly false; see TestCompareSummaryIsReadable")
	}
	joined := strings.Join(res.Notes, " ")
	if !strings.Contains(joined, "not a whole-product equivalence") {
		t.Fatalf("agreement note does not limit its scope: %v", res.Notes)
	}
}
