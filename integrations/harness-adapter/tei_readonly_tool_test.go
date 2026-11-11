package harnessadapter

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// TestTEIOffersOnlyAllowlistedCommands keeps the projection inside TEI's own
// advertised read-only catalog.
func TestTEIOffersOnlyAllowlistedCommands(t *testing.T) {
	tool := NewTEIReadOnlyTool(`C:\bin\tei.exe`, `C:\ws`)
	offers, unsupported := tool.Offers()
	if len(offers) == 0 {
		t.Fatal("no offers produced")
	}
	for _, o := range offers {
		if !strings.HasPrefix(o.Name, "tei.") {
			t.Fatalf("offer name %q does not follow the product.command convention", o.Name)
		}
		if !o.ReadOnly {
			t.Fatalf("offer %q is not marked read-only", o.Name)
		}
		if len(o.AllowedRoots) != 1 || o.AllowedRoots[0] != "tei-workspace" {
			t.Fatalf("offer %q does not name exactly the workspace root: %v", o.Name, o.AllowedRoots)
		}
		if len(o.Command) == 0 || o.Command[0] != `C:\bin\tei.exe` {
			t.Fatalf("offer %q command does not start at the pinned binary: %v", o.Name, o.Command)
		}
		for _, part := range o.Command {
			if strings.Contains(part, `C:\ws`) && !strings.Contains(strings.Join(o.Command, " "), "-workspace") {
				t.Fatalf("offer %q passes the workspace without the flag: %v", o.Name, o.Command)
			}
		}
	}
	// Commands that need a subject reference the projection does not own must be
	// reported, not silently dropped.
	if !containsStr(unsupported, "tei.inspect:missing-required-input") {
		t.Fatalf("inspect not reported as unoffered: %v", unsupported)
	}
}

// TestTEIArgvIsExact pins the argv for the two commands the pilot uses, so a
// flag drift is visible without running anything.
func TestTEIArgvIsExact(t *testing.T) {
	tool := NewTEIReadOnlyTool(`C:\bin\tei.exe`, `C:\ws`)
	got, ok := tool.argvFor("model catalog")
	if !ok {
		t.Fatal("model catalog is not offered")
	}
	want := []string{`C:\bin\tei.exe`, "model", "catalog", "-workspace", `C:\ws`}
	if strings.Join(got, " ") != strings.Join(want, " ") {
		t.Fatalf("argv = %v, want %v", got, want)
	}
	got, ok = tool.argvFor("validate")
	if !ok {
		t.Fatal("validate is not offered")
	}
	want = []string{`C:\bin\tei.exe`, "validate", "-workspace", `C:\ws`, "-json"}
	if strings.Join(got, " ") != strings.Join(want, " ") {
		t.Fatalf("argv = %v, want %v", got, want)
	}
}

// TestTEIWriteCommandsAreNotOffered is the scope guard: a command outside the
// read-only projection must not be buildable, even though TEI dispatches it.
func TestTEIWriteCommandsAreNotOffered(t *testing.T) {
	tool := NewTEIReadOnlyTool(`C:\bin\tei.exe`, `C:\ws`)
	for _, cmd := range []string{"view", "self-build", "dbcheck", "artifacts", "grants"} {
		if _, ok := tool.argvFor(cmd); ok {
			t.Fatalf("command %q is outside the read-only projection but was built", cmd)
		}
	}
}

// TestTEIMissingWorkspaceIsNotOffered keeps a workspace-less projection from
// advertising tools that cannot run.
func TestTEMissingWorkspaceIsNotOffered(t *testing.T) {
	tool := NewTEIReadOnlyTool(`C:\bin\tei.exe`, "")
	offers, unsupported := tool.Offers()
	for _, o := range offers {
		if o.Name != "tei.version" {
			t.Fatalf("offer %q was produced without a workspace", o.Name)
		}
	}
	if len(unsupported) == 0 {
		t.Fatal("no gap reported for the missing workspace")
	}
}

// TestTEIInvokeUsesThePinnedBinary checks the invoker names the exact binary and
// cwd, and records the product exit code separately from any harness status.
func TestTEIInvokeUsesThePinnedBinary(t *testing.T) {
	bin := filepath.Join(t.TempDir(), "tei.exe")
	if err := os.WriteFile(bin, []byte("stub"), 0o644); err != nil {
		t.Fatal(err)
	}
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "validate", Result: ExecResult{ExitCode: 0, Stdout: []byte(`{"ok":true,"result":{"effect":"read-only"}}`)}},
	}}
	tool := NewTEIReadOnlyTool(bin, `C:\ws`)
	tool.Runner = fr
	rec, err := tool.Invoke(context.Background(), "validate")
	if err != nil {
		t.Fatalf("Invoke: %v", err)
	}
	if rec.ExitCode == nil || *rec.ExitCode != 0 {
		t.Fatalf("exit code = %v", rec.ExitCode)
	}
	if rec.ProductVerdict == nil || !rec.ProductVerdict.OperationCompleted {
		t.Fatalf("product verdict missing: %+v", rec.ProductVerdict)
	}
	if len(fr.Calls) != 1 || fr.Calls[0].Argv[0] != bin {
		t.Fatalf("invoker did not use the pinned binary: %v", fr.Calls)
	}
	if fr.Calls[0].Dir != `C:\ws` {
		t.Fatalf("invoker cwd = %q", fr.Calls[0].Dir)
	}
}

// TestTEIInvokeRejectsUnofferedCommand keeps the invoker inside the allowlist.
func TestTEIInvokeRejectsUnofferedCommand(t *testing.T) {
	tool := NewTEIReadOnlyTool(`C:\bin\tei.exe`, `C:\ws`)
	if _, err := tool.Invoke(context.Background(), "view"); err == nil {
		t.Fatal("an unoffered command was invoked")
	}
}

// TestDigestWorkspaceIsAnObservation checks the digest covers what it says it
// covers: the immediate file names and sizes, not the parsed model.
func TestDigestWorkspaceIsAnObservation(t *testing.T) {
	dir := t.TempDir()
	if err := os.WriteFile(filepath.Join(dir, "tei.workspace.yaml"), []byte("x"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(filepath.Join(dir, "semantic"), 0o755); err != nil {
		t.Fatal(err)
	}
	digest, files, bytes, err := DigestWorkspace(dir)
	if err != nil {
		t.Fatalf("DigestWorkspace: %v", err)
	}
	if files != 1 || bytes != 1 {
		t.Fatalf("files=%d bytes=%d, want 1/1 (directories are not files)", files, bytes)
	}
	if !strings.HasPrefix(digest, "sha256:") {
		t.Fatalf("digest = %q", digest)
	}
}

// TestResolveBinaryPrefersExplicitPath checks the evidence can name the exact
// executable that will run.
func TestResolveBinaryPrefersExplicitPath(t *testing.T) {
	dir := t.TempDir()
	bin := filepath.Join(dir, "tei.exe")
	if err := os.WriteFile(bin, []byte("stub"), 0o644); err != nil {
		t.Fatal(err)
	}
	tool := NewTEIReadOnlyTool(bin, dir)
	got, err := tool.ResolveBinary()
	if err != nil {
		t.Fatalf("ResolveBinary: %v", err)
	}
	if got != bin {
		t.Fatalf("resolved = %q, want %q", got, bin)
	}
	tool.Binary = filepath.Join(dir, "missing.exe")
	if _, err := tool.ResolveBinary(); err == nil {
		t.Fatal("a missing explicit binary resolved anyway")
	}
}
