package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

const externalExecutionSample = `{
  "schema": "tai.reference.eki-http-agent/v0",
  "synthetic": false,
  "evidenceKind": "real-execution",
  "publicationAllowed": false,
  "date": "2026-11-01",
  "ekiCommit": "ccaff37",
  "command": "go test ./conformance/process",
  "result": "PASS",
  "observed": {
    "submitStatus": 202,
    "taskID": "tsk_1",
    "acceptedOutcome": "accepted",
    "acceptedResultDigest": "cd2eca35",
    "verification": "same-host re-execution",
    "testProfile": true
  }
}`

func writeExternalExecution(t *testing.T, body string) string {
	t.Helper()
	path := filepath.Join(t.TempDir(), "eki.json")
	if err := os.WriteFile(path, []byte(body), 0o600); err != nil {
		t.Fatal(err)
	}
	return path
}

func TestLoadExternalExecutionPinsDigestAndFields(t *testing.T) {
	path := writeExternalExecution(t, externalExecutionSample)
	component, err := LoadExternalExecution(path)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.HasPrefix(component.Digest, "sha256:") {
		t.Fatalf("digest = %q", component.Digest)
	}
	if component.TaskID != "tsk_1" || component.AcceptedOutcome != "accepted" ||
		component.AcceptedResultDigest != "cd2eca35" || !component.TestProfile {
		t.Fatalf("component = %+v", component)
	}
}

func TestLoadExternalExecutionRejectsSyntheticOrPublished(t *testing.T) {
	cases := map[string]string{
		"synthetic":  strings.Replace(externalExecutionSample, `"synthetic": false`, `"synthetic": true`, 1),
		"published":  strings.Replace(externalExecutionSample, `"publicationAllowed": false`, `"publicationAllowed": true`, 1),
		"no result":  strings.Replace(externalExecutionSample, `"acceptedOutcome": "accepted"`, `"acceptedOutcome": ""`, 1),
		"not passed": strings.Replace(externalExecutionSample, `"result": "PASS"`, `"result": "FAIL"`, 1),
	}
	for name, body := range cases {
		t.Run(name, func(t *testing.T) {
			if _, err := LoadExternalExecution(writeExternalExecution(t, body)); err == nil {
				t.Fatal("invalid receipt was accepted")
			}
		})
	}
}
