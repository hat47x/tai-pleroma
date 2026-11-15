//go:build realconnect

// Package harnessadapter_realconnect holds the real-connection pilot: one Task
// driven through a real external harness and through the deterministic control
// arm, against a synthetic copy of a public workspace.
//
// This file is excluded from every normal build and test run. It is selected
// only by `-tags realconnect` AND only proceeds when HARNESS_ADAPTER_REAL=1.
// There is no code path here that fabricates a harness, and no code path that
// reports a semantic verdict: the assertions below check that observations were
// recorded, not that an answer was correct.
//
// Cost and disclosure: running this makes a real request to an external LLM
// provider. It must be pointed at a synthetic or explicitly public workspace.
package harnessadapter

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

// realPilotConfig is the pinned configuration for one real-connection pilot.
type realPilotConfig struct {
	TEIBinary    string
	TEIWorkspace string // source workspace to copy from
	TEISkill     string // Product Skill directory to place
	TrialDir     string
	Prompt       string
	Timeout      time.Duration
	// Harnesses names the real adapters to run. "direct-control" is always
	// included; it needs no credential.
	Harnesses []string
}

func realPilotConfigFromEnv(t *testing.T) realPilotConfig {
	t.Helper()
	cfg := realPilotConfig{
		TEIBinary:    os.Getenv("HARNESS_ADAPTER_TEI_BIN"),
		TEIWorkspace: os.Getenv("HARNESS_ADAPTER_TEI_WORKSPACE"),
		TEISkill:     os.Getenv("HARNESS_ADAPTER_TEI_SKILL"),
		TrialDir:     os.Getenv("HARNESS_ADAPTER_TRIAL_DIR"),
		Timeout:      15 * time.Minute,
		Harnesses:    splitEnvList(os.Getenv("HARNESS_ADAPTER_HARNESSES")),
	}
	if cfg.TEIBinary == "" {
		t.Skip("HARNESS_ADAPTER_TEI_BIN is not set; no real-connection pilot can run")
	}
	if cfg.TEIWorkspace == "" {
		t.Skip("HARNESS_ADAPTER_TEI_WORKSPACE is not set; refusing to invent a workspace")
	}
	if cfg.TrialDir == "" {
		cfg.TrialDir = t.TempDir()
	}
	if cfg.TEISkill == "" {
		t.Skip("HARNESS_ADAPTER_TEI_SKILL is not set; the skill-less arm is a different experiment")
	}
	if len(cfg.Harnesses) == 0 {
		cfg.Harnesses = []string{"dsh-headless", "direct-control"}
	}
	return cfg
}

// splitEnvList parses a comma-separated environment variable.
func splitEnvList(v string) []string {
	var out []string
	for _, p := range strings.Split(v, ",") {
		if p = strings.TrimSpace(p); p != "" {
			out = append(out, p)
		}
	}
	return out
}

// TestRealPilotDSHHeadlessRunsTEIReadOnly is the first-round check: one real
// external harness calls TEI's read-only CLI, and the same Task also runs
// through the deterministic control arm.
//
// It asserts observations only:
//   - the harness process was started (transport delivered),
//   - a session reference was observed when the harness reported one,
//   - at least one tool call was recorded,
//   - the pinned TEI binary appears in at least one recorded tool call,
//   - the direct-control arm independently completed the same declared tools.
//
// It does not assert that the model answered correctly, that the product
// accepted anything, or that any effect occurred.
func TestRealPilotDSHHeadlessRunsTEIReadOnly(t *testing.T) {
	if os.Getenv("HARNESS_ADAPTER_REAL") != "1" {
		t.Skip("HARNESS_ADAPTER_REAL != 1; real connections are opt-in")
	}
	cfg := realPilotConfigFromEnv(t)
	ctx, cancel := context.WithTimeout(context.Background(), cfg.Timeout)
	defer cancel()

	// 1. Resolve the source executable. Its digest is taken from the copy that
	//    actually lands inside the trial root, so the pin names the bytes the
	//    harness can reach rather than the bytes sitting in the repository.
	if _, err := os.Stat(cfg.TEIBinary); err != nil {
		t.Fatalf("pinned TEI binary: %v", err)
	}

	// 2. Build a synthetic workspace copy. Nothing outside it is offered.
	//
	// The pinned TEI binary is copied INTO the trial root rather than referenced
	// at its repository path. An earlier run of this pilot left the binary at
	// its repository path and the DSH arm read it there: the declared root and
	// the reachable bytes disagreed, and `--permission-mode read-only` did not
	// prevent it. Pinning the root now means the root claim is testable.
	wsRoot := filepath.Join(cfg.TrialDir, "workspace")
	if err := copyTree(cfg.TEIWorkspace, wsRoot); err != nil {
		t.Fatalf("copy workspace: %v", err)
	}
	trialBin := filepath.Join(wsRoot, "bin", "tei.exe")
	if err := os.MkdirAll(filepath.Dir(trialBin), 0o755); err != nil {
		t.Fatalf("mkdir trial bin: %v", err)
	}
	if err := copyFile(cfg.TEIBinary, trialBin); err != nil {
		t.Fatalf("copy binary into trial root: %v", err)
	}
	binBytes, err := os.ReadFile(trialBin)
	if err != nil {
		t.Fatalf("read pinned binary: %v", err)
	}
	sum := sha256.Sum256(binBytes)
	binDigest := "sha256:" + hex.EncodeToString(sum[:])
	wsDigest, files, wsBytes, err := DigestWorkspace(wsRoot)
	if err != nil {
		t.Fatalf("digest workspace: %v", err)
	}

	// 3. Place the Product Skill where each harness scans it, and record the
	//    bytes. DSH scans <projectRoot>/.dsh/skills; Claude Code scans
	//    <projectRoot>/.claude/skills. The same bytes go to both, and each
	//    placement is digested separately so a drift in either is visible.
	skillPins := []SkillPin{}
	placements := map[string]SkillPlacement{}
	for _, root := range append(DSHSkillRoots(wsRoot, "", "")[:1], ClaudeSkillRoots(wsRoot, "")[:1]...) {
		pl, err := PlaceSkill(root.Path, cfg.TEISkill, false)
		if err != nil {
			t.Fatalf("place skill in %s: %v", root.Path, err)
		}
		placements[root.Harness] = pl
		skillPins = append(skillPins, SkillPinFromPlacement(pl))
		t.Logf("skill placed for %s at %s (%s, %d bytes)", root.Harness, pl.PlacedPath, pl.BytesSHA256, pl.ByteCount)
	}

	// 4. Project the read-only tools and build the Task. The projection and the
	//    prompt both name the copy inside the trial root, so the declared root
	//    and the reachable bytes are the same thing.
	tool := NewTEIReadOnlyTool(trialBin, wsRoot)
	offers, unoffered := tool.Offers()
	if len(offers) == 0 {
		t.Fatal("no TEI read-only tools were offered")
	}
	if len(unoffered) > 0 {
		t.Logf("TEI read-only commands not offered by this projection: %v", unoffered)
	}

	task := Task{
		ID: "real-pilot-tei-read-only",
		Prompt: "Use the TEI read-only CLI at " + trialBin + " against the workspace at " + wsRoot +
			". Run `model catalog`, then `validate`, and report the model revision, the world fingerprint, " +
			"the declared counts and the validation result. Do not modify anything.",
		Pins: Pins{
			Source: SourcePin{
				Repo:         "tei-platform",
				ResolvedPath: wsRoot,
				BytesSHA256:  wsDigest,
				ByteCount:    wsBytes,
				Note:         fmt.Sprintf("synthetic copy of %s; %d immediate files", cfg.TEIWorkspace, files),
			},
			Model: ModelPin{Provider: "harness-default", Route: "harness-default"},
			// HarnessPin.ExePath/ExeBytes pin the PRODUCT executable the task
			// drives; the harness executables are pinned by each adapter's own
			// probe and recorded in its Availability.Detail.
			Harness: HarnessPin{Family: "multi", ExePath: cfg.TEIBinary, ExeBytes: binDigest},
			Roots:   []RootPin{{Logical: "tei-workspace", Path: wsRoot, Access: "read-only", Note: "declared, not independently verified"}},
			Skills:  skillPins,
			ToolSchemas: []ToolSchemaPin{
				{Name: "tei.model-catalog", Advertised: true},
				{Name: "tei.validate", Advertised: true},
			},
		},
		ContextRefs: []ContextRef{
			{Kind: "model-catalog", Ref: "tei model catalog -workspace " + wsRoot, Disclosure: "public-synthetic", Required: true},
		},
		Tools:  offers,
		Skills: skillPins,
		Limits: Limits{TimeoutMS: int64(cfg.Timeout / time.Millisecond), MaxTools: 40},
	}

	// 5. Build the adapters the caller asked for, plus the always-available
	//    deterministic control arm.
	direct := NewDirectControlAdapter()
	direct.Runner = ProcessRunner{}
	adapters := []Adapter{direct}
	for _, name := range cfg.Harnesses {
		switch name {
		case "direct-control":
			continue
		case "dsh-headless":
			dsh := NewDSHHeadlessAdapter("headless", wsRoot)
			dsh.Timeout = cfg.Timeout
			dsh.PermissionMode = os.Getenv("HARNESS_ADAPTER_DSH_PERMISSION_MODE")
			dsh.ApprovalPolicy = "never"
			for _, d := range splitEnvList(os.Getenv("HARNESS_ADAPTER_DSH_ADD_DIR")) {
				dsh.AddDirs = append(dsh.AddDirs, d)
			}
			for _, p := range splitEnvList(os.Getenv("HARNESS_ADAPTER_DSH_PATCH")) {
				dsh.PatchFiles = append(dsh.PatchFiles, p)
			}
			// The headless --json projection carries no model field, so the run's
			// model record comes from the effective configuration. That is a
			// declared route, and the adapter labels it as such.
			dsh.ProbeEffectiveConfig = true
			if len(dsh.PatchFiles) > 0 {
				t.Logf("DSH profile overlays supplied by the caller: %v", dsh.PatchFiles)
			}
			adapters = append(adapters, dsh)
		case "claude-code":
			cc := NewClaudeCodeAdapter(wsRoot)
			cc.Timeout = cfg.Timeout
			cc.Tools = os.Getenv("HARNESS_ADAPTER_CC_TOOLS")
			cc.PermissionMode = os.Getenv("HARNESS_ADAPTER_CC_PERMISSION_MODE")
			cc.AddDirs = splitEnvList(os.Getenv("HARNESS_ADAPTER_CC_ADD_DIR"))
			cc.MCPConfigs = splitEnvList(os.Getenv("HARNESS_ADAPTER_CC_MCP_CONFIG"))
			adapters = append(adapters, cc)
		default:
			t.Fatalf("unknown harness adapter %q", name)
		}
	}

	// 6. Probe each external harness. An unreachable one is reported as
	//    ineligible by the pilot; it is never replaced by another.
	for _, a := range adapters {
		av, err := a.Probe(ctx)
		if err != nil {
			t.Fatalf("probe %s: %v", a.Name(), err)
		}
		t.Logf("probe %s: reachable=%v (%s)", a.Name(), av.Reachable, av.Reason)
	}

	rep := Pilot(ctx, adapters, task, nil)

	// 7. Emit the evidence file next to the trial directory.
	outPath := filepath.Join(cfg.TrialDir, "real-pilot-report.json")
	if b, err := rep.JSON(); err == nil {
		if err := os.WriteFile(outPath, b, 0o644); err == nil {
			t.Logf("pilot report written to %s", outPath)
		}
	}
	t.Logf("pilot summary:\n%s", rep.Summary())

	// 8. Observation-only assertions, per requested harness arm.
	for _, want := range cfg.Harnesses {
		if want == "direct-control" {
			continue
		}
		arm := findArm(rep, want)
		if arm == nil {
			t.Fatalf("harness arm %q is missing from the report", want)
		}
		if arm.State == PilotIneligible {
			t.Logf("harness %q is ineligible in this environment: %s", want, arm.Reason)
			continue
		}
		if arm.State != PilotObserved {
			t.Fatalf("harness %q arm state = %s (%s)", want, arm.State, arm.Reason)
		}
		res := arm.Result
		if res.Transport != TransportDelivered {
			t.Fatalf("harness %q transport = %q", want, res.Transport)
		}
		if res.Run == RunUnknown {
			t.Fatalf("harness %q run state is unknown; the stream was not interpretable: %s", want, res.Reason)
		}
		if len(res.ToolCalls) == 0 {
			t.Fatalf("harness %q recorded no tool calls; the pilot observed no harness tool use", want)
		}
		sawBinary := false
		for _, c := range res.ToolCalls {
			if strings.Contains(c.InputJSON, filepath.Base(trialBin)) ||
				strings.Contains(c.InputJSON, trialBin) ||
				strings.Contains(c.ResultText, filepath.Base(trialBin)) {
				sawBinary = true
			}
		}
		if !sawBinary {
			t.Fatalf("harness %q recorded no call naming the pinned TEI binary %q", want, trialBin)
		}
		// Out-of-root reachability is recorded, not asserted. A read outside the
		// declared root is a finding about the harness's confinement, not a test
		// failure, and it must survive into the report.
		for _, c := range res.ToolCalls {
			for _, p := range OutOfRootPaths(c, wsRoot) {
				t.Logf("harness %q touched a path outside the declared root: %s (tool %s)", want, p, c.Tool)
			}
		}
		if res.Session.ExternalID == "" && res.Session.State == SessionCreated {
			t.Fatalf("harness %q reported a created session with no id", want)
		}
		t.Logf("harness %q observed: run=%s exit=%s session=%s tools=%d",
			want, res.Run, ExitString(res.ExitCode), res.Session.ExternalID, len(res.ToolCalls))
	}

	// The control arm must independently complete the same declared tools.
	directArm := findArm(rep, direct.Name())
	if directArm == nil || directArm.State != PilotObserved {
		t.Fatalf("control arm state = %v", directArm)
	}
	if len(directArm.Result.ToolCalls) == 0 {
		t.Fatal("control arm ran no tools")
	}
	for _, c := range directArm.Result.ToolCalls {
		if c.ExitCode == nil {
			t.Fatalf("control arm tool %q recorded no exit code", c.Tool)
		}
	}
	t.Logf("divergences: %v", rep.Divergences)
	for _, o := range rep.Outcomes {
		if o.Result != nil && len(o.Result.Unsupported) > 0 {
			t.Logf("unsupported (%s): %v", o.Adapter, o.Result.Unsupported)
		}
	}
}

// findArm returns one pilot arm by adapter name.
func findArm(rep *PilotReport, name string) *PilotOutcome {
	for i := range rep.Outcomes {
		if rep.Outcomes[i].Adapter == name {
			return &rep.Outcomes[i]
		}
	}
	return nil
}

// copyFile copies one regular file.
func copyFile(src, dst string) error {
	b, err := os.ReadFile(src)
	if err != nil {
		return err
	}
	return os.WriteFile(dst, b, 0o644)
}

// copyTree copies a directory tree, following no symlinks and preserving no
// permissions beyond what a copy needs.
func copyTree(src, dst string) error {
	return filepath.Walk(src, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		rel, err := filepath.Rel(src, path)
		if err != nil {
			return err
		}
		target := filepath.Join(dst, rel)
		if info.IsDir() {
			return os.MkdirAll(target, 0o755)
		}
		if !info.Mode().IsRegular() {
			return nil
		}
		b, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		if err := os.MkdirAll(filepath.Dir(target), 0o755); err != nil {
			return err
		}
		return os.WriteFile(target, b, 0o644)
	})
}

// TestRealProbeDSHAvailable is the minimal real-connection check: the harness
// binary is reachable and reports a version. It exists so a CI job can separate
// "the harness is installed" from "the harness ran a task".
func TestRealProbeDSHAvailable(t *testing.T) {
	if os.Getenv("HARNESS_ADAPTER_REAL") != "1" {
		t.Skip("HARNESS_ADAPTER_REAL != 1; real connections are opt-in")
	}
	a := NewDSHHeadlessAdapter("headless", "")
	av, err := a.Probe(context.Background())
	if err != nil {
		t.Fatalf("probe: %v", err)
	}
	if !av.Reachable {
		t.Skipf("harness not reachable: %s", av.Reason)
	}
	b, _ := json.Marshal(av.Detail)
	t.Logf("reachable: %s", string(b))
}
