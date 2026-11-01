package main

import "testing"

// setDecision finds a decision by ID and applies a mutation, so each
// transition test changes exactly one field of the shared synthetic fixture.
func setDecision(t *testing.T, fixture *Fixture, id string, mutate func(*Decision)) {
	t.Helper()
	for i := range fixture.Decisions {
		if fixture.Decisions[i].ID == id {
			mutate(&fixture.Decisions[i])
			return
		}
	}
	t.Fatalf("decision %s not found", id)
}

func requireFail(t *testing.T, receipt Receipt, ids ...string) {
	t.Helper()
	if receipt.Passed {
		t.Fatalf("receipt should not pass: %+v", receipt)
	}
	for _, id := range ids {
		if got := caseStatus(receipt, id); got != "fail" {
			t.Fatalf("%s should fail, got %q", id, got)
		}
	}
}

// A provisional approval whose draft link does not resolve must not be
// treated as a valid approval (P-07) or as publication (N-07).
func TestProvisionalDraftMissingFails(t *testing.T) {
	fixture := loadFixture(t)
	setDecision(t, &fixture, "DEC-02", func(d *Decision) { d.Draft = "D-99" })
	requireFail(t, Evaluate(fixture), "P-07", "N-07")
}

// A provisional approval that points to a different existing draft is also
// a mismatch, not a valid approval.
func TestProvisionalDraftMismatchFails(t *testing.T) {
	fixture := loadFixture(t)
	setDecision(t, &fixture, "DEC-02", func(d *Decision) { d.Draft = "D-03" })
	requireFail(t, Evaluate(fixture), "P-07", "N-07")
}

// A superseded acceptance must not come back when the decision is marked
// accepted again, even though the later observation has the same text.
func TestRevivedSupersededDecisionFails(t *testing.T) {
	fixture := loadFixture(t)
	setDecision(t, &fixture, "DEC-03", func(d *Decision) { d.Status = "accepted" })
	requireFail(t, Evaluate(fixture), "P-04", "N-01", "N-08")
}

// A pending decision whose subject does not resolve must be detected as a
// broken basis, not silently accepted.
func TestCurrentDecisionSubjectMissingFails(t *testing.T) {
	fixture := loadFixture(t)
	setDecision(t, &fixture, "DEC-04", func(d *Decision) { d.Subject = "O-99" })
	requireFail(t, Evaluate(fixture), "N-08")
}

// A superseded decision whose subject points to a different existing
// observation is a mismatch, not a valid basis.
func TestSupersededDecisionSubjectMismatchFails(t *testing.T) {
	fixture := loadFixture(t)
	setDecision(t, &fixture, "DEC-03", func(d *Decision) { d.Subject = "O-03" })
	requireFail(t, Evaluate(fixture), "N-08")
}
