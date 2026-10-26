package main

import (
	"encoding/json"
	"reflect"
	"testing"
)

func selectedReceipt() MMIReceipt {
	return MMIReceipt{Schema: "tai.reference.mmi-readonly/v0", RealProductConnected: true, ReadOnly: true, ConflictPreserved: true,
		Selected: []MMISelected{
			{ID: "O-02", Text: "  改訂した掲示の文面  ", Source: " notice-copy ", Version: " test-v0 ", Availability: "available"},
			{ID: "O-03", Text: "会議室の利用には事前予約が必要", Source: "guidance-copy", Version: "test-v1", Availability: "available"},
			{ID: "O-07", Text: "  改訂した掲示の文面  ", Source: "redistribution-copy", Version: "test-v2", Availability: "available"},
		}}
}

func TestMMISelectionRejectsAmbiguousOrIncompleteInputWithoutMutation(t *testing.T) {
	for name, mutate := range map[string]func(*Fixture, *MMIReceipt){
		"missing O-07":   func(_ *Fixture, r *MMIReceipt) { r.Selected = r.Selected[:2] },
		"duplicate O-02": func(_ *Fixture, r *MMIReceipt) { r.Selected = append(r.Selected, r.Selected[0]) },
		"conflicting duplicate": func(_ *Fixture, r *MMIReceipt) {
			row := r.Selected[0]
			row.Text = "後勝ちで差し替えられる本文"
			r.Selected = append(r.Selected, row)
		},
		"unrelated known ID": func(_ *Fixture, r *MMIReceipt) {
			row := r.Selected[0]
			row.ID = "O-05"
			r.Selected = append(r.Selected, row)
		},
		"unknown ID": func(_ *Fixture, r *MMIReceipt) {
			row := r.Selected[0]
			row.ID = "O-99"
			r.Selected = append(r.Selected, row)
		},
		"blank ID":                    func(_ *Fixture, r *MMIReceipt) { r.Selected[2].ID = " " },
		"missing source":              func(_ *Fixture, r *MMIReceipt) { r.Selected[2].Source = "" },
		"blank version":               func(_ *Fixture, r *MMIReceipt) { r.Selected[2].Version = " \t" },
		"missing text":                func(_ *Fixture, r *MMIReceipt) { r.Selected[2].Text = "" },
		"missing availability":        func(_ *Fixture, r *MMIReceipt) { r.Selected[2].Availability = "" },
		"unavailable selected row":    func(_ *Fixture, r *MMIReceipt) { r.Selected[2].Availability = "unavailable" },
		"missing target in fixture":   func(f *Fixture, _ *MMIReceipt) { f.Observations = f.Observations[:5] },
		"duplicate target in fixture": func(f *Fixture, _ *MMIReceipt) { f.Observations = append(f.Observations, f.Observations[1]) },
	} {
		t.Run(name, func(t *testing.T) {
			fixture := loadFixture(t)
			receipt := selectedReceipt()
			mutate(&fixture, &receipt)
			before, err := json.Marshal(fixture)
			if err != nil {
				t.Fatal(err)
			}
			if err := ApplyMMIObservations(&fixture, receipt); err == nil {
				t.Fatal("ambiguous or incomplete selection accepted")
			}
			after, err := json.Marshal(fixture)
			if err != nil {
				t.Fatal(err)
			}
			if string(before) != string(after) {
				t.Fatal("rejected selection partially changed fixture")
			}
		})
	}
}

func TestMMISelectionIsOrderIndependentAndPreservesUnselectedState(t *testing.T) {
	for _, order := range [][3]int{{0, 1, 2}, {0, 2, 1}, {1, 0, 2}, {1, 2, 0}, {2, 0, 1}, {2, 1, 0}} {
		fixture := loadFixture(t)
		before := loadFixture(t)
		receipt := selectedReceipt()
		rows := append([]MMISelected(nil), receipt.Selected...)
		for i, index := range order {
			receipt.Selected[i] = rows[index]
		}
		if err := ApplyMMIObservations(&fixture, receipt); err != nil {
			t.Fatal(err)
		}
		for i, got := range fixture.Observations {
			var row *MMISelected
			for j := range rows {
				if rows[j].ID == got.ID {
					row = &rows[j]
				}
			}
			if row == nil {
				if got != before.Observations[i] {
					t.Fatalf("unselected observation changed: %s", got.ID)
				}
				continue
			}
			want := before.Observations[i]
			want.Text = row.Text
			want.Source = row.Source
			want.SourceVersion = row.Version
			want.Availability = row.Availability
			if got != want {
				t.Fatalf("observation changed incorrectly: got=%+v want=%+v", got, want)
			}
		}
		if !reflect.DeepEqual(fixture.Decisions, before.Decisions) || !reflect.DeepEqual(fixture.Drafts, before.Drafts) ||
			!reflect.DeepEqual(fixture.Revisions, before.Revisions) || !reflect.DeepEqual(fixture.Hypotheses, before.Hypotheses) ||
			!reflect.DeepEqual(fixture.Authority, before.Authority) || !reflect.DeepEqual(fixture.Provisional, before.Provisional) {
			t.Fatal("overlay changed synthetic decisions or authority")
		}
		result := EvaluateWithSource(fixture, "mmi-reference", receipt.MmiCommit)
		if !result.Passed || result.HumanReviewed || result.AuthorityVerified || result.PublicationApproved {
			t.Fatalf("valid selection outcome: %+v", result)
		}
	}
}
