//go:build realconnect

// Real four-session H2遶願ｾｿ3遶願ｾｿ3遶願ｾｿ2 paired pilot (H-A-4 / E5).
//
// The allocation is fixed BEFORE the first run: two H2 sessions and two H3
// sessions in the order H2, H3, H3, H2. That order is part of the design because
// a harness that warmed up between runs would otherwise look like a Skill effect.
//
// Two things this test never does:
//   - It does not re-label an H3 whose Skill failed to load as an H2.
//   - It does not compute an accuracy improvement. The denominator is the four
//     allocated sessions (ITT); the accuracy comparison belongs to the
//     independent Expected at TAI #488.
package harnessadapter

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"
	"time"
)

// allocatedArms is the fixed allocation. Do not edit between runs.
var allocatedArms = []struct {
	Name      string
	WithSkill bool
}{
	{"S1-H2", false},
	{"S2-H3", true},
	{"S3-H3", true},
	{"S4-H2", false},
}

// TestRealFourSessionH2H3 runs the allocated four sessions and reports each one.
func TestRealFourSessionH2H3(t *testing.T) {
	if os.Getenv("HARNESS_ADAPTER_REAL") != "1" {
		t.Skip("HARNESS_ADAPTER_REAL != 1; real connections are opt-in")
	}
	trialDir := os.Getenv("HARNESS_ADAPTER_TRIAL_DIR")
	teiMCP := os.Getenv("HARNESS_ADAPTER_TEI_MCP_BIN")
	teiSkill := os.Getenv("HARNESS_ADAPTER_TEI_SKILL")
	if trialDir == "" || teiMCP == "" || teiSkill == "" {
		t.Skip("HARNESS_ADAPTER_TRIAL_DIR / _TEI_MCP_BIN / _TEI_SKILL must be set")
	}
	harnessName := os.Getenv("HARNESS_ADAPTER_SKILL_HARNESS")
	if harnessName == "" {
		harnessName = "dsh-headless"
	}
	if harnessName != "dsh-headless" {
		// Only DSH has produced an eligible H3 arm so far; running the other
		// harnesses would yield ineligible trials, which the paired test already
		// records.
		t.Skipf("harness %q has not produced a loaded H3 arm; the paired test records that gap", harnessName)
	}
	workspace := filepath.Join(trialDir, "workspace")
	if _, err := os.Stat(workspace); err != nil {
		t.Skipf("trial workspace missing: %v", err)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Minute)
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

	// One fixed Task text for all four sessions.
	typedCatalog := MCPToolName("tei", "tei_model_catalog")
	taskPrompt := fmt.Sprintf(
		"Call %s. Report the model revision, the world fingerprint and the declared total. "+
			"Do not run any shell command and do not run the TEI CLI directly.", typedCatalog)

	skillRoot := SkillRootFor(harnessName, workspace)
	if skillRoot == "" {
		t.Fatalf("no skill root known for %q", harnessName)
	}
	h3Pin, err := PlaceSkill(skillRoot, teiSkill, false)
	if err != nil {
		t.Fatalf("place skill: %v", err)
	}
	// Start with the Skill absent; each H3 session places it, each H2 removes it.
	if err := os.RemoveAll(filepath.Join(skillRoot, h3Pin.ID)); err != nil {
		t.Fatalf("clear skill dir: %v", err)
	}
	h3SkillPin := SkillPinFromPlacement(h3Pin)
	t.Logf("Skill bytes for H3: %s (%d bytes)", h3SkillPin.BytesSHA256, h3Pin.ByteCount)

	var sessions []SkillObservation
	for _, arm := range allocatedArms {
		// Placement is a property of the arm, executed immediately before its run.
		if arm.WithSkill {
			if _, err := PlaceSkill(skillRoot, teiSkill, false); err != nil {
				t.Fatalf("%s: place skill: %v", arm.Name, err)
			}
		} else {
			if err := os.RemoveAll(filepath.Join(skillRoot, h3Pin.ID)); err != nil {
				t.Fatalf("%s: remove skill: %v", arm.Name, err)
			}
		}

		dsh := NewDSHHeadlessAdapter("headless", workspace)
		dsh.Timeout = 12 * time.Minute
		dsh.PermissionMode = os.Getenv("HARNESS_ADAPTER_DSH_PERMISSION_MODE")
		dsh.ApprovalPolicy = "never"
		dsh.PatchFiles = splitEnvList(os.Getenv("HARNESS_ADAPTER_DSH_PATCH"))
		dsh.MCPServers = []MCPServerSpec{spec}
		dsh.MCPWorkDir = filepath.Join(trialDir, "overlays")
		dsh.ProbeEffectiveConfig = true
		av, err := dsh.Probe(ctx)
		if err != nil || !av.Reachable {
			t.Skipf("harness not reachable: %v %s", err, av.Reason)
		}
		res, err := dsh.Run(ctx, Task{
			ID:     arm.Name,
			Prompt: taskPrompt,
			Pins: Pins{
				Source: SourcePin{Repo: "tei-platform", ResolvedPath: workspace},
				Roots:  []RootPin{{Logical: "tei-workspace", Path: workspace, Access: "read-only"}},
				Skills: []SkillPin{h3SkillPin},
			},
			Limits: Limits{TimeoutMS: int64(12 * time.Minute / time.Millisecond), MaxTools: 20},
		}, nil)
		if err != nil {
			t.Fatalf("%s run: %v", arm.Name, err)
		}
		// Each session carries the pin that matched its own placement.
		var pin SkillPin
		if arm.WithSkill {
			pin = h3SkillPin
		} else {
			pin = SkillPin{ID: h3SkillPin.ID, LoadState: LoadUnknown}
		}
		obs := ObserveSkillUse(pin, res)
		obs.Note = arm.Name + " | " + obs.Note
		sessions = append(sessions, obs)
		t.Logf("%s: transport=%s run=%s tools=%d exit=%s loadState=%s",
			arm.Name, res.Transport, res.Run, len(res.ToolCalls), ExitString(res.ExitCode), obs.LoadState)
	}

	// Report the ITT denominator: four allocated, and how many produced a load.
	h3Loaded, h2Clean := 0, 0
	for i, arm := range allocatedArms {
		obs := sessions[i]
		if arm.WithSkill && obs.LoadState == LoadLoaded {
			h3Loaded++
		}
		if !arm.WithSkill && obs.LoadState != LoadLoaded {
			h2Clean++
		}
	}
	t.Logf("ITT: allocated=%d, H3 loaded=%d/2, H2 clean=%d/2", len(allocatedArms), h3Loaded, h2Clean)
	if h3Loaded == 2 && h2Clean == 2 {
		t.Log("all four allocated sessions form valid H2 and H3 arms; accuracy is STILL not measured here")
	} else {
		t.Log("not all allocated sessions form valid arms; the counts above are the ITT record, not an effect estimate")
	}
	// A failed H3 load is recorded as such; it is never re-labelled.
	for i, arm := range allocatedArms {
		if arm.WithSkill && sessions[i].LoadState != LoadLoaded {
			t.Logf("%s: H3 did not load the Skill (%s); kept in the ITT denominator", arm.Name, sessions[i].LoadState)
		}
	}

	// The sheet records every allocated session as its own entry, plus the two
	// valid pairs. One session per "pair" with an empty opposite slot would
	// misreport both the count and the arm identity.
	type sessionRecord struct {
		Arm       string           `json:"arm"`
		WithSkill bool             `json:"withSkill"`
		Allocated bool             `json:"allocated"`
		Obs       SkillObservation `json:"observation"`
	}
	var records []sessionRecord
	for i, arm := range allocatedArms {
		records = append(records, sessionRecord{
			Arm: arm.Name, WithSkill: arm.WithSkill, Allocated: true, Obs: sessions[i],
		})
	}
	var pairRecords []SkillPairObservation
	if h2Clean == 2 && h3Loaded == 2 {
		// Pair by allocation order; never pair by picking the better result.
		h2First, h2Last := sessions[0], sessions[3]
		h3First, h3Last := sessions[1], sessions[2]
		for i, p := range [][2]SkillObservation{{h2First, h3First}, {h2Last, h3Last}} {
			pairRecords = append(pairRecords, SkillPairObservation{
				TaskID:      fmt.Sprintf("real-four-session/P%d", i+1),
				H2:          p[0],
				H3:          p[1],
				Eligible:    true,
				SkillEffect: "eligibility-confirmed; accuracy not measured",
			})
		}
	}
	sheet := struct {
		Allocation []string               `json:"allocation"`
		Sessions   []sessionRecord        `json:"sessions"`
		Pairs      []SkillPairObservation `json:"pairs"`
		ITT        map[string]int         `json:"itt"`
		NotClaimed []string               `json:"notClaimed"`
	}{
		Allocation: []string{"S1-H2", "S2-H3", "S3-H3", "S4-H2"},
		Sessions:   records,
		Pairs:      pairRecords,
		ITT:        map[string]int{"allocated": len(allocatedArms), "h3Loaded": h3Loaded, "h2Clean": h2Clean},
		NotClaimed: []string{
			"accuracy or an effect size",
			"a statistical result from four sessions",
			"that a loaded Skill improved the answer",
		},
	}
	outPath := filepath.Join(trialDir, "four-session-observation.json")
	if b, err := json.MarshalIndent(sheet, "", "  "); err == nil {
		if err := os.WriteFile(outPath, b, 0o644); err != nil {
			t.Logf("write sheet: %v", err)
		} else {
			t.Logf("per-session observation written to %s", outPath)
		}
	}
}
