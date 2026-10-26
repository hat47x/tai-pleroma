package main

import (
	"fmt"
	"testing"
)

func TestAmbiguousReviewIdentityIsAlwaysBlocked(t *testing.T) {
	for _, id := range append(append([]string{}, required...), optional...) {
		for _, pendingLast := range []bool{false, true} {
			t.Run(fmt.Sprintf("%s/pending-last=%v", id, pendingLast), func(t *testing.T) {
				status := acceptedStatus()
				pending := Item{ID: id, Status: "pending"}
				if pendingLast {
					status.Items = append(status.Items, pending)
				} else {
					status.Items = append([]Item{pending}, status.Items...)
				}
				result := Evaluate(status)
				if result.Allowed {
					t.Fatalf("conflicting review identity was allowed: %+v", result)
				}
			})
		}
		t.Run(id+"/same-value", func(t *testing.T) {
			status := acceptedStatus()
			for _, item := range status.Items {
				if item.ID == id {
					status.Items = append(status.Items, item)
					break
				}
			}
			if result := Evaluate(status); result.Allowed {
				t.Fatalf("duplicate review identity was allowed: %+v", result)
			}
		})
	}
}

func TestUnexpectedReviewShapeIsBlocked(t *testing.T) {
	for name, mutate := range map[string]func(*Status){
		"wrong scenario":  func(s *Status) { s.Scenario = "other" },
		"missing schema":  func(s *Status) { s.Schema = "" },
		"unknown schema":  func(s *Status) { s.Schema = "future/v999" },
		"unknown review":  func(s *Status) { s.Items = append(s.Items, Item{ID: "R-08", Status: "accepted", Evidence: "external"}) },
		"blank review ID": func(s *Status) { s.Items = append(s.Items, Item{ID: "", Status: "accepted", Evidence: "external"}) },
	} {
		t.Run(name, func(t *testing.T) {
			status := acceptedStatus()
			mutate(&status)
			if result := Evaluate(status); result.Allowed {
				t.Fatalf("unexpected review shape was allowed: %+v", result)
			}
		})
	}
}
