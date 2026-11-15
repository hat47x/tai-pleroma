package harnessadapter

import (
	"context"
	"strings"
	"testing"
)

// claudeStreamJSON is shaped after a real `claude -p --output-format
// stream-json` run (event names and nesting verified against Claude Code
// 2.1.302 on Windows).
func claudeStreamJSON() []byte {
	return []byte(strings.Join([]string{
		`{"type":"system","subtype":"init","cwd":"C:\\ws","session_id":"fa142ccc-668d-4fcf-accf-71aa8dcb7449","tools":["Bash","Read","Glob"],"model":"claude-sonnet-5-5"}`,
		`{"type":"assistant","message":{"model":"claude-sonnet-5-5","content":[{"type":"text","text":"checking the CLI"}]}}`,
		`{"type":"assistant","message":{"model":"claude-sonnet-5-5","content":[{"type":"tool_use","id":"toolu_1","name":"Bash","input":{"command":"tei.exe version","description":"version"}}]}}`,
		`{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"toolu_1","content":"tei tei.cli.version/v0","is_error":false}]}}`,
		`{"type":"assistant","message":{"model":"claude-sonnet-5-5","content":[{"type":"tool_use","id":"toolu_2","name":"Bash","input":{"command":"tei.exe model catalog -workspace .","description":"catalog"}}]}}`,
		`{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"toolu_2","content":[{"type":"text","text":"{\"ok\":true}"}],"is_error":false}]}}`,
		`{"type":"result","subtype":"success","is_error":false,"result":"total is std.money","session_id":"fa142ccc-668d-4fcf-accf-71aa8dcb7449","duration_api_ms":3474,"num_turns":3,"total_cost_usd":0.0842113,"usage":{"input_tokens":4}}`,
	}, "\n") + "\n")
}

func TestParseClaudeStreamJSON(t *testing.T) {
	s, err := ParseClaudeStreamJSON(claudeStreamJSON())
	if err != nil {
		t.Fatalf("parse: %v", err)
	}
	if s.Session.ExternalID != "fa142ccc-668d-4fcf-accf-71aa8dcb7449" {
		t.Fatalf("session id = %q", s.Session.ExternalID)
	}
	if s.Session.CWD != `C:\ws` {
		t.Fatalf("cwd = %q", s.Session.CWD)
	}
	if s.ResultSubtype != "success" {
		t.Fatalf("subtype = %q", s.ResultSubtype)
	}
	if s.FinalText != "total is std.money" {
		t.Fatalf("final text = %q", s.FinalText)
	}
	if s.Model.Model != "claude-sonnet-5-5" {
		t.Fatalf("model = %+v", s.Model)
	}
	if len(s.ToolCalls) != 2 {
		t.Fatalf("tool calls = %d", len(s.ToolCalls))
	}
	if s.ToolCalls[0].Tool != "Bash" || s.ToolCalls[0].HarnessStatus != "completed" {
		t.Fatalf("first call = %+v", s.ToolCalls[0])
	}
	if s.ToolCalls[1].ResultText != `{"ok":true}` {
		t.Fatalf("array-form tool result not normalised: %q", s.ToolCalls[1].ResultText)
	}
	if s.Observations["total-cost-usd"] == "" || s.Observations["num-turns"] != "3" {
		t.Fatalf("vendor observations missing: %v", s.Observations)
	}
	if len(s.AdvertisedTools) != 3 || s.AdvertisedTools[0] != "Bash" {
		t.Fatalf("advertised tools = %v", s.AdvertisedTools)
	}
}

// TestParseClaudeStreamJSONUnknownEventType keeps a new event type visible.
func TestParseClaudeStreamJSONUnknownEventType(t *testing.T) {
	s, err := ParseClaudeStreamJSON([]byte(`{"type":"brand_new","x":1}` + "\n"))
	if err != nil {
		t.Fatalf("parse: %v", err)
	}
	if len(s.UnknownTypes) != 1 || s.UnknownTypes[0] != "brand_new" {
		t.Fatalf("unknown types = %v", s.UnknownTypes)
	}
}

// TestParseClaudeStreamJSONErrorResult checks an error result is not read as a
// completed turn.
func TestParseClaudeStreamJSONErrorResult(t *testing.T) {
	s, err := ParseClaudeStreamJSON([]byte(
		`{"type":"result","subtype":"error_max_turns","is_error":true,"result":"out of turns","session_id":"s1","total_cost_usd":1.5}` + "\n"))
	if err != nil {
		t.Fatalf("parse: %v", err)
	}
	if s.ResultSubtype != "error_max_turns" {
		t.Fatalf("subtype = %q", s.ResultSubtype)
	}
	found := false
	for _, d := range s.Diagnostics {
		if d.Code == "claude-result-is-error" {
			found = true
		}
	}
	if !found {
		t.Fatal("an error result produced no diagnostic")
	}
}

// TestClaudeBuildArgvIsExact pins the argv, including the unattended permission
// setting that a print-mode run needs.
func TestClaudeBuildArgvIsExact(t *testing.T) {
	a := NewClaudeCodeAdapter(`C:\ws`)
	a.Tools = "Bash,Read"
	a.PermissionMode = "plan"
	a.AddDirs = []string{`C:\extra`}
	a.MCPConfigs = []string{`C:\mcp.json`}
	argv := a.buildArgv(Task{ID: "t", Prompt: "read the model"}, &SessionRef{ExternalID: "fa142ccc-668d-4fcf-accf-71aa8dcb7449"})
	want := strings.Join([]string{
		"claude", "-p", "read the model",
		"--output-format", "stream-json", "--verbose",
		"--resume", "fa142ccc-668d-4fcf-accf-71aa8dcb7449",
		"--add-dir", `C:\extra`,
		"--tools", "Bash,Read",
		"--permission-mode", "plan",
		"--permission-prompts", "none",
		"--mcp-config", `C:\mcp.json`,
	}, " ")
	if strings.Join(argv, " ") != want {
		t.Fatalf("argv mismatch\n got: %v\nwant: %v", argv, want)
	}
}

// TestClaudeRunMapsResultSubtype checks the run mapping and that a resumed id
// the harness did not adopt is recorded as rejected, not as continuity.
func TestClaudeRunMapsResultSubtype(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "stream-json", Result: ExecResult{ExitCode: 0, Stdout: claudeStreamJSON()}},
	}}
	a := NewClaudeCodeAdapter(`C:\ws`)
	a.Runner = fr
	res, err := a.Run(context.Background(), Task{ID: "t", Prompt: "p"}, nil)
	if err != nil {
		t.Fatalf("run: %v", err)
	}
	if res.Transport != TransportDelivered || res.Run != RunCompleted {
		t.Fatalf("transport=%q run=%q", res.Transport, res.Run)
	}
	if res.Session.State != SessionCreated {
		t.Fatalf("session state = %q", res.Session.State)
	}
	if res.ObservedModel.Model != "claude-sonnet-5-5" {
		t.Fatalf("observed model = %+v", res.ObservedModel)
	}
	if res.Observations["total-cost-usd"] == "" {
		t.Fatalf("cost observation missing: %v", res.Observations)
	}
	// A requested id the harness did not echo back is a refusal, not a resume.
	fr2 := &FakeRunner{Script: []FakeStep{
		{Match: "stream-json", Result: ExecResult{ExitCode: 0, Stdout: []byte(
			`{"type":"system","subtype":"init","session_id":"other-id","cwd":"C:\\ws","tools":[]}` + "\n" +
				`{"type":"result","subtype":"success","result":"t","session_id":"other-id"}` + "\n")}},
	}}
	a.Runner = fr2
	res2, _ := a.Run(context.Background(), Task{ID: "t", Prompt: "p"}, &SessionRef{ExternalID: "requested-id"})
	if res2.Session.State != SessionRejected {
		t.Fatalf("a non-adopted session id was recorded as %q", res2.Session.State)
	}
}

// TestClaudeProbeSaysAuthIsSeparate records the vendor constraint that a
// reachable binary is not an authenticated harness.
func TestClaudeProbeSaysAuthIsSeparate(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "--version", Result: ExecResult{ExitCode: 0, Stdout: []byte("2.1.302 (Claude Code)\n")}},
	}}
	a := NewClaudeCodeAdapter("")
	a.Runner = fr
	a.PathResolver = FakePathResolver{Paths: map[string]string{"claude": "claude"}}
	av, err := a.Probe(context.Background())
	if err != nil {
		t.Fatalf("probe: %v", err)
	}
	if !av.Reachable {
		t.Fatal("a working version probe reported unreachable")
	}
	if !strings.Contains(av.Reason, "authentication") {
		t.Fatalf("probe reason does not separate auth from reachability: %q", av.Reason)
	}
	if av.Detail["version"] != "2.1.302 (Claude Code)" {
		t.Fatalf("version not captured: %v", av.Detail)
	}
}

// TestClaudeSkillRootsDocumented keeps the Claude Code skill root set explicit
// rather than assuming every harness scans the same place DSH does.
func TestClaudeSkillRootsDocumented(t *testing.T) {
	roots := ClaudeSkillRoots(`C:\repo`, `C:\u\.claude`)
	if len(roots) != 2 {
		t.Fatalf("expected 2 roots, got %d", len(roots))
	}
	for _, r := range roots {
		if r.Harness != "claude-code" {
			t.Fatalf("root not labelled: %+v", r)
		}
	}
	if !strings.HasSuffix(roots[0].Path, `.claude\skills`) {
		t.Fatalf("project root is not .claude/skills: %s", roots[0].Path)
	}
}

// TestSameTaskTwoVendorAdapters is the interchangeability check in contract
// form: the DSH-shaped stream and the Claude-shaped stream decode into the same
// Result shape for the same Task, and the report names where they differ.
func TestSameTaskTwoVendorAdapters(t *testing.T) {
	task := newPilotTask()
	dshArm := &ScriptedAdapter{Family: "dsh", Reachable: true, Stream: dshCompletedStream(), ExitCode: 0}
	claudeArm := &ScriptedAdapter{Family: "claude-code", Reachable: true, Stream: claudeStreamJSON(), ExitCode: 0}
	rep := Pilot(context.Background(), []Adapter{dshArm, claudeArm}, task, nil)
	if len(rep.Outcomes) != 2 {
		t.Fatalf("expected 2 arms, got %d", len(rep.Outcomes))
	}
	for _, o := range rep.Outcomes {
		if o.State != PilotObserved {
			t.Fatalf("arm %s state = %s", o.Adapter, o.State)
		}
		if o.Result == nil || o.Result.Contract != ContractVersion {
			t.Fatalf("arm %s did not produce a contract-conformant result", o.Adapter)
		}
	}
	// Both arms observed tool use, so the comparison has something to say.
	if len(rep.Divergences) == 0 {
		t.Fatal("two vendor streams decoded to identical observations; expected a named divergence")
	}
	// The vendor-specific cost observation must not become a divergence axis.
	for _, d := range rep.Divergences {
		if d == "observations" {
			t.Fatal("vendor-specific observations were treated as a comparable axis")
		}
	}
}

// TestClaudeResultIsErrorWinsOverSuccessSubtype is a bug found by a real run:
// Claude Code returned `subtype: "success"` together with `is_error: true` and
// the message "You've hit your session limit". Reading the subtype alone
// reported `run=completed` for a turn that produced no answer — exactly the
// collapse this contract forbids.
func TestClaudeResultIsErrorWinsOverSuccessSubtype(t *testing.T) {
	raw := []byte(`{"type":"result","subtype":"success","is_error":true,"result":"You've hit your session limit · resets 7:30pm (Asia/Tokyo)","session_id":"s1","total_cost_usd":0}` + "\n")
	a := NewClaudeCodeAdapter(`C:\ws`)
	a.Runner = &FakeRunner{Script: []FakeStep{
		{Match: "stream-json", Result: ExecResult{ExitCode: 1, Stdout: raw}},
	}}
	res, err := a.Run(context.Background(), Task{ID: "t", Prompt: "p"}, nil)
	if err != nil {
		t.Fatalf("run: %v", err)
	}
	if res.Run != RunError {
		t.Fatalf("is_error=true with subtype=success reported run=%q; the error must win", res.Run)
	}
	if res.Observations["quota-limit"] == "" {
		t.Fatalf("a quota limit was not recorded as its own observation: %v", res.Observations)
	}
	if !containsString(res.Unsupported, "run:harness-quota-or-rate-limit") {
		t.Fatalf("quota condition not reported as unsupported: %v", res.Unsupported)
	}
	if !containsString(res.Unsupported, "run:harness-reported-error") {
		t.Fatalf("harness-reported error not recorded: %v", res.Unsupported)
	}
}

// TestClaudeQuotaTextIsNarrow stops an ordinary task failure from being
// relabelled as a quota event.
func TestClaudeQuotaTextIsNarrow(t *testing.T) {
	if got := quotaLimitText("I could not read the file", nil); got != "" {
		t.Fatalf("an ordinary failure was read as a quota limit: %q", got)
	}
	if got := quotaLimitText("", []Diagnostic{{Code: "claude-result-is-error", Message: "some other error"}}); got != "" {
		t.Fatalf("a non-quota diagnostic was read as a quota limit: %q", got)
	}
	if got := quotaLimitText("rate limit reached", nil); got == "" {
		t.Fatal("an explicit rate limit was not recognised")
	}
}

// TestClaudeSuccessStaysCompleted is the positive control: without is_error the
// success subtype still means completed.
func TestClaudeSuccessStaysCompleted(t *testing.T) {
	raw := []byte(`{"type":"result","subtype":"success","is_error":false,"result":"ok","session_id":"s1"}` + "\n")
	a := NewClaudeCodeAdapter(`C:\ws`)
	a.Runner = &FakeRunner{Script: []FakeStep{
		{Match: "stream-json", Result: ExecResult{ExitCode: 0, Stdout: raw}},
	}}
	res, _ := a.Run(context.Background(), Task{ID: "t", Prompt: "p"}, nil)
	if res.Run != RunCompleted {
		t.Fatalf("a clean success reported run=%q", res.Run)
	}
	if res.Observations["quota-limit"] != "" {
		t.Fatalf("a clean success produced a quota observation: %v", res.Observations)
	}
}

// TestClaudeMCPToolsStayAdvertised documents the vendor constraint measured in
// the field: Claude Code keeps MCP tools in the advertised list even after
// --tools narrows the built-in set to "Bash,Read,Glob,Grep".
func TestClaudeMCPToolsStayAdvertised(t *testing.T) {
	raw := []byte(`{"type":"system","subtype":"init","cwd":"C:\\ws","session_id":"s1","tools":["Bash","Read","Glob","Grep","mcp__tei__tei_model_catalog","mcp__tei__tei_validate"]}` + "\n" +
		`{"type":"result","subtype":"success","is_error":false,"result":"ok","session_id":"s1"}` + "\n")
	a := NewClaudeCodeAdapter(`C:\ws`)
	a.Tools = "Bash,Read,Glob,Grep"
	a.Runner = &FakeRunner{Script: []FakeStep{
		{Match: "stream-json", Result: ExecResult{ExitCode: 0, Stdout: raw}},
	}}
	res, _ := a.Run(context.Background(), Task{ID: "t", Prompt: "p"}, nil)
	tools := res.Observations["advertised-tools"]
	if !strings.Contains(tools, "mcp__tei__tei_model_catalog") {
		t.Fatalf("MCP tool was not in the advertised list: %q", tools)
	}
	if !strings.Contains(tools, "Bash") {
		t.Fatalf("built-in tools missing from the record: %q", tools)
	}
}
