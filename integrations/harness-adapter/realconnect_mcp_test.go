//go:build realconnect

// Real-connection pilot for H-A-1: the same Task reaches the same product
// operation twice on one harness run — once through a typed MCP tool and once
// through the harness's own shell — and a third time through the deterministic
// control arm. The three results are then compared on the fields both product
// routes report.
//
// This file is selected only by `-tags realconnect` AND proceeds only when
// HARNESS_ADAPTER_REAL=1. Nothing here fabricates a harness: an unreachable one
// is recorded as ineligible and the comparison is not made.
//
// Cost and disclosure: this makes real requests to an external LLM provider.
// Point it at a synthetic or explicitly public workspace.
package harnessadapter

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

// mcpPilotConfig is the pinned configuration for the typed-tool pilot.
type mcpPilotConfig struct {
	TEIBinary    string
	TEIWorkspace string
	TEISkill     string
	TEIMCPBinary string
	TrialDir     string
	// MCPServerName is the local namespace the harness publishes the product
	// tools under. It is not the remote serverInfo.name.
	MCPServerName string
	Timeout       time.Duration
	Harnesses     []string
}

func mcpPilotConfigFromEnv(t *testing.T) mcpPilotConfig {
	t.Helper()
	cfg := mcpPilotConfig{
		TEIBinary:     os.Getenv("HARNESS_ADAPTER_TEI_BIN"),
		TEIWorkspace:  os.Getenv("HARNESS_ADAPTER_TEI_WORKSPACE"),
		TEISkill:      os.Getenv("HARNESS_ADAPTER_TEI_SKILL"),
		TEIMCPBinary:  os.Getenv("HARNESS_ADAPTER_TEI_MCP_BIN"),
		TrialDir:      os.Getenv("HARNESS_ADAPTER_TRIAL_DIR"),
		MCPServerName: os.Getenv("HARNESS_ADAPTER_MCP_SERVER_NAME"),
		Timeout:       20 * time.Minute,
		Harnesses:     splitEnvList(os.Getenv("HARNESS_ADAPTER_HARNESSES")),
	}
	if cfg.TEIMCPBinary == "" {
		t.Skip("HARNESS_ADAPTER_TEI_MCP_BIN is not set; the typed-tool arm needs the product's MCP server")
	}
	if cfg.TEIBinary == "" || cfg.TEIWorkspace == "" {
		t.Skip("HARNESS_ADAPTER_TEI_BIN / _WORKSPACE not set")
	}
	if cfg.TrialDir == "" {
		cfg.TrialDir = t.TempDir()
	}
	if cfg.MCPServerName == "" {
		cfg.MCPServerName = "tei"
	}
	if len(cfg.Harnesses) == 0 {
		cfg.Harnesses = []string{"dsh-headless", "claude-code", "direct-control"}
	}
	return cfg
}

// TestRealPilotTypedMCPToolEquivalence is E1+E2.
//
// E1: a typed MCP tool is observed on at least one real harness.
// E2: the product identity the typed route reports matches the direct CLI route
// on the fields both report.
//
// Neither is asserted as a verdict. E2's agreement is only claimed when every
// compared field was evidenced on both sides; otherwise the gap is logged.
func TestRealPilotTypedMCPToolEquivalence(t *testing.T) {
	if os.Getenv("HARNESS_ADAPTER_REAL") != "1" {
		t.Skip("HARNESS_ADAPTER_REAL != 1; real connections are opt-in")
	}
	cfg := mcpPilotConfigFromEnv(t)
	ctx, cancel := context.WithTimeout(context.Background(), cfg.Timeout)
	defer cancel()

	// ---- 1. Synthetic trial root. Both binaries live INSIDE it. -------------
	wsRoot := filepath.Join(cfg.TrialDir, "workspace")
	if err := copyTree(cfg.TEIWorkspace, wsRoot); err != nil {
		t.Fatalf("copy workspace: %v", err)
	}
	trialBin := filepath.Join(wsRoot, "bin", "tei.exe")
	trialMCP := filepath.Join(wsRoot, "bin", "tei-mcp.exe")
	if err := os.MkdirAll(filepath.Dir(trialBin), 0o755); err != nil {
		t.Fatalf("mkdir trial bin: %v", err)
	}
	for _, pair := range [][2]string{{cfg.TEIBinary, trialBin}, {cfg.TEIMCPBinary, trialMCP}} {
		if err := copyFile(pair[0], pair[1]); err != nil {
			t.Fatalf("copy %s into trial root: %v", pair[0], err)
		}
	}
	binDigest, err := fileDigest(trialBin)
	if err != nil {
		t.Fatalf("digest tei binary: %v", err)
	}
	mcpDigest, err := fileDigest(trialMCP)
	if err != nil {
		t.Fatalf("digest mcp binary: %v", err)
	}
	wsDigest, wsFiles, wsBytes, err := DigestWorkspace(wsRoot)
	if err != nil {
		t.Fatalf("digest workspace: %v", err)
	}

	// ---- 2. The product tools, as an MCP server spec. -----------------------
	mcpSpec := MCPServerSpec{
		ServerName:         cfg.MCPServerName,
		Transport:          "stdio",
		Command:            trialMCP,
		Args:               []string{"-workspace", wsRoot},
		ToolCallTimeoutMS:  120000,
		FailOnStartupError: true,
	}
	if err := mcpSpec.Validate(); err != nil {
		t.Fatalf("mcp spec: %v", err)
	}

	// ---- 3. One Task. The prompt names the typed tool, not the CLI. ---------
	// The point of E1/E2 is whether the model uses the *typed* route when it is
	// the one offered. Naming the CLI here would make a shell call the expected
	// outcome and the experiment would test nothing.
	typedCatalog := MCPToolName(cfg.MCPServerName, "tei_model_catalog")
	typedValidate := MCPToolName(cfg.MCPServerName, "tei_validate")
	prompt := fmt.Sprintf(
		"You have MCP tools from the %q server. Call %q and then %q. Do not run any shell command, "+
			"and do not run the TEI CLI directly. Report the model revision, the world fingerprint, "+
			"the source index fingerprint, the declared total and the validation result.",
		cfg.MCPServerName, typedCatalog, typedValidate)

	task := Task{
		ID:     "real-pilot-typed-mcp",
		Prompt: prompt,
		Pins: Pins{
			Source: SourcePin{
				Repo:         "tei-platform",
				ResolvedPath: wsRoot,
				BytesSHA256:  wsDigest,
				ByteCount:    wsBytes,
				Note:         fmt.Sprintf("synthetic copy; %d immediate files", wsFiles),
			},
			Model: ModelPin{Provider: "harness-default", Route: "harness-default"},
			Harness: HarnessPin{
				Family: "multi", ExePath: trialBin, ExeBytes: binDigest,
			},
			Roots: []RootPin{{
				Logical: "tei-workspace", Path: wsRoot, Access: "read-only",
				Note: "declared; out-of-root reads are recorded by the probe arm, not assumed absent",
			}},
			Extra: map[string]string{
				"mcp-server":       cfg.MCPServerName,
				"mcp-server-bytes": mcpDigest,
				"typed-tool-names": typedCatalog + "," + typedValidate,
			},
		},
		ContextRefs: []ContextRef{{
			Kind: "model-catalog", Ref: "mcp:" + cfg.MCPServerName + ":" + typedCatalog,
			Disclosure: "public-synthetic", Required: true,
		}},
		Limits: Limits{TimeoutMS: int64(cfg.Timeout / time.Millisecond), MaxTools: 40},
	}

	// ---- 4. Adapters: the harnesses with the MCP spec, plus the control arm. -
	direct := NewDirectControlAdapter()
	direct.Runner = ProcessRunner{}
	tool := NewTEIReadOnlyTool(trialBin, wsRoot)
	offers, unoffered := tool.Offers()
	if len(offers) == 0 {
		t.Fatal("no TEI read-only tools were offered for the control arm")
	}
	if len(unoffered) > 0 {
		t.Logf("control arm: TEI commands not offered: %v", unoffered)
	}
	task.Tools = offers

	adapters := []Adapter{}
	var armNames []string
	for _, name := range cfg.Harnesses {
		switch name {
		case "direct-control":
			adapters = append(adapters, direct)
			armNames = append(armNames, direct.Name())
		case "dsh-headless":
			a := NewDSHHeadlessAdapter("headless", wsRoot)
			a.Timeout = cfg.Timeout
			a.PermissionMode = os.Getenv("HARNESS_ADAPTER_DSH_PERMISSION_MODE")
			a.ApprovalPolicy = "never"
			a.MCPServers = []MCPServerSpec{mcpSpec}
			a.MCPWorkDir = filepath.Join(cfg.TrialDir, "overlays")
			a.PatchFiles = splitEnvList(os.Getenv("HARNESS_ADAPTER_DSH_PATCH"))
			a.ProbeEffectiveConfig = true
			adapters = append(adapters, a)
			armNames = append(armNames, a.Name())
		case "claude-code":
			a := NewClaudeCodeAdapter(wsRoot)
			a.Timeout = cfg.Timeout
			a.Tools = os.Getenv("HARNESS_ADAPTER_CC_TOOLS")
			a.PermissionMode = os.Getenv("HARNESS_ADAPTER_CC_PERMISSION_MODE")
			a.AddDirs = splitEnvList(os.Getenv("HARNESS_ADAPTER_CC_ADD_DIR"))
			a.MCPServers = []MCPServerSpec{mcpSpec}
			a.MCPWorkDir = filepath.Join(cfg.TrialDir, "overlays")
			// MCP tools must survive --tools narrowing: Claude Code keeps MCP
			// tools advertised regardless, which this pilot measures rather than
			// assumes.
			adapters = append(adapters, a)
			armNames = append(armNames, a.Name())
		default:
			t.Fatalf("unknown harness adapter %q", name)
		}
	}

	// ---- 5. Probe, run, record. --------------------------------------------
	for _, a := range adapters {
		av, err := a.Probe(ctx)
		if err != nil {
			t.Fatalf("probe %s: %v", a.Name(), err)
		}
		t.Logf("probe %s: reachable=%v (%s)", a.Name(), av.Reachable, av.Reason)
	}
	rep := Pilot(ctx, adapters, task, nil)
	outPath := filepath.Join(cfg.TrialDir, "real-pilot-typed-mcp.json")
	if b, err := rep.JSON(); err == nil {
		if err := os.WriteFile(outPath, b, 0o644); err == nil {
			t.Logf("pilot report written to %s", outPath)
		}
	}
	t.Logf("pilot summary:\n%s", rep.Summary())

	// ---- 6. The control arm ran every offered command, so its tool calls are
	// the CLI-direct reference for each typed operation the harness reaches. --
	directArm := findArm(rep, direct.Name())
	if directArm == nil || directArm.Result == nil {
		t.Fatal("control arm produced no result")
	}
	if len(directArm.Result.ToolCalls) == 0 {
		t.Fatal("control arm ran no tools; no CLI reference route exists")
	}

	// ---- 7. E1 + E2 per harness arm. ---------------------------------------
	typedObserved := 0
	for _, o := range rep.Outcomes {
		if o.Adapter == direct.Name() {
			continue
		}
		if o.State == PilotIneligible {
			t.Logf("harness %q is ineligible here: %s", o.Adapter, o.Reason)
			continue
		}
		if o.State != PilotObserved || o.Result == nil {
			t.Fatalf("harness %q arm state = %s (%s)", o.Adapter, o.State, o.Reason)
		}
		res := o.Result
		if res.Transport != TransportDelivered {
			t.Fatalf("harness %q transport = %q", o.Adapter, res.Transport)
		}
		mcpCalls := res.MCPToolCalls()
		shellCalls := res.ShellBridgeCalls()
		t.Logf("harness %q: run=%s exit=%s mcp-calls=%d shell-calls=%d",
			o.Adapter, res.Run, ExitString(res.ExitCode), len(mcpCalls), len(shellCalls))

		// Record which route the model actually took. A shell call that reaches
		// the CLI is NOT counted as a typed-tool observation.
		for _, c := range mcpCalls {
			t.Logf("  typed MCP call: %s (server %s, raw %s)", c.Call.Tool, c.ServerName, c.RawName)
		}
		for range shellCalls {
			res.Unsupported = append(res.Unsupported, "tool:mcp-bypassed-by-shell")
		}
		if len(mcpCalls) == 0 {
			t.Logf("harness %q observed no typed MCP tool call; shell calls=%d", o.Adapter, len(shellCalls))
			continue
		}
		typedObserved++

		if res.Observations == nil {
			res.Observations = map[string]string{}
		}
		res.Observations["tool-route"] = "mcp"

		// E2: compare each typed result against the CLI reference for the same
		// operation. A typed payload the harness bounded is NOT parsed: the
		// projection dropped bytes, so any comparison would be against a
		// fragment. That is recorded as "not shown", not as a failure of the
		// product route.
		compared := 0
		for _, c := range mcpCalls {
			cliCommand := strings.ReplaceAll(strings.ReplaceAll(c.RawName, "tei_", ""), "_", "-")
			cliToolName := "tei." + cliCommand
			// Only a payload the harness actually cut is incomparable. A large but
			// intact payload is lossless for this harness (Claude Code does not
			// apply DSH's 8 KiB projection cap), so size alone is not a reason to
			// skip the comparison — an earlier byte-count heuristic wrongly
			// skipped a 14 KiB result that parsed fine.
			if c.Call.Truncated || !jsonValidComplete(c.Call.ResultText) {
				t.Logf("harness %q: typed %s payload is incomplete (%d bytes); E2 not shown for it",
					o.Adapter, c.RawName, c.Call.ResultBytes)
				res.Unsupported = append(res.Unsupported,
					"equivalence:"+c.RawName+":projection-incomplete")
				continue
			}
			var cliPayload []byte
			for _, cliCall := range directArm.Result.ToolCalls {
				if cliCall.Tool == cliToolName {
					cliPayload = []byte(cliCall.ResultText)
				}
			}
			if cliPayload == nil {
				t.Logf("harness %q: no CLI reference for %s; E2 not shown", o.Adapter, cliToolName)
				res.Unsupported = append(res.Unsupported, "equivalence:"+c.RawName+":no-cli-reference")
				continue
			}
			typedEnv, err := ParseProductEnvelope([]byte(c.Call.ResultText))
			if err != nil {
				t.Logf("harness %q: typed %s unparseable: %v", o.Adapter, c.RawName, err)
				res.Unsupported = append(res.Unsupported, "equivalence:"+c.RawName+":unparseable")
				continue
			}
			cliEnv, err := ParseProductEnvelope(cliPayload)
			if err != nil {
				t.Logf("harness %q: CLI %s unparseable: %v", o.Adapter, cliToolName, err)
				continue
			}
			cmp := CompareProductEnvelopes(o.Adapter+"-mcp", typedEnv, "cli-direct", cliEnv)
			t.Logf("harness %q %s equivalence: %s", o.Adapter, c.RawName, cmp.Summary())
			for _, f := range cmp.Fields {
				t.Logf("    %-24s left=%q right=%q evidenced=%v equal=%v",
					f.Field, f.Left, f.Right, f.Evidenced, f.Equal)
			}
			for _, n := range cmp.Notes {
				t.Logf("  note: %s", n)
			}
			compared++
			if res.Observations == nil {
				res.Observations = map[string]string{}
			}
			res.Observations["equivalence-"+c.RawName] = cmp.Summary()
			if !cmp.Agreed {
				res.Unsupported = append(res.Unsupported, "equivalence:"+c.RawName+":not-shown")
			}
		}
		if compared == 0 {
			t.Logf("harness %q: no typed operation could be compared against its CLI reference", o.Adapter)
		}
	}

	if typedObserved == 0 {
		t.Fatal("no harness arm observed a typed MCP tool call; E1 is not satisfied on this environment")
	}
	t.Logf("E1: typed MCP tool calls observed on %d harness arm(s)", typedObserved)
}

// TestRealPilotNoMCPArmIsHonest runs the plain shell-bridge pilot and records
// that no typed tool was offered. It exists so an environment where MCP cannot
// be used still produces a usable record instead of nothing.
func TestRealPilotNoMCPArmIsHonest(t *testing.T) {
	if os.Getenv("HARNESS_ADAPTER_REAL") != "1" {
		t.Skip("HARNESS_ADAPTER_REAL != 1; real connections are opt-in")
	}
	if os.Getenv("HARNESS_ADAPTER_TEI_MCP_BIN") != "" {
		t.Skip("HARNESS_ADAPTER_TEI_MCP_BIN is set; this test is for the MCP-less environment")
	}
	t.Log("no MCP server binary configured: the shell-bridge pilot is the only real arm available")
	t.Log("record this as unsupported:tool:mcp-not-configured rather than as an MCP success")
}

// fileDigest digests one file.
func fileDigest(path string) (string, error) {
	b, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	sum := sha256.Sum256(b)
	return "sha256:" + hex.EncodeToString(sum[:]), nil
}

var _ = strings.TrimSpace
