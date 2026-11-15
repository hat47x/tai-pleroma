package harnessadapter

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// TestSHOOfferPinsOneDocument is the projection's whole point: SHO's inspect takes
// a path, and letting the model supply it would widen the readable range past the
// declared root. The offer must not expose a path input.
func TestSHOOfferPinsOneDocument(t *testing.T) {
	dir := t.TempDir()
	script := filepath.Join(dir, "bin", "sho-inspect.cjs")
	doc := filepath.Join(dir, "note.md")
	for _, p := range []string{script, doc} {
		if err := os.MkdirAll(filepath.Dir(p), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(p, []byte("x"), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	tool := NewSHOReadOnlyTool("node", script, doc, dir)
	offers, unsupported := tool.Offers()
	if len(unsupported) > 0 {
		t.Fatalf("an in-root document was refused: %v", unsupported)
	}
	if len(offers) != 1 {
		t.Fatalf("expected 1 offer, got %d", len(offers))
	}
	o := offers[0]
	if !o.ReadOnly {
		t.Fatal("the SHO offer is not read-only")
	}
	// The schema must declare no properties: the document is pinned, not chosen.
	if strings.Contains(string(o.InputSchema), `"properties":{`) == false {
		t.Fatalf("the SHO input schema is not the empty object: %s", o.InputSchema)
	}
	if !strings.Contains(strings.Join(o.Command, " "), doc) {
		t.Fatalf("the pinned document is missing from argv: %v", o.Command)
	}
	if strings.Contains(string(o.InputSchema), "document") {
		t.Fatalf("the schema exposes a path input: %s", o.InputSchema)
	}
}

// TestSHORefusesDocumentOutsideRoot keeps the projection from naming a path the
// declared root does not cover.
func TestSHORefusesDocumentOutsideRoot(t *testing.T) {
	base := t.TempDir()
	root := filepath.Join(base, "root")
	outside := filepath.Join(base, "outside", "note.md")
	if err := os.MkdirAll(root, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(filepath.Dir(outside), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(outside, []byte("x"), 0o644); err != nil {
		t.Fatal(err)
	}
	tool := NewSHOReadOnlyTool("node", filepath.Join(root, "sho-inspect.cjs"), outside, root)
	_, unsupported := tool.Offers()
	if len(unsupported) == 0 {
		t.Fatal("an out-of-root document was offered")
	}
	if !containsStr(unsupported, "sho.inspect:document-outside-allowed-root") {
		t.Fatalf("the refusal was not named: %v", unsupported)
	}
}

// TestSHONoMCPServerIsReported is the honest gap: SHO has no stdio JSON-RPC
// server, and the adapter does not write one.
func TestSHONoMCPServerIsReported(t *testing.T) {
	tool := NewSHOReadOnlyTool("node", "/x/sho-inspect.cjs", "/r/note.md", "/r")
	if _, err := tool.MCPServerSpec("sho"); err == nil {
		t.Fatal("an MCP server spec was produced for a product that has no MCP server")
	}
}

// TestSHODecodeEnvelopeDoesNotBorrowTEIShape keeps SHO's own result shape
// separate: SHO reports `status` and a bare-string `error`, with no `ok`.
func TestSHODecodeEnvelopeDoesNotBorrowTEIShape(t *testing.T) {
	ok := []byte(`{"status":"indexed","source":{"sha256":"sha256:x","byteLength":3},"linkOccurrenceCount":2}`)
	v, _ := decodeSHOEnvelope(ok)
	if v == nil || !v.OperationCompleted {
		t.Fatalf("a successful index was not read as completed: %+v", v)
	}
	if v.ValidationPassed != nil {
		t.Fatal("SHO evaluates no validation, so ValidationPassed must stay nil")
	}
	failed := []byte(`{"error":"not-found","message":"ENOENT: no such file"}`)
	bad, _ := decodeSHOEnvelope(failed)
	if bad == nil || bad.OperationCompleted {
		t.Fatalf("an error envelope was read as completed: %+v", bad)
	}
	if bad.FailureCode != "not-found" {
		t.Fatalf("the product's own failure code was not kept: %q", bad.FailureCode)
	}
	// A TEI-shaped envelope must not be silently understood as a SHO result.
	teiShaped := []byte(`{"schemaVersion":"tei.cli.validate/v0","ok":true}`)
	tv, _ := decodeSHOEnvelope(teiShaped)
	if tv != nil && tv.OperationCompleted {
		t.Fatal("a TEI-shaped envelope was accepted as a successful SHO result")
	}
}

// TestSHOInvokeUsesPinnedArgv checks the invoker names the script, the pinned
// document and the cwd.
func TestSHOInvokeUsesPinnedArgv(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "inspect", Result: ExecResult{ExitCode: 0, Stdout: []byte(`{"status":"indexed","linkOccurrenceCount":1}`)}},
	}}
	tool := NewSHOReadOnlyTool("node", `C:\sho\bin\sho-inspect.cjs`, `C:\sho\note.md`, `C:\sho`)
	tool.Runner = fr
	rec, err := tool.Invoke(context.Background(), "inspect")
	if err != nil {
		t.Fatalf("Invoke: %v", err)
	}
	if rec.ExitCode == nil || *rec.ExitCode != 0 {
		t.Fatalf("exit = %v", rec.ExitCode)
	}
	if rec.ProductVerdict == nil || !rec.ProductVerdict.OperationCompleted {
		t.Fatalf("verdict missing: %+v", rec.ProductVerdict)
	}
	want := []string{"node", `C:\sho\bin\sho-inspect.cjs`, "inspect", `C:\sho\note.md`}
	if strings.Join(fr.Calls[0].Argv, " ") != strings.Join(want, " ") {
		t.Fatalf("argv = %v, want %v", fr.Calls[0].Argv, want)
	}
	if fr.Calls[0].Dir != `C:\sho` {
		t.Fatalf("cwd = %q", fr.Calls[0].Dir)
	}
}

// TestSHOMissingInputsAreReported keeps an incomplete projection from offering a
// tool that cannot run.
func TestSHOMissingInputsAreReported(t *testing.T) {
	tool := NewSHOReadOnlyTool("node", "", "", "")
	if offers, _ := tool.Offers(); len(offers) != 0 {
		t.Fatalf("a projection with no script or document produced %d offers", len(offers))
	}
	if _, err := tool.Invoke(context.Background(), "inspect"); err == nil {
		t.Fatal("an incomplete projection invoked successfully")
	}
}
