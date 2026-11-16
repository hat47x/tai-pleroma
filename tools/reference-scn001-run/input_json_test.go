package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func ambiguousRunInputs(t *testing.T) map[string][]byte {
	t.Helper()
	raw, err := json.Marshal(recordedRunForMutation(t))
	if err != nil {
		t.Fatal(err)
	}
	valid := string(raw)
	cases := map[string][]byte{
		"hidden human review":    []byte(`{"humanReviewed":true,` + valid[1:]),
		"case alias":             []byte(`{"HumanReviewed":true,` + valid[1:]),
		"escaped alias":          []byte(`{"\u0068umanReviewed":true,` + valid[1:]),
		"unicode alias":          []byte(`{"ſynthetic":false,` + valid[1:]),
		"same duplicate":         []byte(`{"humanReviewed":false,` + valid[1:]),
		"hidden gate result":     []byte(strings.Replace(valid, `"allowed":false`, `"allowed":true,"allowed":false`, 1)),
		"hidden artifact digest": []byte(strings.Replace(valid, `"artifactDigest":"`, `"artifactDigest":"sha256:other","artifactDigest":"`, 1)),
		"hidden case id":         []byte(strings.Replace(valid, `"id":"P-01"`, `"id":"unknown","id":"P-01"`, 1)),
	}
	for name, bad := range cases {
		if string(bad) == valid {
			t.Fatalf("%s did not mutate input", name)
		}
	}
	return cases
}

func TestReadJSONRejectsAmbiguousRunEvidence(t *testing.T) {
	for name, raw := range ambiguousRunInputs(t) {
		t.Run(name, func(t *testing.T) {
			path := filepath.Join(t.TempDir(), "run.json")
			if err := os.WriteFile(path, raw, 0600); err != nil {
				t.Fatal(err)
			}
			var receipt RunReceipt
			if err := readJSON(path, &receipt); err == nil {
				if result := Verify(receipt); result.Passed {
					t.Error("ambiguous claims were hidden behind a valid component digest")
				}
				t.Fatal("ambiguous JSON accepted")
			}
		})
	}
}

func TestReadJSONDoesNotRepairInvalidUTF8(t *testing.T) {
	raw, err := json.Marshal(recordedRunForMutation(t))
	if err != nil {
		t.Fatal(err)
	}
	bad := append([]byte("{\"unexamined\":\""), 0xff)
	bad = append(bad, []byte("\","+string(raw[1:]))...)
	path := filepath.Join(t.TempDir(), "run.json")
	if err := os.WriteFile(path, bad, 0600); err != nil {
		t.Fatal(err)
	}
	var receipt RunReceipt
	if err := readJSON(path, &receipt); err == nil {
		t.Fatal("invalid UTF-8 accepted or silently repaired")
	}
}

func TestEvidenceJSONPreservesPartialProjection(t *testing.T) {
	// Child receipts deliberately contain fields outside this runner's view.
	raw := []byte(`{"passed":true,"metadata":{"large":1e1000,"text":"{\"passed\":false,\"passed\":true}"},"items":[{"name":"a"},{"name":"b"}]}`)
	var projected struct {
		Passed bool `json:"passed"`
	}
	if err := decodeEvidenceJSON(raw, &projected); err != nil {
		t.Fatal(err)
	}
	if !projected.Passed {
		t.Fatal("known component field lost")
	}
	path := filepath.Join(t.TempDir(), "recorded.json")
	receipt := recordedRunForMutation(t)
	encoded, err := json.Marshal(receipt)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, encoded, 0600); err != nil {
		t.Fatal(err)
	}
	var reread RunReceipt
	if err := readJSON(path, &reread); err != nil {
		t.Fatal(err)
	}
	if !Verify(reread).Passed || reread.RunDigest != receipt.RunDigest {
		t.Fatal("valid recorded evidence changed")
	}
}

func TestEvidenceJSONRejectsBeforeProjection(t *testing.T) {
	cases := []string{
		`{"passed":true,"metadata":{"key":1,"KEY":2}}`,
		`{"passed":true,"items":[{"key":1,"key":1}]}`,
		`{"passed":true} {"passed":false}`,
		`{"passed":true} trailing`,
		`{"passed":true,}`,
		`{"passed":true,"items":[1,]}`,
		`{"passed":true`,
		``,
	}
	for _, raw := range cases {
		var projected struct {
			Passed bool `json:"passed"`
		}
		if err := decodeEvidenceJSON([]byte(raw), &projected); err == nil {
			t.Errorf("invalid or ambiguous input accepted: %s", raw)
		}
		if projected.Passed {
			t.Errorf("failed scan modified output: %s", raw)
		}
	}
}
