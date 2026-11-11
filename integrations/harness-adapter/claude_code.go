package harnessadapter

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"path/filepath"
	"runtime"
	"sort"
	"strconv"
	"strings"
	"time"
)

// ClaudeCodeAdapter drives Claude Code in non-interactive print mode.
//
// Vendor facts this adapter is written against (Claude Code 2.1.302, Windows,
// observed from `claude --help` and a real stream-json run):
//
//   - CLI: `claude -p <prompt> --output-format stream-json --verbose [flags]`
//   - stream-json emits one JSON object per line: a `system`/`init` event that
//     carries the session id, cwd, model and the advertised tool list; `assistant`
//     messages whose content blocks carry `tool_use`; `user` messages whose
//     content blocks carry `tool_result`; and a terminal `result` event that
//     carries the session id, cost and usage.
//   - Session identity is a UUID: `--session-id <uuid>` must be a valid UUID and
//     `--resume <id>` adopts one. There is no "unknown id" error path like DSH's;
//     an unusable id is a launch failure instead.
//   - `--tools` restricts the built-in tool set, but MCP-registered tools still
//     appear in the advertised list. Restricting the advertised set is therefore
//     not the same as restricting reachability.
//   - Skills are discovered from `<projectRoot>/.claude/skills/<name>/SKILL.md`.
//
// The adapter records what the harness reported and adds nothing.
type ClaudeCodeAdapter struct {
	// CLI overrides the executable name; empty means "claude".
	CLI string
	// WorkDir is the cwd the harness runs in.
	WorkDir string
	// AddDirs are passed as repeated --add-dir.
	AddDirs []string
	// Tools is passed as --tools when non-empty (e.g. "Bash,Read").
	Tools string
	// PermissionMode is passed as --permission-mode when non-empty.
	PermissionMode string
	// PermissionPrompts is passed as --permission-prompts when non-empty. For an
	// unattended run this must be "none", otherwise anything that would prompt
	// is denied and the run ends without a tool call.
	PermissionPrompts string
	// MCPConfigs are passed as repeated --mcp-config. They are pre-built files
	// the caller supplies; the adapter does not compose them.
	MCPConfigs []string
	// MCPServers are rendered into a Claude Code --mcp-config JSON file for this
	// run, in addition to MCPConfigs. A spec that names environment variables is
	// refused, because this config shape needs literal values and the adapter
	// must not read secrets.
	MCPServers []MCPServerSpec
	// MCPWorkDir is where the generated config file is written. Empty means the
	// adapter's WorkDir.
	MCPWorkDir string
	// Env is extra environment for the child process.
	Env []string
	// Timeout bounds one task.
	Timeout time.Duration

	Runner       Runner
	PathResolver PathResolver
	Clock        func() time.Time
}

// NewClaudeCodeAdapter builds an adapter with production defaults.
func NewClaudeCodeAdapter(workDir string) *ClaudeCodeAdapter {
	return &ClaudeCodeAdapter{
		WorkDir:           workDir,
		Timeout:           10 * time.Minute,
		PermissionPrompts: "none",
		Runner:            ProcessRunner{},
		PathResolver:      OSPathResolver{},
		Clock:             time.Now,
	}
}

// Name implements Adapter.
func (a *ClaudeCodeAdapter) Name() string { return "claude-code" }

// Capabilities: Claude Code has a session id it can resume, discovers skills
// from disk, and can call tools. It reports cost and usage, which DSH's headless
// projection does not.
func (a *ClaudeCodeAdapter) Capabilities() []Capability {
	return []Capability{
		CapSessionCreate, CapSessionResume, CapContextProject, CapToolInvoke,
		CapSkillDiscover, CapSkillLoad, CapResultReceipt, CapDiagnostics,
		CapEvidenceTracking,
	}
}

func (a *ClaudeCodeAdapter) cli() string {
	if a.CLI != "" {
		return a.CLI
	}
	return "claude"
}

// Probe runs a real `claude --version`. It reports Reachable=false with a reason
// when the binary is missing or the probe fails.
func (a *ClaudeCodeAdapter) Probe(ctx context.Context) (Availability, error) {
	exe := a.cli()
	path, err := a.PathResolver.LookPath(exe)
	if err != nil {
		return Availability{
			Reachable: false,
			Reason:    fmt.Sprintf("executable %q not found on PATH: %v", exe, err),
			Detail:    map[string]string{"family": "claude-code", "probe": "lookpath"},
		}, nil
	}
	res, err := a.Runner.Exec(ctx, ExecSpec{Argv: []string{path, "--version"}, Timeout: 60 * time.Second})
	if err != nil {
		return Availability{Reachable: false, Reason: err.Error(),
			Detail: map[string]string{"family": "claude-code", "probe": "version"}}, nil
	}
	if res.LaunchError != "" {
		return Availability{Reachable: false, Reason: "version probe could not start: " + res.LaunchError,
			Detail: map[string]string{"family": "claude-code", "probe": "version"}}, nil
	}
	if res.ExitCode != 0 {
		return Availability{Reachable: false,
			Reason: fmt.Sprintf("version probe exited %d: %s", res.ExitCode, firstLine(res.Stderr)),
			Detail: map[string]string{"family": "claude-code", "probe": "version"}}, nil
	}
	// A reachable binary is not an authenticated harness. The adapter says so
	// rather than letting a later MISSING_CREDENTIAL look like a task failure.
	return Availability{
		Reachable: true,
		Reason:    "version probe ok; authentication is a separate condition the adapter cannot verify",
		Detail: map[string]string{
			"family":   "claude-code",
			"probe":    "version",
			"exePath":  path,
			"version":  strings.TrimSpace(string(res.Stdout)),
			"platform": a.platform(),
		},
	}, nil
}

func (a *ClaudeCodeAdapter) platform() string { return runtime.GOOS }

// buildArgv assembles the exact argv.
func (a *ClaudeCodeAdapter) buildArgv(t Task, session *SessionRef) []string {
	return a.buildArgvWith(t, session, nil)
}

// buildArgvWith is buildArgv plus config files rendered for this one run.
func (a *ClaudeCodeAdapter) buildArgvWith(t Task, session *SessionRef, extraConfigs []string) []string {
	argv := []string{a.cli(), "-p", t.Prompt, "--output-format", "stream-json", "--verbose"}
	if session != nil && session.ExternalID != "" {
		// A Claude Code session id must be a UUID. The adapter forwards whatever
		// it was given and records the outcome; it does not mint ids.
		argv = append(argv, "--resume", session.ExternalID)
	}
	for _, dir := range a.AddDirs {
		if dir != "" {
			argv = append(argv, "--add-dir", dir)
		}
	}
	if a.Tools != "" {
		argv = append(argv, "--tools", a.Tools)
	}
	if a.PermissionMode != "" {
		argv = append(argv, "--permission-mode", a.PermissionMode)
	}
	if a.PermissionPrompts != "" {
		argv = append(argv, "--permission-prompts", a.PermissionPrompts)
	}
	for _, m := range a.MCPConfigs {
		if m != "" {
			argv = append(argv, "--mcp-config", m)
		}
	}
	for _, m := range extraConfigs {
		if m != "" {
			argv = append(argv, "--mcp-config", m)
		}
	}
	return argv
}

// Run implements Adapter.
func (a *ClaudeCodeAdapter) Run(ctx context.Context, t Task, session *SessionRef) (*Result, error) {
	if ctx == nil {
		ctx = context.Background()
	}
	if strings.TrimSpace(t.Prompt) == "" {
		return nil, fmt.Errorf("task %q: prompt is required", t.ID)
	}
	started := a.Clock()
	res := &Result{
		Contract:     ContractVersion,
		Adapter:      a.Name(),
		Transport:    TransportNotAttempted,
		Run:          RunUnknown,
		StartedAt:    started.UTC().Format(time.RFC3339),
		Session:      SessionRef{Adapter: a.Name(), State: SessionUnknown, RequestedID: requestedID(session)},
		Receipt:      Receipt{State: ReceiptNotObserved, Consumer: a.Name()},
		Observations: map[string]string{},
	}

	// Render the caller's MCP servers into a Claude Code --mcp-config file before
	// building argv. A refusal is reported and the run does not start: starting
	// without the tools the task declared would silently change the experiment.
	var extraConfigs []string
	if len(a.MCPServers) > 0 {
		dir := a.MCPWorkDir
		if dir == "" {
			dir = a.WorkDir
		}
		path, digest, err := WriteClaudeMCPConfig(dir, a.MCPServers)
		if err != nil {
			res.Diagnostics = append(res.Diagnostics, Diagnostic{
				Severity: "error", Code: "mcp-config-render-failed", Message: err.Error(),
			})
			res.Unsupported = append(res.Unsupported, "mcp:server-spec-rejected")
			res.FinishedAt = a.Clock().UTC().Format(time.RFC3339)
			return res, nil
		}
		extraConfigs = append(extraConfigs, path)
		res.Outbound = append(res.Outbound, OutboundRecord{
			Direction:   "mcp-config",
			BytesSHA256: digest,
			Detail:      "generated Claude Code --mcp-config for " + mcpServerNames(a.MCPServers),
		})
		res.Observations["mcp-servers"] = mcpServerNames(a.MCPServers)
	}

	argv := a.buildArgvWith(t, session, extraConfigs)

	res.Outbound = append(res.Outbound, OutboundRecord{
		Direction:   "argv",
		BytesSHA256: DigestString(Quote(argv)),
		ByteCount:   int64(len(Quote(argv))),
		Detail:      "claude code print invocation",
	})
	res.Outbound = append(res.Outbound, OutboundRecord{
		Direction:   "task-text",
		BytesSHA256: DigestString(t.Prompt),
		ByteCount:   int64(len(t.Prompt)),
		Detail:      "task prompt",
	})
	for _, s := range t.Skills {
		if s.BytesSHA256 != "" {
			res.Outbound = append(res.Outbound, OutboundRecord{
				Direction:   "skill-bytes",
				BytesSHA256: s.BytesSHA256,
				Detail:      "skill " + s.ID + " placed at " + s.PlacedPath,
			})
		}
	}

	execRes, err := a.Runner.Exec(ctx, ExecSpec{
		Argv:    argv,
		Dir:     a.WorkDir,
		Env:     a.Env,
		Timeout: a.Timeout,
	})
	if err != nil {
		res.Transport = TransportFailed
		res.Diagnostics = append(res.Diagnostics, Diagnostic{
			Severity: "error", Code: "harness-exec-failed", Message: err.Error(),
		})
		res.FinishedAt = a.Clock().UTC().Format(time.RFC3339)
		return res, nil
	}
	if execRes.LaunchError != "" {
		res.Transport = TransportFailed
		res.Run = RunError
		res.Diagnostics = append(res.Diagnostics, Diagnostic{
			Severity: "error", Code: "harness-launch-failed", Message: execRes.LaunchError,
		})
		res.FinishedAt = a.Clock().UTC().Format(time.RFC3339)
		return res, nil
	}
	res.Transport = TransportDelivered
	code := execRes.ExitCode
	res.ExitCode = &code
	if len(execRes.Stderr) > 0 {
		res.Outbound = append(res.Outbound, OutboundRecord{
			Direction:   "stderr",
			BytesSHA256: DigestBytes(execRes.Stderr),
			ByteCount:   int64(len(execRes.Stderr)),
			Detail:      "harness stderr",
		})
		for _, line := range nonEmptyLines(execRes.Stderr) {
			res.Diagnostics = append(res.Diagnostics, Diagnostic{
				Severity: "warning", Code: "harness-stderr", Message: line, Source: "claude-code",
			})
		}
	}

	stream, parseErr := ParseClaudeStreamJSON(execRes.Stdout)
	if parseErr != nil {
		res.Diagnostics = append(res.Diagnostics, Diagnostic{
			Severity: "error", Code: "harness-stream-unparseable", Message: parseErr.Error(), Source: "claude-code",
		})
	}
	res.Session = stream.Session
	res.Session.Adapter = a.Name()
	if session != nil && session.ExternalID != "" {
		if stream.Session.ExternalID == session.ExternalID {
			res.Session.State = SessionResumed
		} else if stream.Session.ExternalID != "" {
			res.Session.State = SessionRejected
			res.Session.Note = "harness reported a different session id than the one requested"
		}
	}
	res.ToolCalls = stream.ToolCalls
	res.FinalText = stream.FinalText
	res.Reason = stream.ResultSubtype
	res.ObservedModel = stream.Model
	for k, v := range stream.Observations {
		res.Observations[k] = v
	}
	for _, d := range stream.Diagnostics {
		res.Diagnostics = append(res.Diagnostics, d)
	}
	switch stream.ResultSubtype {
	case "success":
		res.Run = RunCompleted
	case "":
		res.Run = RunUnknown
	default:
		res.Run = RunError
	}
	if stream.AdvertisedTools != nil {
		res.Observations["advertised-tools"] = strings.Join(stream.AdvertisedTools, ",")
	}
	res.Receipt = Receipt{
		State:    ReceiptNotObserved,
		Consumer: a.Name(),
		Note:     "harness reported delivery; consumer receipt not independently observed",
	}
	if len(t.Skills) > 0 && !anySkillLoadObserved(stream.ToolCalls, t.Skills) {
		res.Unsupported = append(res.Unsupported, "skill:load-not-observed")
	}
	res.FinishedAt = a.Clock().UTC().Format(time.RFC3339)
	return res, nil
}

// ---------------------------------------------------------------------------
// stream-json decoding.
// ---------------------------------------------------------------------------

// ClaudeStream is the decoded projection.
type ClaudeStream struct {
	Session         SessionRef
	ToolCalls       []ToolCallRecord
	FinalText       string
	ResultSubtype   string
	Model           ModelPin
	AdvertisedTools []string
	// Observations are vendor-specific measurements with no cross-vendor
	// meaning: a dollar cost, token counts, a turn count.
	Observations map[string]string
	Diagnostics  []Diagnostic
	UnknownTypes []string
}

type claudeEvent struct {
	Type      string          `json:"type"`
	Subtype   string          `json:"subtype"`
	SessionID string          `json:"session_id"`
	CWD       string          `json:"cwd"`
	Model     string          `json:"model"`
	Tools     []string        `json:"tools"`
	Message   json.RawMessage `json:"message"`
	Result    string          `json:"result"`
	IsError   bool            `json:"is_error"`
	Duration  int64           `json:"duration_api_ms"`
	Turns     int             `json:"num_turns"`
	Cost      float64         `json:"total_cost_usd"`
	Usage     json.RawMessage `json:"usage"`
}

type claudeMessage struct {
	Model   string             `json:"model"`
	Content []claudeContentBlk `json:"content"`
}

type claudeContentBlk struct {
	Type      string          `json:"type"`
	ID        string          `json:"id"`
	Name      string          `json:"name"`
	Input     json.RawMessage `json:"input"`
	Text      string          `json:"text"`
	ToolUseID string          `json:"tool_use_id"`
	Content   json.RawMessage `json:"content"`
	IsError   bool            `json:"is_error"`
}

// ParseClaudeStreamJSON decodes a `claude -p --output-format stream-json` run.
func ParseClaudeStreamJSON(raw []byte) (*ClaudeStream, error) {
	stream := &ClaudeStream{
		Session:      SessionRef{State: SessionUnknown},
		Observations: map[string]string{},
	}
	sc := bufio.NewScanner(bytes.NewReader(raw))
	sc.Buffer(make([]byte, 0, 64*1024), 16*1024*1024)
	lines := 0
	for sc.Scan() {
		line := bytes.TrimSpace(sc.Bytes())
		if len(line) == 0 {
			continue
		}
		lines++
		var ev claudeEvent
		if err := json.Unmarshal(line, &ev); err != nil {
			return stream, fmt.Errorf("line %d: %w", lines, err)
		}
		switch ev.Type {
		case "system":
			if ev.Subtype == "init" {
				stream.Session.ExternalID = ev.SessionID
				stream.Session.CWD = ev.CWD
				stream.Session.State = SessionCreated
				stream.AdvertisedTools = ev.Tools
				if ev.Model != "" {
					stream.Model = ModelPin{Model: ev.Model, Route: "claude-code-print"}
				}
			}
		case "assistant":
			var m claudeMessage
			if json.Unmarshal(ev.Message, &m) == nil {
				if m.Model != "" {
					stream.Model = ModelPin{Model: m.Model, Route: "claude-code-print"}
				}
				for _, b := range m.Content {
					switch b.Type {
					case "tool_use":
						stream.ToolCalls = append(stream.ToolCalls, ToolCallRecord{
							CallID:    b.ID,
							Tool:      b.Name,
							InputJSON: string(b.Input),
							Note:      "harness-reported call; product acceptance not implied",
						})
					case "text":
						// Model-visible text; not evidence of anything happening.
					}
				}
			}
		case "user":
			var m claudeMessage
			if json.Unmarshal(ev.Message, &m) == nil {
				for _, b := range m.Content {
					if b.Type != "tool_result" {
						continue
					}
					text := toolResultText(b.Content)
					foldClaudeToolResult(stream, b.ToolUseID, text, b.IsError)
				}
			}
		case "result":
			stream.ResultSubtype = ev.Subtype
			stream.FinalText = ev.Result
			if ev.SessionID != "" && stream.Session.ExternalID == "" {
				stream.Session.ExternalID = ev.SessionID
				stream.Session.State = SessionCreated
			}
			stream.Observations["total-cost-usd"] = strconv.FormatFloat(ev.Cost, 'f', 6, 64)
			stream.Observations["duration-api-ms"] = strconv.FormatInt(ev.Duration, 10)
			stream.Observations["num-turns"] = strconv.Itoa(ev.Turns)
			if ev.IsError {
				stream.Diagnostics = append(stream.Diagnostics, Diagnostic{
					Severity: "error", Code: "claude-result-is-error", Message: ev.Result, Source: "claude-code",
				})
			}
		default:
			stream.UnknownTypes = append(stream.UnknownTypes, ev.Type)
		}
	}
	if err := sc.Err(); err != nil {
		return stream, fmt.Errorf("scan: %w", err)
	}
	if len(stream.UnknownTypes) > 0 {
		sort.Strings(stream.UnknownTypes)
		stream.Diagnostics = append(stream.Diagnostics, Diagnostic{
			Severity: "warning",
			Code:     "harness-unknown-event-types",
			Message:  "event types this decoder does not model: " + strings.Join(stream.UnknownTypes, ", "),
			Source:   "claude-code",
		})
	}
	return stream, nil
}

// foldClaudeToolResult attaches a tool_result to its matching tool_use, keeping
// an orphan result visible rather than dropping it.
func foldClaudeToolResult(stream *ClaudeStream, id, text string, isError bool) {
	status := "completed"
	if isError {
		status = "error"
	}
	for i := range stream.ToolCalls {
		if stream.ToolCalls[i].CallID == id {
			stream.ToolCalls[i].HarnessStatus = status
			stream.ToolCalls[i].ResultText = text
			stream.ToolCalls[i].ResultBytes = int64(len(text))
			stream.ToolCalls[i].Note = "harness-reported status; not a product verdict"
			return
		}
	}
	stream.ToolCalls = append(stream.ToolCalls, ToolCallRecord{
		CallID:        id,
		HarnessStatus: status,
		ResultText:    text,
		ResultBytes:   int64(len(text)),
		Note:          "harness-reported result with no matching call; not a product verdict",
	})
}

// toolResultText normalises a tool_result content payload, which Claude Code
// sends either as a plain string or as an array of text blocks.
func toolResultText(raw json.RawMessage) string {
	if len(raw) == 0 {
		return ""
	}
	var s string
	if json.Unmarshal(raw, &s) == nil {
		return s
	}
	var blocks []struct {
		Type string `json:"type"`
		Text string `json:"text"`
	}
	if json.Unmarshal(raw, &blocks) == nil {
		var parts []string
		for _, b := range blocks {
			if b.Type == "text" {
				parts = append(parts, b.Text)
			}
		}
		return strings.Join(parts, "")
	}
	return string(raw)
}

// ClaudeSkillRoots returns the local skill roots Claude Code scans. The project
// root is the nearest ancestor containing `.claude`; the user root is
// ~/.claude/skills.
func ClaudeSkillRoots(projectRoot, claudeHome string) []SkillRoot {
	return []SkillRoot{
		{Harness: "claude-code", Path: filepath.Join(projectRoot, ".claude", "skills"), Rank: 100},
		{Harness: "claude-code", Path: filepath.Join(claudeHome, "skills"), Rank: 400},
	}
}
