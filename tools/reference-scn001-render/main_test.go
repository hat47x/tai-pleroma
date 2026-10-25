package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func loadFixture(t *testing.T) Fixture {
	t.Helper()
	path := filepath.Join("..", "reference-scn001", "testdata", "scn001.json")
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	var fixture Fixture
	if err := json.Unmarshal(raw, &fixture); err != nil {
		t.Fatal(err)
	}
	return fixture
}

func TestRenderProvisionalReviewArtifact(t *testing.T) {
	content, receipt, err := Render(loadFixture(t))
	if err != nil {
		t.Fatal(err)
	}
	if !receipt.Passed || receipt.Status != "provisional" || receipt.DraftID != "D-04" ||
		!receipt.ProvisionalApproved || receipt.PublicationApproved ||
		!receipt.ReviewRequired || receipt.ReviewTrigger != "real-object" || receipt.AuthorityVerified {
		t.Fatalf("review artifact receipt overclaims: %+v", receipt)
	}
	if receipt.ArtifactDigest == "" || !strings.HasPrefix(receipt.ArtifactDigest, "sha256:") {
		t.Fatalf("artifact digest is missing: %+v", receipt)
	}
	for _, expected := range []string{"# SCN-001 D-04 暫定案内", "公開承認: **なし**", "review:real-object", "| O-02 |", "| O-03 |"} {
		if !strings.Contains(content, expected) {
			t.Fatalf("review artifact is missing %q:\n%s", expected, content)
		}
	}
}

func TestRenderRejectsPublishedProvisional(t *testing.T) {
	fixture := loadFixture(t)
	fixture.Provisional.PublicationApproved = true
	if _, _, err := Render(fixture); err == nil {
		t.Fatal("published provisional approval was accepted")
	}
}
