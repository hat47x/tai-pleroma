//go:build realconnect

// Real-connection typed-MCP pilot for Step Code (E1's second harness).
//
// Claude Code was quota-limited for this window, so Step Code 0.1.7 is the
// second harness. Its MCP path is a plugin declaration under
// `<cwd>/.stepcode/plugins/<id>/step.plugin.json`, which means:
//
//   - the plugin id becomes part of the model-facing tool name
//     (`<pluginId>__<server>__<tool>`), so the decoder must be told which shape
//     to expect;
//   - the project must be trusted (`--approve`) for the project-scoped plugin to
//     load at all;
//   - unattended writes need `--approval-mode auto --non-interactive-approval allow`,
//     which this test sets explicitly and records.
//
// The test writes the plugin only inside the caller's trial directory; it never
// touches the user's `~/.stepcode` config.
package harnessadapter

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"testing"
	"time"
)

// TestRealPilotStepTypedMCP is E1/E2 for the second harness.
func TestRealPilotStepTypedMCP(t *testing.T) {
	if os.Getenv("HARNESS_ADAPTER_REAL") != "1" {
		t.Skip("HARNESS_ADAPTER_REAL != 1; real connections are opt-in")
	}
	trialDir := os.Getenv("HARNESS_ADAPTER_TRIAL_DIR")
	teiMCP := os.Getenv("HARNESS_ADAPTER_TEI_MCP_BIN")
	teiBin := os.Getenv("HARNESS_ADAPTER_TEI_BIN")
	if trialDir == "" || teiMCP == "" || teiBin == "" {
		t.Skip("HARNESS_ADAPTER_TRIAL_DIR / _TEI_MCP_BIN / _TEI_BIN must be set")
	}
	workspace := filepath.Join(trialDir, "workspace")
	if _, err := os.Stat(workspace); err != nil {
		t.Skipf("trial workspace missing: %v", err)
	}

	// 1. Both binaries inside the trial root.
	trialMCP := filepath.Join(workspace, "bin", "tei-mcp.exe")
	trialTEI := filepath.Join(workspace, "bin", "tei.exe")
	if err := os.MkdirAll(filepath.Dir(trialMCP), 0o755); err != nil {
		t.Fatalf("mkdir bin: %v", err)
	}
	for _, pair := range [][2]string{{teiMCP, trialMCP}, {teiBin, trialTEI}} {
		if err := copyFile(pair[0], pair[1]); err != nil {
			t.Fatalf("copy %s: %v", pair[0], err)
		}
	}

	// 2. A project-scoped plugin, written only inside the trial directory.
	pluginID := "yi-harness-adapter-mcp"
	stepProject := filepath.Join(trialDir, "step-project")
	plugin := StepPluginContract{
		PluginID:      pluginID,
		Name:          "YI Harness Adapter MCP",
		Description:   "Pilot plugin: exposes the TEI read-only MCP server to Step Code.",
		MCPServerName: "tei",
		MCPServer: MCPServerSpec{
			ServerName: "tei", Transport: "stdio",
			Command:           trialMCP,
			Args:              []string{"-workspace", workspace},
			ToolCallTimeoutMS: 120000,
		},
		Dir: filepath.Join(stepProject, ".stepcode", "plugins"),
	}
	pluginPath, pluginDigest, err := plugin.WritePlugin()
	if err != nil {
		t.Fatalf("write step plugin: %v", err)
	}
	t.Logf("step plugin written to %s (%s)", pluginPath, pluginDigest)

	// 3. The Tool name the model will see.
	typedCatalog := plugin.ToolName("tei_model_catalog")
	typedValidate := plugin.ToolName("tei_validate")
	t.Logf("typed tool names: %s, %s", typedCatalog, typedValidate)

	prompt := fmt.Sprintf(
		"Call %q and then %q. Do not use any other tool, and do not run any shell command. "+
			"Report the world fingerprint and the validation result.", typedCatalog, typedValidate)

	// 4. Adapters: Step with the plugin, plus the deterministic control arm.
	direct := NewDirectControlAdapter()
	direct.Runner = ProcessRunner{}
	tool := NewTEIReadOnlyTool(trialTEI, workspace)
	offers, unoffered := tool.Offers()
	if len(offers) == 0 {
		t.Fatal("no TEI read-only tools for the control arm")
	}
	if len(unoffered) > 0 {
		t.Logf("control arm: commands not offered: %v", unoffered)
	}

	task := Task{
		ID:     "real-pilot-step-typed-mcp",
		Prompt: prompt,
		Pins: Pins{
			Source: SourcePin{Repo: "tei-platform", ResolvedPath: workspace,
				Note: "synthetic trial root"},
			Harness: HarnessPin{Family: "step-cli", Profile: "-p --mode json", ExePath: trialTEI},
			Roots:   []RootPin{{Logical: "tei-workspace", Path: workspace, Access: "read-only"}},
			Extra: map[string]string{
				"mcp-server":   "tei",
				"plugin-id":    pluginID,
				"typed-tools":  typedCatalog + "," + typedValidate,
				"plugin-bytes": pluginDigest,
			},
		},
		Tools:  offers,
		Limits: Limits{TimeoutMS: int64(20 * time.Minute / time.Millisecond), MaxTools: 30},
	}

	stepAdapter := NewStepCLIAdapter(stepProject)
	stepAdapter.Timeout = 20 * time.Minute
	stepAdapter.Model = os.Getenv("HARNESS_ADAPTER_STEP_MODEL")
	if stepAdapter.Model == "" {
		stepAdapter.Model = "step-3.7-flash"
	}
	stepAdapter.ApprovalMode = "auto"
	stepAdapter.NonInteractiveApproval = "allow"
	// The API key is supplied as an Env NAME reference resolved here, and it is
	// never written into an evidence record.
	if k := os.Getenv("STEP_API_KEY"); k != "" {
		stepAdapter.Env = []string{"STEP_API_KEY=" + k, "STEP_BASE_URL=" + envOr("STEP_BASE_URL", "https://api.stepfun.ai/step_plan/v1")}
	}

	ctx, cancel := context.WithTimeout(context.Background(), 25*time.Minute)
	defer cancel()

	av, err := stepAdapter.Probe(ctx)
	if err != nil {
		t.Fatalf("probe: %v", err)
	}
	t.Logf("step probe: reachable=%v (%s)", av.Reachable, av.Reason)
	if !av.Reachable {
		t.Skipf("Step Code not reachable: %s", av.Reason)
	}
	if _, err := direct.Probe(ctx); err != nil {
		t.Fatalf("control probe: %v", err)
	}

	rep := Pilot(ctx, []Adapter{stepAdapter, direct}, task, nil)
	outPath := filepath.Join(trialDir, "real-pilot-step-typed-mcp.json")
	if b, err := rep.JSON(); err == nil {
		_ = os.WriteFile(outPath, b, 0o644)
		t.Logf("pilot report written to %s", outPath)
	}
	t.Logf("pilot summary:\n%s", rep.Summary())

	arm := findArm(rep, stepAdapter.Name())
	if arm == nil || arm.Result == nil {
		t.Fatal("the Step arm produced no result")
	}
	if arm.State == PilotIneligible {
		t.Skipf("Step arm ineligible: %s", arm.Reason)
	}
	res := arm.Result
	if res.Transport != TransportDelivered {
		t.Fatalf("transport = %q", res.Transport)
	}
	t.Logf("step arm: run=%s exit=%s tools=%d", res.Run, ExitString(res.ExitCode), len(res.ToolCalls))
	for _, c := range res.ToolCalls {
		t.Logf("  [%s] status=%s bytes=%d", c.Tool, c.HarnessStatus, c.ResultBytes)
	}

	// 5. E1: a typed MCP call reached the product.
	typedSeen := 0
	for _, c := range res.ToolCalls {
		pluginIDDecoded, server, raw, ok := StepToolName(c.Tool)
		if !ok || server != "tei" {
			continue
		}
		t.Logf("  typed MCP call: plugin=%q server=%q raw=%q", pluginIDDecoded, server, raw)
		typedSeen++
	}
	if typedSeen == 0 {
		t.Fatalf("no Step tool call decoded as a typed MCP call; observed tools: %v", res.ToolNames())
	}
	t.Logf("E1 (Step Code): %d typed MCP call(s) observed", typedSeen)

	// 6. E2: compare each comparable typed result against the CLI reference.
	directArm := findArm(rep, direct.Name())
	if directArm == nil || directArm.Result == nil {
		t.Fatal("control arm produced no result")
	}
	compared := 0
	for _, c := range res.ToolCalls {
		_, server, raw, ok := StepToolName(c.Tool)
		if !ok || server != "tei" || c.HarnessStatus != "completed" {
			continue
		}
		cliTool := "tei." + replaceUnderscoreWithDash(stringsTrimPrefixTIE(raw))
		var cliPayload []byte
		for _, cc := range directArm.Result.ToolCalls {
			if cc.Tool == cliTool {
				cliPayload = []byte(cc.ResultText)
			}
		}
		if cliPayload == nil {
			t.Logf("no CLI reference for %s; E2 not shown for it", cliTool)
			continue
		}
		if c.ResultBytes >= 8192 {
			t.Logf("typed %s was bounded (%d bytes); E2 not shown", raw, c.ResultBytes)
			res.Unsupported = append(res.Unsupported, "equivalence:"+raw+":result-bounded")
			continue
		}
		typedEnv, err := ParseProductEnvelope([]byte(c.ResultText))
		if err != nil {
			t.Logf("typed %s unparseable: %v", raw, err)
			continue
		}
		cliEnv, err := ParseProductEnvelope(cliPayload)
		if err != nil {
			t.Logf("CLI %s unparseable: %v", cliTool, err)
			continue
		}
		cmp := CompareProductEnvelopes("step-mcp", typedEnv, "cli-direct", cliEnv)
		t.Logf("%s equivalence: %s", raw, cmp.Summary())
		for _, f := range cmp.Fields {
			t.Logf("    %-24s left=%q right=%q evidenced=%v equal=%v", f.Field, f.Left, f.Right, f.Evidenced, f.Equal)
		}
		compared++
		if res.Observations == nil {
			res.Observations = map[string]string{}
		}
		res.Observations["equivalence-"+raw] = cmp.Summary()
	}
	if compared == 0 {
		t.Log("E2: no typed operation could be compared against its CLI reference in this run")
	}
	t.Logf("divergences: %v", rep.Divergences)
}

// stringsTrimPrefixTIE strips the product's own `tei_` prefix so the raw tool
// name can be mapped to the CLI tool name.
func stringsTrimPrefixTIE(raw string) string {
	const prefix = "tei_"
	if len(raw) >= len(prefix) && raw[:len(prefix)] == prefix {
		return raw[len(prefix):]
	}
	return raw
}

// replaceUnderscoreWithDash maps `tei_model_catalog` to `model-catalog`'s CLI form.
func replaceUnderscoreWithDash(s string) string {
	out := make([]byte, 0, len(s))
	for i := 0; i < len(s); i++ {
		if s[i] == '_' {
			out = append(out, '-')
			continue
		}
		out = append(out, s[i])
	}
	return string(out)
}

// envOr returns the value of name or the fallback.
func envOr(name, fallback string) string {
	if v := os.Getenv(name); v != "" {
		return v
	}
	return fallback
}
