package main

import "testing"

func mmiReceiptFixture() MMIReceipt {
	return MMIReceipt{
		Schema: "tai.reference.mmi-readonly/v0", MmiCommit: "abc123",
		RealProductConnected: true, ReadOnly: true, ConflictPreserved: true,
		Selected: []MMISelected{
			{ID: "O-02", Text: "施設の利用は予約不要", Source: "notice", Version: "v0", Availability: "available"},
			{ID: "O-03", Text: "会議室の利用には事前予約が必要", Source: "old-guidance", Version: "v0", Availability: "available"},
			{ID: "O-07", Text: "施設の利用は予約不要", Source: "distribution", Version: "v2", Availability: "available"},
		},
	}
}

func TestMMIObservationOverlay(t *testing.T) {
	fixture := loadFixture(t)
	receipt := mmiReceiptFixture()
	if err := ApplyMMIObservations(&fixture, receipt); err != nil {
		t.Fatal(err)
	}
	evaluated := EvaluateWithSource(fixture, "mmi-reference", receipt.MmiCommit)
	if !evaluated.Passed || !evaluated.RealProductsConnected || evaluated.ObservationSource != "mmi-reference" || evaluated.MMICommit != "abc123" {
		t.Fatalf("MMI overlay was not recorded: %+v", evaluated)
	}
	if caseStatus(evaluated, "P-02") != "pass" || caseStatus(evaluated, "N-01") != "pass" {
		t.Fatalf("MMI overlay lost the conflict: %+v", evaluated)
	}
}

func TestMMIOverlayRejectsEqualTexts(t *testing.T) {
	fixture := loadFixture(t)
	receipt := mmiReceiptFixture()
	receipt.Selected[1].Text = receipt.Selected[0].Text
	if err := ApplyMMIObservations(&fixture, receipt); err == nil {
		t.Fatal("equal O-02/O-03 texts were accepted")
	}
}
