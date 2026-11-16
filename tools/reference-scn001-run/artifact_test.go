package main

import (
	"crypto/sha256"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestRecordedArtifactBytesVerify(t *testing.T) {
	receipt := recordedRunForMutation(t)
	result := VerifyArtifact(receipt, filepath.Join("..", "..", "evaluations", "artifacts", "SCN-001-D-04-provisional.md"))
	if !result.Passed || !result.ArtifactBytesVerified {
		t.Fatalf("stored artifact: %+v", result)
	}
	if Verify(receipt).ArtifactBytesVerified {
		t.Fatal("JSON-only verification claimed artifact bytes")
	}
}

func TestArtifactRecheckDetectsReplacementAndReadFailure(t *testing.T) {
	receipt := recordedRunForMutation(t)
	original := []byte("# Review only\n\n日本語の観測\n")
	receipt.Components.ReviewArtifact.ArtifactDigest = fmt.Sprintf("sha256:%x", sha256.Sum256(original))
	var err error
	receipt.RunDigest, err = digestJSON(receipt.Components)
	if err != nil {
		t.Fatal(err)
	}
	path := filepath.Join(t.TempDir(), "review.md")
	for name, content := range map[string][]byte{
		"matching bytes":     original,
		"changed text":       []byte("# Different review\n"),
		"empty":              {},
		"converted newlines": []byte(strings.ReplaceAll(string(original), "\n", "\r\n")),
	} {
		t.Run(name, func(t *testing.T) {
			if err := os.WriteFile(path, content, 0600); err != nil {
				t.Fatal(err)
			}
			result := VerifyArtifact(receipt, path)
			want := name == "matching bytes"
			if result.Passed != want || result.ArtifactBytesVerified != want {
				t.Fatalf("result=%+v want matched=%v", result, want)
			}
			// A matching file cannot repair a mismatched receipt digest.
			tampered := receipt
			tampered.Components.MMI.SelectedRows++
			if result := VerifyArtifact(tampered, path); result.Passed || result.ArtifactBytesVerified {
				t.Fatalf("bad receipt accepted: %+v", result)
			}
		})
	}
	for _, missing := range []string{filepath.Join(t.TempDir(), "missing.md"), t.TempDir()} {
		if result := VerifyArtifact(receipt, missing); result.Passed || result.ArtifactBytesVerified || result.Reason == "" {
			t.Fatalf("unreadable artifact accepted: %+v", result)
		}
	}
	// A self-consistent failed run must not become artifact evidence merely by
	// pointing it at matching bytes.
	receipt.Components.ReviewArtifact.Passed = false
	receipt.Passed = false
	receipt.RunDigest, err = digestJSON(receipt.Components)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, original, 0600); err != nil {
		t.Fatal(err)
	}
	if result := VerifyArtifact(receipt, path); result.Passed || result.ArtifactBytesVerified {
		t.Fatalf("failed artifact generation accepted: %+v", result)
	}
}
