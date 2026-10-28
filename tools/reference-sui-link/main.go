package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"sort"
)

type Observation struct {
	ID   string `json:"id"`
	Text string `json:"text"`
}

type Fixture struct {
	Observations []Observation `json:"observations"`
}

type Card struct {
	ID         string `json:"id"`
	ClaimType  string `json:"claimType"`
	TextDigest string `json:"textDigest"`
}

type Island struct {
	ID      string   `json:"id"`
	CardIDs []string `json:"cardIds"`
}

type Edge struct {
	ID     string `json:"id"`
	FromID string `json:"fromId"`
	ToID   string `json:"toId"`
	Type   string `json:"type"`
}

type SUIReceipt struct {
	Passed               bool     `json:"passed"`
	ReadOnly             bool     `json:"readOnly"`
	RealProductConnected bool     `json:"realProductConnected"`
	DocumentRead         bool     `json:"documentRead"`
	DocumentID           string   `json:"documentId"`
	DocumentDigest       string   `json:"documentDigest"`
	DocumentCards        []Card   `json:"documentCards"`
	DocumentIslands      []Island `json:"documentIslands"`
	DocumentEdgeCount    int      `json:"documentEdgeCount"`
	DocumentEdges        []Edge   `json:"documentEdges"`
}

type Receipt struct {
	Schema         string   `json:"schema"`
	DocumentID     string   `json:"documentId"`
	DocumentDigest string   `json:"documentDigest"`
	LinkedCards    []string `json:"linkedCards"`
	IslandGroups   []string `json:"islandGroups"`
	EdgeCount      int      `json:"edgeCount"`
	Contradiction  bool     `json:"contradiction"`
	Passed         bool     `json:"passed"`
	Reason         string   `json:"reason,omitempty"`
	Notes          []string `json:"notes"`
}

func digest(text string) string {
	sum := sha256.Sum256([]byte(text))
	return "sha256:" + hex.EncodeToString(sum[:])
}

func Link(fixture Fixture, sui SUIReceipt) Receipt {
	receipt := Receipt{
		Schema: "tai.reference.sui-scn-link/v0", DocumentID: sui.DocumentID,
		DocumentDigest: sui.DocumentDigest, EdgeCount: sui.DocumentEdgeCount,
		Notes: []string{
			"SUIのcard digestをSCN-001 fixtureの観測と照合する参照。",
			"SUIの実資料・認可・意味形成の正しさは検証しない。",
		},
	}
	if !sui.Passed || !sui.ReadOnly || !sui.RealProductConnected || !sui.DocumentRead {
		receipt.Reason = "SUI receipt is not a read-only document read"
		return receipt
	}
	byID := map[string]Observation{}
	for _, observation := range fixture.Observations {
		byID[observation.ID] = observation
	}
	cards := map[string]Card{}
	for _, card := range sui.DocumentCards {
		cards[card.ID] = card
	}
	for _, id := range []string{"O-02", "O-03", "O-06", "O-07", "O-08"} {
		card, ok := cards[id]
		observation, exists := byID[id]
		if !ok || !exists {
			receipt.Reason = "required card is missing: " + id
			return receipt
		}
		if card.TextDigest != digest(observation.Text) {
			receipt.Reason = "card digest does not match the SCN observation: " + id
			return receipt
		}
		receipt.LinkedCards = append(receipt.LinkedCards, id)
	}
	islands := map[string]Island{}
	for _, island := range sui.DocumentIslands {
		islands[island.ID] = island
	}
	for _, expected := range []struct {
		ID    string
		Cards []string
	}{
		{ID: "I-01", Cards: []string{"O-02", "O-07"}},
		{ID: "I-02", Cards: []string{"O-03", "O-06"}},
		{ID: "I-03", Cards: []string{"O-08"}},
	} {
		island, ok := islands[expected.ID]
		if !ok {
			receipt.Reason = "required island is missing: " + expected.ID
			return receipt
		}
		got := append([]string(nil), island.CardIDs...)
		want := append([]string(nil), expected.Cards...)
		sort.Strings(got)
		sort.Strings(want)
		if fmt.Sprint(got) != fmt.Sprint(want) {
			receipt.Reason = "island cards do not match: " + expected.ID
			return receipt
		}
		receipt.IslandGroups = append(receipt.IslandGroups, expected.ID)
	}
	if sui.DocumentEdgeCount != len(sui.DocumentEdges) {
		receipt.Reason = "documentEdgeCount does not match documentEdges"
		return receipt
	}
	if len(sui.DocumentEdges) != 1 || sui.DocumentEdges[0].Type != "contradicts" ||
		sui.DocumentEdges[0].FromID != "I-01" || sui.DocumentEdges[0].ToID != "I-02" {
		receipt.Reason = "contradicts edge between I-01 and I-02 is missing"
		return receipt
	}
	receipt.Contradiction = true
	receipt.Passed = true
	return receipt
}

func main() {
	fixturePath := flag.String("fixture", "", "SCN-001 fixture")
	suiPath := flag.String("sui-receipt", "", "SUI API probe receipt")
	outPath := flag.String("out", "", "write link receipt")
	flag.Parse()
	if *fixturePath == "" || *suiPath == "" {
		fmt.Fprintln(os.Stderr, "-fixture and -sui-receipt are required")
		os.Exit(2)
	}
	var fixture Fixture
	raw, err := os.ReadFile(*fixturePath)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	if err := json.Unmarshal(raw, &fixture); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	var sui SUIReceipt
	raw, err = os.ReadFile(*suiPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	if err := json.Unmarshal(raw, &sui); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	receipt := Link(fixture, sui)
	encoded, err := json.MarshalIndent(receipt, "", "  ")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	encoded = append(encoded, '\n')
	if *outPath != "" {
		if err := os.WriteFile(*outPath, encoded, 0o644); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
	}
	os.Stdout.Write(encoded)
	if !receipt.Passed {
		os.Exit(1)
	}
}
