package harnessadapter

import (
	"context"
	"fmt"
	"time"
)

// ScriptedAdapter is a contract-test double for a generic external harness. It
// replays a canned NDJSON-ish stream through the same decoding path a real
// adapter uses, so contract tests exercise the adapter's interpretation of
// harness events without any harness being installed.
//
// It is not a product, not a reference implementation of any vendor, and must
// never be used to claim a harness works. Its only purpose is to make the
// adapter-only contract tests possible and honest.
type ScriptedAdapter struct {
	// Family is the harness family this double stands in for.
	Family string
	// Stream is the canned stdout.
	Stream []byte
	// Stderr is the canned stderr.
	Stderr []byte
	// ExitCode is the canned process exit.
	ExitCode int
	// LaunchError, when non-empty, simulates a binary that cannot start.
	LaunchError string
	// ExecErr, when non-nil, makes the runner fail outright.
	ExecErr error
	// Reachable controls Probe's answer. Default false so a test must opt in.
	Reachable bool

	Runner Runner
	Clock  func() time.Time
}

// Name implements Adapter.
func (a *ScriptedAdapter) Name() string {
	if a.Family == "" {
		return "scripted"
	}
	return "scripted-" + a.Family
}

// Capabilities mirrors the DSH set so the comparison code sees a full arm.
func (a *ScriptedAdapter) Capabilities() []Capability {
	return []Capability{
		CapSessionCreate, CapSessionResume, CapContextProject, CapToolInvoke,
		CapSkillDiscover, CapSkillLoad, CapResultReceipt, CapDiagnostics,
		CapEvidenceTracking,
	}
}

// Probe implements Adapter.
func (a *ScriptedAdapter) Probe(context.Context) (Availability, error) {
	return Availability{
		Reachable: a.Reachable,
		Reason:    fmt.Sprintf("scripted double; reachable=%v", a.Reachable),
		Detail:    map[string]string{"family": a.Family, "double": "true"},
	}, nil
}

// Run implements Adapter by feeding the canned stream through the shared
// decoder.
func (a *ScriptedAdapter) Run(_ context.Context, t Task, session *SessionRef) (*Result, error) {
	if a.Clock == nil {
		a.Clock = time.Now
	}
	started := a.Clock()
	res := &Result{
		Contract:  ContractVersion,
		Adapter:   a.Name(),
		Transport: TransportNotAttempted,
		Run:       RunUnknown,
		StartedAt: started.UTC().Format(time.RFC3339),
		Session:   SessionRef{Adapter: a.Name(), State: SessionUnknown},
		Receipt:   Receipt{State: ReceiptNotObserved, Consumer: a.Name()},
	}
	if a.ExecErr != nil {
		res.Transport = TransportFailed
		res.Diagnostics = append(res.Diagnostics, Diagnostic{
			Severity: "error", Code: "double-exec-failed", Message: a.ExecErr.Error(),
		})
		res.FinishedAt = a.Clock().UTC().Format(time.RFC3339)
		return res, nil
	}
	if a.LaunchError != "" {
		res.Transport = TransportFailed
		res.Run = RunError
		res.Diagnostics = append(res.Diagnostics, Diagnostic{
			Severity: "error", Code: "double-launch-failed", Message: a.LaunchError,
		})
		res.FinishedAt = a.Clock().UTC().Format(time.RFC3339)
		return res, nil
	}
	res.Transport = TransportDelivered
	code := a.ExitCode
	res.ExitCode = &code
	stream, err := ParseDSHJSONStream(a.Stream)
	if err != nil {
		res.Run = RunUnknown
		res.Diagnostics = append(res.Diagnostics, Diagnostic{
			Severity: "error", Code: "stream-unparseable", Message: err.Error(),
		})
	} else {
		res.Session = stream.Session
		res.Session.Adapter = a.Name()
		res.ToolCalls = stream.ToolCalls
		res.FinalText = stream.FinalText
		res.Reason = stream.FinalReason
		switch stream.FinalReason {
		case "completed":
			res.Run = RunCompleted
		case "aborted", "user":
			res.Run = RunAborted
		default:
			res.Run = RunError
		}
		if stream.ErrorMessage != "" {
			res.Diagnostics = append(res.Diagnostics, Diagnostic{
				Severity: "error", Code: "harness-error-event", Message: stream.ErrorMessage,
			})
		}
	}
	res.FinishedAt = a.Clock().UTC().Format(time.RFC3339)
	return res, nil
}
