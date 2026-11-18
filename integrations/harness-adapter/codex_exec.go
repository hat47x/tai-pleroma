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
	CLI             string
	ExpectedVersion string // exact `codex --version` output; empty means unqualified
	WorkDir         string
	Timeout         time.Duration
	Runner          Runner
	PathResolver    PathResolver
	Clock           func() time.Time
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
	version := strings.TrimSpace(string(r.Stdout))
	if a.ExpectedVersion != "" && version != a.ExpectedVersion {
		return Availability{Reachable: false,
			Reason: "Codex version changed since the caller's explicit pin",
			Detail: map[string]string{"family": a.Name(), "probe": "version", "version": version,
				"expectedVersion": a.ExpectedVersion}}, nil
	}
	return Availability{Reachable: true,
		Reason: "version probe succeeded; authentication, sandbox and tool access remain unverified",
		Detail: map[string]string{"family": a.Name(), "probe": "version", "exePath": path,
			"version": version, "platform": runtime.GOOS}}, nil
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
	case len(t.Tools) > 0 || len(t.Pins.ToolSchemas) > 0:
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
	// A caller that pins a Codex version must not silently run an upgraded
	// binary. Pilot also probes, but direct Run callers require this check.
	// The version check is not an OS binary hash or a TOCTOU-safe file lock.
	if a.ExpectedVersion != "" {
		availability, err := a.Probe(ctx)
		if err != nil || !availability.Reachable {
			res.Unsupported = []string{"harness:version-not-qualified"}
			res.Diagnostics = append(res.Diagnostics, Diagnostic{Severity: "warning",
				Code: "codex-exec-version-not-qualified", Source: a.Name()})
			return res, nil
		}
		res.Observations["codex-cli-version"] = availability.Detail["version"]
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
	res.Observations["unrecognized-control-events"] = fmt.Sprint(stream.UnknownControlEvents)
	res.Observations["tool-items-unfinished"] = fmt.Sprint(stream.UnfinishedTools)
	res.Observations["tool-results-missing"] = fmt.Sprint(stream.MissingToolBodies)
	res.Observations["command-exits-missing"] = fmt.Sprint(stream.MissingCommandExits)
	res.Observations["file-change-events"] = fmt.Sprint(stream.FileChangeEvents)
	res.Observations["model-reroute-events"] = fmt.Sprint(stream.ModelReroutes)
	// Each marker is an observation, never a Product permission or effect verdict.
	if stream.FileChangeEvents > 0 {
		res.Diagnostics = append(res.Diagnostics, Diagnostic{Severity: "warning",
			Code: "codex-exec-file-change-observed", Source: a.Name()})
	}
	if stream.ModelReroutes > 0 {
		res.Diagnostics = append(res.Diagnostics, Diagnostic{Severity: "warning",
			Code: "codex-exec-model-rerouted", Source: a.Name()})
	}
	if stream.MissingToolBodies > 0 || stream.MissingCommandExits > 0 {
		res.Diagnostics = append(res.Diagnostics, Diagnostic{Severity: "warning",
			Code: "codex-exec-tool-reply-incomplete", Source: a.Name()})
	}
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
	case parseErr != nil || stream.UnknownControlEvents > 0 || stream.UnfinishedTools > 0 || stream.MissingToolBodies > 0 ||
		stream.MissingCommandExits > 0 || stream.FileChangeEvents > 0 || stream.ModelReroutes > 0 || stream.Terminal == "" ||
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
	ThreadID             string
	TurnStarted          bool
	Terminal             string
	FinalText            string
	ToolCalls            []ToolCallRecord
	UnknownEvents        int
	UnknownControlEvents int
	UnfinishedTools      int
	MissingToolBodies    int
	MissingCommandExits  int
	FileChangeEvents     int
	ModelReroutes        int
}

// ParseCodexExecJSONL decodes complete lines and distinguishes terminal turn
// events from tool-item status. Unknown event types are counted, not promoted.
// A truncated final JSON line is rejected even if an earlier item looked good.
func ParseCodexExecJSONL(raw []byte) (CodexExecStream, error) {
	var result CodexExecStream
	scanner := bufio.NewScanner(bytes.NewReader(raw))
	scanner.Buffer(make([]byte, 4096), 16<<20)
	// An item id identifies one tool lifecycle. We never invent a missing
	// start, turn boundary or final reply for a completed-only tool item.
	type toolStart struct {
		kind, server, tool, command string
	}
	pending := map[string]toolStart{}
	seenToolIDs := map[string]bool{}
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
				Message          string          `json:"message"`
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
		// A new event after terminal indicates that the selected Codex version
		// does not obey the single-turn wire sequence this adapter understands.
		if result.Terminal != "" {
			return result, fmt.Errorf("line %d arrives after terminal event", line)
		}
		switch ev.Type {
		case "thread.started":
			if result.ThreadID != "" || result.TurnStarted || ev.ThreadID == "" {
				return result, fmt.Errorf("line %d duplicates or misorders thread start", line)
			}
			result.ThreadID = ev.ThreadID
		case "turn.started":
			if result.ThreadID == "" || result.TurnStarted {
				return result, fmt.Errorf("line %d starts a turn without a single thread", line)
			}
			result.TurnStarted = true
		case "turn.completed", "turn.failed":
			if !result.TurnStarted {
				return result, fmt.Errorf("line %d ends a turn that never started", line)
			}
			result.Terminal = ev.Type
		case "error":
			result.Terminal = ev.Type
		case "item.started":
			if !result.TurnStarted {
				return result, fmt.Errorf("line %d has an item outside the turn", line)
			}
			if ev.Item.Type == "mcp_tool_call" || ev.Item.Type == "command_execution" {
				if ev.Item.ID == "" || seenToolIDs[ev.Item.ID] {
					return result, fmt.Errorf("line %d starts a tool with a missing or reused id", line)
				}
				if ev.Item.Type == "mcp_tool_call" && (ev.Item.Server == "" || ev.Item.Tool == "") {
					return result, fmt.Errorf("line %d starts a tool without server and tool identity", line)
				}
				seenToolIDs[ev.Item.ID] = true
				pending[ev.Item.ID] = toolStart{
					kind: ev.Item.Type, server: ev.Item.Server, tool: ev.Item.Tool, command: ev.Item.Command,
				}
			}
		case "item.updated":
			if ev.Item.Type == "mcp_tool_call" || ev.Item.Type == "command_execution" {
				start, ok := pending[ev.Item.ID]
				if !ok || start.kind != ev.Item.Type ||
					(start.kind == "mcp_tool_call" && (start.server != ev.Item.Server || start.tool != ev.Item.Tool)) ||
					(start.kind == "command_execution" && start.command != "" && ev.Item.Command != "" && start.command != ev.Item.Command) {
					return result, fmt.Errorf("line %d updates a tool without matching start and identity", line)
				}
			}
		case "item.completed":
			if !result.TurnStarted {
				return result, fmt.Errorf("line %d completes an item outside the turn", line)
			}
			switch ev.Item.Type {
			case "agent_message":
				result.FinalText = ev.Item.Text
			case "error":
				// The pinned Codex JSONL renderer maps ModelRerouted into an
				// error item containing this prefix. It is not proof of the pinned
				// model's execution, even when the turn later completes normally.
				if strings.HasPrefix(ev.Item.Message, "model rerouted:") {
					result.ModelReroutes++
				}
			case "mcp_tool_call", "command_execution":
				start, ok := pending[ev.Item.ID]
				if !ok || start.kind != ev.Item.Type {
					return result, fmt.Errorf("line %d completes a tool without its matching start", line)
				}
				if (ev.Item.Type == "mcp_tool_call" && (start.server != ev.Item.Server || start.tool != ev.Item.Tool)) ||
					(ev.Item.Type == "command_execution" && start.command != "" && ev.Item.Command != "" && start.command != ev.Item.Command) {
					return result, fmt.Errorf("line %d changes tool identity between start and completion", line)
				}
				delete(pending, ev.Item.ID)
				if ev.Item.Type == "mcp_tool_call" {
					if ev.Item.Status != "completed" && ev.Item.Status != "failed" {
						return result, fmt.Errorf("line %d completes an MCP tool without a terminal status", line)
					}
					call := ToolCallRecord{CallID: ev.Item.ID, Tool: MCPToolName(ev.Item.Server, ev.Item.Tool),
						InputJSON: string(ev.Item.Arguments), HarnessStatus: ev.Item.Status}
					if ev.Item.Status == "completed" {
						if len(ev.Item.Result) == 0 || string(ev.Item.Result) == "null" {
							call.Note = "result-body-not-observed"
							result.MissingToolBodies++
						} else {
							call.ResultText = string(ev.Item.Result)
							call.ResultBytes = int64(len(ev.Item.Result))
						}
					} else if len(ev.Item.Error) == 0 || string(ev.Item.Error) == "null" {
						call.Note = "failure-body-not-observed"
						result.MissingToolBodies++
					} else {
						call.ResultText = string(ev.Item.Error)
						call.ResultBytes = int64(len(ev.Item.Error))
					}
					result.ToolCalls = append(result.ToolCalls, call)
				} else {
					if ev.Item.Status != "completed" && ev.Item.Status != "failed" && ev.Item.Status != "declined" {
						return result, fmt.Errorf("line %d completes a command without a terminal status", line)
					}
					call := ToolCallRecord{CallID: ev.Item.ID, Tool: "run_command",
						HarnessStatus: ev.Item.Status, ResultText: ev.Item.AggregatedOutput,
						ResultBytes: int64(len(ev.Item.AggregatedOutput)), ExitCode: ev.Item.ExitCode}
					if ev.Item.Status == "completed" && ev.Item.ExitCode == nil {
						call.Note = "command-exit-not-observed"
						result.MissingCommandExits++
					}
					if ev.Item.Command != "" {
						encoded, _ := json.Marshal(map[string]string{"command": ev.Item.Command})
						call.InputJSON = string(encoded)
					}
					result.ToolCalls = append(result.ToolCalls, call)
				}
			}
		default:
			result.UnknownEvents++
			if ev.Type == "" || strings.HasPrefix(ev.Type, "thread.") ||
				strings.HasPrefix(ev.Type, "turn.") || strings.HasPrefix(ev.Type, "item.") {
				result.UnknownControlEvents++
			}
		}
		if (ev.Type == "item.started" || ev.Type == "item.updated" || ev.Type == "item.completed") && ev.Item.Type == "file_change" {
			// The request declared read-only; this notification is an unverified
			// possible effect, not an authorized file write or an OS denial proof.
			result.FileChangeEvents++
		}
	}
	if err := scanner.Err(); err != nil {
		return result, fmt.Errorf("JSONL line exceeds parser limit or cannot be read")
	}
	result.UnfinishedTools = len(pending)
	return result, nil
}
