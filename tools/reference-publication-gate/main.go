package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strings"
)

type Item struct {
	ID       string `json:"id"`
	Status   string `json:"status"`
	Evidence string `json:"evidence"`
}

type Status struct {
	Schema   string `json:"schema"`
	Scenario string `json:"scenario"`
	Items    []Item `json:"items"`
}

type Receipt struct {
	Schema   string   `json:"schema"`
	Scenario string   `json:"scenario"`
	Allowed  bool     `json:"allowed"`
	Blockers []string `json:"blockers"`
	Accepted []string `json:"accepted"`
}

var required = []string{"R-01", "R-02", "R-03", "R-04", "R-05"}
var optional = []string{"R-06", "R-07"}

func Evaluate(status Status) Receipt {
	receipt := Receipt{
		Schema: "tai.reference.scn001-publication-gate/v0", Scenario: status.Scenario,
		Blockers: []string{}, Accepted: []string{},
	}
	byID := map[string]Item{}
	for _, item := range status.Items {
		byID[item.ID] = item
	}
	for _, id := range required {
		item, ok := byID[id]
		if !ok {
			receipt.Blockers = append(receipt.Blockers, id+": missing")
			continue
		}
		if item.Status != "accepted" {
			receipt.Blockers = append(receipt.Blockers, id+": status="+item.Status)
			continue
		}
		if strings.TrimSpace(item.Evidence) == "" {
			receipt.Blockers = append(receipt.Blockers, id+": evidence is empty")
			continue
		}
		receipt.Accepted = append(receipt.Accepted, id)
	}
	for _, id := range optional {
		item, ok := byID[id]
		if !ok {
			receipt.Blockers = append(receipt.Blockers, id+": missing")
			continue
		}
		if item.Status != "accepted" && item.Status != "not-applicable" {
			receipt.Blockers = append(receipt.Blockers, id+": status="+item.Status)
			continue
		}
		if item.Status == "accepted" && strings.TrimSpace(item.Evidence) == "" {
			receipt.Blockers = append(receipt.Blockers, id+": evidence is empty")
			continue
		}
		receipt.Accepted = append(receipt.Accepted, id)
	}
	receipt.Allowed = len(receipt.Blockers) == 0
	return receipt
}

func main() {
	statusPath := flag.String("status", "", "SCN-001 review status JSON")
	outPath := flag.String("out", "", "write gate receipt JSON")
	flag.Parse()
	if *statusPath == "" {
		fmt.Fprintln(os.Stderr, "-status is required")
		os.Exit(2)
	}
	raw, err := os.ReadFile(*statusPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	var status Status
	if err := json.Unmarshal(raw, &status); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	if status.Schema != "tai.reference.scn001-review-status/v0" || status.Scenario != "SCN-001" {
		fmt.Fprintln(os.Stderr, "unexpected review status schema or scenario")
		os.Exit(2)
	}
	receipt := Evaluate(status)
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
	if !receipt.Allowed {
		os.Exit(1)
	}
}
