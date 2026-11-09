package main

import (
	"context"
	"encoding/json"
	"os"
	"strings"
	"testing"
)

func withPins(t *testing.T, mmi, sei *PinSummary) RunReceipt {
	t.Helper()
	receipt := recordedRunForMutation(t)
	receipt.Components.MMI.Pin = mmi
	receipt.Components.SEI.Pin = sei
	return rehashed(t, receipt)
}

func rehashed(t *testing.T, receipt RunReceipt) RunReceipt {
	t.Helper()
	digest, err := digestJSON(receipt.Components)
	if err != nil {
		t.Fatal(err)
	}
	receipt.RunDigest = digest
	return receipt
}

func TestRecordedRunWithoutPinsKeepsItsDigestAndVerifies(t *testing.T) {
	receipt := recordedRunForMutation(t)
	if receipt.Components.MMI.Pin != nil || receipt.Components.SEI.Pin != nil {
		t.Fatal("a stored record from before the pin carries no pin summary")
	}
	verification := Verify(receipt)
	if !verification.Passed || len(verification.PinnedComponents) != 0 {
		t.Fatalf("%+v", verification)
	}
}

func TestVerifyReportsOnlyComponentsWhoseCheckedPinMatched(t *testing.T) {
	receipt := withPins(t, &PinSummary{Checked: true, Result: "match"}, &PinSummary{Checked: false, Result: "not-checked"})
	verification := Verify(receipt)
	if !verification.Passed || strings.Join(verification.PinnedComponents, ",") != "mmi" {
		t.Fatalf("%+v", verification)
	}
}

func TestVerifyRejectsAPassingComponentWhoseCheckedPinDidNotMatch(t *testing.T) {
	for _, result := range []string{"mismatch", "unavailable", "invalid-expectation", "not-checked", ""} {
		receipt := withPins(t, &PinSummary{Checked: true, Result: result}, nil)
		if verification := Verify(receipt); verification.Passed || !strings.Contains(verification.Reason, "version pin did not match") {
			t.Fatalf("result %q: %+v", result, verification)
		}
	}
}

func TestVerifyRejectsAnUncheckedPinThatReportsAResult(t *testing.T) {
	receipt := withPins(t, nil, &PinSummary{Checked: false, Result: "match"})
	if verification := Verify(receipt); verification.Passed || !strings.Contains(verification.Reason, "unchecked") {
		t.Fatalf("%+v", verification)
	}
}

func TestPinSummaryIsPartOfTheRunDigest(t *testing.T) {
	plain := recordedRunForMutation(t)
	pinned := withPins(t, &PinSummary{Checked: true, Result: "match"}, nil)
	if plain.RunDigest == pinned.RunDigest {
		t.Fatal("a pin result must change the run digest")
	}
	tampered := pinned
	tampered.Components.MMI.Pin = &PinSummary{Checked: false, Result: "not-checked"}
	if verification := Verify(tampered); verification.Passed {
		t.Fatalf("removing a pin result must break the digest: %+v", verification)
	}
}

func TestCombinedRunKeepsTheMMIPinSummary(t *testing.T) {
	receipt, err := Run(context.Background(), taiRootForTest(t))
	if err != nil {
		t.Fatal(err)
	}
	pin := receipt.Components.MMI.Pin
	if pin == nil {
		t.Fatal("the MMI tool reports its pin, so the run must keep it")
	}
	if os.Getenv("TAI_MMI_EXPECT_COMMIT") == "" && (pin.Checked || pin.Result != "not-checked") {
		t.Fatalf("an unpinned run only records: %+v", pin)
	}
	if pin.Checked && pin.Result != "match" {
		t.Fatalf("a checked pin that did not match cannot be in a passing run: %+v", pin)
	}
	if verification := Verify(receipt); !verification.Passed {
		t.Fatalf("%+v", verification)
	}
}

// The SEI tool (reference-sei-decision, version pin) reports its pin as a "pin" object that
// also carries the expected and actual values. The run keeps only checked and result.
func TestSEIPinObjectOfTheSEIToolDecodesIntoThePinSummary(t *testing.T) {
	raw := `{"passed":true,"pin":{"checked":true,"result":"match","commit":{"expected":"x","actual":"x"},"goVersion":{"expected":"go1.26.9","actual":"go1.26.9"}}}`
	var sei SEIComponent
	if err := json.Unmarshal([]byte(raw), &sei); err != nil {
		t.Fatal(err)
	}
	if sei.Pin == nil || !sei.Pin.Checked || sei.Pin.Result != "match" {
		t.Fatalf("%+v", sei.Pin)
	}
	receipt := withPins(t, nil, sei.Pin)
	if verification := Verify(receipt); !verification.Passed || strings.Join(verification.PinnedComponents, ",") != "sei" {
		t.Fatalf("%+v", verification)
	}
}
