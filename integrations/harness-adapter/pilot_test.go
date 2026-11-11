package harnessadapter

import (
	"context"
	"strings"
	"testing"
)

// newPilotTask builds one pinned Task used by the pilot tests.
func newPilotTask() Task {
	return Task{
		ID:     "pilot-tei-read-only",
		Prompt: "Read the sales.order model in the pinned workspace and report the attribute that holds the order total.",
		Pins: Pins{
			Source:  SourcePin{Repo: "tei-platform", Revision: "50ebf8014340fd1906f6b35cfa30173e0ee2fc6c", ResolvedPath: `C:\ws`, BytesSHA256: "sha256:src"},
			Model:   ModelPin{Provider: "deepseek-official", Model: "deepseek-flash", Route: "official-api"},
			Harness: HarnessPin{Family: "dsh", Version: "0.2.2-rc.1", Profile: "headless"},
			Roots:   []RootPin{{Logical: "tei-workspace", Path: `C:\ws`, Access: "read-only"}},
			Skills:  []SkillPin{{ID: "yi-tei-modeling", PlacedPath: `C:\ws\.dsh\skills\yi-tei-modeling\SKILL.md`, BytesSHA256: "sha256:skill"}},
			ToolSchemas: []ToolSchemaPin{
				{Name: "tei.model-catalog", Advertised: true, Invoked: true, CallCount: 1},
				{Name: "tei.validate", Advertised: true, Invoked: false},
			},
		},
		Tools: []ToolOffer{{
			Name: "tei.model-catalog", ReadOnly: true, AllowedRoots: []string{"tei-workspace"},
			Command: []string{"tei", "model", "catalog", "-workspace", `C:\ws`},
		}},
	}
}

// TestPilotSameTaskAcrossAdapters is the interchangeability check the pilot
// exists for: one Task, several adapters, one report.
func TestPilotSameTaskAcrossAdapters(t *testing.T) {
	scripted := &ScriptedAdapter{
		Family:    "codex",
		Reachable: true,
		Stream: []byte(
			`{"type":"session","sessionId":"session-a","cwd":"C:\\ws"}` + "\n" +
				`{"type":"tool_call","callId":"c1","tool":"shell","input":{"command":"tei model catalog"}}` + "\n" +
				`{"type":"tool_result","callId":"c1","status":"completed","result":"ok"}` + "\n" +
				`{"type":"final","sessionId":"session-a","reason":{"kind":"completed"},"text":"total is std.money"}` + "\n"),
		ExitCode: 0,
	}
	direct := NewDirectControlAdapter()
	direct.Runner = &FakeRunner{Script: []FakeStep{
		{Match: "tei", Result: ExecResult{ExitCode: 0, Stdout: []byte(`{"ok":true}`)}},
	}}

	rep := Pilot(context.Background(), []Adapter{scripted, direct}, newPilotTask(), nil)
	if rep.TaskID != "pilot-tei-read-only" {
		t.Fatalf("task id = %q", rep.TaskID)
	}
	if len(rep.Outcomes) != 2 {
		t.Fatalf("expected 2 arms, got %d", len(rep.Outcomes))
	}
	for _, o := range rep.Outcomes {
		if o.State != PilotObserved {
			t.Fatalf("arm %s state = %s (%s)", o.Adapter, o.State, o.Reason)
		}
	}
	// The report must carry the shared pins so a reader can see every arm was
	// judged against the same source revision and model route.
	if rep.TaskPins.Source.Revision != "50ebf8014340fd1906f6b35cfa30173e0ee2fc6c" {
		t.Fatalf("source pin lost: %+v", rep.TaskPins.Source)
	}
	if rep.TaskPins.Model.Model != "deepseek-flash" {
		t.Fatalf("model pin lost: %+v", rep.TaskPins.Model)
	}
	// Divergence is expected here: the two arms are different things. The point
	// is that the divergence is named, not hidden.
	if len(rep.Divergences) == 0 {
		t.Fatal("two structurally different arms reported no divergence")
	}
	if !containsStr(rep.Divergences, "run") && !containsStr(rep.Divergences, "tool-names") {
		t.Fatalf("divergences do not name a meaningful axis: %v", rep.Divergences)
	}
	for _, n := range rep.Notes {
		if strings.Contains(n, "PASS") {
			t.Fatalf("report note claims a verdict: %q", n)
		}
	}
}

// TestPilotUnreachableHarnessIsIneligibleNotPassed is the rule that a missing
// harness is recorded as ineligible and never backfilled.
func TestPilotUnreachableHarnessIsIneligibleNotPassed(t *testing.T) {
	dsh := NewDSHHeadlessAdapter("headless", `C:\ws`)
	dsh.PathResolver = FakePathResolver{Paths: map[string]string{}}
	direct := NewDirectControlAdapter()
	direct.Runner = &FakeRunner{Script: []FakeStep{
		{Match: "tei", Result: ExecResult{ExitCode: 0, Stdout: []byte(`{"ok":true}`)}},
	}}
	rep := Pilot(context.Background(), []Adapter{dsh, direct}, newPilotTask(), nil)
	byName := map[string]PilotOutcome{}
	for _, o := range rep.Outcomes {
		byName[o.Adapter] = o
	}
	if byName["dsh-headless"].State != PilotIneligible {
		t.Fatalf("unreachable harness state = %s", byName["dsh-headless"].State)
	}
	if byName["dsh-headless"].Result != nil {
		t.Fatal("an ineligible arm produced a result")
	}
	if byName["direct-control"].State != PilotObserved {
		t.Fatalf("control arm state = %s", byName["direct-control"].State)
	}
	// Divergences must be computed over observed arms only.
	if len(rep.Divergences) != 0 {
		t.Fatalf("divergence computed with an ineligible arm: %v", rep.Divergences)
	}
}

// TestPilotNoVerdictStates asserts the closed disposition set has no PASS.
func TestPilotNoVerdictStates(t *testing.T) {
	for _, s := range []PilotState{PilotNotRun, PilotIneligible, PilotObserved, PilotErrored} {
		if strings.Contains(string(s), "pass") || strings.Contains(string(s), "fail") {
			t.Fatalf("disposition %q reads as a verdict", s)
		}
	}
}

// TestPilotSummaryIsReadable keeps the human-facing table stable enough to paste
// into a PR body.
func TestPilotSummaryIsReadable(t *testing.T) {
	scripted := &ScriptedAdapter{Family: "claude-code", Reachable: true, Stream: []byte(
		`{"type":"final","sessionId":"s","reason":{"kind":"completed"},"text":"t"}` + "\n"), ExitCode: 0}
	rep := Pilot(context.Background(), []Adapter{scripted}, newPilotTask(), nil)
	s := rep.Summary()
	for _, want := range []string{"pilot task=pilot-tei-read-only", "scripted-claude-code", "observed"} {
		if !strings.Contains(s, want) {
			t.Fatalf("summary missing %q:\n%s", want, s)
		}
	}
}

// TestDivergenceAxesAreClosed documents the measured axes so adding one is a
// deliberate act.
func TestDivergenceAxesAreClosed(t *testing.T) {
	rep := &PilotReport{Outcomes: []PilotOutcome{
		{State: PilotObserved, Result: &Result{Transport: TransportDelivered, Run: RunCompleted}},
		{State: PilotObserved, Result: &Result{Transport: TransportDelivered, Run: RunAborted}},
	}}
	got := Divergences(rep)
	if len(got) != 1 || got[0] != "run" {
		t.Fatalf("divergences = %v, want [run]", got)
	}
}
