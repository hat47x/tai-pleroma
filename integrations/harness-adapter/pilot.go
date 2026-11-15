package harnessadapter

import (
	"context"
	"encoding/json"
	"fmt"
	"sort"
	"strings"
	"time"
)

// PilotOutcome is one adapter's arm in a pilot.
type PilotOutcome struct {
	// Adapter is the adapter name.
	Adapter string `json:"adapter"`
	// State is the arm's disposition. It is never "pass".
	State PilotState `json:"state"`
	// Reason is a non-secret explanation of the state.
	Reason string `json:"reason,omitempty"`
	// Availability is the probe result that decided the state.
	Availability Availability `json:"availability"`
	// Result is the adapter's result, when a run happened.
	Result *Result `json:"result,omitempty"`
	// ElapsedMS bounds the arm.
	ElapsedMS int64 `json:"elapsedMs"`
}

// PilotState is a disposition, not a verdict. There is no PASS state on purpose:
// a pilot observes, it does not qualify.
type PilotState string

const (
	// PilotNotRun means the arm was not executed.
	PilotNotRun PilotState = "not-run"
	// PilotIneligible means the adapter could not be reached, so no comparison
	// is possible for it.
	PilotIneligible PilotState = "ineligible"
	// PilotObserved means the arm ran and produced an observation.
	PilotObserved PilotState = "observed"
	// PilotErrored means the arm failed in a way that is not about reachability.
	PilotErrored PilotState = "errored"
)

// PilotReport is the whole comparison. It is the artifact a human reads to
// decide whether two harnesses were interchangeable for one Task.
type PilotReport struct {
	Contract   string `json:"contract"`
	TaskID     string `json:"taskId"`
	StartedAt  string `json:"startedAt"`
	FinishedAt string `json:"finishedAt"`
	// TaskPins is the pin set shared by every arm. Arms that could not run are
	// still recorded against the same pins.
	TaskPins Pins           `json:"taskPins"`
	Outcomes []PilotOutcome `json:"outcomes"`
	// Divergences lists the axes on which the observed arms differ. An empty
	// list means the arms agreed on the axes that were measured, not that they
	// are equivalent.
	Divergences []string `json:"divergences,omitempty"`
	// Notes carries caveats that must survive into any downstream summary.
	Notes []string `json:"notes,omitempty"`
}

// Pilot runs one Task through several adapters, probing each first.
//
// The order matters for the record but not for the claim: each arm is judged on
// its own observation. An arm whose harness is unavailable is recorded as
// ineligible, and the report never averages or backfills it.
func Pilot(ctx context.Context, adapters []Adapter, t Task, sessions map[string]*SessionRef) *PilotReport {
	if ctx == nil {
		ctx = context.Background()
	}
	rep := &PilotReport{
		Contract:  ContractVersion,
		TaskID:    t.ID,
		StartedAt: time.Now().UTC().Format(time.RFC3339),
		TaskPins:  t.Pins,
	}
	for _, a := range adapters {
		start := time.Now()
		out := PilotOutcome{Adapter: a.Name(), State: PilotNotRun}
		avail, err := a.Probe(ctx)
		out.Availability = avail
		if err != nil {
			out.State = PilotErrored
			out.Reason = "probe error: " + err.Error()
			out.ElapsedMS = time.Since(start).Milliseconds()
			rep.Outcomes = append(rep.Outcomes, out)
			continue
		}
		if !avail.Reachable {
			out.State = PilotIneligible
			out.Reason = avail.Reason
			out.ElapsedMS = time.Since(start).Milliseconds()
			rep.Outcomes = append(rep.Outcomes, out)
			continue
		}
		var session *SessionRef
		if sessions != nil {
			session = sessions[a.Name()]
		}
		res, err := a.Run(ctx, t, session)
		if err != nil {
			out.State = PilotErrored
			out.Reason = "run error: " + err.Error()
			out.ElapsedMS = time.Since(start).Milliseconds()
			rep.Outcomes = append(rep.Outcomes, out)
			continue
		}
		out.Result = res
		out.State = PilotObserved
		out.ElapsedMS = time.Since(start).Milliseconds()
		rep.Outcomes = append(rep.Outcomes, out)
	}
	rep.FinishedAt = time.Now().UTC().Format(time.RFC3339)
	rep.Divergences = Divergences(rep)
	rep.Notes = append(rep.Notes,
		"An arm is observed, not passed. No arm in this report is evidence that a harness is interchangeable with another.",
		"Session ids, tool statuses and harness exit codes are recorded separately from product acceptance and permission.",
	)
	return rep
}

// Divergences lists the measured axes on which the observed arms disagree. The
// axes are chosen so that a difference a human must see is a difference this
// function reports.
func Divergences(rep *PilotReport) []string {
	var observed []*Result
	for _, o := range rep.Outcomes {
		if o.State == PilotObserved && o.Result != nil {
			observed = append(observed, o.Result)
		}
	}
	if len(observed) < 2 {
		return nil
	}
	var out []string
	axes := []struct {
		name string
		fn   func(*Result) string
	}{
		{"transport", func(r *Result) string { return string(r.Transport) }},
		{"run", func(r *Result) string { return string(r.Run) }},
		{"exit-code", func(r *Result) string { return ExitString(r.ExitCode) }},
		{"tool-names", func(r *Result) string { return strings.Join(r.ToolNames(), "|") }},
		{"tool-count", func(r *Result) string { return fmt.Sprint(len(r.ToolCalls)) }},
		{"session-state", func(r *Result) string { return string(r.Session.State) }},
		{"receipt-state", func(r *Result) string { return string(r.Receipt.State) }},
		{"unsupported", func(r *Result) string { return UnsupportedList(r.Unsupported) }},
	}
	for _, ax := range axes {
		first := ax.fn(observed[0])
		for _, r := range observed[1:] {
			if ax.fn(r) != first {
				out = append(out, ax.name)
				break
			}
		}
	}
	sort.Strings(out)
	return out
}

// JSON renders the report as indented JSON for an evidence file.
func (rep *PilotReport) JSON() ([]byte, error) {
	return json.MarshalIndent(rep, "", "  ")
}

// Summary renders a compact table for a human or a log line.
func (rep *PilotReport) Summary() string {
	var b strings.Builder
	fmt.Fprintf(&b, "pilot task=%s contract=%s\n", rep.TaskID, rep.Contract)
	for _, o := range rep.Outcomes {
		line := fmt.Sprintf("  %-22s %-12s %s", o.Adapter, o.State, o.Reason)
		if o.Result != nil {
			line += " | " + o.Result.Summary()
		}
		b.WriteString(line + "\n")
	}
	if len(rep.Divergences) > 0 {
		fmt.Fprintf(&b, "  divergences: %s\n", strings.Join(rep.Divergences, ", "))
	} else {
		b.WriteString("  divergences: none measured\n")
	}
	return b.String()
}
