package harnessadapter

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

// TestRootProbeSpecRefusesCanaryInsideRoot is the guard that keeps the probe
// meaningful: a canary sitting inside the declared root is readable by design and
// proves nothing.
func TestRootProbeSpecRefusesCanaryInsideRoot(t *testing.T) {
	dir := t.TempDir()
	root := filepath.Join(dir, "workspace")
	outside := filepath.Join(dir, "outside", "canary.txt")
	canaryInside := filepath.Join(root, "canary.txt")

	spec := RootProbeSpec{
		Logical:      "tei-workspace",
		DeclaredRoot: root,
		CanaryPath:   canaryInside,
		CanaryBytes:  []byte("x"),
	}
	if err := spec.Validate(); err == nil {
		t.Fatal("a canary inside the declared root was accepted")
	}
	spec.CanaryPath = outside
	if err := spec.Validate(); err != nil {
		t.Fatalf("an out-of-root canary was rejected: %v", err)
	}
}

// TestRootProbeSpecRequiresParts refuses a partial spec instead of inventing
// defaults.
func TestRootProbeSpecRequiresParts(t *testing.T) {
	dir := t.TempDir()
	base := RootProbeSpec{
		Logical:      "r",
		DeclaredRoot: filepath.Join(dir, "w"),
		CanaryPath:   filepath.Join(dir, "c", "canary.txt"),
		CanaryBytes:  []byte("x"),
	}
	cases := map[string]func(s *RootProbeSpec){
		"no logical": func(s *RootProbeSpec) { s.Logical = "" },
		"no root":    func(s *RootProbeSpec) { s.DeclaredRoot = "" },
		"no canary":  func(s *RootProbeSpec) { s.CanaryPath = "" },
		"no content": func(s *RootProbeSpec) { s.CanaryBytes = nil },
	}
	for name, mutate := range cases {
		t.Run(name, func(t *testing.T) {
			s := base
			mutate(&s)
			if err := s.Validate(); err == nil {
				t.Fatal("an incomplete spec was accepted")
			}
		})
	}
}

// TestWriteCanaryIsRecognisable keeps the marker distinctive so a leaked echo is
// identifiable in an answer.
func TestWriteCanaryIsRecognisable(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "outside", "canary.txt")
	content, err := WriteCanary(path, "nonce-123")
	if err != nil {
		t.Fatalf("WriteCanary: %v", err)
	}
	if !strings.Contains(string(content), canaryMarkerPrefix) {
		t.Fatalf("canary lacks the marker prefix: %q", content)
	}
	if !strings.Contains(string(content), "nonce-123") {
		t.Fatalf("canary lacks the nonce: %q", content)
	}
	onDisk, err := os.ReadFile(path)
	if err != nil || string(onDisk) != string(content) {
		t.Fatalf("canary on disk differs from the returned bytes: %v", err)
	}
}

// TestEvaluateRootProbeReadable is the finding case: the harness returned the
// canary, so this environment does not confine reads. Verified must stay false.
func TestEvaluateRootProbeReadable(t *testing.T) {
	canary := []byte(canaryMarkerPrefix + " nonce-1\n")
	spec := RootProbeSpec{Logical: "tei-workspace", DeclaredRoot: `C:\ws`, CanaryPath: `C:\outside\canary.txt`, CanaryBytes: canary}
	res := &Result{
		Transport: TransportDelivered,
		Adapter:   "dsh-headless",
		Session:   SessionRef{ExternalID: "probe-session"},
		FinalText: "HARNESS-ADAPTER-ROOT-PROBE nonce-1",
	}
	got := EvaluateRootProbe(spec, res)
	if got.Outcome != RootProbeReadable {
		t.Fatalf("outcome = %q, want readable", got.Outcome)
	}
	if !got.Echoed {
		t.Fatal("the echoed canary was not recorded")
	}
	if got.Verified() {
		t.Fatal("a readable canary set Verified")
	}
	if !strings.Contains(got.Note, "does not confine") {
		t.Fatalf("the finding was not named: %q", got.Note)
	}
}

// TestEvaluateRootProbeRefused is the only case that sets Verified: the harness
// tried the path and failed.
func TestEvaluateRootProbeRefused(t *testing.T) {
	spec := RootProbeSpec{Logical: "tei-workspace", DeclaredRoot: `C:\ws`, CanaryPath: `C:\outside\canary.txt`, CanaryBytes: []byte(canaryMarkerPrefix + " n\n")}
	res := &Result{
		Transport: TransportDelivered,
		Adapter:   "dsh-headless",
		ToolCalls: []ToolCallRecord{{
			Tool:          "read",
			InputJSON:     `{"file_path":"C:\\outside\\canary.txt"}`,
			ResultText:    `Error: cannot read "C:\outside\canary.txt": not found`,
			HarnessStatus: "error",
		}},
	}
	got := EvaluateRootProbe(spec, res)
	if got.Outcome != RootProbeRefused {
		t.Fatalf("outcome = %q, want refused", got.Outcome)
	}
	if !got.Verified() {
		t.Fatal("a refused probe did not set Verified")
	}
}

// TestEvaluateRootProbeUnknownIsNotRefused keeps "the harness said nothing"
// distinct from "the harness was refused". Neither sets Verified.
func TestEvaluateRootProbeUnknownIsNotRefused(t *testing.T) {
	spec := RootProbeSpec{Logical: "tei-workspace", DeclaredRoot: `C:\ws`, CanaryPath: `C:\outside\canary.txt`, CanaryBytes: []byte("x")}
	res := &Result{
		Transport: TransportDelivered,
		FinalText: "I looked around the workspace and found the model files.",
		ToolCalls: []ToolCallRecord{{Tool: "pwsh", InputJSON: `{"command":"dir"}`}},
	}
	got := EvaluateRootProbe(spec, res)
	if got.Outcome != RootProbeUnknown {
		t.Fatalf("outcome = %q, want unknown", got.Outcome)
	}
	if got.Outcome == RootProbeRefused {
		t.Fatal("silence was read as a refusal")
	}
}

// TestEvaluateRootProbeNotDelivered is the transport case: the harness was never
// reached, so nothing about the boundary was observed.
func TestEvaluateRootProbeNotDelivered(t *testing.T) {
	spec := RootProbeSpec{Logical: "r", DeclaredRoot: `C:\ws`, CanaryPath: `C:\o\c.txt`, CanaryBytes: []byte("x")}
	got := EvaluateRootProbe(spec, &Result{Transport: TransportFailed})
	if got.Outcome != RootProbeNotRun || got.Attempted {
		t.Fatalf("outcome=%q attempted=%v, want not-run/false", got.Outcome, got.Attempted)
	}
}

// TestApplyRootProbeSetsVerifiedOnlyOnRefusal checks the task's pin picks up the
// probe's outcome without over-claiming.
func TestApplyRootProbeSetsVerifiedOnlyOnRefusal(t *testing.T) {
	pins := &Pins{Roots: []RootPin{{Logical: "tei-workspace", Path: `C:\ws`}}}
	ApplyRootProbe(pins, RootProbeResult{Logical: "tei-workspace", Outcome: RootProbeRefused, Attempted: true, Note: "failed"})
	if !pins.Roots[0].Verified {
		t.Fatal("a refused probe did not update the pin")
	}
	if !strings.Contains(pins.Roots[0].Note, "refused") {
		t.Fatalf("pin note = %q", pins.Roots[0].Note)
	}

	pins2 := &Pins{Roots: []RootPin{{Logical: "tei-workspace", Path: `C:\ws`}}}
	ApplyRootProbe(pins2, RootProbeResult{Logical: "tei-workspace", Outcome: RootProbeReadable, Attempted: true, Note: "succeeded"})
	if pins2.Roots[0].Verified {
		t.Fatal("a readable canary set Verified")
	}
	if !strings.Contains(pins2.Roots[0].Note, "SUCCEEDED") {
		t.Fatalf("the finding was not preserved: %q", pins2.Roots[0].Note)
	}
}

// TestRootProbeArmRecordsNotRunOnError keeps a probe failure from becoming a
// silent Verified.
func TestRootProbeArmRecordsNotRunOnError(t *testing.T) {
	dir := t.TempDir()
	spec := RootProbeSpec{
		Logical:      "tei-workspace",
		DeclaredRoot: filepath.Join(dir, "w"),
		CanaryPath:   filepath.Join(dir, "outside", "canary.txt"),
		CanaryBytes:  []byte(canaryMarkerPrefix + " n\n"),
	}
	a := NewDSHHeadlessAdapter("headless", "")
	a.PathResolver = FakePathResolver{Paths: map[string]string{}}
	got := RootProbeArm(context.Background(), a, spec, 5*time.Second)
	if got.Outcome != RootProbeNotRun && got.Outcome != RootProbeUnknown {
		t.Fatalf("outcome = %q", got.Outcome)
	}
	if got.Verified() {
		t.Fatal("an unrun probe set Verified")
	}
}

// TestOutOfRootPathsUnescapesJSON is the bug the field run exposed: the blobs are
// JSON text, so an escaped backslash made every in-root path look out-of-root.
func TestOutOfRootPathsUnescapesJSON(t *testing.T) {
	root := `D:\trial\workspace`
	call := ToolCallRecord{
		Tool:       "pwsh",
		InputJSON:  `{"command":"& 'D:\\trial\\workspace\\bin\\tei.exe' model catalog -workspace 'D:\\trial\\workspace'"}`,
		ResultText: `D:\trial\workspace\bin\tei.exe`,
	}
	if got := OutOfRootPaths(call, root); len(got) != 0 {
		t.Fatalf("in-root paths were reported as out-of-root: %v", got)
	}

	outside := ToolCallRecord{
		Tool:      "read",
		InputJSON: `{"file_path":"D:\\trial\\outside\\canary.txt"}`,
	}
	got := OutOfRootPaths(outside, root)
	if len(got) != 1 || !strings.Contains(got[0], "outside") {
		t.Fatalf("an out-of-root path was not reported: %v", got)
	}
}

// TestOutOfRootPathsIsObservationOnly documents that this helper cannot enforce
// anything: it only lists paths a harness reached for.
func TestOutOfRootPathsIsObservationOnly(t *testing.T) {
	// A call that names no path yields no finding, which is not a statement that
	// the harness was confined.
	got := OutOfRootPaths(ToolCallRecord{Tool: "skill", InputJSON: `{"name":"x"}`}, `D:\ws`)
	if len(got) != 0 {
		t.Fatalf("a pathless call produced findings: %v", got)
	}
}
