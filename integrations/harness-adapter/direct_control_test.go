package harnessadapter

import (
	"context"
	"strings"
	"testing"
)

// TestDirectControlIsDeterministic checks that the control arm produces the same
// record twice for the same task, which is what makes it usable as a baseline.
func TestDirectControlIsDeterministic(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "tei", Result: ExecResult{ExitCode: 0, Stdout: []byte(`{"ok":true,"result":{"effect":"read-only","validation":{"ok":true,"errorCount":0,"warningCount":3}}}`)}},
	}}
	task := Task{ID: "t", Prompt: "p", Tools: []ToolOffer{{
		Name: "tei.validate", Command: []string{"tei", "validate", "-workspace", `C:\w`, "-json"},
	}}}
	a := NewDirectControlAdapter()
	a.Runner = fr
	first, err := a.Run(context.Background(), task, nil)
	if err != nil {
		t.Fatalf("run: %v", err)
	}
	second, err := a.Run(context.Background(), task, nil)
	if err != nil {
		t.Fatalf("run: %v", err)
	}
	if first.Summary() != second.Summary() {
		t.Fatalf("control arm is not deterministic:\n%s\n%s", first.Summary(), second.Summary())
	}
	if first.Run != RunCompleted || second.Run != RunCompleted {
		t.Fatalf("expected completed, got %q/%q", first.Run, second.Run)
	}
}

// TestDirectControlHasNoSession is the structural statement that the control arm
// is not a harness: it must not fabricate a session.
func TestDirectControlHasNoSession(t *testing.T) {
	caps := map[Capability]bool{}
	for _, c := range NewDirectControlAdapter().Capabilities() {
		caps[c] = true
	}
	if caps[CapSessionCreate] {
		t.Fatal("control arm claims session:create")
	}
	if caps[CapSessionResume] {
		t.Fatal("control arm claims session:resume")
	}
	if caps[CapSkillLoad] {
		t.Fatal("control arm claims skill:load")
	}
	if !caps[CapToolInvoke] {
		t.Fatal("control arm does not claim tool:invoke")
	}
}

// TestDirectControlSeparatesOperationFromValidation is ADR-0048 §2.4 items 2 and
// 3 in test form: an operation can complete while validation fails.
func TestDirectControlSeparatesOperationFromValidation(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "tei", Result: ExecResult{ExitCode: 0, Stdout: []byte(
			`{"ok":true,"result":{"effect":"read-only","validation":{"ok":false,"errorCount":2,"warningCount":0}}}`)}},
	}}
	task := Task{ID: "t", Tools: []ToolOffer{{
		Name: "tei.validate", Command: []string{"tei", "validate"},
	}}}
	a := NewDirectControlAdapter()
	a.Runner = fr
	res, err := a.Run(context.Background(), task, nil)
	if err != nil {
		t.Fatalf("run: %v", err)
	}
	v := res.ToolCalls[0].ProductVerdict
	if v == nil {
		t.Fatal("product verdict was dropped")
	}
	if !v.OperationCompleted {
		t.Fatal("operation completion was lost")
	}
	if v.ValidationPassed == nil || *v.ValidationPassed {
		t.Fatal("validation failure was not recorded separately")
	}
}

// TestDirectControlReportsNothingRan stops an all-unsupported task from reading
// as a completed run.
func TestDirectControlReportsNothingRan(t *testing.T) {
	task := Task{ID: "t", Tools: []ToolOffer{{Name: "tei.inspect"}}}
	a := NewDirectControlAdapter()
	a.Runner = &FakeRunner{}
	res, err := a.Run(context.Background(), task, nil)
	if err != nil {
		t.Fatalf("run: %v", err)
	}
	if res.Run != RunError {
		t.Fatalf("run state = %q, want error", res.Run)
	}
	found := false
	for _, d := range res.Diagnostics {
		if d.Code == "control-nothing-ran" {
			found = true
		}
	}
	if !found {
		t.Fatal("nothing-ran diagnostic missing")
	}
	if !containsStr(res.Unsupported, "tool:tei.inspect:no-command") {
		t.Fatalf("command-less tool not reported: %v", res.Unsupported)
	}
}

// TestDirectControlRecordsNonZeroExit keeps a failing product CLI visible as a
// failure rather than folding it into "completed".
func TestDirectControlRecordsNonZeroExit(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "tei", Result: ExecResult{ExitCode: 2, Stderr: []byte("unknown command\n")}},
	}}
	task := Task{ID: "t", Tools: []ToolOffer{{Name: "tei.validate", Command: []string{"tei", "validate"}}}}
	a := NewDirectControlAdapter()
	a.Runner = fr
	res, _ := a.Run(context.Background(), task, nil)
	if res.Run != RunError {
		t.Fatalf("non-zero exit mapped to %q", res.Run)
	}
	if res.ToolCalls[0].ExitCode == nil || *res.ToolCalls[0].ExitCode != 2 {
		t.Fatalf("exit code not recorded: %v", res.ToolCalls[0].ExitCode)
	}
}

// TestDecodeProductEnvelopeIgnoresNonJSON keeps a text answer from being parsed
// into a fabricated verdict.
func TestDecodeProductEnvelopeIgnoresNonJSON(t *testing.T) {
	v, diags := decodeProductEnvelope([]byte("tei tei.cli.version/v0 windows/amd64"))
	if v != nil {
		t.Fatalf("non-JSON output produced a verdict: %+v", v)
	}
	if diags != nil {
		t.Fatalf("non-JSON output produced diagnostics: %v", diags)
	}
}

// TestDecodeProductEnvelopeFailureCode keeps the product's own failure code.
func TestDecodeProductEnvelopeFailureCode(t *testing.T) {
	v, _ := decodeProductEnvelope([]byte(`{"ok":false,"failure":{"code":"workspace-not-found","message":"no"}}`))
	if v == nil || v.FailureCode != "workspace-not-found" {
		t.Fatalf("failure code lost: %+v", v)
	}
	if v.OperationCompleted {
		t.Fatal("a failed envelope reported the operation as completed")
	}
}

// TestDirectControlUsesFirstRootAsWorkDir checks the control arm reads from the
// same place a harness would be confined to.
func TestDirectControlUsesFirstRootAsWorkDir(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "tei", Result: ExecResult{ExitCode: 0, Stdout: []byte(`{"ok":true}`)}},
	}}
	a := NewDirectControlAdapter()
	a.Runner = fr
	task := Task{
		ID:    "t",
		Pins:  Pins{Roots: []RootPin{{Logical: "tei-workspace", Path: `C:\ws`}}},
		Tools: []ToolOffer{{Name: "tei.validate", Command: []string{"tei", "validate"}}},
	}
	if _, err := a.Run(context.Background(), task, nil); err != nil {
		t.Fatalf("run: %v", err)
	}
	if len(fr.Calls) != 1 || fr.Calls[0].Dir != `C:\ws` {
		t.Fatalf("control arm cwd = %q", fr.Calls[0].Dir)
	}
}

func containsStr(list []string, want string) bool {
	for _, s := range list {
		if strings.TrimSpace(s) == want {
			return true
		}
	}
	return false
}
