package main

import (
	"encoding/json"
	"strings"
	"testing"
)

// mutateCatalog edits the entries of the honest catalog and returns the new stdout.
func mutateCatalog(t *testing.T, edit func(entries []map[string]any) []map[string]any) string {
	t.Helper()
	var doc map[string]any
	if err := json.Unmarshal([]byte(honestCatalog(fakeTEIScenario{})), &doc); err != nil {
		t.Fatal(err)
	}
	result := doc["result"].(map[string]any)
	var entries []map[string]any
	for _, item := range result["entries"].([]any) {
		entries = append(entries, item.(map[string]any))
	}
	result["entries"] = edit(entries)
	raw, err := json.Marshal(doc)
	if err != nil {
		t.Fatal(err)
	}
	return string(raw)
}

func observationEntry(entries []map[string]any) map[string]any {
	for _, entry := range entries {
		if entry["symbol"] == "Observation" {
			if subject, ok := entry["subject"].(map[string]any); ok && subject["kind"] == "semantic-data" {
				return entry
			}
		}
	}
	return nil
}

// These cases run bindModel directly. The structure (namespace, kind, ambiguity,
// duplicates) is checked against a fake catalog only; they say nothing about the real TEI.
func TestBindModelRejectsStructuralDeviations(t *testing.T) {
	if got := bindModel(honestCatalog(fakeTEIScenario{}), 0); got.Status != "bound" {
		t.Fatalf("honest catalog must bind: %+v", got)
	}
	cases := []struct {
		name string
		edit func(entries []map[string]any) []map[string]any
		want string
	}{
		{"other namespace", func(entries []map[string]any) []map[string]any {
			observationEntry(entries)["parent"] = map[string]any{"kind": "semantic", "id": "other"}
			return entries
		}, "Observation: 0 data entries in namespace scn001"},
		{"ambiguous", func(entries []map[string]any) []map[string]any {
			observationEntry(entries)["ambiguous"] = true
			return entries
		}, "Observation is ambiguous"},
		{"duplicate data", func(entries []map[string]any) []map[string]any {
			dup := map[string]any{}
			for key, value := range observationEntry(entries) {
				dup[key] = value
			}
			dup["subject"] = map[string]any{"kind": "semantic-data", "id": "scn001.observation2"}
			return append(entries, dup)
		}, "Observation: 2 data entries in namespace scn001"},
		{"wrong data kind", func(entries []map[string]any) []map[string]any {
			observationEntry(entries)["subject"].(map[string]any)["kind"] = "semantic"
			return entries
		}, "Observation: 0 data entries in namespace scn001"},
		{"attribute with wrong kind", func(entries []map[string]any) []map[string]any {
			for _, entry := range entries {
				if entry["symbol"] == "sourceVersion" {
					entry["subject"].(map[string]any)["kind"] = "semantic-data"
				}
			}
			return entries
		}, "Observation.sourceVersion is missing"},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := bindModel(mutateCatalog(t, tc.edit), 0)
			if got.Status != "mismatch" || !strings.Contains(strings.Join(got.Differences, "|"), tc.want) {
				t.Fatalf("want mismatch containing %q, got %+v", tc.want, got)
			}
		})
	}
}

func TestPinExpectationFormatsAcceptSHA256AndPrereleaseToolchains(t *testing.T) {
	for _, value := range []string{strings.Repeat("a", 64), strings.Repeat("a", 40)} {
		if !commitPattern.MatchString(value) {
			t.Errorf("commit %d chars must be accepted", len(value))
		}
	}
	for _, value := range []string{strings.Repeat("a", 63), strings.Repeat("a", 41), strings.Repeat("A", 40)} {
		if commitPattern.MatchString(value) {
			t.Errorf("commit %q must be rejected", value)
		}
	}
	for _, value := range []string{"go1.26", "go1.26.9", "go1.27rc1", "go1.27beta2"} {
		if !goVersionPattern.MatchString(value) {
			t.Errorf("go version %q must be accepted", value)
		}
	}
	for _, value := range []string{"1.26.9", "go1.26.9-x", "go1.27rc"} {
		if goVersionPattern.MatchString(value) {
			t.Errorf("go version %q must be rejected", value)
		}
	}
}
