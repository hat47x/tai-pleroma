package main

import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"reflect"
	"strings"
	"testing"
)

func basisBundle(t *testing.T, scope, digest string, opaque bool) []byte {
	t.Helper()
	basis := []any{
		map[string]any{"logical_ref": map[string]string{"kind": "artifact", "id": "D-04", "scope": scope}, "content_digest": digest, "representation_profile": map[string]string{"profile_id": "synthetic-review-markdown", "version": "v0"}},
		map[string]string{"kind": "observation", "id": "O-02", "scope": "synthetic"},
	}
	records := []any{map[string]any{"record_id": "rec-1", "contract": map[string]string{"contract_id": "sei.decision-memory", "version": "v1alpha1"}, "kind": "decision", "payload": map[string]any{"contract": "sei.decision-memory/v1alpha1", "record_type": "decision", "decision": map[string]any{"ref": map[string]string{"kind": "decision", "id": "review-only"}, "statement": "合成の根拠参照。受理・権限は主張しない", "basis_refs": basis}}}}
	if opaque {
		records = append(records, map[string]any{"record_id": "opaque-1", "contract": map[string]string{"contract_id": "future.unknown", "version": "v9"}, "kind": "opaque", "payload": map[string]any{"decision": map[string]string{"statement": "do not interpret"}}})
	}
	raw, err := json.Marshal(map[string]any{"contract": "sei.semantic-interchange/v1alpha1", "bundle_id": "basis-probe", "records": records})
	if err != nil {
		t.Fatal(err)
	}
	return raw
}

func TestBasisSnapshotPreservesVersionScopeAndProfile(t *testing.T) {
	hashA := fmt.Sprintf("sha256:%x", sha256.Sum256([]byte("A")))
	hashB := fmt.Sprintf("sha256:%x", sha256.Sum256([]byte("B")))
	var first json.RawMessage
	for _, state := range []struct{ scope, digest string }{{"source-v1", hashA}, {"source-v2", hashB}, {"source-v3", hashA}} {
		raw := basisBundle(t, state.scope, state.digest, true)
		result, err := basisFromSnapshot(raw)
		if err != nil {
			t.Fatal(err)
		}
		if result.RecordStructureChecked || result.ExactTargetsVerified || result.HumanReviewed || result.AuthorityVerified || result.PublicationApproved {
			t.Fatal("byte extraction claimed semantic verification")
		}
		if result.SourceDigest != fmt.Sprintf("sha256:%x", sha256.Sum256(raw)) || result.RecordCount != 2 || len(result.Decisions) != 1 {
			t.Fatalf("wrong snapshot identity: %+v", result)
		}
		decision := result.Decisions[0]
		if decision.RecordID != "rec-1" || decision.JSONPointer != "/records/0/payload/decision" || len(decision.BasisRefs) != 2 {
			t.Fatalf("wrong source pointer: %+v", decision)
		}
		var original map[string]any
		if err := json.Unmarshal(raw, &original); err != nil {
			t.Fatal(err)
		}
		source := original["records"].([]any)[0].(map[string]any)["payload"].(map[string]any)["decision"].(map[string]any)["basis_refs"]
		var observed []any
		joined, err := json.Marshal(decision.BasisRefs)
		if err != nil {
			t.Fatal(err)
		}
		if err := json.Unmarshal(joined, &observed); err != nil {
			t.Fatal(err)
		}
		if !reflect.DeepEqual(source, any(observed)) {
			t.Fatal("original basis references were flattened")
		}
		if first != nil && string(first) == string(decision.BasisRefs[0]) {
			t.Fatal("different source scopes collapsed")
		}
		if first == nil {
			first = decision.BasisRefs[0]
		}
	}
}

func TestBasisSnapshotRejectsAmbiguousJSON(t *testing.T) {
	raw := string(basisBundle(t, "v1", "sha256:"+strings.Repeat("a", 64), false))
	for name, bad := range map[string]string{
		"duplicate ref":    strings.Replace(raw, `"id":"D-04"`, `"id":"old","id":"D-04"`, 1),
		"case alias":       strings.Replace(raw, `"scope":"v1"`, `"scope":"old","Scope":"v1"`, 1),
		"unicode alias":    strings.Replace(raw, `"scope":"v1"`, `"scope":"old","ſcope":"v1"`, 1),
		"trailing":         raw + `{}`,
		"duplicate record": strings.Replace(raw, `"record_id":"rec-1"`, `"record_id":"old","record_id":"rec-1"`, 1),
	} {
		t.Run(name, func(t *testing.T) {
			if bad == raw {
				t.Fatal("no mutation")
			}
			if _, err := basisFromSnapshot([]byte(bad)); err == nil {
				t.Fatal("ambiguous snapshot accepted")
			}
		})
	}
}

func TestBasisReportNeverOverwritesExistingFiles(t *testing.T) {
	path := filepath.Join(t.TempDir(), "source.json")
	original := []byte("source must survive")
	if err := os.WriteFile(path, original, 0600); err != nil {
		t.Fatal(err)
	}
	if err := writeBasisInspection(path, []byte("report")); err == nil {
		t.Fatal("existing source overwritten")
	}
	after, err := os.ReadFile(path)
	if err != nil || string(after) != string(original) {
		t.Fatal("source changed")
	}
	fresh := filepath.Join(t.TempDir(), "report.json")
	if err := writeBasisInspection(fresh, []byte("report")); err != nil {
		t.Fatal(err)
	}
	if err := writeBasisInspection(fresh, []byte("replacement")); err == nil {
		t.Fatal("existing report overwritten")
	}
}

func TestOriginalBasisInspectionThroughSEIVerify(t *testing.T) {
	root := seiRootForTest(t)
	path := filepath.Join(t.TempDir(), "basis.json")
	for _, scope := range []string{"source-v1", "source-v2", "source-v3"} {
		raw := basisBundle(t, scope, "sha256:"+strings.Repeat("a", 64), true)
		if err := os.WriteFile(path, raw, 0600); err != nil {
			t.Fatal(err)
		}
		result, err := inspectBasis(context.Background(), root, path)
		if err != nil {
			t.Fatal(err)
		}
		if !result.RecordStructureChecked || result.SeiCommit == "" || result.NotVerifiedRecordCount != 1 || len(result.Decisions) != 1 || result.ExactTargetsVerified || result.AuthorityVerified || result.HumanReviewed || result.PublicationApproved {
			t.Fatalf("inspection scope incorrect: %+v", result)
		}
		after, err := os.ReadFile(path)
		if err != nil || string(after) != string(raw) {
			t.Fatal("input bundle changed")
		}
	}
	// A parseable but incomplete ExactBinding must fail SEI verification.
	raw := basisBundle(t, "v1", "sha256:"+strings.Repeat("a", 64), false)
	var invalid map[string]any
	if err := json.Unmarshal(raw, &invalid); err != nil {
		t.Fatal(err)
	}
	refs := invalid["records"].([]any)[0].(map[string]any)["payload"].(map[string]any)["decision"].(map[string]any)["basis_refs"].([]any)
	delete(refs[0].(map[string]any), "representation_profile")
	raw, err := json.Marshal(invalid)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, raw, 0600); err != nil {
		t.Fatal(err)
	}
	if _, err := inspectBasis(context.Background(), root, path); err == nil || !strings.Contains(err.Error(), "partial exact reference") {
		t.Fatal("invalid exact reference accepted")
	}
}

func TestBasisPointersDoNotCollapseRepeatedLogicalDecisionIDs(t *testing.T) {
	var a, b map[string]any
	if err := json.Unmarshal(basisBundle(t, "source-v1", "sha256:"+strings.Repeat("a", 64), true), &a); err != nil {
		t.Fatal(err)
	}
	if err := json.Unmarshal(basisBundle(t, "source-v3", "sha256:"+strings.Repeat("a", 64), false), &b); err != nil {
		t.Fatal(err)
	}
	original := a["records"].([]any)
	later := b["records"].([]any)[0].(map[string]any)
	later["record_id"] = "rec-2"
	a["records"] = []any{original[1], original[0], later}
	raw, err := json.Marshal(a)
	if err != nil {
		t.Fatal(err)
	}
	result, err := basisFromSnapshot(raw)
	if err != nil {
		t.Fatal(err)
	}
	if len(result.Decisions) != 2 || result.Decisions[0].RecordID != "rec-1" || result.Decisions[1].RecordID != "rec-2" ||
		result.Decisions[0].JSONPointer != "/records/1/payload/decision" || result.Decisions[1].JSONPointer != "/records/2/payload/decision" ||
		string(result.Decisions[0].BasisRefs[0]) == string(result.Decisions[1].BasisRefs[0]) {
		t.Fatalf("record locations or scopes collapsed: %+v", result)
	}
}
