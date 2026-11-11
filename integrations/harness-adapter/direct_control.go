package harnessadapter

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"time"
)

// DirectControlAdapter is the deterministic control arm: no model, no external
// harness, no conversation. It runs the task's declared read-only product tools
// in the order the task declares them and reports the product's own exit codes
// and verdicts.
//
// It exists so the same Task can be executed with and without an LLM harness on
// identical pins. That is the HV-0 baseline arm in TAI #168's comparison design,
// and it is the only arm that can be run in CI without credentials. A result
// from this adapter says nothing about what a harness would have answered; it
// says what the product tools return when nothing interprets them.
type DirectControlAdapter struct {
	// Runner executes the product CLI. Tests substitute a fake.
	Runner Runner
	// Clock is injectable for tests.
	Clock func() time.Time
}

// NewDirectControlAdapter builds the control adapter with production defaults.
func NewDirectControlAdapter() *DirectControlAdapter {
	return &DirectControlAdapter{Runner: ProcessRunner{}, Clock: time.Now}
}

// Name implements Adapter.
func (a *DirectControlAdapter) Name() string { return "direct-control" }

// Capabilities: the control arm has no harness, so it has no session and no
// skill loader. Reporting those as unsupported is the point.
func (a *DirectControlAdapter) Capabilities() []Capability {
	return []Capability{
		CapToolInvoke, CapDiagnostics, CapEvidenceTracking,
	}
}

// Probe always succeeds: the control arm is local and needs no external
// harness. It still reports Reachable=true only because nothing external is
// involved, and the reason string says so.
func (a *DirectControlAdapter) Probe(context.Context) (Availability, error) {
	return Availability{
		Reachable: true,
		Reason:    "local deterministic control arm; no external harness involved",
		Detail:    map[string]string{"family": "direct-control"},
	}, nil
}

// Run implements Adapter.
func (a *DirectControlAdapter) Run(ctx context.Context, t Task, _ *SessionRef) (*Result, error) {
	if ctx == nil {
		ctx = context.Background()
	}
	started := a.Clock()
	res := &Result{
		Contract:  ContractVersion,
		Adapter:   a.Name(),
		Transport: TransportDelivered,
		Run:       RunUnknown,
		StartedAt: started.UTC().Format(time.RFC3339),
		Session:   SessionRef{Adapter: a.Name(), State: SessionUnknown, Note: "no harness session exists in the control arm"},
		Receipt:   Receipt{State: ReceiptNotObserved, Consumer: a.Name()},
	}
	res.Outbound = append(res.Outbound, OutboundRecord{
		Direction:   "task-text",
		BytesSHA256: DigestString(t.Prompt),
		ByteCount:   int64(len(t.Prompt)),
		Detail:      "task prompt (not sent to any model)",
	})

	var ran int
	var failures int
	for _, tool := range t.Tools {
		if len(tool.Command) == 0 {
			res.Unsupported = append(res.Unsupported, "tool:"+tool.Name+":no-command")
			continue
		}
		argv := append([]string(nil), tool.Command...)
		execRes, err := a.Runner.Exec(ctx, ExecSpec{Argv: argv, Dir: a.workDir(t), Timeout: time.Duration(t.Limits.TimeoutMS) * time.Millisecond})
		if err != nil {
			res.Transport = TransportFailed
			res.Diagnostics = append(res.Diagnostics, Diagnostic{
				Severity: "error", Code: "control-exec-failed", Message: err.Error(), Source: tool.Name,
			})
			failures++
			continue
		}
		ran++
		code := execRes.ExitCode
		rec := ToolCallRecord{
			CallID:        fmt.Sprintf("control-%s-%d", tool.Name, ran),
			Tool:          tool.Name,
			InputJSON:     "{}",
			HarnessStatus: "not-a-harness",
			ExitCode:      &code,
			ResultBytes:   int64(len(execRes.Stdout)),
			ResultText:    string(execRes.Stdout),
			Note:          "deterministic product invocation; no model involved",
		}
		verdict, diags := decodeProductEnvelope(execRes.Stdout)
		rec.ProductVerdict = verdict
		res.Diagnostics = append(res.Diagnostics, diags...)
		res.ToolCalls = append(res.ToolCalls, rec)
		res.Outbound = append(res.Outbound, OutboundRecord{
			Direction:   "argv",
			BytesSHA256: DigestString(Quote(argv)),
			ByteCount:   int64(len(Quote(argv))),
			Detail:      "product CLI invocation",
		})
		if code != 0 {
			failures++
		}
		if len(execRes.Stderr) > 0 {
			res.Diagnostics = append(res.Diagnostics, Diagnostic{
				Severity: "warning", Code: "product-stderr", Message: firstLine(execRes.Stderr), Source: tool.Name,
			})
		}
	}

	switch {
	case ran == 0 && len(t.Tools) > 0:
		res.Run = RunError
		res.Diagnostics = append(res.Diagnostics, Diagnostic{
			Severity: "error", Code: "control-nothing-ran",
			Message: "no declared tool carried a runnable command",
		})
	case failures > 0:
		res.Run = RunError
	default:
		// "completed" here means the declared invocations finished. It is not a
		// statement about the model, the business outcome or any effect.
		res.Run = RunCompleted
	}
	res.Receipt = Receipt{
		State:    ReceiptNotObserved,
		Consumer: a.Name(),
		Note:     "control arm output is local; consumer receipt is a separate observation",
	}
	res.FinishedAt = a.Clock().UTC().Format(time.RFC3339)
	return res, nil
}

// workDir picks the first allowed root as the control arm's cwd, so the control
// arm reads from the same place a harness would be confined to.
func (a *DirectControlAdapter) workDir(t Task) string {
	for _, r := range t.Pins.Roots {
		if r.Path != "" {
			return r.Path
		}
	}
	return ""
}

// decodeProductEnvelope reads a TEI-style CLI envelope. It deliberately models
// only the three fields the contract separates: operation completion, validation
// outcome, and diagnostics. Everything else is preserved as raw text.
func decodeProductEnvelope(stdout []byte) (*ProductVerdict, []Diagnostic) {
	trimmed := strings.TrimSpace(string(stdout))
	if trimmed == "" || !strings.HasPrefix(trimmed, "{") {
		return nil, nil
	}
	var env struct {
		OK     *bool `json:"ok"`
		Result *struct {
			Effect     string `json:"effect"`
			Schema     string `json:"schemaVersion"`
			Validation *struct {
				OK           bool `json:"ok"`
				ErrorCount   int  `json:"errorCount"`
				WarningCount int  `json:"warningCount"`
			} `json:"validation"`
		} `json:"result"`
		Diagnostics []struct {
			Severity string `json:"severity"`
			Code     string `json:"code"`
			Message  string `json:"message"`
			Source   string `json:"source"`
		} `json:"diagnostics"`
		Failure *struct {
			Code    string `json:"code"`
			Message string `json:"message"`
		} `json:"failure"`
	}
	if err := json.Unmarshal([]byte(trimmed), &env); err != nil {
		return nil, nil
	}
	v := &ProductVerdict{OperationCompleted: env.OK == nil || *env.OK}
	if env.Result != nil && env.Result.Validation != nil {
		passed := env.Result.Validation.OK
		v.ValidationPassed = &passed
	}
	if env.Failure != nil {
		v.FailureCode = env.Failure.Code
	}
	var diags []Diagnostic
	for _, d := range env.Diagnostics {
		diags = append(diags, Diagnostic{Severity: d.Severity, Code: d.Code, Message: d.Message, Source: d.Source})
	}
	return v, diags
}
