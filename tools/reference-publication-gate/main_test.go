package main

import "testing"

func acceptedStatus() Status {
	items := []Item{}
	for _, id := range required {
		items = append(items, Item{ID: id, Status: "accepted", Evidence: "evidence/" + id})
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
