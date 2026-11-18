package harnessadapter

import (
	"context"
	"strings"
	"testing"
)

const codexOKJSONL = `{"type":"thread.started","thread_id":"thread-1"}
{"type":"turn.started"}
{"type":"item.started","item":{"id":"tool-1","type":"mcp_tool_call","server":"tei","tool":"model_catalog","status":"in_progress"}}
{"type":"item.completed","item":{"id":"tool-1","type":"mcp_tool_call","server":"tei","tool":"model_catalog","status":"completed","arguments":{"workspace":"demo"},"result":{"content":[{"type":"text","text":"ok"}]}}}
{"type":"item.completed","item":{"id":"answer-1","type":"agent_message","text":"Only read Source A."}}
{"type":"turn.completed","usage":{"input_tokens":10,"output_tokens":7}}
`

func TestParseCodexExecJSONLSeparatesToolFromTurn(t *testing.T) {
	s, err := ParseCodexExecJSONL([]byte(codexOKJSONL))
	if err != nil {
		t.Fatal(err)
	}
	if s.ThreadID != "thread-1" || !s.TurnStarted || s.Terminal != "turn.completed" || s.UnfinishedTools != 0 {
		t.Fatalf("unexpected event summary: %+v", s)
	}
	if s.FinalText != "Only read Source A." {
		t.Fatalf("final message not found: %q", s.FinalText)
	}
	if len(s.ToolCalls) != 1 || s.ToolCalls[0].Tool != "mcp__tei__model_catalog" ||
		s.ToolCalls[0].ResultBytes == 0 || s.ToolCalls[0].ProductVerdict != nil ||
		s.ToolCalls[0].ExitCode != nil {
		t.Fatalf("typed tool was promoted or lost: %+v", s.ToolCalls)
	}
}

func TestCodexExecRunIsBoundedAndNeverProductAccepted(t *testing.T) {
	fake := &FakeRunner{Default: ExecResult{ExitCode: 0, Stdout: []byte(codexOKJSONL)}}
	a := NewCodexExecAdapter("/fixed/git/worktree")
	a.Runner = fake
	r, err := a.Run(context.Background(), Task{ID: "codex-1", Prompt: "Explain Source A."}, nil)
	if err != nil {
		t.Fatal(err)
	}
	if r.Transport != TransportDelivered || r.Run != RunCompleted ||
		r.Session.State != SessionCreated || r.Session.ExternalID != "thread-1" {
		t.Fatalf("unexpected result: %+v", r)
	}
	if r.Receipt.State != ReceiptNotObserved || r.Promoted() {
		t.Fatal("native turn success was promoted to Product receipt")
	}
	if r.ObservedModel.Model != "" {
		t.Fatal("adapter invented observed model")
	}
	if len(fake.Calls) != 1 {
		t.Fatal("expected one exec invocation")
	}
	spec := fake.Calls[0]
	if spec.Dir != "/fixed/git/worktree" || string(spec.Stdin) != "Explain Source A." {
		t.Fatalf("cwd or stdin not pinned: %+v", spec)
	}
	argv := strings.Join(spec.Argv, " ")
	if strings.Contains(argv, "Explain Source A.") || strings.Contains(argv, "--skip-git-repo-check") ||
		strings.Contains(argv, "--dangerously-") || !strings.Contains(argv, "--sandbox read-only") ||
		!strings.HasSuffix(argv, " -") {
		t.Fatalf("unsafe CLI args: %q", argv)
	}
	if len(r.Outbound) != 2 || r.Outbound[1].Direction != "stdin" {
		t.Fatalf("stdin digest not recorded: %+v", r.Outbound)
	}
}

func TestCodexExecRejectsUnboundCapabilitiesBeforeLaunch(t *testing.T) {
	tests := []struct {
		name    string
		task    Task
		session *SessionRef
		want    string
	}{
		{name: "tool", task: Task{Prompt: "hello", Tools: []ToolOffer{{Name: "tei_model_catalog"}}}, want: "tool:offer-binding"},
		{name: "tool-schema", task: Task{Prompt: "hello", Pins: Pins{ToolSchemas: []ToolSchemaPin{{Name: "mcp__tei__model_catalog"}}}}, want: "tool:offer-binding"},
		{name: "skill", task: Task{Prompt: "hello", Skills: []SkillPin{{ID: "tei"}}}, want: "skill:placement"},
		{name: "context", task: Task{Prompt: "hello", ContextRefs: []ContextRef{{Kind: "source", Ref: "A"}}}, want: "context:projection"},
		{name: "resume", task: Task{Prompt: "hello"}, session: &SessionRef{ExternalID: "old"}, want: "session:resume"},
		{name: "prompt", task: Task{}, want: "task:empty-prompt"},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			f := &FakeRunner{}
			a := NewCodexExecAdapter("/fixed")
			a.Runner = f
			got, err := a.Run(context.Background(), tc.task, tc.session)
			if err != nil {
				t.Fatal(err)
			}
			if got.Transport != TransportNotAttempted || got.Run != RunUnknown || len(f.Calls) != 0 ||
				len(got.Unsupported) != 1 || got.Unsupported[0] != tc.want {
				t.Fatalf("did not fail closed: %+v", got)
			}
		})
	}
}

func TestCodexExecIncompleteResultsDoNotPass(t *testing.T) {
	tests := []struct {
		name, raw string
		exit      int
		want      RunState
	}{
		{"failed-turn", strings.Replace(codexOKJSONL, `{"type":"turn.completed","usage":{"input_tokens":10,"output_tokens":7}}`, `{"type":"turn.failed","error":{"message":"out of quota"}}`, 1), 1, RunError},
		{"incomplete-item", `{"type":"thread.started","thread_id":"a"}
{"type":"turn.started"}
{"type":"item.started","item":{"id":"m","type":"mcp_tool_call"}}
{"type":"turn.completed","usage":{}}
`, 0, RunUnknown},
		{"missing-tool-result", `{"type":"thread.started","thread_id":"a"}
{"type":"turn.started"}
{"type":"item.started","item":{"id":"m","type":"mcp_tool_call","server":"tei","tool":"model_catalog"}}
{"type":"item.completed","item":{"id":"m","type":"mcp_tool_call","server":"tei","tool":"model_catalog","status":"completed","result":null}}
{"type":"turn.completed","usage":{}}
`, 0, RunUnknown},
		{"no-terminal", `{"type":"thread.started","thread_id":"a"}
{"type":"turn.started"}
`, 0, RunUnknown},
		{"bad-json", codexOKJSONL + `{"type":"item.`, 0, RunUnknown},
		{"exit-nonzero", codexOKJSONL, 7, RunError},
		{"no-thread", `{"type":"turn.started"}
{"type":"turn.completed","usage":{}}
`, 0, RunUnknown},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			a := NewCodexExecAdapter("/fixed")
			a.Runner = &FakeRunner{Default: ExecResult{ExitCode: tc.exit, Stdout: []byte(tc.raw)}}
			got, err := a.Run(context.Background(), Task{Prompt: "safe"}, nil)
			if err != nil {
				t.Fatal(err)
			}
			if got.Run != tc.want || got.Receipt.State != ReceiptNotObserved {
				t.Fatalf("incorrect result %s: %+v", tc.name, got)
			}
		})
	}
}

func TestCodexExecRefusesOversizedOutputAndUnknownRoot(t *testing.T) {
	f := &FakeRunner{Default: ExecResult{ExitCode: 0, Stdout: []byte(codexOKJSONL)}}
	a := NewCodexExecAdapter("")
	a.Runner = f
	r, err := a.Run(context.Background(), Task{Prompt: "safe"}, nil)
	if err != nil || len(r.Unsupported) != 1 || r.Unsupported[0] != "workspace:unqualified" || len(f.Calls) != 0 {
		t.Fatalf("unqualified workspace must fail: %+v %v", r, err)
	}
	a.WorkDir = "/fixed"
	r, err = a.Run(context.Background(), Task{Prompt: "safe", Limits: Limits{MaxOutBytes: 8}}, nil)
	if err != nil || r.Run != RunUnknown || r.Reason != "output-limit" || len(f.Calls) != 1 {
		t.Fatalf("output limit did not fail safely: %+v %v", r, err)
	}
}

func TestCodexExecProbeDoesNotAssumeInstallation(t *testing.T) {
	a := NewCodexExecAdapter("/fixed")
	a.PathResolver = FakePathResolver{Paths: map[string]string{}}
	unavailable, err := a.Probe(context.Background())
	if err != nil || unavailable.Reachable {
		t.Fatalf("probe fabricated success: %+v %v", unavailable, err)
	}
	f := &FakeRunner{Default: ExecResult{ExitCode: 0, Stdout: []byte("codex-cli 1.2")}}
	a.Runner = f
	a.PathResolver = FakePathResolver{Paths: map[string]string{"codex": "/binary/codex"}}
	available, err := a.Probe(context.Background())
	if err != nil || !available.Reachable || available.Detail["version"] != "codex-cli 1.2" ||
		len(f.Calls) != 1 || len(f.Calls[0].Argv) != 2 || f.Calls[0].Argv[1] != "--version" {
		t.Fatalf("version probe unexpected: %+v %v", available, err)
	}
}

func TestParseCodexExecUnknownEventAndSplitTerminal(t *testing.T) {
	s, err := ParseCodexExecJSONL([]byte(`{"type":"thread.started","thread_id":"abc"}
{"type":"turn.started"}
{"type":"experimental.new-kind","token":"unknown"}
{"type":"turn.completed","usage":{}}
`))
	if err != nil || s.UnknownEvents != 1 || s.Terminal != "turn.completed" {
		t.Fatalf("unknown event should remain observable: %+v %v", s, err)
	}
	_, err = ParseCodexExecJSONL([]byte(`{"type":"thread.started","thread_id":"abc"}
{"type":"turn.started"}
{"type":"turn.completed","usage":{}}
{"type":"turn.failed","error":{"message":"after completion"}}
`))
	if err == nil {
		t.Fatal("conflicting terminal accepted")
	}
}

// TestCodexExecExactVersionPin prevents an unattended vendor upgrade from
// silently qualifying a different external CLI. It is not binary-byte proof.
func TestCodexExecExactVersionPin(t *testing.T) {
	const expected = "codex-cli 1.2.0"
	f := &FakeRunner{Script: []FakeStep{
		{Match: "--version", Result: ExecResult{ExitCode: 0, Stdout: []byte("codex-cli 1.3.0\n")}},
		{Match: "exec --json", Result: ExecResult{ExitCode: 0, Stdout: []byte(codexOKJSONL)}},
	}}
	a := NewCodexExecAdapter("/fixed")
	a.Runner = f
	a.PathResolver = FakePathResolver{Paths: map[string]string{"codex": "/installed/codex"}}
	a.ExpectedVersion = expected

	unavailable, err := a.Probe(context.Background())
	if err != nil || unavailable.Reachable || unavailable.Detail["version"] != "codex-cli 1.3.0" {
		t.Fatalf("upgraded CLI must be ineligible: %+v %v", unavailable, err)
	}
	got, err := a.Run(context.Background(), Task{Prompt: "Explain Source A"}, nil)
	if err != nil || got.Transport != TransportNotAttempted || got.Run != RunUnknown ||
		len(got.Unsupported) != 1 || got.Unsupported[0] != "harness:version-not-qualified" {
		t.Fatalf("direct Run bypassed version preflight: %+v %v", got, err)
	}
	for _, call := range f.Calls {
		if len(call.Argv) > 1 && call.Argv[1] == "exec" {
			t.Fatal("executed an unqualified Codex version")
		}
	}

	// The same pin may qualify a known version. A real provider, sandbox and
	// actual binary digest are independent checks, not inferred from this probe.
	f.Script[0].Result.Stdout = []byte(expected + "\n")
	got, err = a.Run(context.Background(), Task{Prompt: "Explain Source A"}, nil)
	if err != nil || got.Run != RunCompleted || got.Observations["codex-cli-version"] != expected ||
		got.Receipt.State != ReceiptNotObserved || got.Promoted() {
		t.Fatalf("qualified version did not preserve result boundaries: %+v %v", got, err)
	}
}

func TestCodexExecUnknownControlEventRequiresRequalification(t *testing.T) {
	const control = "{\"type\":\"turn.new_vendor_stage\"}\n"
	raw := strings.Replace(codexOKJSONL, "{\"type\":\"turn.completed\"", control+"{\"type\":\"turn.completed\"", 1)
	s, err := ParseCodexExecJSONL([]byte(raw))
	if err != nil || s.UnknownEvents != 1 || s.UnknownControlEvents != 1 {
		t.Fatalf("new lifecycle event not identified: %+v %v", s, err)
	}
	a := NewCodexExecAdapter("/fixed")
	a.Runner = &FakeRunner{Default: ExecResult{ExitCode: 0, Stdout: []byte(raw)}}
	r, err := a.Run(context.Background(), Task{Prompt: "Explain Source A"}, nil)
	if err != nil || r.Run != RunUnknown || r.Observations["unrecognized-control-events"] != "1" {
		t.Fatalf("unknown lifecycle drift treated as completed: %+v %v", r, err)
	}

	// An unrelated optional telemetry event is visible but does not redefine
	// the lifecycle; it must not silently disappear from the evidence.
	metadata := strings.Replace(codexOKJSONL, "{\"type\":\"turn.completed\"",
		"{\"type\":\"optional.telemetry\"}\n{\"type\":\"turn.completed\"", 1)
	s, err = ParseCodexExecJSONL([]byte(metadata))
	if err != nil || s.UnknownEvents != 1 || s.UnknownControlEvents != 0 {
		t.Fatalf("telemetry event was misclassified: %+v %v", s, err)
	}
	a.Runner = &FakeRunner{Default: ExecResult{ExitCode: 0, Stdout: []byte(metadata)}}
	r, err = a.Run(context.Background(), Task{Prompt: "Explain Source A"}, nil)
	if err != nil || r.Run != RunCompleted || r.Observations["unrecognized-events"] != "1" {
		t.Fatalf("harmless optional event was misclassified: %+v %v", r, err)
	}

	// No later event can be reinterpreted as part of the completed turn.
	_, err = ParseCodexExecJSONL([]byte(codexOKJSONL + "{\"type\":\"item.updated\",\"item\":{}}\n"))
	if err == nil {
		t.Fatal("event after turn terminal was accepted")
	}
}

// TestCodexExecToolLifecycleGuards treats a completed-only tool event as
// unqualified, even though Codex can emit a synthesized item id for it.
// The versioned C1 comparison must not invent the missing request/response link.
func TestCodexExecToolLifecycleGuards(t *testing.T) {
	const head = "{\"type\":\"thread.started\",\"thread_id\":\"a\"}\n{\"type\":\"turn.started\"}\n"
	const started = "{\"type\":\"item.started\",\"item\":{\"id\":\"m\",\"type\":\"mcp_tool_call\",\"server\":\"tei\",\"tool\":\"catalog\"}}\n"
	const done = "{\"type\":\"item.completed\",\"item\":{\"id\":\"m\",\"type\":\"mcp_tool_call\",\"server\":\"tei\",\"tool\":\"catalog\",\"status\":\"completed\",\"result\":{\"content\":[]}}}\n"
	const tail = "{\"type\":\"turn.completed\",\"usage\":{}}\n"
	tests := []struct { name, stream string }{
		{"completed-tool-without-start", head + done + tail},
		{"duplicate-tool-start", head + started + started + done + tail},
		{"duplicate-tool-completion", head + started + done + done + tail},
		{"changed-tool-name", head + started +
			strings.Replace(done, "\"tool\":\"catalog\"", "\"tool\":\"write\"", 1) + tail},
		{"changed-tool-type", head + started +
			strings.Replace(done, "\"type\":\"mcp_tool_call\"", "\"type\":\"command_execution\"", 1) + tail},
		{"changed-tool-during-update", head + started +
			"{\"type\":\"item.updated\",\"item\":{\"id\":\"m\",\"type\":\"mcp_tool_call\",\"server\":\"other\",\"tool\":\"catalog\"}}\n" + done + tail},
		{"updated-tool-without-start", head +
			"{\"type\":\"item.updated\",\"item\":{\"id\":\"m\",\"type\":\"mcp_tool_call\",\"server\":\"tei\",\"tool\":\"catalog\"}}\n" + tail},
		{"unknown-final-status", head + started + strings.Replace(done, "\"status\":\"completed\"", "\"status\":\"in_progress\"", 1) + tail},
		{"duplicate-thread-start", head + "{\"type\":\"thread.started\",\"thread_id\":\"a\"}\n" + started + done + tail},
		{"tool-before-turn", "{\"type\":\"thread.started\",\"thread_id\":\"a\"}\n" + started +
			"{\"type\":\"turn.started\"}\n" + done + tail},
		{"turn-before-thread", "{\"type\":\"turn.started\"}\n" + head + started + done + tail},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			_, err := ParseCodexExecJSONL([]byte(tc.stream))
			if err == nil { t.Fatal("invalid lifecycle accepted as complete") }
			a := NewCodexExecAdapter("/fixed")
			a.Runner = &FakeRunner{Default: ExecResult{Stdout: []byte(tc.stream), ExitCode: 0}}
			out, err := a.Run(context.Background(), Task{Prompt: "read public TEI"}, nil)
			if err != nil || out.Run != RunUnknown || out.Receipt.State != ReceiptNotObserved || out.Promoted() {
				t.Fatalf("unqualified native tool promoted: %+v err=%v", out, err)
			}
		})
	}
}

func TestCodexExecMissingCommandExitAndReadonlyEffects(t *testing.T) {
	const head = "{\"type\":\"thread.started\",\"thread_id\":\"a\"}\n{\"type\":\"turn.started\"}\n"
	const tail = "{\"type\":\"turn.completed\",\"usage\":{}}\n"
	tests := []struct {
		name, stream, observation, value string
		unknown bool
	}{
		{"command-exit-not-observed", head +
			"{\"type\":\"item.started\",\"item\":{\"id\":\"c\",\"type\":\"command_execution\",\"command\":\"cat public.md\"}}\n" +
			"{\"type\":\"item.completed\",\"item\":{\"id\":\"c\",\"type\":\"command_execution\",\"command\":\"cat public.md\",\"status\":\"completed\",\"aggregated_output\":\"ok\",\"exit_code\":null}}\n" + tail,
			"command-exits-missing", "1", true},
		{"command-exit-observed", head +
			"{\"type\":\"item.started\",\"item\":{\"id\":\"c\",\"type\":\"command_execution\",\"command\":\"cat public.md\"}}\n" +
			"{\"type\":\"item.completed\",\"item\":{\"id\":\"c\",\"type\":\"command_execution\",\"command\":\"cat public.md\",\"status\":\"completed\",\"aggregated_output\":\"ok\",\"exit_code\":0}}\n" + tail,
			"command-exits-missing", "0", false},
		{"read-only-file-change", head +
			"{\"type\":\"item.completed\",\"item\":{\"id\":\"f\",\"type\":\"file_change\",\"changes\":[{\"path\":\"public.md\",\"kind\":\"update\"}],\"status\":\"completed\"}}\n" + tail,
			"file-change-events", "1", true},
		{"model-route-changed", head +
			"{\"type\":\"item.completed\",\"item\":{\"id\":\"e\",\"type\":\"error\",\"message\":\"model rerouted: pinned -> other (quota)\"}}\n" + tail,
			"model-reroute-events", "1", true},
		{"generic-warning-is-not-model-reroute", head +
			"{\"type\":\"item.completed\",\"item\":{\"id\":\"e\",\"type\":\"error\",\"message\":\"optional config warning\"}}\n" + tail,
			"model-reroute-events", "0", false},
		{"failed-mcp-without-error-detail", head +
			"{\"type\":\"item.started\",\"item\":{\"id\":\"m\",\"type\":\"mcp_tool_call\",\"server\":\"tei\",\"tool\":\"catalog\"}}\n" +
			"{\"type\":\"item.completed\",\"item\":{\"id\":\"m\",\"type\":\"mcp_tool_call\",\"server\":\"tei\",\"tool\":\"catalog\",\"status\":\"failed\",\"error\":null}}\n" + tail,
			"tool-results-missing", "1", true},
		{"failed-mcp-with-error-detail", head +
			"{\"type\":\"item.started\",\"item\":{\"id\":\"m\",\"type\":\"mcp_tool_call\",\"server\":\"tei\",\"tool\":\"catalog\"}}\n" +
			"{\"type\":\"item.completed\",\"item\":{\"id\":\"m\",\"type\":\"mcp_tool_call\",\"server\":\"tei\",\"tool\":\"catalog\",\"status\":\"failed\",\"error\":{\"message\":\"read denied\"}}}\n" + tail,
			"tool-results-missing", "0", false},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			a := NewCodexExecAdapter("/fixed")
			a.Runner = &FakeRunner{Default: ExecResult{Stdout: []byte(tc.stream), ExitCode: 0}}
			out, err := a.Run(context.Background(), Task{Prompt: "read public TEI"}, nil)
			if err != nil { t.Fatal(err) }
			want := RunCompleted
			if tc.unknown { want = RunUnknown }
			if out.Run != want || out.Observations[tc.observation] != tc.value ||
				out.Receipt.State != ReceiptNotObserved || out.Promoted() {
				t.Fatalf("evidence was promoted or lost: %+v", out)
			}
			if tc.name == "failed-mcp-with-error-detail" {
				if len(out.ToolCalls) != 1 || out.ToolCalls[0].HarnessStatus != "failed" ||
					out.ToolCalls[0].ResultBytes == 0 || out.ToolCalls[0].ProductVerdict != nil {
					t.Fatalf("tool failure must stay a harness observation: %+v", out.ToolCalls)
				}
			}
		})
	}
}
