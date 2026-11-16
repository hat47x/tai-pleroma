package main

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func reviewBytes(t *testing.T) []byte {
	t.Helper()
	raw, err := os.ReadFile(filepath.Join("..", "..", "evaluations", "artifacts", "SCN-001-D-04-provisional.md"))
	if err != nil {
		t.Fatal(err)
	}
	return raw
}

func TestPacketDoesNotInventFrozenRunOrArtifactLinks(t *testing.T) {
	packet, err := BuildOwnerPacket(recordedRunForMutation(t))
	if err != nil {
		t.Fatal(err)
	}
	for _, path := range packet.Evidence {
		if strings.HasPrefix(path, "evaluations/artifacts/") || strings.HasPrefix(path, "evaluations/records/") {
			t.Fatal("metadata-only packet points to unrelated frozen evidence")
		}
	}
	if packet.ArtifactBytesVerified {
		t.Fatal("metadata-only packet claimed file verification")
	}
}

func TestSavedArtifactIsTheOneHandedToReview(t *testing.T) {
	receipt := recordedRunForMutation(t)
	raw := reviewBytes(t)
	path := filepath.Join(t.TempDir(), "this-run.md")
	if err := saveReviewArtifact(receipt, raw, path); err != nil {
		t.Fatal(err)
	}
	packet, err := BuildOwnerPacketWithArtifact(receipt, path)
	if err != nil {
		t.Fatal(err)
	}
	absolute, err := filepath.Abs(path)
	if err != nil {
		t.Fatal(err)
	}
	found := false
	for _, entry := range packet.Evidence {
		if entry == absolute {
			found = true
		}
	}
	if !found || !packet.ArtifactBytesVerified || packet.ReviewArtifactDigest != artifactDigest(raw) {
		t.Fatal("packet is not bound to the selected artifact")
	}
	if packet.Approved || packet.HumanReviewed || packet.AuthorityVerified || packet.PublicationApproved || packet.PublicationAllowed {
		t.Fatal("artifact byte verification granted approval")
	}
	if err := os.WriteFile(path, []byte("replacement"), 0600); err != nil {
		t.Fatal(err)
	}
	if _, err := BuildOwnerPacketWithArtifact(receipt, path); err == nil {
		t.Fatal("replaced artifact reached owner packet")
	}
	if _, err := BuildOwnerPacketWithArtifact(receipt, filepath.Join(t.TempDir(), "missing.md")); err == nil {
		t.Fatal("missing artifact reached owner packet")
	}
}

func TestReviewFilesNeverReplaceSourcesOrEarlierOutputs(t *testing.T) {
	receipt := recordedRunForMutation(t)
	raw := reviewBytes(t)
	path := filepath.Join(t.TempDir(), "existing.md")
	if err := os.WriteFile(path, raw, 0600); err != nil {
		t.Fatal(err)
	}
	if err := saveReviewArtifact(receipt, raw, path); err == nil {
		t.Fatal("artifact output replaced an existing file")
	}
	if err := writeNewReviewFile(path, []byte("packet")); err == nil {
		t.Fatal("packet output replaced an existing file")
	}
	after, err := os.ReadFile(path)
	if err != nil || string(after) != string(raw) {
		t.Fatal("original file changed")
	}
	if err := requireNewReviewPath(path); err == nil {
		t.Fatal("preflight accepted an existing file")
	}
	fresh := filepath.Join(t.TempDir(), "fresh.md")
	if err := saveReviewArtifact(receipt, []byte("wrong run"), fresh); err == nil {
		t.Fatal("mismatched bytes saved")
	}
	if _, err := os.Stat(fresh); !os.IsNotExist(err) {
		t.Fatal("mismatch created a misleading artifact")
	}
	if err := saveReviewArtifact(consistentFailedRun(t), raw, fresh); err == nil {
		t.Fatal("failed run saved a review artifact")
	}
}

func TestRunArtifactSurvivesForIndependentReview(t *testing.T) {
	root := taiRootForTest(t)
	artifact := filepath.Join(t.TempDir(), "review.md")
	receipt, err := runWithArtifactOutput(context.Background(), root, artifact)
	if err != nil {
		t.Fatal(err)
	}
	// The temporary run workspace has already been removed here.
	if result := VerifyArtifact(receipt, artifact); !result.Passed || !result.ArtifactBytesVerified {
		t.Fatalf("saved file cannot be re-observed: %+v", result)
	}
	packet, err := BuildOwnerPacketWithArtifact(receipt, artifact)
	if err != nil {
		t.Fatal(err)
	}
	if !packet.ArtifactBytesVerified || packet.RunDigest != receipt.RunDigest || packet.Approved || packet.PublicationApproved {
		t.Fatal("handoff lost identity or overclaimed approval")
	}
}
