package main

import (
	"encoding/json"
	"slices"
	"testing"
)

func TestLinkRejectsAmbiguousIdentitiesAndIncompleteShape(t *testing.T) {
	cases := map[string]func(*Fixture, *SUIReceipt){
		"conflicting observation first": func(f *Fixture, s *SUIReceipt) {
			f.Observations = append([]Observation{{ID: "O-02", Text: "different observation"}}, f.Observations...)
		},
		"identical observation duplicate": func(f *Fixture, s *SUIReceipt) {
			f.Observations = append(f.Observations, f.Observations[0])
		},
		"conflicting card first": func(f *Fixture, s *SUIReceipt) {
			s.DocumentCards = append([]Card{{ID: "O-02", TextDigest: "sha256:different"}}, s.DocumentCards...)
		},
		"identical card duplicate": func(f *Fixture, s *SUIReceipt) {
			s.DocumentCards = append(s.DocumentCards, s.DocumentCards[0])
		},
		"conflicting island first": func(f *Fixture, s *SUIReceipt) {
			s.DocumentIslands = append([]Island{{ID: "I-01", CardIDs: []string{"O-03"}}}, s.DocumentIslands...)
		},
		"identical island duplicate": func(f *Fixture, s *SUIReceipt) {
			s.DocumentIslands = append(s.DocumentIslands, s.DocumentIslands[0])
		},
		"joined island members": func(f *Fixture, s *SUIReceipt) {
			s.DocumentIslands[0].CardIDs = []string{"O-02 O-07"}
		},
		"no document identity": func(f *Fixture, s *SUIReceipt) { s.DocumentID = "" },
		"no document digest":   func(f *Fixture, s *SUIReceipt) { s.DocumentDigest = "" },
		"no edge":              func(f *Fixture, s *SUIReceipt) { s.DocumentEdgeCount = 0 },
		"extra edge":           func(f *Fixture, s *SUIReceipt) { s.DocumentEdgeCount = 2 },
		"negative edge count":  func(f *Fixture, s *SUIReceipt) { s.DocumentEdgeCount = -1 },
	}
	for name, mutate := range cases {
		t.Run(name, func(t *testing.T) {
			fixture, sui := load(t)
			mutate(&fixture, &sui)
			if result := Link(fixture, sui); result.Passed {
				t.Fatalf("ambiguous or incomplete link accepted: %+v", result)
			}
		})
	}
}

func TestLinkKeepsUnorderedListsAndUniqueAdditionalObjects(t *testing.T) {
	fixture, sui := load(t)
	slices.Reverse(fixture.Observations)
	slices.Reverse(sui.DocumentCards)
	slices.Reverse(sui.DocumentIslands[0].CardIDs)
	slices.Reverse(sui.DocumentIslands)
	fixture.Observations = append(fixture.Observations, Observation{ID: "additional", Text: "outside selected observations"})
	sui.DocumentCards = append(sui.DocumentCards, Card{ID: "additional", TextDigest: "not examined"})
	sui.DocumentIslands = append(sui.DocumentIslands, Island{ID: "additional", CardIDs: []string{"additional"}})
	beforeFixture, _ := json.Marshal(fixture)
	beforeSUI, _ := json.Marshal(sui)
	result := Link(fixture, sui)
	if !result.Passed || !result.Contradiction || !slices.Equal(result.LinkedCards, []string{"O-02", "O-03", "O-06", "O-07", "O-08"}) || !slices.Equal(result.IslandGroups, []string{"I-01", "I-02", "I-03"}) || result.EdgeCount != 1 {
		t.Fatalf("valid unordered selection changed: %+v", result)
	}
	afterFixture, _ := json.Marshal(fixture)
	afterSUI, _ := json.Marshal(sui)
	if string(beforeFixture) != string(afterFixture) || string(beforeSUI) != string(afterSUI) {
		t.Fatal("link changed input observations or SUI objects")
	}
}
