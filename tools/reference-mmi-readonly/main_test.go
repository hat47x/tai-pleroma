package main

import (
	"context"
	"os"
	"path/filepath"
	"testing"
)

func mmiRootForTest(t *testing.T) string {
	t.Helper()
	root := os.Getenv("MMI_ROOT")
	if root == "" {
		root = filepath.Clean(filepath.Join("..", "..", "..", "markdown-matrix-injector"))
	}
	if _, err := os.Stat(filepath.Join(root, "03_Implement", "node_modules")); err != nil {
		t.Skip("MMI node_modules is not available")
	}
	if _, err := os.Stat(filepath.Join(root, "03_Implement", "src", "cli", "mcp.ts")); err != nil {
		t.Skip("MMI MCP source is not available")
	}
	return root
}

func TestReadOnlyInspectKeepsSources(t *testing.T) {
	root := mmiRootForTest(t)
	workspace, err := filepath.Abs(filepath.Join("testdata", "workspace"))
	if err != nil {
		t.Fatal(err)
	}
	receipt := Run(context.Background(), root, workspace)
	if !receipt.Passed {
		t.Fatalf("read-only MMI inspect failed: %+v", receipt)
	}
	if !receipt.RealProductConnected || !receipt.ReadOnly || !receipt.BoundaryRejected {
		t.Fatalf("receipt overclaims or misses a boundary: %+v", receipt)
	}
	if receipt.SourceDigestBefore != receipt.SourceDigestAfter ||
		receipt.GuideDigestBefore != receipt.GuideDigestAfter {
		t.Fatalf("MMI changed a source file: %+v", receipt)
	}
	if receipt.CandidateCount == 0 {
		t.Fatalf("inspect returned no candidates: %+v", receipt)
	}
	if receipt.ProtocolVersion != protocolVersion || receipt.Server == "" {
		t.Fatalf("MCP negotiation evidence is missing: %+v", receipt)
	}
}
