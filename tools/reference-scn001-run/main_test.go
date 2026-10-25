package main

import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
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
	if os.Getenv("MMI_ROOT") == "" {
		if info, err := os.Stat(filepath.Join(root, "..", "markdown-matrix-injector")); err != nil || !info.IsDir() {
			t.Skip("sibling checkout is not available: markdown-matrix-injector")
		}
	}
	if os.Getenv("SEI_ROOT") == "" {
		if info, err := os.Stat(filepath.Join(root, "..", "sei-cognition")); err != nil || !info.IsDir() {
			t.Skip("sibling checkout is not available: sei-cognition")
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
	if receipt.HumanReviewed || receipt.AuthorityVerified || receipt.Published || receipt.PublicationApproved {
		t.Fatalf("combined run overclaims authority: %+v", receipt)
	}
	if !receipt.ProvisionalApproved || !receipt.ReviewRequired || receipt.ReviewTrigger != "real-object" {
		t.Fatalf("provisional approval is missing: %+v", receipt)
	}
	if !receipt.Components.MMI.ConflictPreserved || !receipt.Components.SEI.ReadOnlyProjection ||
		receipt.Components.SCN001.ObservationSource != "mmi-reference" {
		t.Fatalf("component linkage is incomplete: %+v", receipt)
	}
	if !receipt.Components.ReviewArtifact.Passed || receipt.Components.ReviewArtifact.Status != "provisional" ||
		receipt.Components.ReviewArtifact.DraftID != "D-04" || receipt.Components.ReviewArtifact.ArtifactDigest == "" ||
		receipt.Components.ReviewArtifact.PublicationApproved || !receipt.Components.ReviewArtifact.ReviewRequired {
		t.Fatalf("review artifact linkage is incomplete: %+v", receipt.Components.ReviewArtifact)
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
		packet.AuthorityVerified || packet.PublicationApproved || !packet.ProvisionalApproved ||
		packet.ReviewTrigger != "real-object" || len(packet.Questions) != 4 ||
		packet.ReviewArtifactDigest == "" || packet.ReviewArtifactStatus != "provisional" {
		t.Fatalf("owner packet overclaims or is incomplete: %+v", packet)
	}
	if _, err := BuildOwnerPacket(incompleteSCN); err == nil {
		t.Fatal("owner packet was built from an unverifiable run")
	}
}

func TestRecordedRunVerifies(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "evaluations", "records", "SCN-001-run-2026-10-26.json"))
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

func recordedRunForMutation(t *testing.T) RunReceipt {
	t.Helper()
	raw, err := os.ReadFile(filepath.Join("..", "..", "evaluations", "records", "SCN-001-run-2026-10-26.json"))
	if err != nil {
		t.Fatal(err)
	}
	var receipt RunReceipt
	if err := json.Unmarshal(raw, &receipt); err != nil {
		t.Fatal(err)
	}
	return receipt
}

func TestVerifyRejectsFailedCaseEvenWithRecomputedDigest(t *testing.T) {
	receipt := recordedRunForMutation(t)
	receipt.Components.SCN001.Cases[0].Status = "fail"
	digest, err := digestJSON(receipt.Components)
	if err != nil {
		t.Fatal(err)
	}
	receipt.RunDigest = digest
	if result := Verify(receipt); result.Passed {
		t.Fatalf("case failure was accepted after rehashing: %+v", result)
	}
}

func TestVerifyRejectsDuplicateCaseEvenWithRecomputedDigest(t *testing.T) {
	receipt := recordedRunForMutation(t)
	receipt.Components.SCN001.Cases[1].ID = receipt.Components.SCN001.Cases[0].ID
	digest, err := digestJSON(receipt.Components)
	if err != nil {
		t.Fatal(err)
	}
	receipt.RunDigest = digest
	if result := Verify(receipt); result.Passed {
		t.Fatalf("duplicate case was accepted after rehashing: %+v", result)
	}
}

func TestVerifyRejectsAggregateVerdictMismatch(t *testing.T) {
	receipt := recordedRunForMutation(t)
	receipt.Passed = false // components still all report success
	if result := Verify(receipt); result.Passed {
		t.Fatalf("aggregate outcome contradicted components: %+v", result)
	}
}

func TestMMIResolvedObservationIsAlsoRenderedInD04(t *testing.T) {
	// No real MMI/SEI checkout is required: this checks the two Go tool entrypoints.
	work := t.TempDir()
	mmiPath := filepath.Join(work, "mmi.json")
	resolvedPath := filepath.Join(work, "resolved.json")
	scnReceiptPath := filepath.Join(work, "scn.json")
	d04Path := filepath.Join(work, "d04.md")
	modified := "施設予約は原則不要（TAIの改訂試験）"
	mmi := map[string]any{
		"schema":               "tai.reference.mmi-readonly/v0",
		"realProductConnected": true,
		"readOnly":             true,
		"conflictPreserved":    true,
		"selected": []map[string]string{
			{"id": "O-02", "text": modified, "source": "mmi-test", "version": "test-v0", "availability": "available"},
			{"id": "O-03", "text": "会議室の利用には事前予約が必要", "source": "mmi-test", "version": "test-v1", "availability": "available"},
			{"id": "O-07", "text": modified, "source": "mmi-test", "version": "test-v2", "availability": "available"},
		},
	}
	data, err := json.Marshal(mmi)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(mmiPath, data, 0o600); err != nil {
		t.Fatal(err)
	}

	scn := exec.Command("go", "run", ".", "-fixture", "testdata/scn001.json",
		"-mmi-receipt", mmiPath, "-out-fixture", resolvedPath, "-out", scnReceiptPath)
	scn.Dir = filepath.Join("..", "reference-scn001")
	if output, err := scn.CombinedOutput(); err != nil {
		t.Fatalf("SCN evaluation rejected the mutated synthetic receipt: %v: %s", err, output)
	}

	render := exec.Command("go", "run", ".", "-fixture", resolvedPath, "-out", d04Path)
	render.Dir = filepath.Join("..", "reference-scn001-render")
	renderOutput, err := render.CombinedOutput()
	if err != nil {
		t.Fatalf("D-04 renderer rejected the resolved fixture: %v: %s", err, renderOutput)
	}
	markdown, err := os.ReadFile(d04Path)
	if err != nil {
		t.Fatal(err)
	}
	var artifactReceipt struct {
		ArtifactDigest string `json:"artifactDigest"`
	}
	if err := json.Unmarshal(renderOutput, &artifactReceipt); err != nil {
		t.Fatalf("renderer did not return JSON receipt: %v: %s", err, renderOutput)
	}
	artifactHash := fmt.Sprintf("sha256:%x", sha256.Sum256(markdown))
	if artifactReceipt.ArtifactDigest != artifactHash {
		t.Fatalf("rendered artifact byte mismatch: declared=%s actual=%s", artifactReceipt.ArtifactDigest, artifactHash)
	}
	digest := fmt.Sprintf("sha256:%x", sha256.Sum256([]byte(modified)))
	if !strings.Contains(string(markdown), "| O-02 | "+modified+" | mmi-test | test-v0 |") ||
		!strings.Contains(string(markdown), digest) ||
		strings.Contains(string(markdown), "| O-02 | 施設の利用は予約不要 |") {
		t.Fatalf("D-04 does not use the same MMI-resolved observation as SCN: %s", markdown)
	}
	raw, err := os.ReadFile(scnReceiptPath)
	if err != nil {
		t.Fatal(err)
	}
	var scnResult struct {
		Passed             bool              `json:"passed"`
		ObservationDigests map[string]string `json:"observationDigests"`
	}
	if err := json.Unmarshal(raw, &scnResult); err != nil {
		t.Fatal(err)
	}
	if !scnResult.Passed || scnResult.ObservationDigests["O-02"] != digest {
		t.Fatalf("SCN and D-04 observation digests disagree: %+v", scnResult)
	}
}
