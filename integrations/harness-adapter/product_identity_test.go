package harnessadapter

import (
	"strings"
	"testing"
)

// TestParseSEIResumeEnvelope checks the SEI shape this contract now reads: a
// product that names its identity fields differently from TEI.
func TestParseSEIResumeEnvelope(t *testing.T) {
	payload := `{"bundle_id":"sei-store-2026-11-11-f8126225","snapshot_digest":"sha256:95965add","coverage":{"case_completeness":"not_assessed"},"record_count":0,"decisions":[],"unrecommended":[],"not_verified_record_count":0}`
	env, err := ParseProductEnvelope([]byte(payload))
	if err != nil {
		t.Fatalf("parse: %v", err)
	}
	if env.Identity["snapshot_digest"] != "sha256:95965add" {
		t.Fatalf("snapshot_digest not read: %+v", env.Identity)
	}
	if env.Identity["bundle_id"] != "sei-store-2026-11-11-f8126225" {
		t.Fatalf("bundle_id not read: %+v", env.Identity)
	}
	if env.Identity["record_count"] != "0" {
		t.Fatalf("record_count not read: %+v", env.Identity)
	}
	// SEI reports no `ok`; the contract must not invent one.
	if env.EnvelopeOK != nil {
		t.Fatalf("an ok flag was invented for a product that reports none: %v", *env.EnvelopeOK)
	}
}

// TestCompareTwoProductsComparesIntersection is the cross-product rule: two
// products that name identity differently are compared only on keys they share.
// No shared key means no identity comparison, and the report says so.
func TestCompareTwoProductsComparesIntersection(t *testing.T) {
	tei := ProductEnvelope{SchemaVersion: "tei.cli.model/v0", Identity: map[string]string{
		"worldFingerprint": "sha256:c92de09f", "sourceIndexFingerprint": "sha256:1827f4b4",
	}}
	sei := ProductEnvelope{Identity: map[string]string{
		"snapshot_digest": "sha256:95965add", "bundle_id": "sei-store-1",
	}}
	res := CompareProductEnvelopes("tei", tei, "sei", sei)
	if res.Agreed {
		t.Fatal("two products with no shared identity key were reported as agreeing")
	}
	for _, f := range res.Fields {
		if strings.HasPrefix(f.Field, "identity:") {
			t.Fatalf("an identity field was compared across products that share no key: %+v", f)
		}
	}
	joined := strings.Join(res.Notes, " ")
	if !strings.Contains(joined, "no shared identity key") {
		t.Fatalf("the reason was not recorded: %v", res.Notes)
	}
}

// TestCompareSameProductDifferentRoutesComparesAllKeys is the same-product case:
// both routes report the same identity keys, so all of them are compared.
func TestCompareSameProductDifferentRoutesComparesAllKeys(t *testing.T) {
	a := ProductEnvelope{SchemaVersion: "tei.cli.view/v0", Identity: map[string]string{
		"worldFingerprint": "sha256:w", "sourceIndexFingerprint": "sha256:s",
	}}
	b := a
	res := CompareProductEnvelopes("mcp", a, "cli-direct", b)
	identityFields := 0
	for _, f := range res.Fields {
		if strings.HasPrefix(f.Field, "identity:") {
			identityFields++
			if !f.Evidenced || !f.Equal {
				t.Fatalf("shared identity key was not compared: %+v", f)
			}
		}
	}
	if identityFields != 2 {
		t.Fatalf("expected 2 identity comparisons, got %d", identityFields)
	}
}
