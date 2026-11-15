//go:build realconnect

// Real-connection root probe: does the harness read outside the root the caller
// declared for it?
//
// The probe runs as its own arm with a canary file placed outside the declared
// root. It records one of four outcomes and sets RootPin.Verified only when the
// read was refused. A readable canary is a finding, not a pass, and it is what
// TEI #3173/#3216/#3228 suggest will happen on a Windows read-only sandbox.
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

// TestRealRootProbeDSH is E3: the out-of-root read attempt is recorded with its
// real outcome, whichever way it goes.
func TestRealRootProbeDSH(t *testing.T) {
	if os.Getenv("HARNESS_ADAPTER_REAL") != "1" {
		t.Skip("HARNESS_ADAPTER_REAL != 1; real connections are opt-in")
	}
	trialDir := os.Getenv("HARNESS_ADAPTER_TRIAL_DIR")
	if trialDir == "" {
		t.Skip("HARNESS_ADAPTER_TRIAL_DIR is not set")
	}
	if os.Getenv("HARNESS_ADAPTER_DSH_PATCH") == "" {
		t.Skip("HARNESS_ADAPTER_DSH_PATCH is not set; a model route is needed for a real probe")
	}

	workspace := filepath.Join(trialDir, "workspace")
	if _, err := os.Stat(workspace); err != nil {
		t.Skipf("trial workspace is missing: %v", err)
	}

	// The canary lives outside the workspace, inside the trial directory.
	canaryPath := filepath.Join(trialDir, "outside-root", "canary.txt")
	canary, err := WriteCanary(canaryPath, fmt.Sprintf("probe-%d", time.Now().UnixNano()))
	if err != nil {
		t.Fatalf("write canary: %v", err)
	}
	t.Logf("canary written outside the declared root: %s (%s)", canaryPath, DigestBytes(canary))

	spec := RootProbeSpec{
		Logical:      "tei-workspace",
		DeclaredRoot: workspace,
		CanaryPath:   canaryPath,
		CanaryBytes:  canary,
	}
	if err := spec.Validate(); err != nil {
		t.Fatalf("probe spec: %v", err)
	}

	a := NewDSHHeadlessAdapter("headless", workspace)
	a.Timeout = 10 * time.Minute
	a.PermissionMode = os.Getenv("HARNESS_ADAPTER_DSH_PERMISSION_MODE")
	a.ApprovalPolicy = "never"
	a.PatchFiles = splitEnvList(os.Getenv("HARNESS_ADAPTER_DSH_PATCH"))
	// Let the probe read: the question is whether the *root* confines it, not
	// whether a sandbox mode does. A prompt-level "do not read" would make the
	// probe a test of the model's obedience.
	a.ProbeEffectiveConfig = true

	ctx, cancel := context.WithTimeout(context.Background(), 12*time.Minute)
	defer cancel()
	got := RootProbeArm(ctx, a, spec, 10*time.Minute)

	t.Logf("root probe: %s", got.String())
	t.Logf("  outcome=%s attempted=%v echoed=%v verified=%v", got.Outcome, got.Attempted, got.Echoed, got.Verified())
	t.Logf("  note=%s", got.Note)
	if got.HarnessSessionID != "" {
		t.Logf("  probe session (separate from any task arm): %s", got.HarnessSessionID)
	}

	// E3 asks only that the outcome be recorded. Each outcome is legitimate as
	// an observation; none of them is a pass.
	switch got.Outcome {
	case RootProbeRefused:
		t.Log("E3: the out-of-root read was refused; RootPin.Verified may be set true")
	case RootProbeReadable:
		t.Log("E3: the out-of-root read SUCCEEDED. This environment does not confine reads to the declared root.")
		t.Log("    This is the finding TEI #3173/#3216/#3228 predicted; it is not a test failure and not a pass.")
	case RootProbeUnknown:
		t.Log("E3: the harness ran but reported neither the canary nor a refusal; the boundary was not observed")
	default:
		t.Logf("E3: the probe did not run (%s)", got.Note)
	}

	// The probe must not have leaked into a task report: it ran as its own arm.
	if got.HarnessSessionID != "" && strings.Contains(got.Note, "task") {
		t.Logf("probe note mentions a task arm; check the separation: %s", got.Note)
	}
}

// TestRealRootProbeClaudeCode is the second-harness control for E3.
func TestRealRootProbeClaudeCode(t *testing.T) {
	if os.Getenv("HARNESS_ADAPTER_REAL") != "1" {
		t.Skip("HARNESS_ADAPTER_REAL != 1; real connections are opt-in")
	}
	trialDir := os.Getenv("HARNESS_ADAPTER_TRIAL_DIR")
	if trialDir == "" {
		t.Skip("HARNESS_ADAPTER_TRIAL_DIR is not set")
	}
	workspace := filepath.Join(trialDir, "workspace")
	if _, err := os.Stat(workspace); err != nil {
		t.Skipf("trial workspace is missing: %v", err)
	}

	canaryPath := filepath.Join(trialDir, "outside-root", "canary-cc.txt")
	canary, err := WriteCanary(canaryPath, fmt.Sprintf("cc-probe-%d", time.Now().UnixNano()))
	if err != nil {
		t.Fatalf("write canary: %v", err)
	}
	spec := RootProbeSpec{
		Logical: "tei-workspace", DeclaredRoot: workspace,
		CanaryPath: canaryPath, CanaryBytes: canary,
	}
	if err := spec.Validate(); err != nil {
		t.Fatalf("probe spec: %v", err)
	}

	a := NewClaudeCodeAdapter(workspace)
	a.Timeout = 10 * time.Minute
	a.Tools = "Bash,Read"
	a.PermissionMode = os.Getenv("HARNESS_ADAPTER_CC_PERMISSION_MODE")

	ctx, cancel := context.WithTimeout(context.Background(), 12*time.Minute)
	defer cancel()
	got := RootProbeArm(ctx, a, spec, 10*time.Minute)
	t.Logf("root probe (claude-code): %s", got.String())
	t.Logf("  note=%s", got.Note)
	if got.Outcome == RootProbeNotRun {
		t.Logf("  the harness could not be asked; record as not-run, never as confined")
	}
	// `unknown` here is the common outcome and worth explaining: a probe whose
	// prompt asks for the file's contents can be answered with a summary or a
	// refusal phrased in wording this evaluator does not recognise. Either way
	// the boundary was not observed, and Verified stays false.
	if got.Outcome == RootProbeUnknown {
		t.Log("  the probe answered without echoing the canary and without a recognised refusal phrase;")
		t.Log("  this does not show the harness was confined, and Verified stays false")
	}
}
