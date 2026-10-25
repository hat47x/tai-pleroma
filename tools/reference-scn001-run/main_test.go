package main

import (
	"context"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"testing"
)

func taiRootForTest(t *testing.T) string {
	t.Helper()
	if _, err := exec.LookPath("go"); err != nil {
		t.Skip("go is not available")
	}
	if _, err := exec.LookPath("node"); err != nil {
		t.Skip("node is not available")
	}
	root := filepath.Clean(filepath.Join("..", ".."))
	for _, dir := range []string{
		filepath.Join(root, "tools", "reference-mmi-readonly"),
		filepath.Join(root, "tools", "reference-sei-decision"),
		filepath.Join(root, "tools", "reference-scn001"),
	} {
		if info, err := os.Stat(dir); err != nil || !info.IsDir() {
			t.Skip("component tool is not available: " + dir)
		}
	}
	return root
}

func TestCombinedRun(t *testing.T) {
	receipt, err := Run(context.Background(), taiRootForTest(t))
	if err != nil {
		t.Fatal(err)
	}
	if !receipt.Passed || !receipt.RealProductsConnected {
		t.Fatalf("combined run failed: %+v", receipt)
	}
	if receipt.HumanReviewed || receipt.AuthorityVerified || receipt.Published {
		t.Fatalf("combined run overclaims authority: %+v", receipt)
	}
	if !receipt.Components.MMI.ConflictPreserved || !receipt.Components.SEI.ReadOnlyProjection ||
		receipt.Components.SCN001.ObservationSource != "mmi-reference" {
		t.Fatalf("component linkage is incomplete: %+v", receipt)
	}
	if receipt.RunDigest == "" {
		t.Fatalf("run digest is missing: %+v", receipt)
	}
	if verification := Verify(receipt); !verification.Passed {
		t.Fatalf("generated run did not verify: %+v", verification)
	}

	tampered := receipt
	tampered.Components.MMI.SelectedRows = 99
	if verification := Verify(tampered); verification.Passed {
		t.Fatalf("tampered run verified: %+v", verification)
	}

	overclaim := receipt
	overclaim.HumanReviewed = true
	if verification := Verify(overclaim); verification.Passed {
		t.Fatalf("overclaimed run verified: %+v", verification)
	}

	incompleteSEI := receipt
	incompleteSEI.Components.SEI.Decision.ID = "other"
	if verification := Verify(incompleteSEI); verification.Passed {
		t.Fatalf("incomplete SEI component verified: %+v", verification)
	}

	incompleteSCN := receipt
	incompleteSCN.Components.SCN001.ObservationSource = "fixture"
	if verification := Verify(incompleteSCN); verification.Passed {
		t.Fatalf("incomplete SCN-001 component verified: %+v", verification)
	}

	packet, err := BuildOwnerPacket(receipt)
	if err != nil {
		t.Fatal(err)
	}
	if packet.Status != "awaiting-owner" || packet.Approved || packet.HumanReviewed ||
		packet.AuthorityVerified || packet.PublicationApproved || len(packet.Questions) != 4 {
		t.Fatalf("owner packet overclaims or is incomplete: %+v", packet)
	}
	if _, err := BuildOwnerPacket(incompleteSCN); err == nil {
		t.Fatal("owner packet was built from an unverifiable run")
	}
}

func TestRecordedRunVerifies(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "evaluations", "records", "SCN-001-run-2026-10-25.json"))
	if err != nil {
		t.Fatal(err)
	}
	var receipt RunReceipt
	if err := json.Unmarshal(raw, &receipt); err != nil {
		t.Fatal(err)
	}
	if verification := Verify(receipt); !verification.Passed {
		t.Fatalf("recorded run does not verify: %+v", verification)
	}
	if packet, err := BuildOwnerPacket(receipt); err != nil || packet.Status != "awaiting-owner" {
		t.Fatalf("recorded run cannot produce an owner packet: %+v %v", packet, err)
	}
}
