package main

import (
	"context"
	"os"
	"os/exec"
	"path/filepath"
	"testing"
)

func seiRootForTest(t *testing.T) string {
	t.Helper()
	if _, err := exec.LookPath("go"); err != nil {
		t.Skip("go is not available")
	}
	root := os.Getenv("SEI_ROOT")
	if root == "" {
		root = filepath.Clean(filepath.Join("..", "..", "..", "sei-cognition"))
	}
	if _, err := os.Stat(filepath.Join(root, "runtime", "go", "cmd", "sei")); err != nil {
		t.Skip("SEI runtime is not available")
	}
	return root
}

func TestSCN001DecisionMemoryProjection(t *testing.T) {
	receipt := Run(context.Background(), seiRootForTest(t))
	if !receipt.Passed {
		t.Fatalf("SEI decision projection failed: %+v", receipt)
	}
	if !receipt.StoreCreated || !receipt.ReadOnlyProjection || receipt.AuthorityVerified || receipt.HumanReviewed || receipt.Published {
		t.Fatalf("receipt overclaims authority or publication: %+v", receipt)
	}
	if receipt.Decision.ID != "dec-01" || len(receipt.Unresolved) != 1 || receipt.Unresolved[0].Ref != "authority:unknown" {
		t.Fatalf("decision memory is incomplete: %+v", receipt)
	}
	if receipt.SeiCommit == "" || receipt.GoVersion == "" {
		t.Fatalf("version evidence is missing: %+v", receipt)
	}
}
