package harnessadapter

import (
	"context"
	"errors"
	"os/exec"
	"strings"
	"testing"
)

// TestFakeRunnerRecordsSpecs checks the test double records exactly what the
// adapter produced, which is what makes an argv assertion meaningful.
func TestFakeRunnerRecordsSpecs(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "validate", Result: ExecResult{ExitCode: 0, Stdout: []byte("ok")}},
	}}
	got, err := fr.Exec(context.Background(), ExecSpec{
		Argv:  []string{"tei", "validate", "-workspace", `C:\ws`},
		Dir:   `C:\ws`,
		Stdin: []byte("in"),
	})
	if err != nil {
		t.Fatalf("exec: %v", err)
	}
	if got.ExitCode != 0 || string(got.Stdout) != "ok" {
		t.Fatalf("scripted result not replayed: %+v", got)
	}
	if len(fr.Calls) != 1 {
		t.Fatalf("calls = %d", len(fr.Calls))
	}
	if fr.Calls[0].Dir != `C:\ws` || string(fr.Calls[0].Stdin) != "in" {
		t.Fatalf("spec not recorded: %+v", fr.Calls[0])
	}
}

// TestFakeRunnerDefaultAndErrors keeps the double honest about failure paths.
func TestFakeRunnerDefaultAndErrors(t *testing.T) {
	fr := &FakeRunner{Default: ExecResult{ExitCode: 3}}
	got, err := fr.Exec(context.Background(), ExecSpec{Argv: []string{"x"}})
	if err != nil || got.ExitCode != 3 {
		t.Fatalf("default not used: %+v %v", got, err)
	}
	fr2 := &FakeRunner{Script: []FakeStep{{Match: "x", Err: errors.New("boom")}}}
	if _, err := fr2.Exec(context.Background(), ExecSpec{Argv: []string{"x"}}); err == nil {
		t.Fatal("scripted error was swallowed")
	}
}

// TestProcessRunnerRejectsEmptyArgv keeps a malformed spec from spawning
// something unintended.
func TestProcessRunnerRejectsEmptyArgv(t *testing.T) {
	if _, err := (ProcessRunner{}).Exec(context.Background(), ExecSpec{}); err == nil {
		t.Fatal("empty argv was accepted")
	}
}

// TestFakePathResolverShapesErrNotFound keeps "not installed" distinguishable
// from "found but broken".
func TestFakePathResolverShapesErrNotFound(t *testing.T) {
	p := FakePathResolver{Paths: map[string]string{"dsh": `C:\dsh.cmd`}}
	if got, err := p.LookPath("dsh"); err != nil || got != `C:\dsh.cmd` {
		t.Fatalf("known path not resolved: %q %v", got, err)
	}
	_, err := p.LookPath("nope")
	var ee *exec.Error
	if !errors.As(err, &ee) || !errors.Is(ee.Err, exec.ErrNotFound) {
		t.Fatalf("unknown path error is not ErrNotFound: %v", err)
	}
}

// TestQuoteIsEvidenceOnly documents that Quote is for records, not for building
// commands: no adapter may shell out through it.
func TestQuoteIsEvidenceOnly(t *testing.T) {
	got := Quote([]string{"tei", "validate", "-workspace", `C:\my ws`})
	if !strings.HasPrefix(got, "tei validate -workspace ") {
		t.Fatalf("quote = %q", got)
	}
	if !strings.Contains(got, `"C:\my ws"`) {
		t.Fatalf("a path with a space was not quoted: %q", got)
	}
}
