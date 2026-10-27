package main

import (
	"context"
	"os"
	"os/exec"
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
	if _, err := exec.LookPath("node"); err != nil {
		t.Skip("node is not available")
	}
	return root
}

func TestReadOnlyInspectKeepsSources(t *testing.T) {
	root := mmiRootForTest(t)
	workspace, err := filepath.Abs(filepath.Join("testdata", "workspace"))
	if err != nil {
		t.Fatal(err)
	}
	// Expectations come from the environment only, through the same parsing main
	// uses. Without them the run is record-only, so a checkout at another commit
	// (or a dirty one) still passes.
	config, err := parseConfig(nil, os.Getenv)
	if err != nil {
		t.Fatal(err)
	}
	options := config.Options
	receipt := RunWithOptions(context.Background(), root, workspace, options)
	if !receipt.Passed {
		t.Fatalf("read-only MMI inspect failed: %+v", receipt)
	}
	if !receipt.RealProductConnected || !receipt.ReadOnly || !receipt.BoundaryRejected || !receipt.MissingSourceRejected {
		t.Fatalf("receipt overclaims or misses a boundary: %+v", receipt)
	}
	if receipt.SourceDigestBefore != receipt.SourceDigestAfter ||
		receipt.GuideDigestBefore != receipt.GuideDigestAfter {
		t.Fatalf("MMI changed a source file: %+v", receipt)
	}
	if receipt.CandidateCount == 0 {
		t.Fatalf("inspect returned no candidates: %+v", receipt)
	}
	if receipt.SelectedRows != 3 || !receipt.ConflictPreserved {
		t.Fatalf("select did not preserve the conflict: %+v", receipt)
	}
	if len(receipt.ObservedIDs) != 3 || len(receipt.Selected) != 3 {
		t.Fatalf("selected observations are missing: %+v", receipt)
	}
	for _, observation := range receipt.Selected {
		if observation.ID == "" || observation.Text == "" || observation.Source == "" ||
			observation.SourceVersion == "" || observation.Availability == "" {
			t.Fatalf("selected observation is incomplete: %+v", observation)
		}
	}
	if receipt.ProtocolVersion != protocolVersion || receipt.Server == "" {
		t.Fatalf("MCP negotiation evidence is missing: %+v", receipt)
	}
	if receipt.MmiCommit == "" || receipt.PackageLockDigest == "" || receipt.NodeVersion == "" {
		t.Fatalf("version pinning evidence is missing: %+v", receipt)
	}
	// MMI's own values must not contradict what TAI computed or read. A value MMI
	// does not return is "unavailable": recorded, and only a pinned run requires it.
	if receipt.Binding.SourceDigest == "mismatch" || receipt.Binding.Rows.Status == "incomplete" || receipt.Binding.FingerprintCrossCheck == "mismatch" {
		t.Fatalf("MMI values contradict TAI's: %+v", receipt.Binding)
	}
	if receipt.Binding.SourceDigest == "match" && receipt.Binding.MMISourceDigest != receipt.SourceDigestBefore {
		t.Fatalf("inspect sourceDigest is not the TAI-computed CSV digest: %+v", receipt.Binding)
	}
	if receipt.WorkspaceTree.DigestBefore == "" || receipt.WorkspaceTree.DigestBefore != receipt.WorkspaceTree.DigestAfter {
		t.Fatalf("workspace tree changed: %+v", receipt.WorkspaceTree)
	}
	t.Logf("pin=%s binding=%s/%s/%s rejection kinds=%+v tools=%v write-capable=%v", receipt.Pin.Result,
		receipt.Binding.SourceDigest, receipt.Binding.FingerprintCrossCheck, receipt.Binding.Rows.Status,
		receipt.RejectionKind, receipt.ToolSurface.Tools, receipt.ToolSurface.WriteCapable)
	if options.specified() {
		if receipt.Binding.SourceDigest != "match" || receipt.Binding.FingerprintCrossCheck != "match" || receipt.Binding.Rows.Status != "complete" {
			t.Fatalf("a pinned run must bind MMI's values to TAI's: %+v", receipt.Binding)
		}
		if receipt.ToolSurface.Status != "listed" || len(receipt.ToolSurface.WriteCapable) != 0 || len(receipt.ToolSurface.Unmeasured) != 0 {
			t.Fatalf("tool surface: %+v", receipt.ToolSurface)
		}
		if !receipt.Pin.Checked || receipt.Pin.Result != "match" || receipt.Pin.Commit.Status != "match" || receipt.Pin.SourceTree.Status != "clean" {
			t.Fatalf("expectations were given but the pin did not match: %+v", receipt.Pin)
		}
		if receipt.RejectionKind.Boundary != "outside-workspace" || receipt.RejectionKind.Missing != "not-found" {
			t.Fatalf("rejection reason kinds: %+v", receipt.RejectionKind)
		}
	} else if receipt.Pin.Checked || receipt.Pin.Result != "not-checked" {
		t.Fatalf("no expectation was given, yet the pin claims to be checked: %+v", receipt.Pin)
	}
}
