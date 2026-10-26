package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func acceptedStatus() Status {
	items := []Item{}
	for _, id := range required {
		items = append(items, Item{ID: id, Status: "accepted", Evidence: "evidence/" + id, EvidenceKind: "real-object"})
	}
	for _, id := range optional {
		items = append(items, Item{ID: id, Status: "not-applicable"})
	}
	return Status{Schema: "tai.reference.scn001-review-status/v0", Scenario: "SCN-001", Items: items}
}

func TestPendingStatusIsBlocked(t *testing.T) {
	status := acceptedStatus()
	for index := range status.Items {
		if status.Items[index].ID == "R-01" {
			status.Items[index].Status = "pending"
		}
	}
	receipt := Evaluate(status)
	if receipt.Allowed || len(receipt.Blockers) == 0 {
		t.Fatalf("pending review was allowed: %+v", receipt)
	}
}

func TestAcceptedStatusIsAllowed(t *testing.T) {
	receipt := Evaluate(acceptedStatus())
	if !receipt.Allowed || len(receipt.Blockers) != 0 || len(receipt.Accepted) != len(required)+len(optional) {
		t.Fatalf("accepted review was blocked: %+v", receipt)
	}
}

func TestMissingEvidenceIsBlocked(t *testing.T) {
	status := acceptedStatus()
	status.Items[0].Evidence = ""
	receipt := Evaluate(status)
	if receipt.Allowed {
		t.Fatalf("missing evidence was allowed: %+v", receipt)
	}
}

func TestSyntheticEvidenceIsBlocked(t *testing.T) {
	status := acceptedStatus()
	status.Items[0].EvidenceKind = "synthetic"
	receipt := Evaluate(status)
	if receipt.Allowed {
		t.Fatalf("synthetic evidence was allowed: %+v", receipt)
	}
}

func TestOptionalNotApplicableIsAllowed(t *testing.T) {
	status := acceptedStatus()
	for index := range status.Items {
		if status.Items[index].ID == "R-07" {
			status.Items[index].Status = "not-applicable"
		}
	}
	if receipt := Evaluate(status); !receipt.Allowed {
		t.Fatalf("not-applicable optional review was blocked: %+v", receipt)
	}
}

func TestRepositoryStatusIsBlocked(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "evaluations", "SCN-001-review-status.json"))
	if err != nil {
		t.Fatal(err)
	}
	var status Status
	if err := json.Unmarshal(raw, &status); err != nil {
		t.Fatal(err)
	}
	receipt := Evaluate(status)
	if receipt.Allowed {
		t.Fatal("repository review status was allowed without real-object evidence")
	}
	for _, id := range required {
		found := false
		for _, blocker := range receipt.Blockers {
			if strings.HasPrefix(blocker, id+":") {
				found = true
			}
		}
		if !found {
			t.Fatalf("%s is not represented in the blockers: %+v", id, receipt)
		}
	}
}
