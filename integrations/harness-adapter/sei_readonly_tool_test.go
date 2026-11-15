package harnessadapter

import (
	"context"
	"strings"
	"testing"
)

// TestSEIOffersOnlyReadOnlyCommands keeps a write command out of the projection.
// SEI's own CLI has init/add/export/gate; offering any of them through the
// adapter would put a write behind the read-only contract.
func TestSEIOffersOnlyReadOnlyCommands(t *testing.T) {
	tool := NewSEIReadOnlyTool("sei.exe", `C:\store`)
	offers, unsupported := tool.Offers()
	if len(offers) == 0 {
		t.Fatal("no SEI offers produced")
	}
	for _, o := range offers {
		if !o.ReadOnly {
			t.Fatalf("offer %q is not read-only", o.Name)
		}
		if !strings.HasPrefix(o.Name, "sei.") {
			t.Fatalf("offer %q does not follow the product.command convention", o.Name)
		}
		for _, writeCmd := range []string{"sei.init", "sei.add", "sei.export", "sei.gate", "sei.mcp"} {
			if o.Name == writeCmd {
				t.Fatalf("a write or transport command was offered: %q", o.Name)
			}
		}
	}
	// verify needs a bundle path the projection does not own.
	if !containsStr(unsupported, "sei.verify:missing-required-input") {
		t.Fatalf("verify not reported as unoffered: %v", unsupported)
	}
}

// TestSEIResumeArgvIsJSON pins the argv: the adapter compares structured
// identity, so a prose resume is not offered.
func TestSEIResumeArgvIsJSON(t *testing.T) {
	tool := NewSEIReadOnlyTool(`C:\bin\sei.exe`, `C:\store`)
	argv, ok := tool.argvFor("resume")
	if !ok {
		t.Fatal("resume is not offered")
	}
	want := []string{`C:\bin\sei.exe`, "resume", "-data-root", `C:\store`, "-json"}
	if strings.Join(argv, " ") != strings.Join(want, " ") {
		t.Fatalf("argv = %v, want %v", argv, want)
	}
}

// TestSEIMCPSpecIsReadOnly is the structural guarantee: the rendered spec carries
// -read-only, so the harness cannot reach add_recommendation/add_decision through
// this projection.
func TestSEIMCPSpecIsReadOnly(t *testing.T) {
	tool := NewSEIReadOnlyTool(`C:\bin\sei.exe`, `C:\store`)
	spec := tool.MCPServerSpec("sei")
	if err := spec.Validate(); err != nil {
		t.Fatalf("spec: %v", err)
	}
	joined := strings.Join(spec.Args, " ")
	if !strings.Contains(joined, "-read-only") {
		t.Fatalf("the SEI MCP spec does not pass -read-only: %v", spec.Args)
	}
	if !strings.Contains(joined, "--data-root") {
		t.Fatalf("the SEI MCP spec does not name its store: %v", spec.Args)
	}
	if strings.Contains(joined, "-allow-decision") {
		t.Fatalf("the spec would offer a decision write: %v", spec.Args)
	}
}

// TestSEIMissingDataRootNotOffered keeps a store-less projection from
// advertising commands that cannot run.
func TestSEIMissingDataRootNotOffered(t *testing.T) {
	tool := NewSEIReadOnlyTool(`C:\bin\sei.exe`, "")
	offers, unsupported := tool.Offers()
	for _, o := range offers {
		if o.Name != "sei.version" {
		}
		if o.Name != "sei.version" {
			t.Fatalf("offer %q was produced without a data root", o.Name)
		}
	}
	if len(unsupported) == 0 {
		t.Fatal("no gap reported for the missing store")
	}
}

// TestSEIInvokeUsesPinnedBinary checks the invoker names the exact binary and
// cwd, and records the product exit separately.
func TestSEIInvokeUsesPinnedBinary(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "resume", Result: ExecResult{ExitCode: 0, Stdout: []byte(`{"bundle_id":"b","snapshot_digest":"sha256:x","record_count":0}`)}},
	}}
	tool := NewSEIReadOnlyTool(`C:\bin\sei.exe`, `C:\store`)
	tool.Runner = fr
	rec, err := tool.Invoke(context.Background(), "resume")
	if err != nil {
		t.Fatalf("Invoke: %v", err)
	}
	if rec.ExitCode == nil || *rec.ExitCode != 0 {
		t.Fatalf("exit = %v", rec.ExitCode)
	}
	if rec.ProductVerdict == nil || !rec.ProductVerdict.OperationCompleted {
		t.Fatalf("verdict missing: %+v", rec.ProductVerdict)
	}
	if len(fr.Calls) != 1 || fr.Calls[0].Argv[0] != `C:\bin\sei.exe` {
		t.Fatalf("invoker did not use the pinned binary: %v", fr.Calls)
	}
	if fr.Calls[0].Dir != `C:\store` {
		t.Fatalf("invoker cwd = %q", fr.Calls[0].Dir)
	}
}

// TestSEIInvokeRejectsUnofferedCommand keeps the invoker inside the allowlist.
func TestSEIInvokeRejectsUnofferedCommand(t *testing.T) {
	tool := NewSEIReadOnlyTool(`C:\bin\sei.exe`, `C:\store`)
	for _, cmd := range []string{"add", "init", "export", "gate", "mcp", "verify"} {
		if _, err := tool.Invoke(context.Background(), cmd); err == nil {
			t.Fatalf("unoffered command %q was invoked", cmd)
		}
	}
}
