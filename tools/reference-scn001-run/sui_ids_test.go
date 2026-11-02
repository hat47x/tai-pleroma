package main

import (
	"slices"
	"testing"
)

func TestSUILinkIDsCannotBeReplacedBehindMatchingCounts(t *testing.T) {
	for name, mutate := range map[string]func(*SUILinkComponent){
		"duplicate card":   func(s *SUILinkComponent) { s.LinkedCards[4] = s.LinkedCards[3] },
		"different card":   func(s *SUILinkComponent) { s.LinkedCards[4] = "O-other" },
		"empty card":       func(s *SUILinkComponent) { s.LinkedCards[4] = "" },
		"duplicate island": func(s *SUILinkComponent) { s.IslandGroups[2] = s.IslandGroups[1] },
		"different island": func(s *SUILinkComponent) { s.IslandGroups[2] = "I-other" },
		"empty island":     func(s *SUILinkComponent) { s.IslandGroups[2] = "" },
	} {
		t.Run(name, func(t *testing.T) {
			receipt := recordedRunForMutation(t)
			link := receipt.Components.SUILink
			if link == nil {
				t.Fatal("recorded fixture needs a SUI component")
			}
			mutate(link)
			if len(link.LinkedCards) != 5 || len(link.IslandGroups) != 3 {
				t.Fatal("test changed the counts")
			}
			var err error
			receipt.RunDigest, err = digestJSON(receipt.Components)
			if err != nil {
				t.Fatal(err)
			}
			if Verify(receipt).Passed {
				t.Error("matching counts hid different or duplicate identities")
			}
			if _, err := BuildOwnerPacket(receipt); err == nil {
				t.Error("invalid identity set reached the owner packet")
			}
		})
	}
}

func TestSUILinkOrderDoesNotChangeIdentityOrApproval(t *testing.T) {
	receipt := recordedRunForMutation(t)
	if receipt.Components.SUILink == nil {
		t.Fatal("recorded fixture needs a SUI component")
	}
	slices.Reverse(receipt.Components.SUILink.LinkedCards)
	slices.Reverse(receipt.Components.SUILink.IslandGroups)
	var err error
	receipt.RunDigest, err = digestJSON(receipt.Components)
	if err != nil {
		t.Fatal(err)
	}
	if result := Verify(receipt); !result.Passed {
		t.Fatalf("valid unordered identities rejected: %+v", result)
	}
	packet, err := BuildOwnerPacket(receipt)
	if err != nil {
		t.Fatal(err)
	}
	if packet.Approved || packet.HumanReviewed || packet.AuthorityVerified || packet.PublicationApproved {
		t.Fatal("identity checks promoted the packet to approval")
	}
}
