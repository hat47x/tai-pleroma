package main

import (
	"encoding/json"
	"os"
	"testing"
)

func loadFixture(t *testing.T) Fixture {
	t.Helper()
	raw, err := os.ReadFile("testdata/scn001.json")
	if err != nil {
		t.Fatal(err)
	}
	var fixture Fixture
	if err := json.Unmarshal(raw, &fixture); err != nil {
		t.Fatal(err)
	}
	return fixture
}

func caseStatus(receipt Receipt, id string) string {
	for _, result := range receipt.Cases {
		if result.ID == id {
			return result.Status
		}
	}
	return ""
}

func TestSyntheticWalkthroughPasses(t *testing.T) {
	receipt := Evaluate(loadFixture(t))
	if !receipt.Passed {
		t.Fatalf("synthetic walkthrough failed: %+v", receipt)
	}
	if !receipt.Synthetic || receipt.RealProductsConnected || receipt.HumanReviewed || receipt.AuthorityVerified {
		t.Fatalf("receipt overclaims scope: %+v", receipt)
	}
	for _, result := range receipt.Cases {
		switch result.ID {
		case "P-06", "N-05":
			if result.Status != "not-run" {
				t.Fatalf("%s should be not-run: %+v", result.ID, result)
			}
		default:
			if result.Status != "pass" {
				t.Fatalf("%s should pass: %+v", result.ID, result)
			}
		}
	}
}

func TestPublishedDraftFails(t *testing.T) {
	fixture := loadFixture(t)
	fixture.Drafts[0].Published = true
	receipt := Evaluate(fixture)
	if receipt.Passed || caseStatus(receipt, "P-03") != "fail" || caseStatus(receipt, "N-02") != "fail" {
		t.Fatalf("published draft was accepted: %+v", receipt)
	}
}

func TestAdoptedHypothesisFails(t *testing.T) {
	fixture := loadFixture(t)
	fixture.Hypotheses[0].Adopted = true
	receipt := Evaluate(fixture)
	if receipt.Passed || caseStatus(receipt, "P-02") != "fail" || caseStatus(receipt, "N-04") != "fail" {
		t.Fatalf("adopted hypothesis was accepted: %+v", receipt)
	}
}

func TestRevisionOverwriteFails(t *testing.T) {
	fixture := loadFixture(t)
	fixture.Revisions[2].Observations = []string{"O-01", "O-02", "O-03", "O-04", "O-05", "O-07", "O-08"}
	receipt := Evaluate(fixture)
	if receipt.Passed || caseStatus(receipt, "P-05") != "fail" {
		t.Fatalf("non-prefix revision was accepted: %+v", receipt)
	}
}

func TestProvisionalApprovalDoesNotPublish(t *testing.T) {
	fixture := loadFixture(t)
	for index := range fixture.Decisions {
		if fixture.Decisions[index].ID == "DEC-02" {
			fixture.Decisions[index].PublicationApproved = true
		}
	}
	receipt := Evaluate(fixture)
	if receipt.Passed || caseStatus(receipt, "P-04") != "fail" || caseStatus(receipt, "P-07") != "fail" || caseStatus(receipt, "N-07") != "fail" {
		t.Fatalf("provisional publication was accepted: %+v", receipt)
	}
}

func TestProvisionalApprovalRequiresReview(t *testing.T) {
	fixture := loadFixture(t)
	fixture.Provisional.ReviewRequired = false
	receipt := Evaluate(fixture)
	if receipt.Passed || caseStatus(receipt, "P-07") != "fail" {
		t.Fatalf("provisional approval without review was accepted: %+v", receipt)
	}
}

func TestUnavailableSourceIsNotAbsence(t *testing.T) {
	fixture := loadFixture(t)
	for index := range fixture.Observations {
		if fixture.Observations[index].ID == "O-08" {
			fixture.Observations[index].Availability = "available"
			fixture.Observations[index].Text = "予約規程は存在しない"
		}
	}
	receipt := Evaluate(fixture)
	if receipt.Passed || caseStatus(receipt, "N-03") != "fail" {
		t.Fatalf("absence claim was accepted: %+v", receipt)
	}
}

func TestFutureObservationCannotSupportEarlierDraft(t *testing.T) {
	fixture := loadFixture(t)
	fixture.Drafts[0].References = append(fixture.Drafts[0].References, "O-07")
	receipt := Evaluate(fixture)
	if receipt.Passed || caseStatus(receipt, "N-06") != "fail" {
		t.Fatalf("T0 draft accepted an observation first present in T2: %+v", receipt)
	}
}

func TestDuplicateObservationIDIsRejected(t *testing.T) {
	fixture := loadFixture(t)
	fixture.Observations = append(fixture.Observations, fixture.Observations[1])
	receipt := Evaluate(fixture)
	if receipt.Passed || caseStatus(receipt, "N-06") != "fail" {
		t.Fatalf("duplicate observation ID was accepted: %+v", receipt)
	}
}

func TestDuplicateDraftIDIsRejected(t *testing.T) {
	fixture := loadFixture(t)
	fixture.Drafts = append(fixture.Drafts, fixture.Drafts[1])
	receipt := Evaluate(fixture)
	if receipt.Passed || caseStatus(receipt, "N-06") != "fail" {
		t.Fatalf("duplicate draft ID was accepted: %+v", receipt)
	}
}

func TestDuplicateObservationWithinRevisionIsRejected(t *testing.T) {
	fixture := loadFixture(t)
	fixture.Revisions[3].Observations = append(fixture.Revisions[3].Observations, "O-02")
	receipt := Evaluate(fixture)
	if receipt.Passed || caseStatus(receipt, "N-06") != "fail" {
		t.Fatalf("repeated observation within revision was accepted: %+v", receipt)
	}
}

func TestDraftOnlyRevisionMayKeepTheSameObservationSet(t *testing.T) {
	fixture := loadFixture(t)
	// The existing T3/D-04 in the reference fixture uses the same observations as T2.
	receipt := Evaluate(fixture)
	if !receipt.Passed || caseStatus(receipt, "P-05") != "pass" || caseStatus(receipt, "N-06") != "pass" {
		t.Fatalf("draft-only revision should retain previously available evidence: %+v", receipt)
	}
}
