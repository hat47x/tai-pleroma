package main

import (
	"strings"
	"testing"
)

// changedFields must name every kind of difference between the checkout before and
// after the EKI commands ran, one at a time.
func TestChangedFieldsSeesEachKindOfChange(t *testing.T) {
	base := CheckoutFacts{Commit: strings.Repeat("a", 40), TrackedDigest: "t", UntrackedDigest: "u", BuildInputsDigest: "b"}
	if got := base.changedFields(base); len(got) != 0 {
		t.Fatalf("identical facts must not differ: %v", got)
	}
	cases := map[string]struct {
		change func(*CheckoutFacts)
		field  string
	}{
		"HEAD only":                {func(f *CheckoutFacts) { f.Commit = strings.Repeat("b", 40) }, "HEAD"},
		"hidden flag count only":   {func(f *CheckoutFacts) { f.HiddenFlaggedFiles = 1 }, "hidden-flagged files"},
		"tracked digest only":      {func(f *CheckoutFacts) { f.TrackedDigest = "t2" }, "tracked changes"},
		"untracked digest only":    {func(f *CheckoutFacts) { f.UntrackedDigest = "u2" }, "untracked files"},
		"build input digest only":  {func(f *CheckoutFacts) { f.BuildInputsDigest = "b2" }, "untracked build inputs"},
		"tracked change count":     {func(f *CheckoutFacts) { f.TrackedChanges = 1 }, "tracked changes"},
		"untracked build inputs n": {func(f *CheckoutFacts) { f.UntrackedBuildInputs = 1 }, "untracked build inputs"},
	}
	for name, test := range cases {
		t.Run(name, func(t *testing.T) {
			after := base
			test.change(&after)
			got := strings.Join(base.changedFields(after), ",")
			if !strings.Contains(got, test.field) {
				t.Fatalf("%s: want %q in %q", name, test.field, got)
			}
		})
	}
}

// The receipt must not say the CLI compared the binary digests: it only records them.
func TestNotesDoNotClaimABinaryDigestCheck(t *testing.T) {
	text := strings.Join(newReceipt().Notes, "\n")
	if strings.Contains(text, "sha256が期待と合った") {
		t.Fatalf("the CLI has no expectation for the binary digest: %s", text)
	}
	if !strings.Contains(text, "記録するだけで照合しない") {
		t.Fatalf("the note must say the digest is recorded, not compared: %s", text)
	}
}
