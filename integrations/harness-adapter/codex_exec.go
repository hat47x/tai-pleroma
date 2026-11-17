package harnessadapter

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"runtime"
	"strings"
	"time"
)

// CodexExecAdapter is a bounded, one-turn adapter for Codex's non-interactive
// JSONL protocol. It does not implement the bidirectional App Server protocol,
// resume persistent sessions, install MCP servers, or attest sandbox isolation.
//
// Source inspected: openai/codex at 640b86dc879ceaaa126cdf183b417731e291f476,
// codex-rs/exec/src/{cli.rs,exec_events.rs,lib.rs}. The actual executable and
// authentication must be qualified separately at the selected version.
type CodexExecAdapter struct {
	CLI          string
	WorkDir      string
	Timeout      time.Duration
	Runner       Runner
	PathResolver PathResolver
	Clock        func() time.Time
}

func NewCodexExecAdapter(workDir string) *CodexExecAdapter {
	return &CodexExecAdapter{
		CLI:          "codex",
		WorkDir:      workDir,
		Timeout:      10 * time.Minute,
		Runner:       ProcessRunner{},
		PathResolver: OSPathResolver{},
		Clock:        time.Now,
	}
}

func (a *CodexExecAdapter) Name() string { return "codex-exec" }

// A thread is created for this invocation, but --ephemeral makes its ID
// unsuitable as evidence of persistence or later resumability.
func (a *CodexExecAdapter) Capabilities() []Capability {
	return []Capability{CapSessionCreate, CapDiagnostics, CapEvidenceTracking}
}

func (a *CodexExecAdapter) cli() string {
	if a.CLI != "" {
		return a.CLI
	}
	return "codex"
}

func (a *CodexExecAdapter) Probe(ctx context.Context) (Availability, error) {
	exe := a.cli()
	path, err := a.PathResolver.LookPath(exe)
	if err != nil {
		return Availability{Reachable: false, Reason: "Codex executable not found",
			Detail: map[string]string{"family": a.Name(), "probe": "lookpath"}}, nil
	}
	r, err := a.Runner.Exec(ctx, ExecSpec{Argv: []string{path, "--version"}, Timeout: time.Minute})
	if err != nil || r.LaunchError != "" || r.ExitCode != 0 {
		return Availability{Reachable: false, Reason: "Codex version probe failed",
			Detail: map[string]string{"family": a.Name(), "probe": "version"}}, nil
	}
	return Availability{Reachable: true,
		Reason: "version probe succeeded; authentication, sandbox and tool access remain unverified",
		Detail: map[string]string{"family": a.Name(), "probe": "version", "exePath": path,
			"version": strings.TrimSpace(string(r.Stdout)), "platform": runtime.GOOS}}, nil
}

// buildArgv keeps the task text off argv. '-' forces Codex to consume stdin.
// Never add --skip-git-repo-check, --add-dir, --trust, or unsafe bypass flags.
func (a *CodexExecAdapter) buildArgv(t Task) []string {
	argv := []string{a.cli(), "exec", "--json", "--ephemeral", "--sandbox", "read-only"}
	if t.Pins.Model.Model != "" {
		argv = append(argv, "--model", t.Pins.Model.Model)
	}
	return append(argv, "-")
}

func (a *CodexExecAdapter) Run(ctx context.Context, t Task, session *SessionRef) (*Result, error) {
	now := a.Clock
	if now == nil {
		now = time.Now
	}
	res := &Result{
		Contract: ContractVersion, Adapter: a.Name(), Transport: TransportNotAttempted,
		Run: RunUnknown, Session: SessionRef{Adapter: a.Name(), State: SessionUnknown,
			RequestedID: requestedID(session)},
		Receipt: Receipt{State: ReceiptNotObserved}, StartedAt: now().UTC().Format(time.RFC3339),
		Observations: map[string]string{"sandbox-declaration": "read-only; not independently enforced",
			"session-storage": "ephemeral", "model-route": "not-observed"},
	}
	defer func() { res.FinishedAt = now().UTC().Format(time.RFC3339) }()

	// A dropped ToolOffer, ContextRef or Skill silently changes the Task. C1
	// has no verified Codex tool/skill configuration mechanism; fail closed.
	switch {
	case requestedID(session) != "":
		res.Unsupported = []string{"session:resume"}
	case len(t.Tools) > 0:
		res.Unsupported = []string{"tool:offer-binding"}
	case len(t.Skills) > 0 || len(t.Pins.Skills) > 0:
		res.Unsupported = []string{"skill:placement"}
	case len(t.ContextRefs) > 0:
		res.Unsupported = []string{"context:projection"}
	case t.Prompt == "":
		res.Unsupported = []string{"task:empty-prompt"}
	}
	if len(res.Unsupported) != 0 {
		res.Diagnostics = append(res.Diagnostics, Diagnostic{
			Severity: "warning", Code: "codex-exec-unsupported",
			Message: strings.Join(res.Unsupported, ", "), Source: a.Name(),
		})
		return res, nil
	}
	dir := a.WorkDir
	if dir == "" {
		dir = t.WorkDirHint()
	}
	if dir == "" {
		res.Unsupported = []string{"workspace:unqualified"}
		return res, nil
	}
	argv := a.buildArgv(t)
	res.Outbound = append(res.Outbound,
		OutboundRecord{Direction: "argv", BytesSHA256: DigestString(Quote(argv)),
			ByteCount: int64(len(Quote(argv))), Detail: "codex exec one-turn invocation"},
		OutboundRecord{Direction: "stdin", BytesSHA256: DigestString(t.Prompt),
			ByteCount: int64(len(t.Prompt)), Detail: "task prompt (not in argv)"},
	)
	runner := a.Runner
	if runner == nil {
		runner = ProcessRunner{}
	}
	execRes, err := runner.Exec(ctx, ExecSpec{
		Argv: argv, Dir: dir, Stdin: []byte(t.Prompt), Timeout: a.Timeout,
	})
	if err != nil || execRes.LaunchError != "" {
		res.Transport = TransportFailed
		res.Run = RunError
		res.Diagnostics = append(res.Diagnostics, Diagnostic{Severity: "error",
			Code: "codex-exec-launch-failed", Message: "process launch failed", Source: a.Name()})
		return res, nil
	}
	res.Transport = TransportDelivered
	exit := execRes.ExitCode
	res.ExitCode = &exit
	if len(execRes.Stderr) > 0 {
		res.Outbound = append(res.Outbound, OutboundRecord{Direction: "stderr",
			BytesSHA256: DigestBytes(execRes.Stderr), ByteCount: int64(len(execRes.Stderr)),
			Detail: "Codex diagnostics; raw content not recorded by adapter"})
		res.Diagnostics = append(res.Diagnostics, Diagnostic{Severity: "warning",
			Code: "codex-exec-stderr-present", Source: a.Name()})
	}
	if t.Limits.MaxOutBytes > 0 && int64(len(execRes.Stdout)) > t.Limits.MaxOutBytes {
		res.Diagnostics = append(res.Diagnostics, Diagnostic{Severity: "error",
			Code: "codex-exec-output-limit", Source: a.Name()})
		res.Reason = "output-limit"
		return res, nil
	}
	stream, parseErr := ParseCodexExecJSONL(execRes.Stdout)
	res.ToolCalls = stream.ToolCalls
	res.FinalText = stream.FinalText
	res.Reason = stream.Terminal
	res.Observations["unrecognized-events"] = fmt.Sprint(stream.UnknownEvents)
	res.Observations["tool-items-unfinished"] = fmt.Sprint(stream.UnfinishedTools)
	if stream.ThreadID != "" {
		res.Session.ExternalID = stream.ThreadID
		res.Session.State = SessionCreated
		res.Session.CWD = dir // effective process cwd, NOT an upstream reported field
	}
	if parseErr != nil {
		res.Diagnostics = append(res.Diagnostics, Diagnostic{Severity: "error",
			Code: "codex-exec-invalid-jsonl", Message: parseErr.Error(), Source: a.Name()})
	}
	switch {
	case parseErr != nil || stream.UnfinishedTools > 0 || stream.Terminal == "" ||
		!stream.TurnStarted || stream.ThreadID == "":
		res.Run = RunUnknown
	case stream.Terminal == "turn.failed" || stream.Terminal == "error" || exit != 0:
		res.Run = RunError
	case stream.Terminal == "turn.completed" && exit == 0:
		res.Run = RunCompleted
	default:
		res.Run = RunUnknown
	}
	return res, nil
}

// CodexExecStream is an observation of the JSONL emitted by 'codex exec --json',
// not the durable conversation history and not a Product receipt.
type CodexExecStream struct {
	ThreadID        string
	TurnStarted     bool
	Terminal        string
	FinalText       string
	ToolCalls       []ToolCallRecord
	UnknownEvents   int
	UnfinishedTools int
}

// ParseCodexExecJSONL decodes complete lines and distinguishes terminal turn
// events from tool-item status. Unknown event types are counted, not promoted.
// A truncated final JSON line is rejected even if an earlier item looked good.
func ParseCodexExecJSONL(raw []byte) (CodexExecStream, error) {
	var result CodexExecStream
	scanner := bufio.NewScanner(bytes.NewReader(raw))
	scanner.Buffer(make([]byte, 4096), 16<<20)
	pending := map[string]bool{}
	for line := 1; scanner.Scan(); line++ {
		b := bytes.TrimSpace(scanner.Bytes())
		if len(b) == 0 {
			continue
		}
		var ev struct {
			Type     string `json:"type"`
			ThreadID string `json:"thread_id"`
			Item     struct {
				ID               string          `json:"id"`
				Type             string          `json:"type"`
				Text             string          `json:"text"`
				Command          string          `json:"command"`
				AggregatedOutput string          `json:"aggregated_output"`
				ExitCode         *int            `json:"exit_code"`
				Status           string          `json:"status"`
				Server           string          `json:"server"`
				Tool             string          `json:"tool"`
				Arguments        json.RawMessage `json:"arguments"`
				Result           json.RawMessage `json:"result"`
				Error            json.RawMessage `json:"error"`
			} `json:"item"`
		}
		if err := json.Unmarshal(b, &ev); err != nil {
			return result, fmt.Errorf("line %d is not complete JSON", line)
		}
		switch ev.Type {
		case "thread.started":
			if ev.ThreadID == "" || (result.ThreadID != "" && result.ThreadID != ev.ThreadID) {
				return result, fmt.Errorf("line %d has missing or conflicting thread id", line)
			}
			result.ThreadID = ev.ThreadID
		case "turn.started":
			if result.TurnStarted {
				return result, fmt.Errorf("line %d starts an additional turn", line)
			}
			result.TurnStarted = true
		case "turn.completed", "turn.failed", "error":
			if result.Terminal != "" {
				return result, fmt.Errorf("line %d adds a second terminal event", line)
			}
			result.Terminal = ev.Type
		case "item.started":
			if ev.Item.ID != "" && (ev.Item.Type == "mcp_tool_call" || ev.Item.Type == "command_execution") {
				pending[ev.Item.ID] = true
			}
		case "item.completed":
			if ev.Item.ID != "" {
				delete(pending, ev.Item.ID)
			}
			switch ev.Item.Type {
			case "agent_message":
				result.FinalText = ev.Item.Text
			case "mcp_tool_call":
				if ev.Item.ID == "" || ev.Item.Server == "" || ev.Item.Tool == "" {
					return result, fmt.Errorf("line %d has incomplete MCP tool identity", line)
				}
				call := ToolCallRecord{CallID: ev.Item.ID, Tool: "mcp__" + ev.Item.Server + "__" + ev.Item.Tool,
					InputJSON: string(ev.Item.Arguments), HarnessStatus: ev.Item.Status}
				if len(ev.Item.Result) > 0 && string(ev.Item.Result) != "null" {
					call.ResultText = string(ev.Item.Result)
					call.ResultBytes = int64(len(ev.Item.Result))
				} else if ev.Item.Status == "completed" {
					call.Note = "result-body-not-observed"
				}
				result.ToolCalls = append(result.ToolCalls, call)
			case "command_execution":
				if ev.Item.ID == "" {
					return result, fmt.Errorf("line %d has missing command item id", line)
				}
				call := ToolCallRecord{CallID: ev.Item.ID, Tool: "run_command",
					HarnessStatus: ev.Item.Status, ResultText: ev.Item.AggregatedOutput,
					ResultBytes: int64(len(ev.Item.AggregatedOutput)), ExitCode: ev.Item.ExitCode}
				if ev.Item.Command != "" {
					encoded, _ := json.Marshal(map[string]string{"command": ev.Item.Command})
					call.InputJSON = string(encoded)
				}
				result.ToolCalls = append(result.ToolCalls, call)
			}
		case "item.updated":
			// A partial item does not prove a completed Tool result.
		default:
			result.UnknownEvents++
		}
	}
	if err := scanner.Err(); err != nil {
		return result, fmt.Errorf("JSONL line exceeds parser limit or cannot be read")
	}
	result.UnfinishedTools = len(pending)
	return result, nil
}
