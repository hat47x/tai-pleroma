package main

import (
	"context"
	"os"
	"path/filepath"
	"testing"
)

func rehash(t *testing.T, receipt *RunReceipt) {
	t.Helper()
	digest, err := digestJSON(receipt.Components)
	if err != nil {
		t.Fatal(err)
	}
	receipt.RunDigest = digest
}

func boundRunForMutation(t *testing.T) RunReceipt {
	t.Helper()
	receipt := recordedRunForMutation(t)
	if verification := Verify(receipt); !verification.Passed || !verification.InputBindingVerified {
		t.Fatalf("recorded run does not carry a verified input binding: %+v", verification)
	}
	return receipt
}

func TestRecordedRunBindsMMISelectionToEvaluationAndD04(t *testing.T) {
	receipt := boundRunForMutation(t)
	for _, id := range []string{"O-02", "O-03", "O-07"} {
		want := receipt.Components.MMI.SelectedDigests[id]
		if want == "" || receipt.Components.SCN001.ObservationDigests[id] != want ||
			receipt.Components.ReviewArtifact.ObservationDigests[id] != want {
			t.Fatalf("%s is not bound across MMI, SCN-001, and D-04", id)
		}
	}
	packet, err := BuildOwnerPacket(receipt)
	if err != nil || !packet.InputBindingVerified || packet.Approved || packet.HumanReviewed {
		t.Fatalf("owner packet does not report the binding without approval: %+v %v", packet, err)
	}
}

func TestInputBindingRejectsSubstitutionEvenAfterRehash(t *testing.T) {
	other := artifactDigest([]byte("差し替えた本文"))
	for name, mutate := range map[string]func(*RunReceipt){
		"SCN-001 evaluated other text": func(r *RunReceipt) { r.Components.SCN001.ObservationDigests["O-02"] = other },
		"D-04 rendered other text":     func(r *RunReceipt) { r.Components.ReviewArtifact.ObservationDigests["O-03"] = other },
		"MMI selected other text":      func(r *RunReceipt) { r.Components.MMI.SelectedDigests["O-07"] = other },
		"D-04 omits selected row":      func(r *RunReceipt) { delete(r.Components.ReviewArtifact.ObservationDigests, "O-07") },
		"MMI digests dropped":          func(r *RunReceipt) { r.Components.MMI.SelectedDigests = nil },
		"D-04 digests dropped":         func(r *RunReceipt) { r.Components.ReviewArtifact.ObservationDigests = nil },
		"malformed digest":             func(r *RunReceipt) { r.Components.SCN001.ObservationDigests["O-06"] = "sha256:" },
		"blank ID":                     func(r *RunReceipt) { r.Components.MMI.SelectedDigests[" "] = other },
		"selected count mismatch": func(r *RunReceipt) {
			r.Components.MMI.SelectedDigests["O-06"] = r.Components.SCN001.ObservationDigests["O-06"]
		},
	} {
		t.Run(name, func(t *testing.T) {
			receipt := boundRunForMutation(t)
			mutate(&receipt)
			rehash(t, &receipt)
			if result := Verify(receipt); result.Passed {
				t.Fatalf("substituted input binding verified: %+v", result)
			}
			if _, err := BuildOwnerPacket(receipt); err == nil {
				t.Fatal("substituted input binding reached the owner packet")
			}
		})
	}
}

func TestRecordWithoutBindingFieldsStaysVerifiableButUnbound(t *testing.T) {
	receipt := boundRunForMutation(t)
	receipt.Components.MMI.SelectedDigests = nil
	receipt.Components.SCN001.ObservationDigests = nil
	receipt.Components.ReviewArtifact.ObservationDigests = nil
	rehash(t, &receipt)
	result := Verify(receipt)
	if !result.Passed || result.InputBindingVerified {
		t.Fatalf("legacy record must verify without claiming a binding: %+v", result)
	}
	packet, err := BuildOwnerPacket(receipt)
	if err != nil || packet.InputBindingVerified {
		t.Fatalf("legacy packet claims a binding: %+v %v", packet, err)
	}
}

func TestSelectedDigestsRejectAmbiguousMMIRows(t *testing.T) {
	dir := t.TempDir()
	for name, body := range map[string]string{
		"duplicate": `{"selected":[{"id":"O-02","text":"a"},{"id":"O-02","text":"b"}]}`,
		"blank ID":  `{"selected":[{"id":" ","text":"a"}]}`,
	} {
		path := filepath.Join(dir, name+".json")
		if err := os.WriteFile(path, []byte(body), 0o600); err != nil {
			t.Fatal(err)
		}
		if _, err := selectedDigests(path); err == nil {
			t.Fatalf("%s MMI rows accepted", name)
		}
	}
}

func TestCombinedRunBindsInputs(t *testing.T) {
	receipt, err := Run(context.Background(), taiRootForTest(t))
	if err != nil {
		t.Fatal(err)
	}
	if result := Verify(receipt); !result.Passed || !result.InputBindingVerified {
		t.Fatalf("combined run is not bound: %+v", result)
	}
	if len(receipt.Components.MMI.SelectedDigests) != receipt.Components.MMI.SelectedRows {
		t.Fatalf("MMI selected digests are incomplete: %+v", receipt.Components.MMI)
	}
}
