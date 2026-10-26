package main

import "testing"

func TestReviewSummaryCannotDisagreeWithComponents(t *testing.T) {
	for name, mutate := range map[string]func(*RunReceipt){
		"drop all blockers":         func(r *RunReceipt) { r.PublicationBlockers = nil },
		"omit one blocker":          func(r *RunReceipt) { r.PublicationBlockers = r.PublicationBlockers[1:] },
		"substitute blocker":        func(r *RunReceipt) { r.PublicationBlockers = []string{"different review blocker"} },
		"wrong scenario":            func(r *RunReceipt) { r.Scenario = "SCN-other" },
		"hide synthetic scope":      func(r *RunReceipt) { r.Synthetic = false },
		"hide provisional approval": func(r *RunReceipt) { r.ProvisionalApproved = false },
		"hide product connection":   func(r *RunReceipt) { r.RealProductsConnected = false },
	} {
		t.Run(name, func(t *testing.T) {
			receipt := recordedRunForMutation(t)
			mutate(&receipt)
			hash, err := digestJSON(receipt.Components)
			if err != nil || hash != receipt.RunDigest {
				t.Fatal("test changed component evidence")
			}
			if result := Verify(receipt); result.Passed {
				t.Errorf("contradictory summary verified: %+v", result)
			}
			if packet, err := BuildOwnerPacket(receipt); err == nil {
				t.Errorf("contradictory summary reached owner packet: %+v", packet)
			}
		})
	}
}

func TestOwnerPacketKeepsEveryGateBlocker(t *testing.T) {
	receipt := recordedRunForMutation(t)
	packet, err := BuildOwnerPacket(receipt)
	if err != nil {
		t.Fatal(err)
	}
	if len(packet.PublicationBlockers) == 0 || len(packet.PublicationBlockers) != len(receipt.Components.PublicationGate.Blockers) {
		t.Fatal("gate blockers lost")
	}
	for i, blocker := range receipt.Components.PublicationGate.Blockers {
		if packet.PublicationBlockers[i] != blocker {
			t.Fatal("owner packet changed a gate blocker")
		}
	}
	if packet.Approved || packet.HumanReviewed || packet.AuthorityVerified || packet.PublicationApproved || packet.PublicationAllowed {
		t.Fatal("current pending review gained approval")
	}
}

func consistentFailedRun(t *testing.T) RunReceipt {
	t.Helper()
	receipt := RunReceipt{Schema: "tai.reference.scn001-run/v0", Scenario: "SCN-001", Synthetic: true, PublicationBlockers: []string{"reference run failed"}}
	receipt.Components.PublicationGate = GateComponent{Schema: "tai.reference.scn001-publication-gate/v0", Blockers: []string{"reference run failed"}}
	var err error
	receipt.RunDigest, err = digestJSON(receipt.Components)
	if err != nil {
		t.Fatal(err)
	}
	return receipt
}

func TestOwnerPacketRequiresSuccessfulReferenceRun(t *testing.T) {
	receipt := consistentFailedRun(t)
	if result := Verify(receipt); !result.Passed {
		t.Fatalf("self-consistent failed evidence should remain inspectable: %+v", result)
	}
	if _, err := BuildOwnerPacket(receipt); err == nil {
		t.Fatal("self-consistent failure became a successful-review packet")
	}
	receipt.ReviewRequired = true
	if result := Verify(receipt); result.Passed {
		t.Fatal("failed summary accepted an unsupported review requirement")
	}
}

func TestUnknownGateSchemaCannotBeRehashedIntoKnownEvidence(t *testing.T) {
	receipt := recordedRunForMutation(t)
	receipt.Components.PublicationGate.Schema = "unknown.gate/v999"
	var err error
	receipt.RunDigest, err = digestJSON(receipt.Components)
	if err != nil {
		t.Fatal(err)
	}
	if result := Verify(receipt); result.Passed {
		t.Fatal("unknown gate schema accepted after rehashing")
	}
	if _, err := BuildOwnerPacket(receipt); err == nil {
		t.Fatal("unknown gate reached owner packet")
	}
}

func TestConsistentGateSummaryDoesNotGrantApproval(t *testing.T) {
	receipt := recordedRunForMutation(t)
	receipt.Components.PublicationGate.Allowed = true
	receipt.Components.PublicationGate.Blockers = []string{}
	receipt.PublicationAllowed = true
	receipt.PublicationBlockers = nil // Both representations mean no blockers.
	var err error
	receipt.RunDigest, err = digestJSON(receipt.Components)
	if err != nil {
		t.Fatal(err)
	}
	if result := Verify(receipt); !result.Passed {
		t.Fatalf("consistent gate conditions were rejected: %+v", result)
	}
	packet, err := BuildOwnerPacket(receipt)
	if err != nil {
		t.Fatal(err)
	}
	if !packet.PublicationAllowed || len(packet.PublicationBlockers) != 0 || packet.Approved || packet.HumanReviewed || packet.AuthorityVerified || packet.PublicationApproved {
		t.Fatal("gate conditions were promoted to approval")
	}
}
