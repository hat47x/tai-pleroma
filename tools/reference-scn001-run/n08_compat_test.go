package main

import "testing"

func TestSuccessfulRunAcceptsLegacyAndPassingN08Only(t *testing.T) {
	for _, tc := range []struct {
		name       string
		additional []CaseResult
		valid      bool
	}{
		{"legacy", nil, true},
		{"passing N08", []CaseResult{{ID: "N-08", Status: "pass"}}, true},
		{"failed N08", []CaseResult{{ID: "N-08", Status: "fail"}}, false},
		{"unknown", []CaseResult{{ID: "N-09", Status: "pass"}}, false},
		{"duplicate N08", []CaseResult{{ID: "N-08", Status: "pass"}, {ID: "N-08", Status: "pass"}}, false},
	} {
		t.Run(tc.name, func(t *testing.T) {
			run := recordedRunForMutation(t)
			run.Components.SCN001.Cases = append(run.Components.SCN001.Cases, tc.additional...)
			var err error
			run.RunDigest, err = digestJSON(run.Components)
			if err != nil {
				t.Fatal(err)
			}
			if got := Verify(run).Passed; got != tc.valid {
				t.Fatalf("Verify = %v, want %v", got, tc.valid)
			}
		})
	}
}

func TestN08CannotReplaceRequiredCase(t *testing.T) {
	run := recordedRunForMutation(t)
	run.Components.SCN001.Cases[0] = CaseResult{ID: "N-08", Status: "pass"}
	var err error
	run.RunDigest, err = digestJSON(run.Components)
	if err != nil {
		t.Fatal(err)
	}
	if Verify(run).Passed {
		t.Fatal("N-08 replaced a required case")
	}
}
