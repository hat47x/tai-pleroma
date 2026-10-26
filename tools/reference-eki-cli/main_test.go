package main

import (
	"context"
	"os"
	"os/exec"
	"path/filepath"
	"testing"
)

func ekiRootForTest(t *testing.T) string {
	t.Helper()
	if _, err := exec.LookPath("go"); err != nil {
		t.Skip("go is not available")
	}
	root := os.Getenv("EKI_ROOT")
	if root == "" {
		root = filepath.Clean(filepath.Join("..", "..", "..", "eki-fabric"))
	}
	if _, err := os.Stat(filepath.Join(root, "cmd", "eki-control")); err != nil {
		t.Skip("EKI runtime is not available")
	}
	return root
}

func TestEKIVersionProbe(t *testing.T) {
	receipt := Run(context.Background(), ekiRootForTest(t))
	if !receipt.Passed {
		t.Fatalf("EKI version probe failed: %+v", receipt)
	}
	if !receipt.ReadOnly || receipt.TaskDelegated || receipt.AuthorityVerified {
		t.Fatalf("EKI probe overclaims: %+v", receipt)
	}
	if receipt.ControlVersion == "" || receipt.AgentVersion == "" || receipt.EkiCommit == "" || receipt.GoVersion == "" {
		t.Fatalf("EKI probe evidence is incomplete: %+v", receipt)
	}
}
