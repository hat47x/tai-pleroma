package harnessadapter

import (
	"encoding/json"
	"sort"
	"strings"
)

// SkillObservation is what a pilot recorded about Skill use in one arm. It is the
// input TAI #488's comparison sheet needs, and it is produced without measuring
// correctness: whether a Skill helped is a separate question from whether it
// loaded, and conflating them is the failure this file prevents.
type SkillObservation struct {
	// Arm is the adapter name.
	Arm string `json:"arm"`
	// SkillID is the Skill the Task pinned.
	SkillID string `json:"skillId"`
	// Placed is true when the adapter put the bytes somewhere the harness scans.
	Placed bool `json:"placed"`
	// PlacedBytesSHA256 digests the bytes placed.
	PlacedBytesSHA256 string `json:"placedBytesSha256,omitempty"`
	// LoadState is the observed three-valued state.
	LoadState LoadState `json:"loadState"`
	// LoadedVia names the harness tool that loaded it, when observed.
	LoadedVia string `json:"loadedVia,omitempty"`
	// ToolCallsAfterLoad counts the arm's tool calls, so a reader can see whether
	// a load was followed by any work at all.
	ToolCallsAfterLoad int `json:"toolCallsAfterLoad"`
	// AnswerPresent is whether the arm produced a final text at all. A load with
	// no answer is not evidence that the Skill helped.
	AnswerPresent bool `json:"answerPresent"`
	// Cost is the arm's own reported cost, when the harness reports one. It is
	// vendor vocabulary and is never summed across vendors.
	Cost string `json:"cost,omitempty"`
	// SkillHistory is the harness's own skill activity states, verbatim. A
	// harness that reports only `discovered` has listed the file, not loaded it.
	SkillHistory string `json:"skillHistory,omitempty"`
	// Note carries a non-secret explanation of a gap.
	Note string `json:"note,omitempty"`
}

// ObserveSkillUse derives the Skill observation for one arm's result.
//
// SkillPlacementStates are the harness-reported states a skill can be in, as
// distinct from a loader-tool call. A harness that reports `discovered` has seen
// the skill file; that is a placement observation, not a load.
const (
	// SkillHistoryDiscovered marks a skill the harness listed in its catalog.
	SkillHistoryDiscovered = "discovered"
)

// It reads only what the arm recorded. A `skill_loaded` self-report boolean is
// never consulted: the load must be visible as either a loader tool call naming
// the Skill, or a harness skill-history state that says more than `discovered`.
func ObserveSkillUse(pin SkillPin, res *Result) SkillObservation {
	obs := SkillObservation{
		SkillID:           pin.ID,
		Placed:            pin.PlacedPath != "",
		PlacedBytesSHA256: pin.BytesSHA256,
		LoadState:         LoadUnknown,
	}
	if res == nil {
		obs.Note = "the arm produced no result"
		return obs
	}
	obs.Arm = res.Adapter
	obs.AnswerPresent = strings.TrimSpace(res.FinalText) != ""
	obs.ToolCallsAfterLoad = len(res.ToolCalls)
	if res.Observations != nil {
		obs.Cost = res.Observations["total-cost-usd"]
		// Some harnesses report a skill history rather than a loader tool. A state
		// stronger than `discovered` is a load; `discovered` alone is not.
		if hist := res.Observations["skill-history"]; hist != "" {
			obs.SkillHistory = hist
			if strongerThanDiscovered(hist) {
				obs.LoadState = LoadLoaded
				obs.LoadedVia = "skill-history"
			}
		}
	}
	for _, c := range res.ToolCalls {
		if !isSkillLoadTool(c.Tool) {
			continue
		}
		var payload struct {
			Name string `json:"name"`
		}
		if json.Unmarshal([]byte(c.InputJSON), &payload) != nil || payload.Name != pin.ID {
			continue
		}
		obs.LoadState = LoadLoaded
		obs.LoadedVia = c.Tool
		return obs
	}
	if obs.LoadState == LoadLoaded {
		return obs
	}
	if obs.SkillHistory != "" {
		// The harness saw the skill file but reported nothing stronger.
		obs.LoadState = LoadNotLoaded
		obs.Note = "the harness reported skill-history " + obs.SkillHistory + ", which is placement, not a load"
		return obs
	}
	if pin.PlacedPath != "" {
		obs.LoadState = LoadNotLoaded
		obs.Note = "the Skill was placed but no loader tool call named it"
	} else {
		obs.Note = "the adapter did not place the Skill for this arm"
	}
	return obs
}

// strongerThanDiscovered reports whether a harness skill-history state asserts
// more than "the file was listed". Only an explicit activation counts.
func strongerThanDiscovered(hist string) bool {
	for _, state := range strings.Split(hist, ",") {
		switch strings.TrimSpace(state) {
		case "", SkillHistoryDiscovered:
			continue
		default:
			return true
		}
	}
	return false
}

// SkillPairObservation is one paired trial: the same Task with the Skill placed
// (H3) and without it (H2).
//
// The pair is the unit TAI #168 compares. A pair is "eligible" only when both
// arms ran and only the Skill placement differed; a pair where H3 failed to load
// is not a pair where the Skill had no effect, and the report says which.
type SkillPairObservation struct {
	TaskID string           `json:"taskId"`
	H2     SkillObservation `json:"h2"`
	H3     SkillObservation `json:"h3"`
	// Eligible is true only when both arms ran, H2 did not load the Skill, and H3
	// did.
	Eligible bool `json:"eligible"`
	// IneligibleReasons names every condition that kept the pair from being
	// comparable. It is never empty when Eligible is false.
	IneligibleReasons []string `json:"ineligibleReasons,omitempty"`
	// SkillEffect is NOT a verdict. It records whether the arms differed on any
	// measured axis while leaving the question "did the Skill help?" to the
	// independent Expected scoring that this package does not perform.
	SkillEffect string `json:"skillEffect"`
}

// ObserveSkillPair turns two arm results into one pair observation.
//
// Each arm carries its OWN pin, because the two arms place different bytes: H3
// places the Skill and H2 does not. An earlier version took one shared pin and
// recorded `placed=true` for an arm whose Skill directory had been removed —
// exactly the misreport this contract exists to prevent. It was caught by the
// real H2/H3 run, not by the contract tests.
func ObserveSkillPair(taskID string, h2Pin, h3Pin SkillPin, h2, h3 *Result) SkillPairObservation {
	pair := SkillPairObservation{
		TaskID:      taskID,
		H2:          ObserveSkillUse(h2Pin, h2),
		H3:          ObserveSkillUse(h3Pin, h3),
		SkillEffect: "not-measured",
	}
	var reasons []string
	if h2 == nil || h2.Adapter == "" {
		reasons = append(reasons, "H2 arm did not run")
	}
	if h3 == nil || h3.Adapter == "" {
		reasons = append(reasons, "H3 arm did not run")
	}
	// The two arms must be the same Skill identity; otherwise they are not a
	// contrast of one variable.
	if h2Pin.ID != h3Pin.ID {
		reasons = append(reasons, "the arms name different Skills ("+h2Pin.ID+" vs "+h3Pin.ID+")")
	}
	// The H2 arm must not have placed the Skill at all, and must not have loaded
	// it. An H2 with either is an H3 under the wrong label.
	if pair.H2.Placed {
		reasons = append(reasons, "H2 arm had the Skill placed; the pair is not a contrast")
	}
	if pair.H2.LoadState == LoadLoaded {
		reasons = append(reasons, "H2 arm loaded the Skill; the pair is not a contrast")
	}
	// The H3 arm must have placed it and loaded it. A failed load is
	// `not-loaded`, not "no effect".
	if !pair.H3.Placed {
		reasons = append(reasons, "H3 arm did not place the Skill")
	}
	if pair.H3.LoadState != LoadLoaded {
		reasons = append(reasons, "H3 arm did not load the Skill ("+string(pair.H3.LoadState)+")")
	}
	if h2 != nil && h3 != nil {
		// Only the Skill placement may differ on these axes.
		if string(h2.Transport) != string(h3.Transport) {
			reasons = append(reasons, "the arms differ on transport")
		}
	}
	pair.IneligibleReasons = reasons
	pair.Eligible = len(reasons) == 0
	if pair.Eligible {
		// Even an eligible pair does not yield a Skill verdict here: the accuracy
		// comparison belongs to the independent Expected at TAI #488.
		pair.SkillEffect = "eligibility-confirmed; accuracy not measured"
	}
	return pair
}

// SkillObservationJSON renders the pair for the TAI #488 comparison sheet.
func SkillObservationJSON(pairs []SkillPairObservation) ([]byte, error) {
	sort.Slice(pairs, func(i, j int) bool { return pairs[i].TaskID < pairs[j].TaskID })
	return json.MarshalIndent(pairs, "", "  ")
}
