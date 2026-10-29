package main

import (
	"bytes"
	"context"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
)

type approvalFixture struct {
	id          string
	statement   string
	unresolved  string
	responsible string
}

var approvalFixtures = []approvalFixture{
	{"dec-approval-budget", "予算承認は未完了", "approval:budget-pending", "role:budget-owner"},
	{"dec-approval-procurement", "調達承認は未完了", "approval:procurement-pending", "role:procurement"},
	{"dec-approval-safety", "安全承認は未完了", "approval:safety-pending", "role:safety"},
}

func RunApproval(ctx context.Context, seiRoot string) Receipt {
	receipt := Receipt{
		Schema: "tai.reference.sei-decision/v0", Variant: "scn002-approvals", ReadOnlyProjection: true,
		AuthorityVerified: false, HumanReviewed: false, Published: false,
		Notes: []string{
			"SEIの一時storeへ3名の承認待ちdecisionを記録する。",
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
	store, err := os.MkdirTemp("", "tai-sei-approval-")
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	defer os.RemoveAll(store)
	receipt.SeiCommit = output(ctx, seiRoot, "git", "rev-parse", "HEAD")
	receipt.GoVersion = output(ctx, runtimeDir, "go", "version")

	steps := [][]string{
		{"run", "./cmd/sei", "init", "--data-root", store, "--bundle-id", "scn002-approvals"},
		{"run", "./cmd/sei", "add", "recommendation", "--data-root", store,
			"--id", "rec-approval", "--statement", "D-06の承認状態を確認中", "--source", "tai",
			"--basis", "observation:O-21", "--basis", "observation:O-22"},
	}
	for _, fixture := range approvalFixtures {
		steps = append(steps, []string{
			"run", "./cmd/sei", "add", "decision", "--data-root", store,
			"--id", fixture.id, "--statement", fixture.statement, "--source", "tai",
			"--unresolved", fixture.unresolved, "--unresolved", "authority:unknown",
			"--recommendation", "rec-approval", "--responsible", fixture.responsible,
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
	if view.BundleID != "scn002-approvals" || view.RecordCount != 4 || len(view.Decisions) != 3 ||
		view.NotVerifiedRecordCount != 0 {
		receipt.Reason = "resume projection does not match the approval fixture"
		return receipt
	}
	for _, fixture := range approvalFixtures {
		decision, ok := findDecision(view.Decisions, fixture.id)
		if !ok {
			receipt.Reason = "missing approval decision: " + fixture.id
			return receipt
		}
		if !unresolved[fixture.unresolved] || !unresolved["authority:unknown"] {
			receipt.Reason = "approval is not pending: " + fixture.id
			return receipt
		}
		receipt.ApprovalDecisions = append(receipt.ApprovalDecisions, decision)
	}
	receipt.Decision = receipt.ApprovalDecisions[0]
	receipt.ProvisionalDecision = receipt.ApprovalDecisions[1]
	receipt.Passed = true
	return receipt
}
