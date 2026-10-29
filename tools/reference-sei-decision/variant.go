package main

import (
	"bytes"
	"context"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

type variantFixture struct {
	bundle       string
	recommendID  string
	recommend    string
	decisionID   string
	decision     string
	unresolved   string
	unresolved2  string
	provisional  string
	provisionalD string
}

var variantFixtures = map[string]variantFixture{
	"b": {
		bundle:       "scn001-variant-b",
		recommendID:  "rec-variant-b",
		recommend:    "本館と別館の予約条件を比較中",
		decisionID:   "dec-variant-b-01",
		decision:     "本館は予約制、別館は予約不要として扱う。別館の現行案内は未確認",
		unresolved:   "scope:annex",
		provisional:  "dec-variant-b-02",
		provisionalD: "D-04 variant-bを内部レビュー用に仮承認。公開は未承認",
	},
	"c": {
		bundle:       "scn001-variant-c",
		recommendID:  "rec-variant-c",
		recommend:    "全館予約制と旧掲示の差を確認中",
		decisionID:   "dec-variant-c-01",
		decision:     "現行規程を優先するが、旧掲示の撤去は未確認",
		unresolved:   "notice:old",
		provisional:  "dec-variant-c-02",
		provisionalD: "D-04 variant-cを内部レビュー用に仮承認。公開は未承認",
	},
	"scn002": {
		bundle:       "scn002-maintenance",
		recommendID:  "rec-scn002",
		recommend:    "A拠点の期限差、B拠点の故障、予算上限を比較中",
		decisionID:   "dec-scn002-01",
		decision:     "A拠点を最優先、B拠点を次点、C拠点は保留",
		unresolved:   "due:conflict",
		unresolved2:  "budget:unapproved",
		provisional:  "dec-scn002-02",
		provisionalD: "D-05優先度案を内部レビュー用に仮承認。公開・発注は未承認",
	},
}

func RunVariant(ctx context.Context, seiRoot, variant string) Receipt {
	fixture, ok := variantFixtures[variant]
	if !ok {
		return Receipt{Reason: "unknown SEI variant: " + variant}
	}
	receipt := Receipt{
		Schema: "tai.reference.sei-decision/v0", Variant: variant, ReadOnlyProjection: true,
		AuthorityVerified: false, HumanReviewed: false, Published: false,
		Notes: []string{
			"SEIの一時storeへ合成variant fixtureを記録し、resumeのprojectionだけを読む参照。",
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
	store, err := os.MkdirTemp("", "tai-sei-variant-")
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	defer os.RemoveAll(store)
	receipt.SeiCommit = output(ctx, seiRoot, "git", "rev-parse", "HEAD")
	receipt.GoVersion = output(ctx, runtimeDir, "go", "version")

	decisionStep := []string{
		"run", "./cmd/sei", "add", "decision", "--data-root", store,
		"--id", fixture.decisionID, "--statement", fixture.decision, "--source", "tai",
		"--unresolved", fixture.unresolved, "--unresolved", "authority:unknown",
	}
	if fixture.unresolved2 != "" {
		decisionStep = append(decisionStep, "--unresolved", fixture.unresolved2)
	}
	decisionStep = append(decisionStep, "--recommendation", fixture.recommendID, "--responsible", "role:facility-owner")

	steps := [][]string{
		{"run", "./cmd/sei", "init", "--data-root", store, "--bundle-id", fixture.bundle},
		{"run", "./cmd/sei", "add", "recommendation", "--data-root", store,
			"--id", fixture.recommendID, "--statement", fixture.recommend, "--source", "tai",
			"--basis", "observation:O-02", "--basis", "observation:O-03"},
		decisionStep,
		{"run", "./cmd/sei", "add", "decision", "--data-root", store,
			"--id", fixture.provisional, "--statement", fixture.provisionalD, "--source", "tai",
			"--unresolved", "authority:unknown", "--unresolved", "publication:unapproved",
			"--unresolved", "review:real-object",
			"--recommendation", fixture.recommendID, "--responsible", "role:provisional-owner"},
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
	decision, hasDecision := findDecision(view.Decisions, fixture.decisionID)
	provisional, hasProvisional := findDecision(view.Decisions, fixture.provisional)
	receipt.Decision = decision
	receipt.ProvisionalDecision = provisional
	unresolved := map[string]bool{}
	for _, item := range view.Unresolved {
		unresolved[item.Ref] = true
	}
	if view.BundleID != fixture.bundle || view.RecordCount != 3 || len(view.Decisions) != 2 ||
		!hasDecision || !hasProvisional || !unresolved[fixture.unresolved] ||
		(fixture.unresolved2 != "" && !unresolved[fixture.unresolved2]) ||
		!unresolved["authority:unknown"] || !unresolved["publication:unapproved"] ||
		!unresolved["review:real-object"] || view.NotVerifiedRecordCount != 0 {
		receipt.Reason = "resume projection does not match the SEI variant fixture"
		return receipt
	}
	if len(decision.Recommendations) != 1 || decision.Recommendations[0] != "recommendation:"+fixture.recommendID ||
		len(provisional.Recommendations) != 1 || provisional.Recommendations[0] != "recommendation:"+fixture.recommendID {
		receipt.Reason = "variant decision does not rely on its recommendation"
		return receipt
	}
	if !strings.Contains(provisional.Statement, "仮承認") || strings.Contains(provisional.Statement, "公開承認") {
		receipt.Reason = "variant provisional decision is not scoped to internal review"
		return receipt
	}
	receipt.ProvisionalApproved = true
	receipt.ReviewTrigger = "real-object"
	receipt.Passed = true
	return receipt
}
