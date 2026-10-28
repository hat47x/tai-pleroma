package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

func load(t *testing.T) (Fixture, SUIReceipt) {
	t.Helper()
	raw, err := os.ReadFile(filepath.Join("..", "reference-scn001", "testdata", "scn001.json"))
	if err != nil {
		t.Fatal(err)
	}
	var fixture Fixture
	if err := json.Unmarshal(raw, &fixture); err != nil {
		t.Fatal(err)
	}
	raw, err = os.ReadFile(filepath.Join("..", "..", "evaluations", "records", "SUI-api-2026-10-26.json"))
	if err != nil {
		t.Fatal(err)
	}
	var sui SUIReceipt
	if err := json.Unmarshal(raw, &sui); err != nil {
		t.Fatal(err)
	}
	return fixture, sui
}

func TestLinkMatchesObservationsAndIslands(t *testing.T) {
	fixture, sui := load(t)
	receipt := Link(fixture, sui)
	if !receipt.Passed || !receipt.Contradiction || len(receipt.LinkedCards) != 5 || len(receipt.IslandGroups) != 3 || receipt.EdgeCount != 1 {
		t.Fatalf("link did not match: %+v", receipt)
	}
}

func TestLinkRejectsChangedCardDigest(t *testing.T) {
	fixture, sui := load(t)
	sui.DocumentCards[0].TextDigest = "sha256:changed"
	if receipt := Link(fixture, sui); receipt.Passed {
		t.Fatalf("changed card digest was accepted: %+v", receipt)
	}
}

func TestLinkRejectsEdgeCountMismatch(t *testing.T) {
	fixture, sui := load(t)
	sui.DocumentEdgeCount = 2
	if receipt := Link(fixture, sui); receipt.Passed {
		t.Fatalf("edge count mismatch was accepted: %+v", receipt)
	}
}

func TestLinkRejectsMissingIsland(t *testing.T) {
	fixture, sui := load(t)
	sui.DocumentIslands = sui.DocumentIslands[:1]
	if receipt := Link(fixture, sui); receipt.Passed {
		t.Fatalf("missing island was accepted: %+v", receipt)
	}
}
