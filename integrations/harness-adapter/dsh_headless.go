package harnessadapter

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"runtime"
	"sort"
	"strings"
	"time"
)

// DSHHeadlessAdapter drives DeepSeek Harness in headless one-task mode.
//
// Vendor facts this adapter is written against (DSH 0.2.2-rc.1, Windows,
// observed from the shipped @deepseek-ai/dsh-headless bundle):
//
//   - CLI: `dsh --profile <p> --json [--session-id <id>] [--permission-mode <m>]
//     [--approval-policy never|ask] [--add-dir <path>] <task>`
//   - stdout is newline-delimited JSON when --json is passed; diagnostics go to
//     stderr.
//   - process exit is 0 only when the durable turn reason is "completed".
//   - The `--json` stream is a bounded projection, not the durable session log:
//     every non-final string/key is capped at 8 KiB and every event line at
//     32 KiB, with `truncated: true` added when something was cut. The `final`
//     event is exempt and lossless.
//   - The session id is the harness's own; an unknown --session-id is an error,
//     not a silent new session.
//
// The adapter deliberately does not read DSH's internal session store, does not
// parse its zstd JSONL, and does not treat a session id or a tool_result status
// as product acceptance or permission.
type DSHHeadlessAdapter struct {
	// Profile is the DSH profile to boot (e.g. "headless").
	Profile string
	// CLI overrides the executable name; empty means "dsh".
	CLI string
	// PermissionMode is passed as --permission-mode when non-empty.
	PermissionMode string
	// ApprovalPolicy is passed as --approval-policy when non-empty.
	ApprovalPolicy string
	// AddDirs are passed as repeated --add-dir.
	AddDirs []string
	// PatchFiles are passed as repeated --patch, DSH's documented extra
	// patch-list overlay. The adapter does not decide what to patch; the caller
	// supplies a file and the adapter records that it was used.
	PatchFiles []string
	// ProbeEffectiveConfig, when true, makes Run first execute
	// `--dump-config` and record the effective default model route. The
	// headless `--json` projection carries no model field, so without this the
	// only model record for a DSH run is the caller's pin. This is opt-in
	// because it is a second process and an observation of declared
	// configuration, not of what the turn actually used.
	ProbeEffectiveConfig bool
	// WorkDir is the cwd the harness runs in.
	WorkDir string
	// Timeout bounds one task.
	Timeout time.Duration

	Runner       Runner
	PathResolver PathResolver
	// Clock is injectable for tests.
	Clock func() time.Time
}

// NewDSHHeadlessAdapter builds an adapter with production defaults.
func NewDSHHeadlessAdapter(profile, workDir string) *DSHHeadlessAdapter {
	return &DSHHeadlessAdapter{
		Profile:      profile,
		WorkDir:      workDir,
		Timeout:      10 * time.Minute,
		Runner:       ProcessRunner{},
		PathResolver: OSPathResolver{},
		Clock:        time.Now,
	}
}

// Name implements Adapter.
func (a *DSHHeadlessAdapter) Name() string { return "dsh-headless" }

// Capabilities reports what this adapter can do. Session resume is supported by
// the CLI flag, but resume equivalence (same cwd, same preset, no live owner) is
// a harness-side condition the adapter cannot verify, so it is reported with a
// caveat in the evidence rather than assumed.
func (a *DSHHeadlessAdapter) Capabilities() []Capability {
	return []Capability{
		CapSessionCreate, CapSessionResume, CapContextProject, CapToolInvoke,
		CapSkillDiscover, CapSkillLoad, CapResultReceipt, CapDiagnostics,
		CapEvidenceTracking,
	}
}

// cli resolves the executable name.
func (a *DSHHeadlessAdapter) cli() string {
	if a.CLI != "" {
		return a.CLI
	}
	return "dsh"
}

// Probe runs a real `dsh --version`. It reports Reachable=false with a reason
// when the binary is missing or the probe fails; it never returns true without
// having executed something.
func (a *DSHHeadlessAdapter) Probe(ctx context.Context) (Availability, error) {
	exe := a.cli()
	path, err := a.PathResolver.LookPath(exe)
	if err != nil {
		return Availability{
			Reachable: false,
			Reason:    fmt.Sprintf("executable %q not found on PATH: %v", exe, err),
			Detail:    map[string]string{"family": "dsh", "probe": "lookpath"},
		}, nil
	}
	res, err := a.Runner.Exec(ctx, ExecSpec{Argv: []string{path, "--version"}, Timeout: 30 * time.Second})
	if err != nil {
		return Availability{Reachable: false, Reason: err.Error(),
			Detail: map[string]string{"family": "dsh", "probe": "version"}}, nil
	}
	if res.LaunchError != "" {
		return Availability{Reachable: false, Reason: "version probe could not start: " + res.LaunchError,
			Detail: map[string]string{"family": "dsh", "probe": "version"}}, nil
	}
	if res.ExitCode != 0 {
		return Availability{Reachable: false,
			Reason: fmt.Sprintf("version probe exited %d: %s", res.ExitCode, firstLine(res.Stderr)),
			Detail: map[string]string{"family": "dsh", "probe": "version"}}, nil
	}
	return Availability{
		Reachable: true,
		Reason:    "version probe ok",
		Detail: map[string]string{
			"family":   "dsh",
			"probe":    "version",
			"exePath":  path,
			"version":  strings.TrimSpace(string(res.Stdout)),
			"platform": a.platform(),
		},
	}, nil
}

func (a *DSHHeadlessAdapter) platform() string { return runtime.GOOS }

// buildArgv assembles the exact argv.
//
// Order matters and is a vendor constraint, not a style choice: DSH's launcher
// flags (`--profile`, `--patch`) must precede the booted app's own flags
// (`--json`, `--session-id`, `--permission-mode`, `--approval-policy`,
// `--add-dir`). Putting `--patch` after `--json` makes the headless app reject
// it with `unknown option '--patch'` and exit 1 before any turn runs, which
// looks exactly like a harness failure. This function is pure so a test can pin
// the order without running anything.
func (a *DSHHeadlessAdapter) buildArgv(t Task, session *SessionRef) []string {
	argv := []string{a.cli(), "--profile", a.Profile}
	for _, p := range a.PatchFiles {
		if p != "" {
			argv = append(argv, "--patch", p)
		}
	}
	argv = append(argv, "--json")
	if session != nil && session.ExternalID != "" {
		argv = append(argv, "--session-id", session.ExternalID)
	}
	if a.PermissionMode != "" {
		argv = append(argv, "--permission-mode", a.PermissionMode)
	}
	if a.ApprovalPolicy != "" {
		argv = append(argv, "--approval-policy", a.ApprovalPolicy)
	}
	for _, dir := range a.AddDirs {
		if dir != "" {
			argv = append(argv, "--add-dir", dir)
		}
	}
	argv = append(argv, t.Prompt)
	return argv
}

// Run implements Adapter.
func (a *DSHHeadlessAdapter) Run(ctx context.Context, t Task, session *SessionRef) (*Result, error) {
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
		Detail:      "dsh headless invocation",
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

	// The headless projection does not report the model. Ask the launcher for
	// the effective configuration first, so the record names the route the task
	// is about to run under, and label it as a declared route rather than as an
	// observation of what the turn used.
	if a.ProbeEffectiveConfig {
		model, note := a.effectiveModel(ctx)
		if model.Model != "" {
			res.ObservedModel = model
			res.Observations["effective-model"] = model.Provider + "/" + model.Model
		}
		if note != "" {
			res.Observations["effective-model-note"] = note
		}
	}

	execRes, err := a.Runner.Exec(ctx, ExecSpec{
		Argv:    argv,
		Dir:     a.WorkDir,
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

	// The process ran, so the request was delivered to the harness. That is a
	// transport fact only.
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
				Severity: "warning", Code: "harness-stderr", Message: line, Source: "dsh",
			})
		}
	}

	stream, parseErr := ParseDSHJSONStream(execRes.Stdout)
	if parseErr != nil {
		res.Run = RunUnknown
		res.Diagnostics = append(res.Diagnostics, Diagnostic{
			Severity: "error", Code: "harness-stream-unparseable", Message: parseErr.Error(), Source: "dsh",
		})
	}
	res.Session = stream.Session
	res.Session.Adapter = a.Name()
	if res.Session.State == SessionUnknown {
		res.Session.State = SessionUnknown
	}
	res.ToolCalls = stream.ToolCalls
	res.Reason = stream.FinalReason
	res.FinalText = stream.FinalText
	if stream.ErrorMessage != "" {
		res.Diagnostics = append(res.Diagnostics, Diagnostic{
			Severity: "error", Code: "harness-error-event", Message: stream.ErrorMessage, Source: "dsh",
		})
	}
	for _, d := range stream.Diagnostics {
		res.Diagnostics = append(res.Diagnostics, d)
	}

	switch {
	case stream.FinalReason == "completed":
		res.Run = RunCompleted
	case stream.FinalReason == "aborted" || stream.FinalReason == "user":
		res.Run = RunAborted
	case stream.FinalReason != "":
		res.Run = RunError
	case parseErr != nil:
		res.Run = RunUnknown
	default:
		res.Run = RunUnknown
	}

	// A session id the harness echoes back is recorded as an observation. It is
	// not stored as an accepted identity and grants nothing.
	res.Receipt = Receipt{
		State:    ReceiptNotObserved,
		Consumer: a.Name(),
		Note:     "harness reported delivery; consumer receipt not independently observed",
	}
	res.FinishedAt = a.Clock().UTC().Format(time.RFC3339)

	// Report the capabilities the harness could not exercise for this task
	// rather than implying they worked.
	if len(t.Skills) > 0 && !anySkillLoadObserved(stream.ToolCalls, t.Skills) {
		res.Unsupported = append(res.Unsupported, "skill:load-not-observed")
	}
	if stream.Truncated {
		res.Unsupported = append(res.Unsupported, "result:projection-truncated")
	}
	return res, nil
}

// requestedID extracts the id the caller asked to resume, if any.
func requestedID(s *SessionRef) string {
	if s == nil {
		return ""
	}
	return s.ExternalID
}

// effectiveModel runs `--dump-config` and reads the composed
// agent-default-model row. It is an observation of the declared configuration,
// not of the model the turn used, and it says so in the returned note.
func (a *DSHHeadlessAdapter) effectiveModel(ctx context.Context) (ModelPin, string) {
	argv := []string{a.cli(), "--profile", a.Profile}
	for _, p := range a.PatchFiles {
		if p != "" {
			argv = append(argv, "--patch", p)
		}
	}
	argv = append(argv, "--dump-config")
	res, err := a.Runner.Exec(ctx, ExecSpec{Argv: argv, Timeout: 60 * time.Second})
	if err != nil || res.ExitCode != 0 || res.LaunchError != "" {
		return ModelPin{}, "effective configuration could not be read"
	}
	// The dump is YAML-ish text; match the two keys the row carries rather than
	// parsing the whole tree.
	var provider, model string
	for _, line := range nonEmptyLines(res.Stdout) {
		t := strings.TrimSpace(line)
		switch {
		case strings.HasPrefix(t, "provider:"):
			provider = strings.TrimSpace(strings.TrimPrefix(t, "provider:"))
		case strings.HasPrefix(t, "model:"):
			model = strings.TrimSpace(strings.TrimPrefix(t, "model:"))
		}
	}
	if model == "" {
		return ModelPin{}, "agent-default-model row not found in the effective configuration"
	}
	return ModelPin{
		Provider: provider,
		Model:    model,
		Route:    "dsh-effective-config",
	}, "declared default model route from --dump-config; not an observation of what this turn used"
}

// anySkillLoadObserved reports whether any tool call named a skill id.
func anySkillLoadObserved(calls []ToolCallRecord, skills []SkillPin) bool {
	if len(skills) == 0 {
		return false
	}
	names := map[string]bool{}
	for _, s := range skills {
		names[s.ID] = true
	}
	for _, c := range calls {
		if !isSkillLoadTool(c.Tool) {
			continue
		}
		var payload struct {
			Name string `json:"name"`
		}
		if json.Unmarshal([]byte(c.InputJSON), &payload) == nil && names[payload.Name] {
			return true
		}
		if names[c.Tool] {
			return true
		}
	}
	return false
}

// isSkillLoadTool reports whether a tool name is a skill loader. DSH names it
// "skill"; other harnesses differ, which is why this is a helper and not a
// contract constant.
func isSkillLoadTool(tool string) bool {
	switch strings.ToLower(tool) {
	case "skill", "skill_load", "load_skill", "read_skill":
		return true
	}
	return false
}

// ---------------------------------------------------------------------------
// NDJSON projection decoding.
// ---------------------------------------------------------------------------

// DSHStream is the decoded projection. Every field is what the harness said,
// nothing more.
type DSHStream struct {
	Session      SessionRef
	ToolCalls    []ToolCallRecord
	FinalText    string
	FinalReason  string
	ErrorMessage string
	// Truncated is true when any projected event carried `truncated: true`,
	// meaning the projection dropped bytes the durable log still holds.
	Truncated bool
	// EventCounts counts observed event types.
	EventCounts map[string]int
	// UnknownTypes lists event types this decoder does not model.
	UnknownTypes []string
	// Diagnostics are derived observations about the stream itself, not product
	// diagnostics.
	Diagnostics []Diagnostic
}

type dshEvent struct {
	Type      string          `json:"type"`
	SessionID string          `json:"sessionId"`
	CWD       string          `json:"cwd"`
	Phase     string          `json:"phase"`
	Turn      int             `json:"turn"`
	Step      int             `json:"step"`
	CallID    string          `json:"callId"`
	Tool      string          `json:"tool"`
	Input     json.RawMessage `json:"input"`
	Status    string          `json:"status"`
	Result    string          `json:"result"`
	Error     json.RawMessage `json:"error"`
	Message   string          `json:"message"`
	Text      string          `json:"text"`
	Truncated bool            `json:"truncated"`
	// Reason is polymorphic in the projection: the terminal `final` event
	// carries an object (`{"kind":"completed"}`) while the `status`/turn_end
	// event carries a bare string. Both shapes are decoded; neither is
	// interpreted beyond recording it.
	Reason json.RawMessage `json:"reason"`
}

// reasonKind extracts the kind from either shape, returning "" when absent.
func (e dshEvent) reasonKind() string {
	if len(e.Reason) == 0 {
		return ""
	}
	var obj struct {
		Kind string `json:"kind"`
	}
	if err := json.Unmarshal(e.Reason, &obj); err == nil && obj.Kind != "" {
		return obj.Kind
	}
	var s string
	if err := json.Unmarshal(e.Reason, &s); err == nil {
		return s
	}
	return ""
}

// ParseDSHJSONStream decodes a DSH headless --json stream. Unknown event types
// are counted and listed, never dropped silently: a harness that starts emitting
// a new event type must surface as a gap, not as a shorter stream.
func ParseDSHJSONStream(raw []byte) (*DSHStream, error) {
	stream := &DSHStream{
		Session:     SessionRef{State: SessionUnknown},
		EventCounts: map[string]int{},
	}
	sc := bufio.NewScanner(bytes.NewReader(raw))
	sc.Buffer(make([]byte, 0, 64*1024), 8*1024*1024)
	lines := 0
	for sc.Scan() {
		line := bytes.TrimSpace(sc.Bytes())
		if len(line) == 0 {
			continue
		}
		lines++
		var ev dshEvent
		if err := json.Unmarshal(line, &ev); err != nil {
			return stream, fmt.Errorf("line %d: %w", lines, err)
		}
		stream.EventCounts[ev.Type]++
		if ev.Truncated {
			stream.Truncated = true
		}
		switch ev.Type {
		case "session":
			stream.Session.ExternalID = ev.SessionID
			stream.Session.CWD = ev.CWD
			stream.Session.State = SessionCreated
		case "status":
			// phase is recorded only through the counts; turn/step numbers are
			// harness-internal and not a product progress measure.
		case "thinking", "text":
			// Model-visible text is a projection of a committed assistant
			// message; it is not evidence of anything having happened.
		case "tool_call":
			rec := ToolCallRecord{
				CallID:    ev.CallID,
				Tool:      ev.Tool,
				InputJSON: string(ev.Input),
				Note:      "harness-reported call; product acceptance not implied",
			}
			stream.ToolCalls = append(stream.ToolCalls, rec)
		case "tool_result":
			applyToolResult(stream, ev)
		case "final":
			stream.FinalText = ev.Text
			stream.FinalReason = ev.reasonKind()
		case "error":
			stream.ErrorMessage = ev.Message
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
			Source:   "dsh",
		})
	}
	if stream.Truncated {
		stream.Diagnostics = append(stream.Diagnostics, Diagnostic{
			Severity: "warning",
			Code:     "harness-projection-truncated",
			Message:  "the --json projection bounded at least one payload; the durable session log may hold more",
			Source:   "dsh",
		})
	}
	return stream, nil
}

// applyToolResult folds a tool_result event into its matching tool_call. A
// result with no matching call is kept as an orphan so the gap stays visible.
func applyToolResult(stream *DSHStream, ev dshEvent) {
	idx := -1
	for i := len(stream.ToolCalls) - 1; i >= 0; i-- {
		if stream.ToolCalls[i].CallID == ev.CallID {
			idx = i
			break
		}
	}
	if idx < 0 {
		// No call to attach to. Keep it as its own record so the stream does not
		// silently lose a result the harness reported.
		stream.ToolCalls = append(stream.ToolCalls, ToolCallRecord{
			CallID:        ev.CallID,
			HarnessStatus: ev.Status,
			ResultText:    ev.Result,
			ResultBytes:   int64(len(ev.Result)),
			Truncated:     ev.Truncated,
			Note:          "harness-reported result with no matching call; not a product verdict",
		})
		return
	}
	stream.ToolCalls[idx].HarnessStatus = ev.Status
	stream.ToolCalls[idx].ResultText = ev.Result
	stream.ToolCalls[idx].ResultBytes = int64(len(ev.Result))
	stream.ToolCalls[idx].Truncated = ev.Truncated
	stream.ToolCalls[idx].Note = "harness-reported status; not a product verdict"
}

// firstLine returns the first non-empty line, truncated for evidence.
func firstLine(b []byte) string {
	for _, l := range nonEmptyLines(b) {
		return l
	}
	return ""
}

func nonEmptyLines(b []byte) []string {
	var out []string
	for _, l := range bytes.Split(b, []byte("\n")) {
		s := strings.TrimSpace(string(l))
		if s != "" {
			out = append(out, s)
		}
	}
	return out
}
