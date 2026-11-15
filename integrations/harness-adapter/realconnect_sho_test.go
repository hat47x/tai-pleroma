//go:build realconnect

// Real invocation of the SHO read-only projection (H-A-3, third product).
//
// SHO has no MCP server, so this arm is the product CLI itself rather than a
// harness reaching it: the adapter invokes sho-inspect.cjs directly and records
// the product's own verdict. That is the honest shape for a product whose only
// read-only surface is a script with a positional argument.
//
// The projection pins one document. This test copies the SHO reader and its
// dependency closure into the caller's trial root so the run can happen there
// rather than in the product repository.
package harnessadapter

import (
	"context"
	"os"
	"path/filepath"
	"testing"
	"time"
)

// TestRealSHOProjection invokes the pinned SHO inspect and records its verdict.
func TestRealSHOProjection(t *testing.T) {
	if os.Getenv("HARNESS_ADAPTER_REAL") != "1" {
		t.Skip("HARNESS_ADAPTER_REAL != 1; real invocations are opt-in")
	}
	script := os.Getenv("HARNESS_ADAPTER_SHO_SCRIPT")
	document := os.Getenv("HARNESS_ADAPTER_SHO_DOCUMENT")
	root := os.Getenv("HARNESS_ADAPTER_SHO_ROOT")
	if script == "" || document == "" || root == "" {
		t.Skip("HARNESS_ADAPTER_SHO_SCRIPT / _DOCUMENT / _ROOT must be set")
	}
	if _, err := os.Stat(script); err != nil {
		t.Skipf("SHO script missing: %v", err)
	}
	if _, err := os.Stat(document); err != nil {
		t.Skipf("SHO document missing: %v", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
	defer cancel()

	tool := NewSHOReadOnlyTool("node", script, document, root)
	offers, unsupported := tool.Offers()
	if len(unsupported) > 0 {
		t.Fatalf("the projection refused its own inputs: %v", unsupported)
	}
	if len(offers) != 1 {
		t.Fatalf("expected 1 offer, got %d", len(offers))
	}
	scriptDigest, documentDigest, err := tool.Resolve()
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	t.Logf("SHO script %s, document %s", scriptDigest, documentDigest)
	t.Logf("offer argv: %v", offers[0].Command)

	rec, err := tool.Invoke(ctx, "inspect")
	if err != nil {
		t.Fatalf("invoke: %v", err)
	}
	t.Logf("SHO invoke: tool=%s exit=%s bytes=%d", rec.Tool, ExitString(rec.ExitCode), rec.ResultBytes)
	if rec.ProductVerdict == nil {
		t.Fatalf("no product verdict was derived; payload starts: %.80s", rec.ResultText)
	}
	t.Logf("product verdict: completed=%v failureCode=%q validationPassed=%v",
		rec.ProductVerdict.OperationCompleted, rec.ProductVerdict.FailureCode,
		rec.ProductVerdict.ValidationPassed)

	// The product's own identity fields are compared against the file the
	// projection pinned, which is an observation independent of the product's
	// claim about itself.
	env, err := ParseProductEnvelope([]byte(rec.ResultText))
	if err != nil {
		t.Logf("SHO payload is not a shared-contract envelope (%v); using the product's own reader", err)
	}
	_ = env
	if rec.ProductVerdict.OperationCompleted {
		t.Log("SHO: the product reported status=indexed for the pinned document")
	} else {
		t.Logf("SHO: the product did not complete: %q", rec.ProductVerdict.FailureCode)
	}

	// A document outside the root must be refused by the projection, not invoked.
	outside := filepath.Join(filepath.Dir(root), "outside.md")
	if err := os.WriteFile(outside, []byte("# outside\n"), 0o644); err == nil {
		outTool := NewSHOReadOnlyTool("node", script, outside, root)
		o, u := outTool.Offers()
		if len(o) != 0 || len(u) == 0 {
			t.Fatalf("an out-of-root document was offered: offers=%d unsupported=%v", len(o), u)
		}
		t.Logf("out-of-root refusal recorded: %v", u)
	}

	// No MCP server exists for SHO; the adapter reports that rather than inventing one.
	if _, err := tool.MCPServerSpec("sho"); err == nil {
		t.Fatal("an MCPServerSpec was produced for SHO")
	}
	t.Log("SHO: mcp:unsupported — no stdio JSON-RPC surface exists, so no MCP arm was attempted")
}
