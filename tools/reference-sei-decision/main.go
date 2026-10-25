package main

import (
	"bytes"
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

type DecisionView struct {
	ID              string   `json:"id"`
	Statement       string   `json:"statement"`
	Recommendations []string `json:"recommendations"`
	Responsible     []string `json:"responsible"`
}

type UnresolvedView struct {
	Ref        string `json:"ref"`
	LeftOpenBy string `json:"left_open_by_decision"`
}

type ResumeView struct {
	BundleID               string           `json:"bundle_id"`
	RecordCount            int              `json:"record_count"`
	Decisions              []DecisionView   `json:"decisions"`
	RecommendationsOpen    []any            `json:"recommendations_not_yet_relied_on"`
	RecommendationsRelied  []any            `json:"recommendations_relied_on"`
	Unresolved             []UnresolvedView `json:"unresolved"`
	NotVerifiedRecordCount int              `json:"not_verified_record_count"`
}

type Receipt struct {
	Schema                 string           `json:"schema"`
	SeiCommit              string           `json:"seiCommit"`
	GoVersion              string           `json:"goVersion"`
	StoreCreated           bool             `json:"storeCreated"`
	ReadOnlyProjection     bool             `json:"readOnlyProjection"`
	BundleID               string           `json:"bundleId"`
	RecordCount            int              `json:"recordCount"`
	Decision               DecisionView     `json:"decision"`
	ProvisionalDecision    DecisionView     `json:"provisionalDecision"`
	Unresolved             []UnresolvedView `json:"unresolved"`
	NotVerifiedRecordCount int              `json:"notVerifiedRecordCount"`
	ProvisionalApproved    bool             `json:"provisionalApproved"`
	AuthorityVerified      bool             `json:"authorityVerified"`
	HumanReviewed          bool             `json:"humanReviewed"`
	Published              bool             `json:"published"`
	Passed                 bool             `json:"passed"`
	Reason                 string           `json:"reason,omitempty"`
	Notes                  []string         `json:"notes"`
}

func run(ctx context.Context, dir string, args ...string) ([]byte, error) {
	cmd := exec.CommandContext(ctx, "go", args...)
	cmd.Dir = dir
	output, err := cmd.CombinedOutput()
	if err != nil {
		return output, fmt.Errorf("go %s: %w: %s", strings.Join(args, " "), err, strings.TrimSpace(string(output)))
	}
	return output, nil
}

func output(ctx context.Context, dir, name string, args ...string) string {
	cmd := exec.CommandContext(ctx, name, args...)
	cmd.Dir = dir
	raw, err := cmd.Output()
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(raw))
}

func Run(ctx context.Context, seiRoot string) Receipt {
	receipt := Receipt{
		Schema: "tai.reference.sei-decision/v0", ReadOnlyProjection: true,
		AuthorityVerified: false, HumanReviewed: false, Published: false,
		Notes: []string{
			"SEIの一時storeへ合成fixtureを記録し、resumeのprojectionだけを読む参照。",
			"決定の意味・権限・公開を検証しない。実運用のstoreではない。",
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
	store, err := os.MkdirTemp("", "tai-sei-")
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	defer os.RemoveAll(store)
	receipt.SeiCommit = output(ctx, seiRoot, "git", "rev-parse", "HEAD")
	receipt.GoVersion = output(ctx, runtimeDir, "go", "version")

	steps := [][]string{
		{"run", "./cmd/sei", "init", "--data-root", store, "--bundle-id", "scn001"},
		{"run", "./cmd/sei", "add", "recommendation", "--data-root", store,
			"--id", "rec-01", "--statement", "O-02/O-03の矛盾を確認中", "--source", "tai",
			"--basis", "observation:O-02", "--basis", "observation:O-03"},
		{"run", "./cmd/sei", "add", "decision", "--data-root", store,
			"--id", "dec-01", "--statement", "公開は保留", "--source", "tai",
			"--unresolved", "authority:unknown", "--recommendation", "rec-01",
			"--responsible", "role:facility-owner"},
		{"run", "./cmd/sei", "add", "decision", "--data-root", store,
			"--id", "dec-02", "--statement", "D-04を内部レビュー用に仮承認。公開は未承認", "--source", "tai",
			"--unresolved", "authority:unknown", "--unresolved", "publication:unapproved",
			"--recommendation", "rec-01", "--responsible", "role:provisional-owner"},
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
	dec01, hasDec01 := findDecision(view.Decisions, "dec-01")
	dec02, hasDec02 := findDecision(view.Decisions, "dec-02")
	receipt.Decision = dec01
	receipt.ProvisionalDecision = dec02
	unresolved := map[string]bool{}
	for _, item := range view.Unresolved {
		unresolved[item.Ref] = true
	}
	if view.BundleID != "scn001" || view.RecordCount != 3 || len(view.Decisions) != 2 ||
		!hasDec01 || !hasDec02 || !unresolved["authority:unknown"] ||
		!unresolved["publication:unapproved"] || view.NotVerifiedRecordCount != 0 {
		receipt.Reason = "resume projection does not match the SCN-001 decision fixture"
		return receipt
	}
	if len(dec01.Recommendations) != 1 || dec01.Recommendations[0] != "recommendation:rec-01" ||
		len(dec02.Recommendations) != 1 || dec02.Recommendations[0] != "recommendation:rec-01" {
		receipt.Reason = "decision does not rely on rec-01"
		return receipt
	}
	if !strings.Contains(dec02.Statement, "仮承認") || strings.Contains(dec02.Statement, "公開承認") {
		receipt.Reason = "provisional decision is not scoped to internal review"
		return receipt
	}
	receipt.ProvisionalApproved = true
	receipt.Passed = true
	return receipt
}

func findDecision(decisions []DecisionView, id string) (DecisionView, bool) {
	for _, decision := range decisions {
		if decision.ID == id {
			return decision, true
		}
	}
	return DecisionView{}, false
}

func main() {
	seiRoot := flag.String("sei-root", "", "SEI checkout root (default: SEI_ROOT or ../../../sei-cognition)")
	outPath := flag.String("out", "", "write receipt JSON to this file")
	flag.Parse()
	root := *seiRoot
	if root == "" {
		root = os.Getenv("SEI_ROOT")
	}
	if root == "" {
		root = filepath.Clean(filepath.Join("..", "..", "..", "sei-cognition"))
	}
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	defer cancel()
	receipt := Run(ctx, root)
	encoded, err := json.MarshalIndent(receipt, "", "  ")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	encoded = append(encoded, '\n')
	if *outPath != "" {
		if err := os.WriteFile(*outPath, encoded, 0o644); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
	}
	os.Stdout.Write(encoded)
	if !receipt.Passed {
		os.Exit(1)
	}
}
