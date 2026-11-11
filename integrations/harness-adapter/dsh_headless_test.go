package harnessadapter

import (
	"context"
	"strings"
	"testing"
)

// dshCompletedStream is shaped after a real DSH 0.2.2-rc.1 headless --json run
// (event names, field names and nesting verified against the shipped
// @deepseek-ai/dsh-headless json-stream projection).
func dshCompletedStream() []byte {
	return []byte(strings.Join([]string{
		`{"type":"session","sessionId":"session-050904a2-78c8-4294-842a-91d63394f1e2","cwd":"C:\\work\\trial"}`,
		`{"type":"status","phase":"turn_start","turn":1}`,
		`{"type":"status","phase":"step_start","turn":1,"step":1}`,
		`{"type":"thinking","text":"check the workspace first"}`,
		`{"type":"text","text":"first confirm the workspace and the TEI CLI."}`,
		`{"type":"tool_call","callId":"call_1","tool":"pwsh","input":{"command":"tei.exe version","description":"check version"}}`,
		`{"type":"tool_result","callId":"call_1","status":"completed","result":"tei tei.cli.version/v0"}`,
		`{"type":"tool_call","callId":"call_2","tool":"pwsh","input":{"command":"tei.exe model catalog -workspace .\\workspace","description":"catalog"}}`,
		`{"type":"tool_result","callId":"call_2","status":"completed","result":"{\"schemaVersion\":\"tei.cli.model/v0\",\"ok\":true}"}`,
		`{"type":"status","phase":"step_end","turn":1,"step":1}`,
		`{"type":"status","phase":"turn_end","turn":1,"reason":"completed"}`,
		`{"type":"final","sessionId":"session-050904a2-78c8-4294-842a-91d63394f1e2","reason":{"kind":"completed"},"text":"sales.order.total is std.money."}`,
	}, "\n") + "\n")
}

func TestParseDSHJSONStreamCompleted(t *testing.T) {
	s, err := ParseDSHJSONStream(dshCompletedStream())
	if err != nil {
		t.Fatalf("parse: %v", err)
	}
	if s.Session.ExternalID != "session-050904a2-78c8-4294-842a-91d63394f1e2" {
		t.Fatalf("session id not captured: %q", s.Session.ExternalID)
	}
	if s.Session.State != SessionCreated {
		t.Fatalf("session state = %q", s.Session.State)
	}
	if s.FinalReason != "completed" || s.FinalText == "" {
		t.Fatalf("final not captured: reason=%q text=%q", s.FinalReason, s.FinalText)
	}
	if len(s.ToolCalls) != 2 {
		t.Fatalf("expected 2 tool calls, got %d", len(s.ToolCalls))
	}
	if s.ToolCalls[0].HarnessStatus != "completed" {
		t.Fatalf("tool status not folded into the call: %q", s.ToolCalls[0].HarnessStatus)
	}
	if s.ToolCalls[0].ResultText == "" {
		t.Fatal("tool result text was dropped")
	}
	if s.EventCounts["tool_call"] != 2 || s.EventCounts["final"] != 1 {
		t.Fatalf("event counts wrong: %v", s.EventCounts)
	}
	if s.Truncated {
		t.Fatal("truncated flag set on an untruncated stream")
	}
}

// TestParseDSHJSONStreamErrorEvent covers the case where the runner fails before
// any turn, so there is an error event and no final.
func TestParseDSHJSONStreamErrorEvent(t *testing.T) {
	raw := []byte(`{"type":"session","sessionId":"s1","cwd":"C:\\w"}` + "\n" +
		`{"type":"error","message":"session \"session-x\" does not exist; omit --session-id to start a new Session"}` + "\n")
	s, err := ParseDSHJSONStream(raw)
	if err != nil {
		t.Fatalf("parse: %v", err)
	}
	if s.ErrorMessage == "" {
		t.Fatal("error event message was dropped")
	}
	if s.FinalReason != "" {
		t.Fatalf("final reason invented: %q", s.FinalReason)
	}
	if s.Session.State != SessionCreated {
		t.Fatalf("a stream with only a session event should still report created, got %q", s.Session.State)
	}
}

// TestParseDSHJSONStreamTruncatedFlag checks that the projection's own
// truncation marker survives decoding, because a truncated projection is not a
// lossless audit record.
func TestParseDSHJSONStreamTruncatedFlag(t *testing.T) {
	raw := []byte(`{"type":"tool_result","callId":"c1","status":"completed","result":"partial","truncated":true}` + "\n")
	s, err := ParseDSHJSONStream(raw)
	if err != nil {
		t.Fatalf("parse: %v", err)
	}
	if !s.Truncated {
		t.Fatal("truncated flag was lost")
	}
	if len(s.ToolCalls) != 1 || !s.ToolCalls[0].Truncated {
		t.Fatalf("orphan tool_result not preserved as a call: %+v", s.ToolCalls)
	}
	found := false
	for _, d := range s.Diagnostics {
		if d.Code == "harness-projection-truncated" {
			found = true
		}
	}
	if !found {
		t.Fatal("truncation produced no diagnostic")
	}
}

// TestParseDSHJSONStreamUnknownEventType keeps a new harness event type visible
// as a gap instead of silently shortening the stream.
func TestParseDSHJSONStreamUnknownEventType(t *testing.T) {
	raw := []byte(`{"type":"brand_new_thing","payload":1}` + "\n")
	s, err := ParseDSHJSONStream(raw)
	if err != nil {
		t.Fatalf("parse: %v", err)
	}
	if len(s.UnknownTypes) != 1 || s.UnknownTypes[0] != "brand_new_thing" {
		t.Fatalf("unknown event type not reported: %v", s.UnknownTypes)
	}
}

// TestParseDSHJSONStreamUnparseable checks that a broken line is an error, not a
// shorter stream that looks complete.
func TestParseDSHJSONStreamUnparseable(t *testing.T) {
	_, err := ParseDSHJSONStream([]byte("{\"type\":\"session\"\n"))
	if err == nil {
		t.Fatal("a truncated JSON line parsed without error")
	}
}

// TestDSHBuildArgvIsExact pins the argv so a flag change is visible in review.
func TestDSHBuildArgvIsExact(t *testing.T) {
	a := NewDSHHeadlessAdapter("headless", `C:\work\trial`)
	a.CLI = "dsh"
	a.PermissionMode = "read-only"
	a.ApprovalPolicy = "never"
	a.AddDirs = []string{`C:\work\extra`}
	task := Task{ID: "t1", Prompt: "read the sales order model"}
	argv := a.buildArgv(task, &SessionRef{ExternalID: "session-abc"})
	want := []string{
		"dsh", "--profile", "headless", "--json",
		"--session-id", "session-abc",
		"--permission-mode", "read-only",
		"--approval-policy", "never",
		"--add-dir", `C:\work\extra`,
		"read the sales order model",
	}
	if strings.Join(argv, " ") != strings.Join(want, " ") {
		t.Fatalf("argv mismatch\n got: %v\nwant: %v", argv, want)
	}
}

// TestDSHBuildArgvOmitsEmptyFlags keeps an empty permission mode from being
// sent as an empty flag value.
func TestDSHBuildArgvOmitsEmptyFlags(t *testing.T) {
	a := NewDSHHeadlessAdapter("headless", "")
	argv := a.buildArgv(Task{ID: "t", Prompt: "x"}, nil)
	for _, f := range argv {
		if f == "" {
			t.Fatalf("empty argv element produced: %v", argv)
		}
	}
	if strings.Contains(strings.Join(argv, " "), "--permission-mode") {
		t.Fatalf("empty permission mode was sent: %v", argv)
	}
}

// TestDSHProbeReportsUnreachableHonestly is the core anti-fake check: a missing
// binary must produce Reachable=false with a reason, never a fabricated true.
func TestDSHProbeReportsUnreachableHonestly(t *testing.T) {
	a := NewDSHHeadlessAdapter("headless", "")
	a.PathResolver = FakePathResolver{Paths: map[string]string{}}
	av, err := a.Probe(context.Background())
	if err != nil {
		t.Fatalf("probe returned an error instead of a report: %v", err)
	}
	if av.Reachable {
		t.Fatal("a missing binary reported reachable")
	}
	if av.Reason == "" {
		t.Fatal("unreachable probe carried no reason")
	}
	if av.Detail["family"] != "dsh" {
		t.Fatalf("probe detail missing family: %v", av.Detail)
	}
}

// TestDSHProbeUsesRealVersionProbe checks that Reachable=true only follows an
// actual executed probe.
func TestDSHProbeUsesRealVersionProbe(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "--version", Result: ExecResult{ExitCode: 0, Stdout: []byte("0.2.2-rc.1\n")}},
	}}
	a := NewDSHHeadlessAdapter("headless", "")
	a.Runner = fr
	a.PathResolver = FakePathResolver{Paths: map[string]string{"dsh": `C:\dsh\dsh.cmd`}}
	av, err := a.Probe(context.Background())
	if err != nil {
		t.Fatalf("probe: %v", err)
	}
	if !av.Reachable {
		t.Fatalf("version probe failed unexpectedly: %s", av.Reason)
	}
	if av.Detail["version"] != "0.2.2-rc.1" {
		t.Fatalf("version not captured: %v", av.Detail)
	}
	if len(fr.Calls) != 1 || strings.Join(fr.Calls[0].Argv, " ") != `C:\dsh\dsh.cmd --version` {
		t.Fatalf("probe did not run the expected argv: %v", fr.Calls)
	}
}

// TestDSHProbeNonZeroExitIsUnreachable keeps a failing version probe from
// reading as success.
func TestDSHProbeNonZeroExitIsUnreachable(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "--version", Result: ExecResult{ExitCode: 1, Stderr: []byte("node not found\n")}},
	}}
	a := NewDSHHeadlessAdapter("headless", "")
	a.Runner = fr
	a.PathResolver = FakePathResolver{Paths: map[string]string{"dsh": "dsh"}}
	av, _ := a.Probe(context.Background())
	if av.Reachable {
		t.Fatal("a failing version probe reported reachable")
	}
	if !strings.Contains(av.Reason, "node not found") {
		t.Fatalf("reason does not carry the probe output: %q", av.Reason)
	}
}

// TestDSHRunMapsExitAndReason checks the exit/reason mapping without asserting
// that either means the product accepted anything.
func TestDSHRunMapsExitAndReason(t *testing.T) {
	cases := []struct {
		name    string
		reason  string
		exit    int
		wantRun RunState
	}{
		{"completed", "completed", 0, RunCompleted},
		{"aborted", "aborted", 1, RunAborted},
		{"user-stop", "user", 1, RunAborted},
		{"error-reason", "error", 1, RunError},
		{"no-final", "", 1, RunUnknown},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			stream := `{"type":"session","sessionId":"s","cwd":"C:\\w"}` + "\n"
			if tc.reason != "" {
				stream += `{"type":"final","sessionId":"s","reason":{"kind":"` + tc.reason + `"},"text":"t"}` + "\n"
			}
			fr := &FakeRunner{Script: []FakeStep{
				{Match: "--json", Result: ExecResult{ExitCode: tc.exit, Stdout: []byte(stream)}},
			}}
			a := NewDSHHeadlessAdapter("headless", `C:\w`)
			a.Runner = fr
			res, err := a.Run(context.Background(), Task{ID: "t", Prompt: "p"}, nil)
			if err != nil {
				t.Fatalf("run: %v", err)
			}
			if res.Run != tc.wantRun {
				t.Fatalf("run state = %q, want %q", res.Run, tc.wantRun)
			}
			if res.Transport != TransportDelivered {
				t.Fatalf("transport = %q", res.Transport)
			}
			if res.ExitCode == nil || *res.ExitCode != tc.exit {
				t.Fatalf("exit code = %v", res.ExitCode)
			}
			if res.Receipt.State != ReceiptNotObserved {
				t.Fatalf("receipt was invented: %q", res.Receipt.State)
			}
		})
	}
}

// TestDSHRunLaunchFailureIsTransportFailure separates "could not start" from
// "ran and failed".
func TestDSHRunLaunchFailureIsTransportFailure(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "--json", Result: ExecResult{LaunchError: "exec: \"dsh\": executable file not found"}},
	}}
	a := NewDSHHeadlessAdapter("headless", "")
	a.Runner = fr
	res, err := a.Run(context.Background(), Task{ID: "t", Prompt: "p"}, nil)
	if err != nil {
		t.Fatalf("run: %v", err)
	}
	if res.Transport != TransportFailed || res.Run != RunError {
		t.Fatalf("launch failure mapped to transport=%q run=%q", res.Transport, res.Run)
	}
	if res.Receipt.State != ReceiptNotObserved {
		t.Fatal("a launch failure produced a receipt")
	}
}

// TestDSHRunRecordsOutboundDigests checks that the argv and the prompt are
// digested separately, so a prompt change and a flag change are distinguishable.
func TestDSHRunRecordsOutboundDigests(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "--json", Result: ExecResult{ExitCode: 0, Stdout: []byte(`{"type":"final","sessionId":"s","reason":{"kind":"completed"},"text":"t"}` + "\n")}},
	}}
	a := NewDSHHeadlessAdapter("headless", "")
	a.Runner = fr
	res, _ := a.Run(context.Background(), Task{
		ID:     "t",
		Prompt: "read the model",
		Skills: []SkillPin{{ID: "yi-tei-modeling", PlacedPath: `C:\w\.dsh\skills\yi-tei-modeling\SKILL.md`, BytesSHA256: "sha256:abc"}},
	}, nil)
	dirs := map[string]OutboundRecord{}
	for _, o := range res.Outbound {
		dirs[o.Direction] = o
	}
	for _, want := range []string{"argv", "task-text", "skill-bytes"} {
		if _, ok := dirs[want]; !ok {
			t.Fatalf("outbound record %q missing; got %v", want, res.Outbound)
		}
	}
	if dirs["task-text"].BytesSHA256 != DigestString("read the model") {
		t.Fatalf("prompt digest wrong: %s", dirs["task-text"].BytesSHA256)
	}
	if dirs["skill-bytes"].BytesSHA256 != "sha256:abc" {
		t.Fatalf("skill digest not forwarded: %s", dirs["skill-bytes"].BytesSHA256)
	}
}

// TestDSHRunReportsUnobservedSkillLoad stops a placed skill from reading as a
// loaded one.
func TestDSHRunReportsUnobservedSkillLoad(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "--json", Result: ExecResult{ExitCode: 0, Stdout: []byte(
			`{"type":"session","sessionId":"s","cwd":"C:\\w"}` + "\n" +
				`{"type":"tool_call","callId":"c","tool":"pwsh","input":{"command":"dir"}}` + "\n" +
				`{"type":"final","sessionId":"s","reason":{"kind":"completed"},"text":"t"}` + "\n")}},
	}}
	a := NewDSHHeadlessAdapter("headless", "")
	a.Runner = fr
	res, _ := a.Run(context.Background(), Task{
		ID:     "t",
		Prompt: "p",
		Skills: []SkillPin{{ID: "yi-tei-modeling", PlacedPath: `C:\w\skills\x\SKILL.md`}},
	}, nil)
	if !containsString(res.Unsupported, "skill:load-not-observed") {
		t.Fatalf("unobserved skill load not reported: %v", res.Unsupported)
	}
}

// TestDSHRunObservedSkillLoad checks the positive case: a `skill` tool call
// naming the placed skill clears the unsupported entry.
func TestDSHRunObservedSkillLoad(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "--json", Result: ExecResult{ExitCode: 0, Stdout: []byte(
			`{"type":"session","sessionId":"s","cwd":"C:\\w"}` + "\n" +
				`{"type":"tool_call","callId":"c","tool":"skill","input":{"name":"yi-tei-modeling"}}` + "\n" +
				`{"type":"tool_result","callId":"c","status":"completed","result":"<skill_content>...</skill_content>"}` + "\n" +
				`{"type":"final","sessionId":"s","reason":{"kind":"completed"},"text":"t"}` + "\n")}},
	}}
	a := NewDSHHeadlessAdapter("headless", "")
	a.Runner = fr
	res, _ := a.Run(context.Background(), Task{
		ID:     "t",
		Prompt: "p",
		Skills: []SkillPin{{ID: "yi-tei-modeling", PlacedPath: `C:\w\skills\x\SKILL.md`}},
	}, nil)
	if containsString(res.Unsupported, "skill:load-not-observed") {
		t.Fatalf("an observed skill load was still reported as unobserved: %v", res.Unsupported)
	}
}

// TestDSHRunRejectsEmptyPrompt keeps a silent empty task from being sent.
func TestDSHRunRejectsEmptyPrompt(t *testing.T) {
	a := NewDSHHeadlessAdapter("headless", "")
	if _, err := a.Run(context.Background(), Task{ID: "t", Prompt: "   "}, nil); err == nil {
		t.Fatal("an empty prompt was accepted")
	}
}

// TestDSHBuildArgvIncludesPatchFiles pins the documented --patch mechanism, which
// is how a caller narrows the harness profile without the adapter inventing a
// configuration of its own. It also pins the ordering constraint: launcher
// flags must precede the headless app's own flags, or the app rejects them
// before any turn runs.
func TestDSHBuildArgvIncludesPatchFiles(t *testing.T) {
	a := NewDSHHeadlessAdapter("headless", "")
	a.PatchFiles = []string{`C:\trial\patch.yml`}
	argv := a.buildArgv(Task{ID: "t", Prompt: "p"}, nil)
	joined := strings.Join(argv, " ")
	if !strings.Contains(joined, `--patch C:\trial\patch.yml`) {
		t.Fatalf("patch flag missing: %v", argv)
	}
	patchIdx := indexOf(argv, "--patch")
	jsonIdx := indexOf(argv, "--json")
	if patchIdx < 0 || jsonIdx < 0 || patchIdx > jsonIdx {
		t.Fatalf("launcher flag --patch must precede the headless app flag --json: %v", argv)
	}
}

func indexOf(argv []string, want string) int {
	for i, a := range argv {
		if a == want {
			return i
		}
	}
	return -1
}

// TestDSHEffectiveModelRecordsDeclaredRouteNotTurnUse covers the gap that the
// headless --json projection carries no model: the adapter can only read the
// declared configuration, and must label it as such.
func TestDSHEffectiveModelRecordsDeclaredRouteNotTurnUse(t *testing.T) {
	dump := "- id: agent-default-model\n  name: '@deepseek-ai/dsh-agent-default-model'\n  config:\n    provider: openrouter\n    model: ~deepseek/deepseek-flash-latest\n"
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "--dump-config", Result: ExecResult{ExitCode: 0, Stdout: []byte(dump)}},
		{Match: "--json", Result: ExecResult{ExitCode: 0, Stdout: []byte(
			`{"type":"session","sessionId":"s","cwd":"C:\\w"}` + "\n" +
				`{"type":"final","sessionId":"s","reason":{"kind":"completed"},"text":"t"}` + "\n")}},
	}}
	a := NewDSHHeadlessAdapter("headless", "")
	a.Runner = fr
	a.ProbeEffectiveConfig = true
	res, err := a.Run(context.Background(), Task{ID: "t", Prompt: "p"}, nil)
	if err != nil {
		t.Fatalf("run: %v", err)
	}
	if res.ObservedModel.Model != "~deepseek/deepseek-flash-latest" {
		t.Fatalf("effective model = %+v", res.ObservedModel)
	}
	if res.ObservedModel.Route != "dsh-effective-config" {
		t.Fatalf("route = %q", res.ObservedModel.Route)
	}
	if !strings.Contains(res.Observations["effective-model-note"], "not an observation") {
		t.Fatalf("the declared route was not labelled as such: %q", res.Observations["effective-model-note"])
	}
	// The config probe must precede the task run so the record names the route
	// the task ran under.
	if len(fr.Calls) != 2 || !strings.Contains(strings.Join(fr.Calls[0].Argv, " "), "--dump-config") {
		t.Fatalf("config probe order wrong: %v", fr.Calls)
	}
}

// TestDSHEffectiveModelFailureIsRecordedNotFatal keeps a broken config probe
// from turning into a task failure.
func TestDSHEffectiveModelFailureIsRecordedNotFatal(t *testing.T) {
	fr := &FakeRunner{Script: []FakeStep{
		{Match: "--dump-config", Result: ExecResult{ExitCode: 1, Stderr: []byte("boom\n")}},
		{Match: "--json", Result: ExecResult{ExitCode: 0, Stdout: []byte(
			`{"type":"session","sessionId":"s","cwd":"C:\\w"}` + "\n" +
				`{"type":"final","sessionId":"s","reason":{"kind":"completed"},"text":"t"}` + "\n")}},
	}}
	a := NewDSHHeadlessAdapter("headless", "")
	a.Runner = fr
	a.ProbeEffectiveConfig = true
	res, err := a.Run(context.Background(), Task{ID: "t", Prompt: "p"}, nil)
	if err != nil {
		t.Fatalf("run: %v", err)
	}
	if res.Run != RunCompleted {
		t.Fatalf("run = %q; a failed config probe must not fail the task", res.Run)
	}
	if res.ObservedModel.Model != "" {
		t.Fatalf("a failed probe produced a model: %+v", res.ObservedModel)
	}
	if res.Observations["effective-model-note"] == "" {
		t.Fatal("the failed probe left no note")
	}
}

func containsString(list []string, want string) bool {
	for _, s := range list {
		if s == want {
			return true
		}
	}
	return false
}
