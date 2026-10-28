package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func load(t *testing.T) (SUILink, []byte) {
	t.Helper()
	raw, err := os.ReadFile(filepath.Join("..", "..", "evaluations", "records", "SUI-SCN-link-2026-10-26.json"))
	if err != nil {
		t.Fatal(err)
	}
	var link SUILink
	if err := json.Unmarshal(raw, &link); err != nil {
		t.Fatal(err)
	}
	artifact, err := os.ReadFile(filepath.Join("..", "..", "evaluations", "artifacts", "SCN-001-D-04-provisional.md"))
	if err != nil {
		t.Fatal(err)
	}
	return link, artifact
}

func TestLinkMatchesDraft(t *testing.T) {
	link, artifact := load(t)
	receipt := Link(link, artifact)
	if !receipt.Passed || !receipt.PublicationBlocked || len(receipt.LinkedCards) != 5 {
		t.Fatalf("link failed: %+v", receipt)
	}
	if !strings.HasPrefix(receipt.ArtifactDigest, "sha256:") {
		t.Fatalf("artifact digest is missing: %+v", receipt)
	}
}

func TestLinkRejectsAvailableO08(t *testing.T) {
	link, artifact := load(t)
	lines := strings.Split(string(artifact), "\n")
	for index, line := range lines {
		if strings.HasPrefix(line, "| O-08 |") {
			lines[index] = strings.ReplaceAll(line, "| unavailable |", "| available |")
		}
	}
	if receipt := Link(link, []byte(strings.Join(lines, "\n"))); receipt.Passed {
		t.Fatalf("available O-08 was accepted: %+v", receipt)
	}
}

func TestLinkRejectsMissingBoundary(t *testing.T) {
	link, artifact := load(t)
	broken := strings.Replace(string(artifact), "- 公開承認: **なし**", "- 公開承認: **あり**", 1)
	if receipt := Link(link, []byte(broken)); receipt.Passed {
		t.Fatalf("changed boundary was accepted: %+v", receipt)
	}
}
