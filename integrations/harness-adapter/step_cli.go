package harnessadapter

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"strings"
	"time"
)

// stepCLIAdapter drives the Step Code CLI in non-interactive (`-p`) JSON mode.
//
// Vendor facts this adapter is written against (Step Code 0.1.7, Windows,
// observed from `step --help`, `docs/mcp-catalog.md` and real runs):
//
//   - CLI: `step --approve [--approval-mode auto] [--non-interactive-approval allow]
//     --mode json -p [--model <m>] [--skill <path>] "<task>"`
//   - `--mode json` emits one JSON object per line: a `session` event, repeated
//     `entry_appended` custom events, `message_start`/`message_end`,
//     `tool_execution_start`/`tool_execution_end`, `turn_*`, and a terminal
//     `agent_settled`.
//   - MCP servers are declared in `~/.stepcode/config.toml` as
//     `[mcp_servers.<name>]`, or in a plugin's `step.plugin.json` under
//     `mcpServers`. A project-scoped plugin lives at
//     `<cwd>/.stepcode/plugins/<safe-name>/step.plugin.json` and needs the
//     project trusted (`--approve`).
//   - Tool names are `<server>__<tool>` for a config.toml server and
//     `<pluginId>__<server>__<tool>` for a plugin-declared one. This adapter
//     decodes both shapes and records which one was used, because a reader must
//     be able to tell them apart.
//   - A skill is reported as `kind:"skill", stage:"discovered"` only. There is no
//     observed activation stage, so `--skill` yields `discovered` and nothing
//     stronger.
//   - `--mode json` is a run log, not a durable session transcript; the file a
//     session persists is separate.
//
// The adapter does not speak MCP, does not start the server, and does not
// rewrite Step's config: the caller supplies the declaration and this adapter
// records what was declared and what was reached.
type StepCLIAdapter struct {
	// CLI overrides the executable name; empty means "step".
	CLI string
	// WorkDir is the cwd the harness runs in. A project-scoped plugin is found
	// relative to it.
	WorkDir string
	// Model is passed as --model when non-empty.
	Model string
	// Skills are passed as repeated --skill.
	Skills []string
	// ApprovalMode is passed as --approval-mode ("auto" allows unattended writes).
	ApprovalMode string
	// NonInteractiveApproval is passed as --non-interactive-approval.
	NonInteractiveApproval string
	// Tools restricts the built-in tool set when non-empty (comma separated).
	Tools string
	// Env is extra environment for the child process. Credentials belong here and
	// are never recorded.
	Env []string
	// Timeout bounds one task.
	Timeout time.Duration

	Runner       Runner
	PathResolver PathResolver
	Clock        func() time.Time
}

// NewStepCLIAdapter builds an adapter with production defaults.
func NewStepCLIAdapter(workDir string) *StepCLIAdapter {
	return &StepCLIAdapter{
		WorkDir:                workDir,
		Timeout:                10 * time.Minute,
		ApprovalMode:           "auto",
		NonInteractiveApproval: "allow",
		Runner:                 ProcessRunner{},
		PathResolver:           OSPathResolver{},
		Clock:                  time.Now,
	}
}

// Name implements Adapter.
func (a *StepCLIAdapter) Name() string { return "step-cli" }

// Capabilities: Step has a session it can continue, discovers skills from disk,
// and calls tools. Its JSON log reports usage but no dollar cost.
func (a *StepCLIAdapter) Capabilities() []Capability {
	return []Capability{
		CapSessionCreate, CapSessionResume, CapContextProject, CapToolInvoke,
		CapSkillDiscover, CapSkillLoad, CapResultReceipt, CapDiagnostics,
		CapEvidenceTracking,
	}
}

func (a *StepCLIAdapter) cli() string {
	if a.CLI != "" {
		return a.CLI
	}
	return "step"
}

// Probe runs a real `step --version`. It reports Reachable=false with a reason
// when the binary is missing or the probe fails, and it does not treat a
// reachable binary as an authenticated one.
func (a *StepCLIAdapter) Probe(ctx context.Context) (Availability, error) {
	exe := a.cli()
	path, err := a.PathResolver.LookPath(exe)
	if err != nil {
		return Availability{
			Reachable: false,
			Reason:    fmt.Sprintf("executable %q not found on PATH: %v", exe, err),
			Detail:    map[string]string{"family": "step-cli", "probe": "lookpath"},
		}, nil
	}
	res, err := a.Runner.Exec(ctx, ExecSpec{Argv: []string{path, "--version"}, Timeout: 60 * time.Second})
	if err != nil {
		return Availability{Reachable: false, Reason: err.Error(),
			Detail: map[string]string{"family": "step-cli", "probe": "version"}}, nil
	}
	if res.LaunchError != "" {
		return Availability{Reachable: false, Reason: "version probe could not start: " + res.LaunchError,
			Detail: map[string]string{"family": "step-cli", "probe": "version"}}, nil
	}
	if res.ExitCode != 0 {
		return Availability{Reachable: false,
			Reason: fmt.Sprintf("version probe exited %d: %s", res.ExitCode, firstLine(res.Stderr)),
			Detail: map[string]string{"family": "step-cli", "probe": "version"}}, nil
	}
	return Availability{
		Reachable: true,
		Reason:    "version probe ok; model availability and authentication are separate conditions the adapter cannot verify",
		Detail: map[string]string{
			"family":   "step-cli",
			"probe":    "version",
			"exePath":  path,
			"version":  strings.TrimSpace(string(res.Stdout)),
			"platform": runtime.GOOS,
		},
	}, nil
}

// buildArgv assembles the exact argv.
func (a *StepCLIAdapter) buildArgv(t Task, session *SessionRef) []string {
	argv := []string{a.cli(), "--approve", "--mode", "json", "-p"}
	if a.ApprovalMode != "" {
		argv = append(argv, "--approval-mode", a.ApprovalMode)
	}
	if a.NonInteractiveApproval != "" {
		argv = append(argv, "--non-interactive-approval", a.NonInteractiveApproval)
	}
	if a.Model != "" {
		argv = append(argv, "--model", a.Model)
	}
	for _, s := range a.Skills {
		if s != "" {
			argv = append(argv, "--skill", s)
		}
	}
	if a.Tools != "" {
		argv = append(argv, "--tools", a.Tools)
	}
	if session != nil && session.ExternalID != "" {
		// Step resumes by session file/id; the adapter forwards it and records the
		// outcome rather than assuming continuity.
		argv = append(argv, "--session-id", session.ExternalID)
	}
	argv = append(argv, t.Prompt)
	return argv
}

// Run implements Adapter.
func (a *StepCLIAdapter) Run(ctx context.Context, t Task, session *SessionRef) (*Result, error) {
	if ctx == nil {
		ctx = context.Background()
	}
	if strings.TrimSpace(t.Prompt) == "" {
		return nil, fmt.Errorf("task %q: prompt is required", t.ID)
	}
	started := a.Clock()
	argv := a.buildArgv(t, session)
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
	res.Outbound = append(res.Outbound, OutboundRecord{
		Direction:   "argv",
		BytesSHA256: DigestString(Quote(argv)),
		ByteCount:   int64(len(Quote(argv))),
		Detail:      "step code print invocation",
	})
	res.Outbound = append(res.Outbound, OutboundRecord{
		Direction:   "task-text",
		BytesSHA256: DigestString(t.Prompt),
		ByteCount:   int64(len(t.Prompt)),
		Detail:      "task prompt",
	})

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
				Severity: "warning", Code: "harness-stderr", Message: line, Source: "step-cli",
			})
		}
	}

	stream, parseErr := ParseStepJSONStream(execRes.Stdout)
	if parseErr != nil {
		res.Diagnostics = append(res.Diagnostics, Diagnostic{
			Severity: "error", Code: "harness-stream-unparseable", Message: parseErr.Error(), Source: "step-cli",
		})
	}
	res.Session = stream.Session
	res.Session.Adapter = a.Name()
	res.ToolCalls = stream.ToolCalls
	res.FinalText = stream.FinalText
	res.ObservedModel = stream.Model
	for k, v := range stream.Observations {
		res.Observations[k] = v
	}
	res.Diagnostics = append(res.Diagnostics, stream.Diagnostics...)
	if len(stream.SkillStages) > 0 {
		res.Observations["skill-stages"] = strings.Join(stream.SkillStages, ",")
	}
	// The run verdict comes from the terminal event and an explicit tool error,
	// never from exit 0 alone.
	switch {
	case stream.Settled && !stream.ToolError:
		res.Run = RunCompleted
	case stream.ToolError:
		res.Run = RunError
	case !stream.Settled:
		res.Run = RunUnknown
	default:
		res.Run = RunCompleted
	}
	res.Receipt = Receipt{
		State:    ReceiptNotObserved,
		Consumer: a.Name(),
		Note:     "harness reported delivery; consumer receipt not independently observed",
	}
	if len(t.Skills) > 0 && !streamAnySkillLoadObserved(stream.ToolCalls, t.Skills) && !stream.SkillLoaded() {
		res.Unsupported = append(res.Unsupported, "skill:load-not-observed")
	}
	res.FinishedAt = a.Clock().UTC().Format(time.RFC3339)
	return res, nil
}

// streamAnySkillLoadObserved is anySkillLoadObserved for Step's tool vocabulary.
func streamAnySkillLoadObserved(calls []ToolCallRecord, skills []SkillPin) bool {
	return anySkillLoadObserved(calls, skills)
}

// ---------------------------------------------------------------------------
// Step name decoding. Step publishes `<server>__<tool>` for config.toml servers
// and `<pluginId>__<server>__<tool>` for plugin-declared ones.
// ---------------------------------------------------------------------------

// StepToolName decodes a Step model-facing tool name into its optional plugin id,
// server namespace and raw tool name.
//
// The shape is not `mcp__x__y`: Step uses `__` as a plain separator with no
// prefix, so a two-part name is a config.toml server and a three-part name is a
// plugin-declared one. A name with four or more parts cannot be decoded.
//
// The prefix check is on the START of the name, not on containment: a plugin id
// such as `yi-harness-adapter-mcp` legitimately contains `mcp__` in the middle
// once the separator follows it, and a containment test would reject it.
func StepToolName(name string) (pluginID, server, raw string, ok bool) {
	if strings.HasPrefix(name, MCPToolPrefix) {
		// A DSH/Claude-style name is not a Step name.
		return "", "", "", false
	}
	parts := strings.Split(name, "__")
	switch len(parts) {
	case 2:
		if parts[0] == "" || parts[1] == "" {
			return "", "", "", false
		}
		return "", parts[0], parts[1], true
	case 3:
		if parts[0] == "" || parts[1] == "" || parts[2] == "" {
			return "", "", "", false
		}
		return parts[0], parts[1], parts[2], true
	}
	return "", "", "", false
}

// StepPluginContract is one caller-supplied plugin declaration for Step. It is
// data the caller supplies; the adapter writes it only where the caller says.
type StepPluginContract struct {
	// PluginID is the safe plugin id Step uses as the plugin namespace. It must
	// match Step's safe-name rule.
	PluginID string
	// Name and Description are recorded in the manifest.
	Name        string
	Description string
	// MCPServerName is the server namespace inside the plugin.
	MCPServerName string
	// MCPServer is the declaration rendered under that namespace.
	MCPServer MCPServerSpec
	// Dir is where the plugin directory is written. Empty means no write.
	Dir string
}

// Validate checks the parts a Step plugin needs.
func (p StepPluginContract) Validate() error {
	if p.PluginID == "" {
		return fmt.Errorf("step plugin: pluginId is required")
	}
	if !stepSafeName(p.PluginID) {
		return fmt.Errorf("step plugin %q: pluginId must match Step's safe-name rule", p.PluginID)
	}
	if p.MCPServerName == "" || p.MCPServer.ServerName != p.MCPServerName {
		return fmt.Errorf("step plugin %q: serverName must name the declared MCP server", p.PluginID)
	}
	if err := p.MCPServer.Validate(); err != nil {
		return err
	}
	return nil
}

// ToolName renders the model-facing name Step will publish for this plugin's tool.
func (p StepPluginContract) ToolName(rawTool string) string {
	return p.PluginID + "__" + p.MCPServerName + "__" + rawTool
}

// WritePlugin writes `<dir>/<pluginId>/step.plugin.json` with the MCP declaration
// inline, and returns the path and digest of the written bytes.
//
// Step reads a plugin's manifest from `step.plugin.json`; an inline `mcpServers`
// object is accepted (its reader also accepts a relative declaration path, which
// this function does not use so the file count stays at one).
func (p StepPluginContract) WritePlugin() (path, digest string, err error) {
	if err := p.Validate(); err != nil {
		return "", "", err
	}
	if p.Dir == "" {
		return "", "", fmt.Errorf("step plugin %q: dir is empty, so nothing would be written", p.PluginID)
	}
	decl := map[string]any{
		"id":          p.PluginID,
		"version":     "0.0.0",
		"description": p.Description,
		"mcpServers": map[string]any{
			p.MCPServerName: stepServerDeclaration(p.MCPServer),
		},
	}
	if p.Name != "" {
		decl["name"] = p.Name
	}
	data, err := json.MarshalIndent(decl, "", "  ")
	if err != nil {
		return "", "", err
	}
	data = append(data, '\n')
	path = filepath.Join(p.Dir, p.PluginID, "step.plugin.json")
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return "", "", fmt.Errorf("mkdir %s: %w", filepath.Dir(path), err)
	}
	if err := os.WriteFile(path, data, 0o644); err != nil {
		return "", "", err
	}
	return path, DigestBytes(data), nil
}

// stepServerDeclaration renders one MCPServerSpec as Step's declaration shape.
// Env values are not written: like the other vendors, this adapter does not read
// secrets. A spec that needs env is refused by the caller, not silently dropped.
func stepServerDeclaration(s MCPServerSpec) map[string]any {
	d := map[string]any{}
	if s.Transport == "stdio" {
		d["command"] = s.Command
		if len(s.Args) > 0 {
			d["args"] = s.Args
		}
		if s.CWD != "" {
			d["cwd"] = s.CWD
		}
	} else {
		d["url"] = s.URL
	}
	if s.ToolCallTimeoutMS > 0 {
		d["tool_timeout_sec"] = int(s.ToolCallTimeoutMS / 1000)
	}
	if s.FailOnStartupError {
		// Step has no such field; the caller learns this from the returned
		// observation instead of a silently-ignored key.
		d["__unsupported_failOnStartupError"] = true
	}
	return d
}

// stepSafeName mirrors Step's SAFE_NAME check closely enough to refuse a
// namespace Step would reject.
func stepSafeName(v string) bool {
	if v == "" || v == "." || v == ".." {
		return false
	}
	for _, r := range v {
		switch {
		case r >= 'a' && r <= 'z', r >= 'A' && r <= 'Z', r >= '0' && r <= '9':
		case r == '-', r == '_', r == '.':
		default:
			return false
		}
	}
	return true
}

// ---------------------------------------------------------------------------
// Step JSON run-log decoding.
// ---------------------------------------------------------------------------

// StepStream is the decoded run log.
type StepStream struct {
	Session      SessionRef
	ToolCalls    []ToolCallRecord
	FinalText    string
	Model        ModelPin
	Settled      bool
	ToolError    bool
	Diagnostics  []Diagnostic
	Observations map[string]string
	// SkillStages lists the observed skill activity stages in order.
	SkillStages []string
	// SkillNames lists the skills Step reported discovering.
	SkillNames []string
	// UnknownTypes lists event types this decoder does not model.
	UnknownTypes []string
}

// SkillLoaded reports whether any activation stage was observed. Step reports
// `discovered` only, so this is false unless a future version emits more.
func (s StepStream) SkillLoaded() bool {
	for _, stage := range s.SkillStages {
		if stage != "discovered" {
			return true
		}
	}
	return false
}

type stepEvent struct {
	Type       string          `json:"type"`
	ToolCallID string          `json:"toolCallId"`
	ToolName   string          `json:"toolName"`
	Args       json.RawMessage `json:"args"`
	Result     json.RawMessage `json:"result"`
	Message    json.RawMessage `json:"message"`
	ID         string          `json:"id"`
	Entry      json.RawMessage `json:"entry"`
	Version    int             `json:"version"`
}

type stepEntry struct {
	Type       string          `json:"type"`
	CustomType string          `json:"customType"`
	Data       json.RawMessage `json:"data"`
}

type stepActivity struct {
	Kind       string `json:"kind"`
	Stage      string `json:"stage"`
	ResourceID string `json:"resourceId"`
	Name       string `json:"name"`
}

type stepMessage struct {
	Role    string `json:"role"`
	Model   string `json:"model"`
	Content []struct {
		Type       string          `json:"type"`
		Text       string          `json:"text"`
		Thinking   string          `json:"thinking"`
		ToolCallID string          `json:"id"`
		Name       string          `json:"name"`
		Arguments  json.RawMessage `json:"arguments"`
	} `json:"content"`
	Usage json.RawMessage `json:"usage"`
}

// ParseStepJSONStream decodes `step --mode json -p`. Unknown event types are
// counted and listed so a new Step event type surfaces as a gap.
func ParseStepJSONStream(raw []byte) (*StepStream, error) {
	stream := &StepStream{
		Session:      SessionRef{State: SessionUnknown},
		Observations: map[string]string{},
	}
	// toolCallId -> index into ToolCalls, so a result folds into its start.
	open := map[string]int{}
	sc := bufio.NewScanner(bytes.NewReader(raw))
	sc.Buffer(make([]byte, 0, 64*1024), 16*1024*1024)
	lines := 0
	var lastAssistantText []string
	for sc.Scan() {
		line := bytes.TrimSpace(sc.Bytes())
		if len(line) == 0 {
			continue
		}
		lines++
		var ev stepEvent
		if err := json.Unmarshal(line, &ev); err != nil {
			return stream, fmt.Errorf("line %d: %w", lines, err)
		}
		switch ev.Type {
		case "session":
			stream.Session.ExternalID = ev.ID
			if ev.ID == "" {
				stream.Session.ExternalID = ev.ToolCallID
			}
			stream.Session.State = SessionCreated
		case "entry_appended":
			var entry stepEntry
			if json.Unmarshal(ev.Entry, &entry) == nil && entry.CustomType == "step.activity" {
				var act stepActivity
				if json.Unmarshal(entry.Data, &act) == nil && act.Kind == "skill" {
					stream.SkillStages = append(stream.SkillStages, act.Stage)
					if act.Name != "" {
						stream.SkillNames = append(stream.SkillNames, strings.TrimPrefix(act.Name, "$"))
					}
				}
			}
		case "message_end":
			var m stepMessage
			if json.Unmarshal(ev.Message, &m) == nil {
				if m.Model != "" {
					stream.Model = ModelPin{Model: m.Model, Route: "step-cli-json"}
				}
				for _, c := range m.Content {
					switch c.Type {
					case "text":
						if m.Role == "assistant" {
							lastAssistantText = append(lastAssistantText, c.Text)
						}
					case "toolCall":
						// A call announced in a message but not executed is kept
						// visible; the execution event is the stronger record.
						stream.ToolCalls = append(stream.ToolCalls, ToolCallRecord{
							CallID:    c.ToolCallID,
							Tool:      c.Name,
							InputJSON: string(c.Arguments),
							Note:      "announced in an assistant message; execution not yet observed",
						})
						open[c.ToolCallID] = len(stream.ToolCalls) - 1
					}
				}
			}
		case "tool_execution_start":
			// The assistant message may already have announced this call id. Fold
			// the execution into that record instead of adding a second one, so one
			// call is never counted twice.
			rec := ToolCallRecord{
				CallID:    ev.ToolCallID,
				Tool:      ev.ToolName,
				InputJSON: string(ev.Args),
				Note:      "harness-reported execution start",
			}
			if idx, ok := open[ev.ToolCallID]; ok {
				stream.ToolCalls[idx].Tool = ev.ToolName
				stream.ToolCalls[idx].InputJSON = string(ev.Args)
				stream.ToolCalls[idx].Note = "harness-reported execution start"
				continue
			}
			stream.ToolCalls = append(stream.ToolCalls, rec)
			open[ev.ToolCallID] = len(stream.ToolCalls) - 1
		case "tool_execution_end":
			var result struct {
				IsError bool `json:"isError"`
				Content []struct {
					Type string `json:"type"`
					Text string `json:"text"`
				} `json:"content"`
			}
			_ = json.Unmarshal(ev.Result, &result)
			var text []string
			for _, c := range result.Content {
				if c.Type == "text" {
					text = append(text, c.Text)
				}
			}
			status := "completed"
			if result.IsError {
				status = "error"
				stream.ToolError = true
			}
			idx, ok := open[ev.ToolCallID]
			if !ok {
				stream.ToolCalls = append(stream.ToolCalls, ToolCallRecord{
					CallID: ev.ToolCallID, Tool: ev.ToolName, HarnessStatus: status,
					ResultText: strings.Join(text, ""), Note: "result with no observed start",
				})
				continue
			}
			stream.ToolCalls[idx].HarnessStatus = status
			stream.ToolCalls[idx].ResultText = strings.Join(text, "")
			stream.ToolCalls[idx].ResultBytes = int64(len(strings.Join(text, "")))
			stream.ToolCalls[idx].Note = "harness-reported status; not a product verdict"
		case "agent_settled":
			stream.Settled = true
		case "turn_end", "agent_end", "turn_start", "agent_start", "message_start":
			// Progress events; they are counted and otherwise not interpreted.
		default:
			stream.UnknownTypes = append(stream.UnknownTypes, ev.Type)
		}
	}
	if err := sc.Err(); err != nil {
		return stream, fmt.Errorf("scan: %w", err)
	}
	if len(lastAssistantText) > 0 {
		stream.FinalText = lastAssistantText[len(lastAssistantText)-1]
	}
	if len(stream.UnknownTypes) > 0 {
		sort.Strings(stream.UnknownTypes)
		stream.Diagnostics = append(stream.Diagnostics, Diagnostic{
			Severity: "warning",
			Code:     "harness-unknown-event-types",
			Message:  "event types this decoder does not model: " + strings.Join(stream.UnknownTypes, ", "),
			Source:   "step-cli",
		})
	}
	return stream, nil
}
