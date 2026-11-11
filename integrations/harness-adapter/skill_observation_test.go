package harnessadapter

import (
	"encoding/json"
	"strings"
	"testing"
)

// TestObserveSkillUseLoadIsToolCallNotSelfReport is the core rule: a load must be
// visible as a tool call naming the Skill. A self-report boolean in observations
// is never consulted, because the model asserting it is not an observation.
func TestObserveSkillUseLoadIsToolCallNotSelfReport(t *testing.T) {
	pin := SkillPin{ID: "yi-tei-modeling", PlacedPath: `C:\ws\.dsh\skills\x\SKILL.md`, BytesSHA256: "sha256:abc"}
	res := &Result{
		Adapter:      "dsh-headless",
		Transport:    TransportDelivered,
		Run:          RunCompleted,
		FinalText:    "the total is std.money",
		ToolCalls:    []ToolCallRecord{{Tool: "skill", InputJSON: `{"name":"yi-tei-modeling"}`}},
		Observations: map[string]string{"skill_loaded": "true"},
	}
	obs := ObserveSkillUse(pin, res)
	if obs.LoadState != LoadLoaded {
		t.Fatalf("load state = %q, want loaded", obs.LoadState)
	}
	if obs.LoadedVia != "skill" {
		t.Fatalf("loaded via = %q", obs.LoadedVia)
	}
	if !obs.AnswerPresent {
		t.Fatal("an answer was present but not recorded")
	}

	// Without the tool call, the self-report must not produce "loaded".
	res2 := &Result{Adapter: "dsh-headless", FinalText: "x", Observations: map[string]string{"skill_loaded": "true"}}
	obs2 := ObserveSkillUse(pin, res2)
	if obs2.LoadState == LoadLoaded {
		t.Fatal("a self-report boolean produced a loaded state")
	}
	if obs2.LoadState != LoadNotLoaded {
		t.Fatalf("load state = %q, want not-loaded", obs2.LoadState)
	}
}

// TestObserveSkillUseUnknownWhenNotPlaced keeps "the adapter never placed it"
// from reading as "the model chose not to use it".
func TestObserveSkillUseUnknownWhenNotPlaced(t *testing.T) {
	pin := SkillPin{ID: "s"}
	obs := ObserveSkillUse(pin, &Result{Adapter: "claude-code"})
	if obs.Placed {
		t.Fatal("a pin with no path was recorded as placed")
	}
	if obs.LoadState != LoadUnknown {
		t.Fatalf("load state = %q, want unknown", obs.LoadState)
	}
	if !strings.Contains(obs.Note, "did not place") {
		t.Fatalf("note = %q", obs.Note)
	}
}

// TestObserveSkillPairEligibleOnlyOnRealContrast checks the H2/H3 pairing rule.
func TestObserveSkillPairEligibleOnlyOnRealContrast(t *testing.T) {
	pin := SkillPin{ID: "s", PlacedPath: `C:\ws\s\SKILL.md`, BytesSHA256: "sha256:a"}
	h2 := &Result{Adapter: "h2", Transport: TransportDelivered, Run: RunCompleted, FinalText: "a"}
	h3 := &Result{
		Adapter: "h3", Transport: TransportDelivered, Run: RunCompleted, FinalText: "b",
		ToolCalls: []ToolCallRecord{{Tool: "skill", InputJSON: `{"name":"s"}`}},
	}
	pair := ObserveSkillPair("task-1", pin, h2, h3)
	if !pair.Eligible {
		t.Fatalf("a real contrast was judged ineligible: %v", pair.IneligibleReasons)
	}
	if !strings.Contains(pair.SkillEffect, "accuracy not measured") {
		t.Fatalf("the pair claimed an accuracy result: %q", pair.SkillEffect)
	}
}

// TestObserveSkillPairRejectsH2ThatLoaded is the mislabelled-arm case: an "H2"
// that loaded the Skill is an H3 under the wrong name.
func TestObserveSkillPairRejectsH2ThatLoaded(t *testing.T) {
	pin := SkillPin{ID: "s", PlacedPath: `C:\ws\s\SKILL.md`}
	h2 := &Result{Adapter: "h2", Transport: TransportDelivered, ToolCalls: []ToolCallRecord{{Tool: "skill", InputJSON: `{"name":"s"}`}}}
	h3 := &Result{Adapter: "h3", Transport: TransportDelivered, ToolCalls: []ToolCallRecord{{Tool: "skill", InputJSON: `{"name":"s"}`}}}
	pair := ObserveSkillPair("t", pin, h2, h3)
	if pair.Eligible {
		t.Fatal("a pair where H2 loaded the Skill was judged eligible")
	}
	if !containsStr(pair.IneligibleReasons, "H2 arm loaded the Skill; the pair is not a contrast") {
		t.Fatalf("reason not recorded: %v", pair.IneligibleReasons)
	}
}

// TestObserveSkillPairFailedLoadIsNotNoEffect is the trap TAI #168 warns about:
// an H3 that failed to load is an ineligible trial, not evidence that the Skill
// made no difference.
func TestObserveSkillPairFailedLoadIsNotNoEffect(t *testing.T) {
	pin := SkillPin{ID: "s", PlacedPath: `C:\ws\s\SKILL.md`}
	h2 := &Result{Adapter: "h2", Transport: TransportDelivered, FinalText: "a"}
	h3 := &Result{Adapter: "h3", Transport: TransportDelivered, FinalText: "b"} // no loader call
	pair := ObserveSkillPair("t", pin, h2, h3)
	if pair.Eligible {
		t.Fatal("a pair whose H3 never loaded was judged eligible")
	}
	if pair.SkillEffect == "no-effect" {
		t.Fatal("a failed load was reported as no effect")
	}
	if pair.SkillEffect != "not-measured" {
		t.Fatalf("skill effect = %q", pair.SkillEffect)
	}
	joined := strings.Join(pair.IneligibleReasons, " ")
	if !strings.Contains(joined, "did not load") {
		t.Fatalf("the failed load was not named: %v", pair.IneligibleReasons)
	}
}

// TestObserveSkillPairMissingArmIsIneligible keeps a half-run pair from being
// scored as a zero.
func TestObserveSkillPairMissingArmIsIneligible(t *testing.T) {
	pin := SkillPin{ID: "s", PlacedPath: `C:\ws\s\SKILL.md`}
	pair := ObserveSkillPair("t", pin, nil, &Result{Adapter: "h3"})
	if pair.Eligible {
		t.Fatal("a pair with no H2 arm was judged eligible")
	}
	if len(pair.IneligibleReasons) == 0 {
		t.Fatal("an ineligible pair carried no reason")
	}
}

// TestSkillObservationJSONShape keeps the sheet a stable artifact.
func TestSkillObservationJSONShape(t *testing.T) {
	pin := SkillPin{ID: "s", PlacedPath: `C:\ws\s\SKILL.md`, BytesSHA256: "sha256:a"}
	h2 := &Result{Adapter: "h2", Transport: TransportDelivered, FinalText: "a"}
	h3 := &Result{Adapter: "h3", Transport: TransportDelivered, FinalText: "b", ToolCalls: []ToolCallRecord{{Tool: "skill", InputJSON: `{"name":"s"}`}}}
	b, err := SkillObservationJSON([]SkillPairObservation{ObserveSkillPair("t", pin, h2, h3)})
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	var back []SkillPairObservation
	if err := json.Unmarshal(b, &back); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}
	if len(back) != 1 || !back[0].Eligible {
		t.Fatalf("round trip lost the pair: %s", string(b))
	}
}

// TestSkillCostIsVendorVocabularyNotSummed stops a dollar cost from one vendor
// being compared with a token count from another.
func TestSkillCostIsVendorVocabularyNotSummed(t *testing.T) {
	pin := SkillPin{ID: "s", PlacedPath: `C:\ws\s\SKILL.md`}
	cc := &Result{Adapter: "claude-code", Observations: map[string]string{"total-cost-usd": "0.04"}}
	dsh := &Result{Adapter: "dsh-headless", Observations: map[string]string{}}
	if ObserveSkillUse(pin, cc).Cost != "0.04" {
		t.Fatal("a reported cost was dropped")
	}
	if ObserveSkillUse(pin, dsh).Cost != "" {
		t.Fatal("a cost was invented for a harness that reports none")
	}
}
