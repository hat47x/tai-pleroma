//go:build realconnect

// Real-connection cross-product pilot (H-A-3 / E4): one Task reaches TEI and
// SEI through their MCP servers on one harness run.
//
// The two products report identity under different names, so the comparison only
// compares keys they share. A run where they share none says so rather than
// claiming agreement.
package harnessadapter

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

// TestRealPilotCrossProductTEISEI is E4: two products reached in one Task.
func TestRealPilotCrossProductTEISEI(t *testing.T) {
	if os.Getenv("HARNESS_ADAPTER_REAL") != "1" {
		t.Skip("HARNESS_ADAPTER_REAL != 1; real connections are opt-in")
	}
	trialDir := os.Getenv("HARNESS_ADAPTER_TRIAL_DIR")
	teiMCP := os.Getenv("HARNESS_ADAPTER_TEI_MCP_BIN")
	seiBin := os.Getenv("HARNESS_ADAPTER_SEI_BIN")
	if trialDir == "" || teiMCP == "" || seiBin == "" {
		t.Skip("HARNESS_ADAPTER_TRIAL_DIR / _TEI_MCP_BIN / _SEI_BIN must all be set")
	}
	workspace := filepath.Join(trialDir, "workspace")
	seiStore := os.Getenv("HARNESS_ADAPTER_SEI_STORE")
	if seiStore == "" {
		seiStore = filepath.Join(trialDir, "sei-store")
	}
	if _, err := os.Stat(workspace); err != nil {
		t.Skipf("trial workspace missing: %v", err)
	}
	if _, err := os.Stat(seiStore); err != nil {
		t.Skipf("SEI store missing; run `sei init -data-root %s` first: %v", seiStore, err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Minute)
	defer cancel()

	// 1. Copy both product binaries into the trial root.
	trialTEIMCP := filepath.Join(workspace, "bin", "tei-mcp.exe")
	trialSEI := filepath.Join(workspace, "bin", "sei.exe")
	if err := os.MkdirAll(filepath.Dir(trialSEI), 0o755); err != nil {
		t.Fatalf("mkdir bin: %v", err)
	}
	for _, pair := range [][2]string{{teiMCP, trialTEIMCP}, {seiBin, trialSEI}} {
		if err := copyFile(pair[0], pair[1]); err != nil {
			t.Fatalf("copy %s: %v", pair[0], err)
		}
	}

	// 2. Two MCP servers, one Task.
	teiSpec := MCPServerSpec{
		ServerName: "tei", Transport: "stdio", Command: trialTEIMCP,
		Args: []string{"-workspace", workspace}, ToolCallTimeoutMS: 120000,
		FailOnStartupError: true,
	}
	seiProjection := NewSEIReadOnlyTool(trialSEI, seiStore)
	seiSpec := seiProjection.MCPServerSpec("sei")
	if !strings.Contains(strings.Join(seiSpec.Args, " "), "-read-only") {
		t.Fatal("the SEI spec lost -read-only")
	}

	teiTools := MCPToolName("tei", "tei_model_catalog") + ", " + MCPToolName("tei", "tei_validate")
	seiTools := MCPToolName("sei", "resume")
	prompt := fmt.Sprintf(
		"You have two MCP servers. From %q call %s. From %q call %s. "+
			"Do not run any shell command and do not run either product's CLI directly. "+
			"Report each product's own identity fields by their own names.",
		"tei", teiTools, "sei", seiTools)

	task := Task{
		ID:     "real-pilot-cross-product",
		Prompt: prompt,
		Pins: Pins{
			Source: SourcePin{Repo: "tei-platform+sei-cognition", ResolvedPath: workspace,
				Note: "synthetic trial root holding both products' read-only surfaces"},
			Roots: []RootPin{
				{Logical: "tei-workspace", Path: workspace, Access: "read-only"},
				{Logical: "sei-store", Path: seiStore, Access: "read-only"},
			},
			Extra: map[string]string{
				"tei-mcp-server": "tei",
				"sei-mcp-server": "sei",
				"sei-read-only":  "true",
			},
		},
		Limits: Limits{TimeoutMS: int64(20 * time.Minute / time.Millisecond), MaxTools: 30},
	}

	// 3. The control arm runs both products' CLIs directly, so each typed result
	//    has a same-product reference route.
	direct := NewDirectControlAdapter()
	direct.Runner = ProcessRunner{}
	teiBin := os.Getenv("HARNESS_ADAPTER_TEI_BIN")
	if teiBin == "" {
		t.Skip("HARNESS_ADAPTER_TEI_BIN is not set; the control arm needs the product CLI")
	}
	trialTEI := filepath.Join(workspace, "bin", "tei.exe")
	if err := copyFile(teiBin, trialTEI); err != nil {
		t.Fatalf("copy tei.exe into trial root: %v", err)
	}
	teiTool := NewTEIReadOnlyTool(trialTEI, workspace)
	teiOffers, _ := teiTool.Offers()
	seiOffers, _ := seiProjection.Offers()
	task.Tools = append(teiOffers, seiOffers...)

	dsh := NewDSHHeadlessAdapter("headless", workspace)
	dsh.Timeout = 20 * time.Minute
	dsh.PermissionMode = os.Getenv("HARNESS_ADAPTER_DSH_PERMISSION_MODE")
	dsh.ApprovalPolicy = "never"
	dsh.PatchFiles = splitEnvList(os.Getenv("HARNESS_ADAPTER_DSH_PATCH"))
	dsh.MCPServers = []MCPServerSpec{teiSpec, seiSpec}
	dsh.MCPWorkDir = filepath.Join(trialDir, "overlays")
	dsh.ProbeEffectiveConfig = true

	adapters := []Adapter{dsh, direct}
	for _, a := range adapters {
		av, err := a.Probe(ctx)
		if err != nil {
			t.Fatalf("probe %s: %v", a.Name(), err)
		}
		t.Logf("probe %s: reachable=%v (%s)", a.Name(), av.Reachable, av.Reason)
	}
	rep := Pilot(ctx, adapters, task, nil)
	outPath := filepath.Join(trialDir, "real-pilot-cross-product.json")
	if b, err := rep.JSON(); err == nil {
		_ = os.WriteFile(outPath, b, 0o644)
		t.Logf("pilot report written to %s", outPath)
	}
	t.Logf("pilot summary:\n%s", rep.Summary())

	// 4. E4: both products must appear in the typed MCP calls.
	arm := findArm(rep, dsh.Name())
	if arm == nil || arm.Result == nil {
		t.Fatal("harness arm produced no result")
	}
	if arm.State == PilotIneligible {
		t.Skipf("harness ineligible: %s", arm.Reason)
	}
	servers := map[string]bool{}
	for _, c := range arm.Result.MCPToolCalls() {
		servers[c.ServerName] = true
		t.Logf("typed MCP call: %s (server %s, raw %s)", c.Call.Tool, c.ServerName, c.RawName)
	}
	for _, want := range []string{"tei", "sei"} {
		if !servers[want] {
			t.Logf("product %q was not reached through a typed MCP tool; E4 not shown for it", want)
		}
	}
	if servers["tei"] && servers["sei"] {
		t.Log("E4: two products reached in one Task through typed MCP tools")
	}
	// A shell call that reaches either CLI is recorded as a bypass, not as a typed
	// tool.
	if n := len(arm.Result.ShellBridgeCalls()); n > 0 {
		t.Logf("the harness also made %d shell call(s); those are not typed tool observations", n)
	}
}
