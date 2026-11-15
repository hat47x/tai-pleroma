//go:build realconnect

// Real-connection H2/H3 pair (H-A-4 / E5): the same Task run twice on the same
// harness, once with the Product Skill placed and once without, and the
// eligibility of that pair reported.
//
// What this measures is eligibility and Skill load, not whether the Skill helped.
// The accuracy comparison belongs to the independent Expected at TAI #488, and
// this test deliberately does not produce a verdict on it.
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

// TestRealSkillPairH2H3 runs one H2 arm (no Skill placed) and one H3 arm (Skill
// placed) on the same harness with the same Task, then reports the pair.
func TestRealSkillPairH2H3(t *testing.T) {
	if os.Getenv("HARNESS_ADAPTER_REAL") != "1" {
		t.Skip("HARNESS_ADAPTER_REAL != 1; real connections are opt-in")
	}
	trialDir := os.Getenv("HARNESS_ADAPTER_TRIAL_DIR")
	teiSkill := os.Getenv("HARNESS_ADAPTER_TEI_SKILL")
	teiMCP := os.Getenv("HARNESS_ADAPTER_TEI_MCP_BIN")
	if trialDir == "" || teiSkill == "" || teiMCP == "" {
		t.Skip("HARNESS_ADAPTER_TRIAL_DIR / _TEI_SKILL / _TEI_MCP_BIN must be set")
	}
	workspace := filepath.Join(trialDir, "workspace")
	if _, err := os.Stat(workspace); err != nil {
		t.Skipf("trial workspace missing: %v", err)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Minute)
	defer cancel()

	trialMCP := filepath.Join(workspace, "bin", "tei-mcp.exe")
	if err := copyFile(teiMCP, trialMCP); err != nil {
		t.Fatalf("copy tei-mcp: %v", err)
	}
	spec := MCPServerSpec{
		ServerName: "tei", Transport: "stdio", Command: trialMCP,
		Args: []string{"-workspace", workspace}, ToolCallTimeoutMS: 120000,
		FailOnStartupError: true,
	}

	// The Task is identical in both arms. Only the Skill placement differs, which
	// is what makes the pair a contrast rather than two different experiments.
	typedCatalog := MCPToolName("tei", "tei_model_catalog")
	taskPrompt := fmt.Sprintf(
		"Call %s. Report the model revision, the world fingerprint and the declared total. "+
			"Do not run any shell command and do not run the TEI CLI directly.", typedCatalog)

	// H3 placement: the Product Skill in the root the chosen harness scans. H2
	// gets the same workspace with the Skill directory removed. The root differs
	// per harness, so it is chosen from the harness rather than assumed.
	harnessName := os.Getenv("HARNESS_ADAPTER_SKILL_HARNESS")
	if harnessName == "" {
		harnessName = "dsh-headless"
	}
	skillRoot := SkillRootFor(harnessName, workspace)
	if skillRoot == "" {
		t.Skipf("no skill root is known for harness %q", harnessName)
	}
	pl, err := PlaceSkill(skillRoot, teiSkill, false)
	if err != nil {
		t.Fatalf("place skill: %v", err)
	}
	pin := SkillPinFromPlacement(pl)
	t.Logf("Skill placed for H3 in %s: %s (%s, %d bytes)", skillRoot, pl.PlacedPath, pl.BytesSHA256, pl.ByteCount)

	run := func(arm string, withSkill bool) *Result {
		if !withSkill {
			// Remove the placed Skill so H2 sees the same workspace without it.
			if err := os.RemoveAll(filepath.Join(skillRoot, pl.ID)); err != nil {
				t.Fatalf("remove skill for H2: %v", err)
			}
		} else if _, err := os.Stat(filepath.Join(skillRoot, pl.ID)); err != nil {
			// Re-place for the second H3-style arm if needed.
			if _, err := PlaceSkill(skillRoot, teiSkill, false); err != nil {
				t.Fatalf("re-place skill: %v", err)
			}
		}
		// The harness is caller-chosen so the same paired Task can be run on more
		// than one harness. Only the harness changes; the Task, Skill bytes and
		// placement rule stay identical.
		var adapter Adapter
		switch harnessName {
		case "claude-code":
			cc := NewClaudeCodeAdapter(workspace)
			cc.Timeout = 12 * time.Minute
			cc.Tools = os.Getenv("HARNESS_ADAPTER_CC_TOOLS")
			cc.PermissionMode = os.Getenv("HARNESS_ADAPTER_CC_PERMISSION_MODE")
			cc.MCPServers = []MCPServerSpec{spec}
			cc.MCPWorkDir = filepath.Join(trialDir, "overlays")
			adapter = cc
		case "step-cli":
			st := NewStepCLIAdapter(filepath.Join(trialDir, "step-project"))
			st.Timeout = 12 * time.Minute
			st.Model = os.Getenv("HARNESS_ADAPTER_STEP_MODEL")
			if st.Model == "" {
				st.Model = "step-3.7-flash"
			}
			st.ApprovalMode = "auto"
			st.NonInteractiveApproval = "allow"
			if k := os.Getenv("STEP_API_KEY"); k != "" {
				st.Env = []string{"STEP_API_KEY=" + k, "STEP_BASE_URL=" + envOr("STEP_BASE_URL", "https://api.stepfun.ai/step_plan/v1")}
			}
			adapter = st
		default:
			dsh := NewDSHHeadlessAdapter("headless", workspace)
			dsh.Timeout = 12 * time.Minute
			dsh.PermissionMode = os.Getenv("HARNESS_ADAPTER_DSH_PERMISSION_MODE")
			dsh.ApprovalPolicy = "never"
			dsh.PatchFiles = splitEnvList(os.Getenv("HARNESS_ADAPTER_DSH_PATCH"))
			dsh.MCPServers = []MCPServerSpec{spec}
			dsh.MCPWorkDir = filepath.Join(trialDir, "overlays")
			dsh.ProbeEffectiveConfig = true
			adapter = dsh
		}
		av, err := adapter.Probe(ctx)
		if err != nil || !av.Reachable {
			t.Skipf("harness not reachable for %s: %v %s", arm, err, av.Reason)
		}
		res, err := adapter.Run(ctx, Task{
			ID:     arm,
			Prompt: taskPrompt,
			Pins: Pins{
				Source: SourcePin{Repo: "tei-platform", ResolvedPath: workspace},
				Roots:  []RootPin{{Logical: "tei-workspace", Path: workspace, Access: "read-only"}},
				Skills: []SkillPin{pin},
			},
			Limits: Limits{TimeoutMS: int64(12 * time.Minute / time.Millisecond), MaxTools: 20},
		}, nil)
		if err != nil {
			t.Fatalf("%s run: %v", arm, err)
		}
		t.Logf("%s: transport=%s run=%s tools=%d exit=%s", arm, res.Transport, res.Run, len(res.ToolCalls), ExitString(res.ExitCode))
		for _, c := range res.ToolCalls {
			t.Logf("  [%s] status=%s", c.Tool, c.HarnessStatus)
		}
		return res
	}

	h3 := run("H3-skill-placed", true)
	h2 := run("H2-skill-removed", false)

	// The H2 arm ran with the Skill directory removed, so its pin must say so.
	// Passing the H3 placement pin to ObserveSkillPair would record
	// `placed=true` for an arm that had no such file, which is the kind of
	// quiet misreport this contract exists to prevent.
	h2Pin := SkillPin{ID: pin.ID, LoadState: LoadUnknown}
	pair := ObserveSkillPair("real-skill-pair", h2Pin, pin, h2, h3)
	t.Logf("H2 loadState=%s placed=%v answer=%v", pair.H2.LoadState, pair.H2.Placed, pair.H2.AnswerPresent)
	t.Logf("H3 loadState=%s placed=%v answer=%v loadedVia=%s", pair.H3.LoadState, pair.H3.Placed, pair.H3.AnswerPresent, pair.H3.LoadedVia)
	t.Logf("pair eligible=%v skillEffect=%q", pair.Eligible, pair.SkillEffect)
	for _, r := range pair.IneligibleReasons {
		t.Logf("  ineligible: %s", r)
	}

	// E5 asks for the observation, not a verdict. Both outcomes are recorded.
	switch {
	case pair.Eligible:
		t.Log("E5: the pair is a valid H2/H3 contrast; accuracy is still not measured here")
	case pair.H3.LoadState == LoadNotLoaded:
		t.Log("E5: H3 did not load the Skill, so the pair is an ineligible trial, NOT evidence of no effect")
	case pair.H2.LoadState == LoadLoaded:
		t.Log("E5: H2 loaded the Skill, so the pair is not a contrast")
	default:
		t.Logf("E5: the pair is ineligible for the recorded reasons: %s", strings.Join(pair.IneligibleReasons, "; "))
	}
	// The sheet is written next to the trial for TAI #488 to consume.
	sheetPath := filepath.Join(trialDir, "skill-pair-observation.json")
	if b, err := SkillObservationJSON([]SkillPairObservation{pair}); err == nil {
		if err := os.WriteFile(sheetPath, b, 0o644); err == nil {
			t.Logf("skill pair observation written to %s", sheetPath)
		}
	}
}
