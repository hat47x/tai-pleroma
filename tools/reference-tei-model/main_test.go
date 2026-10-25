package main

import (
	"context"
	"os"
	"os/exec"
	"path/filepath"
	"testing"
)

func teiRootForTest(t *testing.T) string {
	t.Helper()
	if _, err := exec.LookPath("go"); err != nil {
		t.Skip("go is not available")
	}
	root := os.Getenv("TEI_ROOT")
	if root == "" {
		root = filepath.Clean(filepath.Join("..", "..", "..", "tei-platform"))
	}
	if _, err := os.Stat(filepath.Join(root, "cmd", "tei")); err != nil {
		t.Skip("TEI runtime is not available")
	}
	return root
}

func TestTEIWorkspaceValidation(t *testing.T) {
	receipt := Run(context.Background(), teiRootForTest(t), filepath.Join("testdata", "workspace"))
	if !receipt.Passed {
		t.Fatalf("TEI validation failed: %+v", receipt)
	}
	if !receipt.ReadOnly || receipt.Validation != "ok" || receipt.WorkspaceDigest == "" {
		t.Fatalf("receipt is incomplete: %+v", receipt)
	}
	if receipt.TeiCommit == "" || receipt.GoVersion == "" {
		t.Fatalf("version evidence is missing: %+v", receipt)
	}
}
