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

func TestFutureEvidenceInEarlierDraftFails(t *testing.T) {
	fixture := loadFixture(t)
	fixture.Drafts[0].References = append(fixture.Drafts[0].References, "O-07")
	receipt := Evaluate(fixture)
	if receipt.Passed || caseStatus(receipt, "N-06") != "fail" {
		t.Fatalf("future observation accepted in T0 draft: %+v", receipt)
	}
}

func TestDuplicateObservationIdentityFails(t *testing.T) {
	fixture := loadFixture(t)
	fixture.Observations = append(fixture.Observations, fixture.Observations[1])
	receipt := Evaluate(fixture)
	if receipt.Passed || caseStatus(receipt, "N-06") != "fail" {
		t.Fatalf("duplicate observation ID was accepted: %+v", receipt)
	}
}

func TestDraftOnlyRevisionCanReuseObservedEvidence(t *testing.T) {
	fixture := loadFixture(t)
	fixture.Revisions[1].Observations = append([]string{}, fixture.Revisions[0].Observations...)
	fixture.Drafts[1].References = []string{"O-02", "O-03"}
	fixture.Drafts[1].Text = "案内資料の相違を引き続き確認中です。"
	receipt := Evaluate(fixture)
	if !receipt.Passed || caseStatus(receipt, "P-05") != "pass" || caseStatus(receipt, "N-06") != "pass" {
		t.Fatalf("draft-only revision should preserve valid evidence: %+v", receipt)
	}
}
