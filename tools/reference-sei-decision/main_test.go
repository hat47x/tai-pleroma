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
	if receipt.Decision.ID != "dec-01" || receipt.ProvisionalDecision.ID != "dec-02" ||
		!receipt.ProvisionalApproved || len(receipt.Unresolved) < 2 {
		t.Fatalf("decision memory is incomplete: %+v", receipt)
	}
	refs := map[string]bool{}
	for _, item := range receipt.Unresolved {
		refs[item.Ref] = true
	}
	if !refs["authority:unknown"] || !refs["publication:unapproved"] {
		t.Fatalf("unresolved refs are incomplete: %+v", receipt)
	}
	if receipt.SeiCommit == "" || receipt.GoVersion == "" {
		t.Fatalf("version evidence is missing: %+v", receipt)
	}
}
