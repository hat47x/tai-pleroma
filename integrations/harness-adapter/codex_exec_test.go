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
