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
	h3Pin := SkillPin{ID: "s", PlacedPath: `C:\ws\s\SKILL.md`, BytesSHA256: "sha256:a"}
	h2 := &Result{Adapter: "h2", Transport: TransportDelivered, Run: RunCompleted, FinalText: "a"}
	h3 := &Result{
		Adapter: "h3", Transport: TransportDelivered, Run: RunCompleted, FinalText: "b",
		ToolCalls: []ToolCallRecord{{Tool: "skill", InputJSON: `{"name":"s"}`}},
	}
	pair := ObserveSkillPair("task-1", SkillPin{ID: "s"}, h3Pin, h2, h3)
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
	h3Pin := SkillPin{ID: "s", PlacedPath: `C:\ws\s\SKILL.md`}
	h2 := &Result{Adapter: "h2", Transport: TransportDelivered, ToolCalls: []ToolCallRecord{{Tool: "skill", InputJSON: `{"name":"s"}`}}}
	h3 := &Result{Adapter: "h3", Transport: TransportDelivered, ToolCalls: []ToolCallRecord{{Tool: "skill", InputJSON: `{"name":"s"}`}}}
	pair := ObserveSkillPair("t", SkillPin{ID: "s"}, h3Pin, h2, h3)
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
	h3Pin := SkillPin{ID: "s", PlacedPath: `C:\ws\s\SKILL.md`}
	h2 := &Result{Adapter: "h2", Transport: TransportDelivered, FinalText: "a"}
	h3 := &Result{Adapter: "h3", Transport: TransportDelivered, FinalText: "b"} // no loader call
	pair := ObserveSkillPair("t", SkillPin{ID: "s"}, h3Pin, h2, h3)
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
	h3Pin := SkillPin{ID: "s", PlacedPath: `C:\ws\s\SKILL.md`}
	pair := ObserveSkillPair("t", SkillPin{ID: "s"}, h3Pin, nil, &Result{Adapter: "h3"})
	if pair.Eligible {
		t.Fatal("a pair with no H2 arm was judged eligible")
	}
	if len(pair.IneligibleReasons) == 0 {
		t.Fatal("an ineligible pair carried no reason")
	}
}

// TestSkillObservationJSONShape keeps the sheet a stable artifact.
func TestSkillObservationJSONShape(t *testing.T) {
	h3Pin := SkillPin{ID: "s", PlacedPath: `C:\ws\s\SKILL.md`, BytesSHA256: "sha256:a"}
	h2 := &Result{Adapter: "h2", Transport: TransportDelivered, FinalText: "a"}
	h3 := &Result{Adapter: "h3", Transport: TransportDelivered, FinalText: "b", ToolCalls: []ToolCallRecord{{Tool: "skill", InputJSON: `{"name":"s"}`}}}
	b, err := SkillObservationJSON([]SkillPairObservation{ObserveSkillPair("t", SkillPin{ID: "s"}, h3Pin, h2, h3)})
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

// TestObserveSkillPairRejectsH2WithPlacement is the bug the real H2/H3 run
// exposed: passing one shared pin recorded `placed=true` for the H2 arm whose
// Skill directory had been removed. Placement is per-arm.
func TestObserveSkillPairRejectsH2WithPlacement(t *testing.T) {
	h3Pin := SkillPin{ID: "s", PlacedPath: `C:\ws\s\SKILL.md`}
	h2Pin := SkillPin{ID: "s", PlacedPath: `C:\ws\s\SKILL.md`} // wrongly shared
	h2 := &Result{Adapter: "h2", Transport: TransportDelivered, FinalText: "a"}
	h3 := &Result{Adapter: "h3", Transport: TransportDelivered, FinalText: "b",
		ToolCalls: []ToolCallRecord{{Tool: "skill", InputJSON: `{"name":"s"}`}}}
	pair := ObserveSkillPair("t", h2Pin, h3Pin, h2, h3)
	if pair.Eligible {
		t.Fatal("an H2 arm with a placed Skill was judged a valid contrast")
	}
	if !containsStr(pair.IneligibleReasons, "H2 arm had the Skill placed; the pair is not a contrast") {
		t.Fatalf("reason not recorded: %v", pair.IneligibleReasons)
	}
}

// TestObserveSkillPairRejectsDifferentSkillIDs keeps a pair that names two
// different Skills from being read as a contrast of one variable.
func TestObserveSkillPairRejectsDifferentSkillIDs(t *testing.T) {
	h2Pin := SkillPin{ID: "s"}
	h3Pin := SkillPin{ID: "other", PlacedPath: `C:\ws\s\SKILL.md`}
	h2 := &Result{Adapter: "h2", Transport: TransportDelivered}
	h3 := &Result{Adapter: "h3", Transport: TransportDelivered,
		ToolCalls: []ToolCallRecord{{Tool: "skill", InputJSON: `{"name":"other"}`}}}
	pair := ObserveSkillPair("t", h2Pin, h3Pin, h2, h3)
	if pair.Eligible {
		t.Fatal("a pair naming two different Skills was judged eligible")
	}
	joined := strings.Join(pair.IneligibleReasons, " ")
	if !strings.Contains(joined, "different Skills") {
		t.Fatalf("the mismatch was not named: %v", pair.IneligibleReasons)
	}
}

// TestObserveSkillPairRejectsUnplacedH3 keeps an H3 that never placed the Skill
// from being scored as an H3.
func TestObserveSkillPairRejectsUnplacedH3(t *testing.T) {
	h2Pin := SkillPin{ID: "s"}
	h3Pin := SkillPin{ID: "s"}
	h2 := &Result{Adapter: "h2", Transport: TransportDelivered, FinalText: "a"}
	h3 := &Result{Adapter: "h3", Transport: TransportDelivered, FinalText: "b"}
	pair := ObserveSkillPair("t", h2Pin, h3Pin, h2, h3)
	if pair.Eligible {
		t.Fatal("an H3 arm that never placed the Skill was judged eligible")
	}
	if !containsStr(pair.IneligibleReasons, "H3 arm did not place the Skill") {
		t.Fatalf("reason not recorded: %v", pair.IneligibleReasons)
	}
}

// TestSkillHistoryDiscoveredIsPlacementNotLoad is the Step Code case: the harness
// reports `discovered` for every skill it listed, including ones it never
// activated. Placement must not become a load.
func TestSkillHistoryDiscoveredIsPlacementNotLoad(t *testing.T) {
	pin := SkillPin{ID: "yi-tei-modeling", PlacedPath: `C:\ws\skills\x\SKILL.md`}
	res := &Result{
		Adapter:      "step-cli",
		Observations: map[string]string{"skill-history": "discovered"},
		FinalText:    "ready",
	}
	obs := ObserveSkillUse(pin, res)
	if obs.LoadState == LoadLoaded {
		t.Fatal("`discovered` was read as a load")
	}
	if obs.LoadState != LoadNotLoaded {
		t.Fatalf("load state = %q", obs.LoadState)
	}
	if !strings.Contains(obs.Note, "placement, not a load") {
		t.Fatalf("the distinction was not named: %q", obs.Note)
	}
}

// TestSkillHistoryStrongerStateIsALoad checks the positive case: a state beyond
// discovery IS a load, and is recorded as having come from the history rather
// than from a loader tool.
func TestSkillHistoryStrongerStateIsALoad(t *testing.T) {
	pin := SkillPin{ID: "s", PlacedPath: `C:\ws\s\SKILL.md`}
	res := &Result{Adapter: "x", Observations: map[string]string{"skill-history": "discovered,activated"}}
	obs := ObserveSkillUse(pin, res)
	if obs.LoadState != LoadLoaded {
		t.Fatalf("load state = %q; an activation state should count", obs.LoadState)
	}
	if obs.LoadedVia != "skill-history" {
		t.Fatalf("loaded via = %q", obs.LoadedVia)
	}
}

// TestLoaderToolCallWinsOverHistory keeps the stronger evidence when both are present.
func TestLoaderToolCallWinsOverHistory(t *testing.T) {
	pin := SkillPin{ID: "s", PlacedPath: `C:\ws\s\SKILL.md`}
	res := &Result{
		Adapter:      "dsh-headless",
		Observations: map[string]string{"skill-history": "discovered"},
		ToolCalls:    []ToolCallRecord{{Tool: "skill", InputJSON: `{"name":"s"}`}},
	}
	obs := ObserveSkillUse(pin, res)
	if obs.LoadState != LoadLoaded || obs.LoadedVia != "skill" {
		t.Fatalf("a loader tool call was overridden by history: %+v", obs)
	}
}
