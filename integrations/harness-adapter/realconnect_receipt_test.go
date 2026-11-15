//go:build realconnect

// Real-connection receipt check (H-A-5 / E6): after a harness arm produces its
// final answer, a SEPARATE reader opens a file the arm wrote and digests it.
//
// The producer here is the harness arm running under a prompt that asks it to
// write its answer to a file inside the trial root. The consumer is this test,
// reading that file with no harness involved. A receipt is `complete` only when
// the two digests match.
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

// TestRealReceiptFileReadback is E6: an independent reader observes what was
// delivered.
func TestRealReceiptFileReadback(t *testing.T) {
	if os.Getenv("HARNESS_ADAPTER_REAL") != "1" {
		t.Skip("HARNESS_ADAPTER_REAL != 1; real connections are opt-in")
	}
	trialDir := os.Getenv("HARNESS_ADAPTER_TRIAL_DIR")
	teiMCP := os.Getenv("HARNESS_ADAPTER_TEI_MCP_BIN")
	if trialDir == "" || teiMCP == "" {
		t.Skip("HARNESS_ADAPTER_TRIAL_DIR / _TEI_MCP_BIN must be set")
	}
	workspace := filepath.Join(trialDir, "workspace")
	if _, err := os.Stat(workspace); err != nil {
		t.Skipf("trial workspace missing: %v", err)
	}

	// The answer file is inside the trial root and outside the workspace, so the
	// harness must be granted the second directory explicitly.
	answerDir := filepath.Join(trialDir, "consumed")
	answerPath := filepath.Join(answerDir, "answer.md")
	if err := os.MkdirAll(answerDir, 0o755); err != nil {
		t.Fatalf("mkdir answer dir: %v", err)
	}

	trialMCP := filepath.Join(workspace, "bin", "tei-mcp.exe")
	if err := copyFile(teiMCP, trialMCP); err != nil {
		t.Fatalf("copy tei-mcp: %v", err)
	}
	spec := MCPServerSpec{
		ServerName: "tei", Transport: "stdio", Command: trialMCP,
		Args: []string{"-workspace", workspace}, ToolCallTimeoutMS: 120000,
		FailOnStartupError: true,
	}

	prompt := fmt.Sprintf(
		"Call %s. Then write your answer, verbatim, to the file %s using your file-write tool. "+
			"Write nothing else there. Report the model revision and the world fingerprint in the file.",
		MCPToolName("tei", "tei_model_catalog"), answerPath)

	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Minute)
	defer cancel()

	dsh := NewDSHHeadlessAdapter("headless", workspace)
	dsh.Timeout = 20 * time.Minute
	dsh.PermissionMode = os.Getenv("HARNESS_ADAPTER_DSH_PERMISSION_MODE")
	dsh.ApprovalPolicy = "never"
	// Writing needs workspace-write plus the answer directory.
	dsh.PermissionMode = "workspace-write"
	dsh.AddDirs = []string{answerDir}
	dsh.PatchFiles = splitEnvList(os.Getenv("HARNESS_ADAPTER_DSH_PATCH"))
	dsh.MCPServers = []MCPServerSpec{spec}
	dsh.MCPWorkDir = filepath.Join(trialDir, "overlays")
	dsh.ProbeEffectiveConfig = true

	av, err := dsh.Probe(ctx)
	if err != nil {
		t.Fatalf("probe: %v", err)
	}
	if !av.Reachable {
		t.Skipf("harness not reachable: %s", av.Reason)
	}

	task := Task{
		ID:     "real-receipt-file-readback",
		Prompt: prompt,
		Pins: Pins{
			Source: SourcePin{Repo: "tei-platform", ResolvedPath: workspace,
				Note: "synthetic trial root"},
			Roots: []RootPin{
				{Logical: "tei-workspace", Path: workspace, Access: "workspace-write"},
				{Logical: "answer-dir", Path: answerDir, Access: "workspace-write"},
			},
		},
		Limits: Limits{TimeoutMS: int64(20 * time.Minute / time.Millisecond), MaxTools: 30},
	}
	res, err := dsh.Run(ctx, task, nil)
	if err != nil {
		t.Fatalf("run: %v", err)
	}
	t.Logf("harness arm: %s", res.Summary())
	for _, d := range res.Diagnostics {
		t.Logf("  diagnostic [%s] %s: %s", d.Severity, d.Code, d.Message)
	}
	t.Logf("receipt before readback: %s", res.Receipt.State)

	// The producer records nothing about the file; the CONSUMER reads it. The
	// expected digest is whatever the harness itself reported as its answer, so
	// the comparison is "did what was written match what was said", not "did the
	// test like the answer".
	// The consumer checks the delivered file against claims a SECOND route
	// established: the product's own typed tool result, read independently by
	// this test. Comparing the file against the harness's own summary would let a
	// self-consistent fabrication pass; comparing it against an independently
	// obtained product answer does not.
	cliClaims := map[string]string{}
	for _, c := range res.MCPToolCalls() {
		if c.RawName != "tei_model_catalog" {
			continue
		}
		env, err := ParseProductEnvelope([]byte(c.Call.ResultText))
		if err != nil {
			t.Logf("typed catalog payload unparseable, no claims available: %v", err)
			continue
		}
		for k, v := range env.Identity {
			if v != "" {
				cliClaims[k] = v
			}
		}
	}
	if len(cliClaims) == 0 {
		// The typed catalog result was bounded or absent. Fall back to the
		// product CLI's own values by running it directly.
		tool := NewTEIReadOnlyTool(filepath.Join(workspace, "bin", "tei.exe"), workspace)
		if rec, err := tool.Invoke(ctx, "model catalog"); err == nil {
			if env, err := ParseProductEnvelope([]byte(rec.ResultText)); err == nil {
				for k, v := range env.Identity {
					if v != "" {
						cliClaims[k] = v
					}
				}
			}
		}
	}
	t.Logf("consumer claims from an independent product route: %v", cliClaims)

	expected := DigestString(res.FinalText)
	digestRead := FileReadback("independent-file-reader", answerPath, expected)
	t.Logf("digest readback: %s", digestRead.String())
	claimRead := ClaimReadback("independent-claim-reader", answerPath, cliClaims)
	t.Logf("claim readback: %s", claimRead.String())
	if claimRead.Note != "" {
		t.Logf("  note=%s", claimRead.Note)
	}
	// The claim form is the one that can honestly reach `complete`, because
	// its expectations come from outside the producing arm.
	got := claimRead
	ApplyReceipt(res, got)
	t.Logf("receipt after readback: %s (consumer %s)", res.Receipt.State, res.Receipt.Consumer)

	// E6 asks that the receipt leave `not-observed` with a real read.
	switch got.State {
	case ReceiptComplete:
		t.Log("E6: an independent reader read the file and its digest matched the harness's own answer")
	case ReceiptPartial:
		t.Log("E6: an independent reader read bytes at the location, but the receipt is partial; see the note")
	case ReceiptNotObserved:
		t.Log("E6: no file was readable at the expected location; the receipt stays not-observed")
	}
	// Regardless of outcome, this is an observation. A harness that never wrote
	// the file is a finding about the harness, not a pass and not a failure of the
	// consumer.
	if got.State == ReceiptNotObserved && len(res.ToolCalls) == 0 {
		t.Log("  the harness also made no tool calls, so it could not have written anything")
	}
}

// TestRealReceiptDirectReadbackIsWeak documents the fallback shape on a real arm:
// it must never report complete.
func TestRealReceiptDirectReadbackIsWeak(t *testing.T) {
	if os.Getenv("HARNESS_ADAPTER_REAL") != "1" {
		t.Skip("HARNESS_ADAPTER_REAL != 1; real connections are opt-in")
	}
	trialDir := os.Getenv("HARNESS_ADAPTER_TRIAL_DIR")
	if trialDir == "" {
		t.Skip("HARNESS_ADAPTER_TRIAL_DIR is not set")
	}
	workspace := filepath.Join(trialDir, "workspace")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Minute)
	defer cancel()

	dsh := NewDSHHeadlessAdapter("headless", workspace)
	dsh.Timeout = 10 * time.Minute
	dsh.PermissionMode = os.Getenv("HARNESS_ADAPTER_DSH_PERMISSION_MODE")
	dsh.ApprovalPolicy = "never"
	dsh.PatchFiles = splitEnvList(os.Getenv("HARNESS_ADAPTER_DSH_PATCH"))
	res, err := dsh.Run(ctx, Task{ID: "weak-receipt", Prompt: "Reply with the single word: ready."}, nil)
	if err != nil {
		t.Fatalf("run: %v", err)
	}
	if strings.TrimSpace(res.FinalText) == "" {
		t.Skip("the arm produced no final text; nothing to digest")
	}
	got := DirectReadback("adapter-self-check", res, DigestString(res.FinalText))
	t.Logf("%s", got.String())
	if got.State == ReceiptComplete {
		t.Fatal("the weak readback reported complete on a real arm")
	}
	t.Logf("  note=%s", got.Note)
}
