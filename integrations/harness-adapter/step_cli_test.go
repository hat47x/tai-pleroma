package harnessadapter

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// stepRunLog is shaped after a real `step --mode json -p` run (event names and
// nesting verified against Step Code 0.1.7 on Windows).
func stepRunLog() []byte {
	return []byte(strings.Join([]string{
		`{"type":"session","version":3,"id":"01a1c9d7-3cf6-7fe6-95df-d8923f8edbb1","timestamp":"2026-11-11T09:01:28.694Z","cwd":"C:\\ws"}`,
		`{"type":"entry_appended","entry":{"type":"custom","customType":"step.activity_capabilities","data":{"version":1,"sessionId":"s","skillDiscovery":true,"skillActivation":true}},"id":"a","timestamp":"t"}`,
		`{"type":"entry_appended","entry":{"type":"custom","customType":"step.activity","data":{"version":1,"sessionId":"s","kind":"skill","stage":"discovered","resourceId":"C:\\ws\\skills\\x\\SKILL.md","name":"$yi-tei-modeling","runId":"discovery:C:\\ws\\skills\\x\\SKILL.md"}},"id":"b","timestamp":"t"}`,
		`{"type":"agent_start"}`,
		`{"type":"turn_start"}`,
		`{"type":"message_start","message":{"role":"user","content":[{"type":"text","text":"call the tool"}]}}`,
		`{"type":"message_end","message":{"role":"user","content":[{"type":"text","text":"call the tool"}]}}`,
		`{"type":"message_end","message":{"role":"assistant","model":"step-3.7-flash","content":[{"type":"toolCall","id":"call-1","name":"yi-harness-adapter-mcp__tei__tei_model_catalog","arguments":{}}]}}`,
		`{"type":"tool_execution_start","toolCallId":"call-1","toolName":"yi-harness-adapter-mcp__tei__tei_model_catalog","args":{}}`,
		`{"type":"tool_execution_end","toolCallId":"call-1","toolName":"yi-harness-adapter-mcp__tei__tei_model_catalog","result":{"content":[{"type":"text","text":"{\"ok\":true}"}],"isError":false}}`,
		`{"type":"message_end","message":{"role":"assistant","model":"step-3.7-flash","content":[{"type":"text","text":"the world fingerprint is sha256:abc"}],"usage":{"input":10,"output":5}}}`,
		`{"type":"turn_end"}`,
		`{"type":"agent_end","willRetry":false}`,
		`{"type":"agent_settled"}`,
	}, "\n") + "\n")
}

// TestParseStepJSONStreamCompleted covers the success path.
func TestParseStepJSONStreamCompleted(t *testing.T) {
	s, err := ParseStepJSONStream(stepRunLog())
	if err != nil {
		t.Fatalf("parse: %v", err)
	}
	if s.Session.ExternalID != "01a1c9d7-3cf6-7fe6-95df-d8923f8edbb1" {
		t.Fatalf("session id = %q", s.Session.ExternalID)
	}
	if !s.Settled {
		t.Fatal("the terminal agent_settled event was not observed")
	}
	if s.ToolError {
		t.Fatal("a clean run was marked as a tool error")
	}
	if len(s.ToolCalls) != 1 {
		t.Fatalf("expected 1 tool call, got %d", len(s.ToolCalls))
	}
	if s.ToolCalls[0].Tool != "yi-harness-adapter-mcp__tei__tei_model_catalog" {
		t.Fatalf("tool = %q", s.ToolCalls[0].Tool)
	}
	if s.ToolCalls[0].HarnessStatus != "completed" {
		t.Fatalf("status = %q", s.ToolCalls[0].HarnessStatus)
	}
	if s.Model.Model != "step-3.7-flash" {
		t.Fatalf("model = %+v", s.Model)
	}
	if !strings.Contains(s.FinalText, "sha256:abc") {
		t.Fatalf("final text = %q", s.FinalText)
	}
	if len(s.SkillStages) != 1 || s.SkillStages[0] != "discovered" {
		t.Fatalf("skill stages = %v", s.SkillStages)
	}
	if s.SkillLoaded() {
		t.Fatal("Step reported only `discovered`, so SkillLoaded must be false")
	}
}

// TestParseStepJSONStreamToolError keeps a tool-level error from being reported
// as a clean turn.
func TestParseStepJSONStreamToolError(t *testing.T) {
	raw := []byte(strings.Join([]string{
		`{"type":"session","version":3,"id":"s1"}`,
		`{"type":"tool_execution_start","toolCallId":"c1","toolName":"tei__tei_validate","args":{}}`,
		`{"type":"tool_execution_end","toolCallId":"c1","toolName":"tei__tei_validate","result":{"content":[{"type":"text","text":"blocked"}],"isError":true}}`,
		`{"type":"agent_settled"}`,
	}, "\n") + "\n")
	s, err := ParseStepJSONStream(raw)
	if err != nil {
		t.Fatalf("parse: %v", err)
	}
	if !s.ToolError {
		t.Fatal("an isError result did not set ToolError")
	}
	if s.ToolCalls[0].HarnessStatus != "error" {
		t.Fatalf("status = %q", s.ToolCalls[0].HarnessStatus)
	}
}

// TestParseStepJSONStreamDeduplicatesAnnouncedAndExecuted keeps one call from
// appearing twice when both an assistant message and an execution event name it.
func TestParseStepJSONStreamDeduplicatesAnnouncedAndExecuted(t *testing.T) {
	raw := []byte(strings.Join([]string{
		`{"type":"session","version":3,"id":"s1"}`,
		`{"type":"message_end","message":{"role":"assistant","model":"m","content":[{"type":"toolCall","id":"c1","name":"tei__tei_model_catalog","arguments":{"namespace":""}}]}}`,
		`{"type":"tool_execution_start","toolCallId":"c1","toolName":"tei__tei_model_catalog","args":{"namespace":""}}`,
		`{"type":"tool_execution_end","toolCallId":"c1","toolName":"tei__tei_model_catalog","result":{"content":[{"type":"text","text":"ok"}],"isError":false}}`,
		`{"type":"agent_settled"}`,
	}, "\n") + "\n")
	s, _ := ParseStepJSONStream(raw)
	// The announced entry is kept and the execution folds into it, so the count is
	// not two records for one call.
	count := 0
	for _, c := range s.ToolCalls {
		if c.CallID == "c1" {
			count++
		}
	}
	if count != 1 {
		t.Fatalf("one call produced %d records", count)
	}
	if s.ToolCalls[len(s.ToolCalls)-1].HarnessStatus != "completed" {
		t.Fatal("the result did not fold into the announced call")
	}
}

// TestParseStepJSONStreamUnknownEventType keeps a new Step event visible.
func TestParseStepJSONStreamUnknownEventType(t *testing.T) {
	s, _ := ParseStepJSONStream([]byte(`{"type":"brand_new_event"}` + "\n"))
	if len(s.UnknownTypes) != 1 {
		t.Fatalf("unknown types = %v", s.UnknownTypes)
	}
}

// TestStepToolNameDecodesBothShapes is the naming rule: config.toml servers are
// `<server>__<tool>`, plugin-declared ones are `<pluginId>__<server>__<tool>`.
func TestStepToolNameDecodesBothShapes(t *testing.T) {
	plugin, server, raw, ok := StepToolName("yi-harness-adapter-mcp__tei__tei_model_catalog")
	if !ok || plugin != "yi-harness-adapter-mcp" || server != "tei" || raw != "tei_model_catalog" {
		t.Fatalf("plugin shape decoded wrong: %q %q %q %v", plugin, server, raw, ok)
	}
	_, server, raw, ok = StepToolName("tei__tei_model_catalog")
	if !ok || server != "tei" || raw != "tei_model_catalog" {
		t.Fatalf("config shape decoded wrong: %q %q %v", server, raw, ok)
	}
	// A DSH/Claude-style name is not a Step name.
	if _, _, _, ok := StepToolName("mcp__tei__tei_model_catalog"); ok {
		t.Fatal("an mcp__ prefixed name was decoded as a Step name")
	}
	for _, name := range []string{"pwsh", "a__b__c__d", "____", "a__"} {
		if _, _, _, ok := StepToolName(name); ok {
			t.Fatalf("%q was accepted as a Step tool name", name)
		}
	}
}

// TestStepPluginWritesManifest pins the file Step actually reads.
func TestStepPluginWritesManifest(t *testing.T) {
	dir := t.TempDir()
	p := StepPluginContract{
		PluginID:      "yi-harness-adapter-mcp",
		Name:          "YI Harness Adapter MCP",
		Description:   "trial",
		MCPServerName: "tei",
		MCPServer: MCPServerSpec{
			ServerName: "tei", Transport: "stdio",
			Command: `C:\trial\bin\tei-mcp.exe`,
			Args:    []string{"-workspace", `C:\trial\workspace`},
		},
		Dir: dir,
	}
	path, digest, err := p.WritePlugin()
	if err != nil {
		t.Fatalf("WritePlugin: %v", err)
	}
	if filepath.Base(path) != "step.plugin.json" {
		t.Fatalf("Step reads `step.plugin.json`, not %q", filepath.Base(path))
	}
	data, _ := os.ReadFile(path)
	if digest != DigestBytes(data) {
		t.Fatal("digest does not match the written bytes")
	}
	var got struct {
		ID         string `json:"id"`
		MCPServers map[string]struct {
			Command string   `json:"command"`
			Args    []string `json:"args"`
		} `json:"mcpServers"`
	}
	if err := json.Unmarshal(data, &got); err != nil {
		t.Fatalf("manifest is not JSON: %v\n%s", err, data)
	}
	if got.ID != "yi-harness-adapter-mcp" {
		t.Fatalf("id = %q", got.ID)
	}
	srv, ok := got.MCPServers["tei"]
	if !ok || srv.Command != `C:\trial\bin\tei-mcp.exe` {
		t.Fatalf("server declaration wrong: %+v", got.MCPServers)
	}
	if p.ToolName("tei_model_catalog") != "yi-harness-adapter-mcp__tei__tei_model_catalog" {
		t.Fatalf("tool name = %q", p.ToolName("tei_model_catalog"))
	}
}

// TestStepPluginRefusesUnsafeID keeps a namespace Step would reject from being
// written.
func TestStepPluginRefusesUnsafeID(t *testing.T) {
	for _, id := range []string{"", ".", "..", "has space", "slash/id"} {
		p := StepPluginContract{PluginID: id, MCPServerName: "tei",
			MCPServer: MCPServerSpec{ServerName: "tei", Transport: "stdio", Command: "x"}}
		if err := p.Validate(); err == nil {
			t.Fatalf("unsafe plugin id %q was accepted", id)
		}
	}
}

// TestStepPluginDoesNotWriteEnv is the anti-secret rule, same as for the other
// vendors: the declaration carries no literal env value.
func TestStepPluginDoesNotWriteEnv(t *testing.T) {
	dir := t.TempDir()
	p := StepPluginContract{
		PluginID: "p", MCPServerName: "tei",
		MCPServer: MCPServerSpec{ServerName: "tei", Transport: "stdio", Command: "x",
			EnvVarNames: []string{"TEI_TOKEN"}},
		Dir: dir,
	}
	path, _, err := p.WritePlugin()
	if err != nil {
		t.Fatalf("WritePlugin: %v", err)
	}
	data, _ := os.ReadFile(path)
	if strings.Contains(string(data), "TEI_TOKEN") {
		// The name may appear, but a VALUE must not. Assert no "env" object.
	}
	if strings.Contains(string(data), `"env"`) {
		t.Fatalf("an env object was written:\n%s", data)
	}
	if v := os.Getenv("TEI_TOKEN"); v != "" && strings.Contains(string(data), v) {
		t.Fatal("the environment value was written into the manifest")
	}
}

// TestStepBuildArgvIsExact pins the invocation, including the unattended
// approval flags a print-mode run needs.
func TestStepBuildArgvIsExact(t *testing.T) {
	a := NewStepCLIAdapter(`C:\ws`)
	a.Model = "step-3.7-flash"
	a.Skills = []string{`C:\ws\skills\x`}
	a.Tools = "read"
	argv := a.buildArgv(Task{ID: "t", Prompt: "call the tool"}, nil)
	want := strings.Join([]string{
		"step", "--approve", "--mode", "json", "-p",
		"--approval-mode", "auto",
		"--non-interactive-approval", "allow",
		"--model", "step-3.7-flash",
		"--skill", `C:\ws\skills\x`,
		"--tools", "read",
		"call the tool",
	}, " ")
	if strings.Join(argv, " ") != want {
		t.Fatalf("argv mismatch\n got: %v\nwant: %v", argv, want)
	}
}

// TestStepRunMapsSettledToCompleted checks the run verdict: exit 0 alone is not
// a completion.
func TestStepRunMapsSettledToCompleted(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "--mode json", Result: ExecResult{ExitCode: 0, Stdout: stepRunLog()}},
	}}
	a := NewStepCLIAdapter(`C:\ws`)
	a.Runner = fr
	// The task pins a Skill, so the arm must report whether it was loaded.
	task := Task{
		ID:     "t",
		Prompt: "p",
		Skills: []SkillPin{{ID: "yi-tei-modeling", PlacedPath: `C:\ws\skills\x\SKILL.md`}},
	}
	res, err := a.Run(context.Background(), task, nil)
	if err != nil {
		t.Fatalf("run: %v", err)
	}
	if res.Run != RunCompleted {
		t.Fatalf("run = %q", res.Run)
	}
	if res.Observations["skill-stages"] != "discovered" {
		t.Fatalf("skill stages = %q", res.Observations["skill-stages"])
	}
	// Step reports only `discovered`, so a Skill pinned for the task must be
	// reported as not-loaded rather than assumed loaded.
	if !containsString(res.Unsupported, "skill:load-not-observed") {
		t.Fatalf("an unobserved skill load was not reported: %v", res.Unsupported)
	}
}

// TestStepRunWithoutSettleIsUnknown keeps a truncated log from reading as
// completed.
func TestStepRunWithoutSettleIsUnknown(t *testing.T) {
	raw := []byte(`{"type":"session","version":3,"id":"s1"}` + "\n" +
		`{"type":"tool_execution_start","toolCallId":"c1","toolName":"tei__x","args":{}}` + "\n")
	a := NewStepCLIAdapter(`C:\ws`)
	a.Runner = &FakeRunner{Script: []FakeStep{
		{Match: "--mode json", Result: ExecResult{ExitCode: 0, Stdout: raw}},
	}}
	res, _ := a.Run(context.Background(), Task{ID: "t", Prompt: "p"}, nil)
	if res.Run != RunUnknown {
		t.Fatalf("a log with no agent_settled reported run=%q", res.Run)
	}
}

// TestStepProbeSaysAuthIsSeparate records the vendor constraint the field run
// confirmed: the binary is reachable, but no model is configured.
func TestStepProbeSaysAuthIsSeparate(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "--version", Result: ExecResult{ExitCode: 0, Stdout: []byte("0.1.7\n")}},
	}}
	a := NewStepCLIAdapter("")
	a.Runner = fr
	a.PathResolver = FakePathResolver{Paths: map[string]string{"step": "step"}}
	av, err := a.Probe(context.Background())
	if err != nil {
		t.Fatalf("probe: %v", err)
	}
	if av.Detail["version"] != "0.1.7" {
		t.Fatalf("version = %v", av.Detail)
	}
	if !strings.Contains(av.Reason, "authentication") {
		t.Fatalf("the probe reason does not separate auth from reachability: %q", av.Reason)
	}
}
