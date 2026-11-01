package main

import (
	"errors"
	"testing"
)

func TestRunPassesOnSyntheticBoundary(t *testing.T) {
	receipt := Run()
	if !receipt.Passed {
		t.Fatalf("synthetic boundary failed: %+v", receipt)
	}
	if !receipt.Synthetic || receipt.RealProductsConnected {
		t.Fatalf("receipt overclaims scope: %+v", receipt)
	}
}

func TestReadIsReadOnlyAndKeepsCanonical(t *testing.T) {
	product := NewProduct()
	before := product.Digest()
	harness := NewHarness(product, "session-1")
	read, err := harness.Read("policy")
	if err != nil {
		t.Fatal(err)
	}
	if !read.ReadOnly || read.CanonicalDigest != before {
		t.Fatalf("read receipt is not read-only: %+v", read)
	}
	if product.Digest() != before {
		t.Fatal("read changed the canonical digest")
	}
}

func TestWriteIsDeniedAndCanonicalUnchanged(t *testing.T) {
	product := NewProduct()
	before := product.Digest()
	harness := NewHarness(product, "session-1")
	if err := harness.Write("policy", "tampered"); !errors.Is(err, ErrWriteDenied) {
		t.Fatalf("write was not denied: %v", err)
	}
	if product.Digest() != before {
		t.Fatal("denied write changed the canonical digest")
	}
}

func TestHandoffIsRecordedWithoutCanonicalWrite(t *testing.T) {
	product := NewProduct()
	before := product.Digest()
	harness := NewHarness(product, "session-1")
	handoff, err := harness.Handoff("会議室の予約要否を確認する")
	if err != nil {
		t.Fatal(err)
	}
	if len(product.handoffs) != 1 || product.handoffs[0] != handoff {
		t.Fatalf("handoff not recorded: %+v", product.handoffs)
	}
	if product.Digest() != before {
		t.Fatal("handoff changed the canonical digest")
	}
}

func TestHandoffRecordsDeferredWhenBudgetExhausted(t *testing.T) {
	product := NewProduct()
	before := product.Digest()
	harness := NewHarness(product, "session-1")
	first, err := harness.Handoff("最初の課題")
	if err != nil {
		t.Fatal(err)
	}
	second, err := harness.Handoff("上限の後の課題")
	if err != nil {
		t.Fatal(err)
	}
	if first.Deferred {
		t.Fatal("the first handoff should be passed")
	}
	if !second.Deferred {
		t.Fatal("the second handoff should be deferred")
	}
	if len(product.handoffs) != 2 || product.handoffs[0] != first || product.handoffs[1] != second {
		t.Fatalf("handoffs not recorded: %+v", product.handoffs)
	}
	if product.Digest() != before {
		t.Fatal("deferred handoff changed the canonical digest")
	}
}

func TestSessionEndKeepsProductReadable(t *testing.T) {
	product := NewProduct()
	harness := NewHarness(product, "session-1")
	harness.EndSession()
	if _, err := harness.Read("policy"); err == nil {
		t.Fatal("harness read after session end should fail")
	}
	if _, err := product.Read("policy"); err != nil {
		t.Fatalf("product canonical should stay readable: %v", err)
	}
}

func TestProviderEncounterIsRecordedWithoutCanonicalWrite(t *testing.T) {
	product := NewProduct()
	before := product.Digest()
	harness := NewHarness(product, "session-1")
	encounter, err := harness.Encounter(Provider{ID: "provider-a", Version: "v1"}, "課題を処理する")
	if err != nil {
		t.Fatal(err)
	}
	if len(harness.encounters) != 1 || harness.encounters[0] != encounter {
		t.Fatalf("encounter not recorded: %+v", harness.encounters)
	}
	if product.Digest() != before {
		t.Fatal("encounter changed the canonical digest")
	}
}

func TestProviderExchangeIsRecordedAsEncounter(t *testing.T) {
	product := NewProduct()
	before := product.Digest()
	harness := NewHarness(product, "session-1")
	first, err := harness.Encounter(Provider{ID: "provider-a", Version: "v1"}, "最初の課題")
	if err != nil {
		t.Fatal(err)
	}
	second, err := harness.Encounter(Provider{ID: "provider-b", Version: "v2"}, "交換後の課題")
	if err != nil {
		t.Fatal(err)
	}
	if len(harness.encounters) != 2 || harness.encounters[0] != first || harness.encounters[1] != second {
		t.Fatalf("encounters not recorded: %+v", harness.encounters)
	}
	if first.ProviderID == second.ProviderID {
		t.Fatal("the exchange should change the provider")
	}
	if product.Digest() != before {
		t.Fatal("provider exchange changed the canonical digest")
	}
}
