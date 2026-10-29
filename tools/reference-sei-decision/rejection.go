package main

import (
	"bytes"
	"context"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
)

type rejectionFixture struct {
	id          string
	statement   string
	unresolved  string
	responsible string
}

var rejectionFixtures = []rejectionFixture{
	{"dec-reject-safety", "安全担当が差戻し: 工事停止範囲が未特定", "rejection:safety", "role:safety"},
	{"dec-reject-procurement", "調達が差戻し: 見積条件が不足", "rejection:procurement", "role:procurement"},
}

func RunRejection(ctx context.Context, seiRoot string) Receipt {
	receipt := Receipt{
		Schema: "tai.reference.sei-decision/v0", Variant: "scn002-rejections", ReadOnlyProjection: true,
		AuthorityVerified: false, HumanReviewed: false, Published: false,
		Notes: []string{
			"SEIの一時storeへ差戻しdecisionを記録する。",
			"承認・発注・公開は実行しない。実在の権限でもない。",
		},
	}
	runtimeDir := filepath.Join(seiRoot, "runtime", "go")
	if _, err := os.Stat(filepath.Join(runtimeDir, "cmd", "sei")); err != nil {
		receipt.Reason = "SEI runtime is unavailable: " + err.Error()
		return receipt
	}
	if _, err := exec.LookPath("go"); err != nil {
		receipt.Reason = "go is unavailable: " + err.Error()
		return receipt
	}
	store, err := os.MkdirTemp("", "tai-sei-rejection-")
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	defer os.RemoveAll(store)
	receipt.SeiCommit = output(ctx, seiRoot, "git", "rev-parse", "HEAD")
	receipt.GoVersion = output(ctx, runtimeDir, "go", "version")

	steps := [][]string{
		{"run", "./cmd/sei", "init", "--data-root", store, "--bundle-id", "scn002-rejections"},
		{"run", "./cmd/sei", "add", "recommendation", "--data-root", store,
			"--id", "rec-rejection", "--statement", "安全・調達の差戻し理由を確認中", "--source", "tai",
			"--basis", "observation:O-10", "--basis", "observation:O-22"},
	}
	for _, fixture := range rejectionFixtures {
		steps = append(steps, []string{
			"run", "./cmd/sei", "add", "decision", "--data-root", store,
			"--id", fixture.id, "--statement", fixture.statement, "--source", "tai",
			"--unresolved", fixture.unresolved, "--unresolved", "authority:unknown",
			"--recommendation", "rec-rejection", "--responsible", fixture.responsible,
		})
	}
	for _, step := range steps {
		if _, err := run(ctx, runtimeDir, step...); err != nil {
			receipt.Reason = err.Error()
			return receipt
		}
	}
	receipt.StoreCreated = true
	resume, err := run(ctx, runtimeDir, "run", "./cmd/sei", "resume", "--data-root", store, "--json")
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	var view ResumeView
	if err := json.Unmarshal(bytes.TrimSpace(resume), &view); err != nil {
		receipt.Reason = "resume output is invalid: " + err.Error()
		return receipt
	}
	receipt.BundleID = view.BundleID
	receipt.RecordCount = view.RecordCount
	receipt.Unresolved = view.Unresolved
	receipt.NotVerifiedRecordCount = view.NotVerifiedRecordCount
	unresolved := map[string]bool{}
	for _, item := range view.Unresolved {
		unresolved[item.Ref] = true
	}
	if view.BundleID != "scn002-rejections" || view.RecordCount != 3 || len(view.Decisions) != 2 ||
		view.NotVerifiedRecordCount != 0 {
		receipt.Reason = "resume projection does not match the rejection fixture"
		return receipt
	}
	for _, fixture := range rejectionFixtures {
		decision, ok := findDecision(view.Decisions, fixture.id)
		if !ok {
			receipt.Reason = "missing rejection decision: " + fixture.id
			return receipt
		}
		if !unresolved[fixture.unresolved] || !unresolved["authority:unknown"] {
			receipt.Reason = "rejection reason is not unresolved: " + fixture.id
			return receipt
		}
		receipt.RejectionDecisions = append(receipt.RejectionDecisions, decision)
	}
	receipt.Decision = receipt.RejectionDecisions[0]
	receipt.ProvisionalDecision = receipt.RejectionDecisions[1]
	receipt.Rejected = true
	receipt.Passed = true
	return receipt
}
