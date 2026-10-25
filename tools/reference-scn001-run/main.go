package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

type MMIComponent struct {
	Passed                bool   `json:"passed"`
	Server                string `json:"server,omitempty"`
	ProtocolVersion       string `json:"protocolVersion,omitempty"`
	MmiCommit             string `json:"mmiCommit,omitempty"`
	SelectedRows          int    `json:"selectedRows"`
	ConflictPreserved     bool   `json:"conflictPreserved"`
	BoundaryRejected      bool   `json:"boundaryRejected"`
	MissingSourceRejected bool   `json:"missingSourceRejected"`
	SourceDigestBefore    string `json:"sourceDigestBefore,omitempty"`
	SourceDigestAfter     string `json:"sourceDigestAfter,omitempty"`
}

type DecisionView struct {
	ID              string   `json:"id"`
	Statement       string   `json:"statement"`
	Recommendations []string `json:"recommendations"`
}

type SEIComponent struct {
	Passed              bool         `json:"passed"`
	SeiCommit           string       `json:"seiCommit,omitempty"`
	GoVersion           string       `json:"goVersion,omitempty"`
	BundleID            string       `json:"bundleId,omitempty"`
	RecordCount         int          `json:"recordCount"`
	Decision            DecisionView `json:"decision"`
	ProvisionalDecision DecisionView `json:"provisionalDecision"`
	ProvisionalApproved bool         `json:"provisionalApproved"`
	ReviewTrigger       string       `json:"reviewTrigger,omitempty"`
	AuthorityVerified   bool         `json:"authorityVerified"`
	HumanReviewed       bool         `json:"humanReviewed"`
	Published           bool         `json:"published"`
	ReadOnlyProjection  bool         `json:"readOnlyProjection"`
}

type ArtifactComponent struct {
	Passed              bool   `json:"passed"`
	Status              string `json:"status"`
	DraftID             string `json:"draftId"`
	ArtifactDigest      string `json:"artifactDigest"`
	ProvisionalApproved bool   `json:"provisionalApproved"`
	PublicationApproved bool   `json:"publicationApproved"`
	ReviewRequired      bool   `json:"reviewRequired"`
	ReviewTrigger       string `json:"reviewTrigger"`
	AuthorityVerified   bool   `json:"authorityVerified"`
}

type GateComponent struct {
	Schema   string   `json:"schema"`
	Allowed  bool     `json:"allowed"`
	Blockers []string `json:"blockers"`
}

type CaseResult struct {
	ID     string `json:"id"`
	Status string `json:"status"`
}

type SCNComponent struct {
	Passed                bool         `json:"passed"`
	ObservationSource     string       `json:"observationSource"`
	RealProductsConnected bool         `json:"realProductsConnected"`
	Synthetic             bool         `json:"synthetic"`
	HumanReviewed         bool         `json:"humanReviewed"`
	AuthorityVerified     bool         `json:"authorityVerified"`
	ProvisionalApproved   bool         `json:"provisionalApproved"`
	PublicationApproved   bool         `json:"publicationApproved"`
	ReviewRequired        bool         `json:"reviewRequired"`
	ReviewTrigger         string       `json:"reviewTrigger,omitempty"`
	Cases                 []CaseResult `json:"cases"`
}

type RunReceipt struct {
	Schema      string `json:"schema"`
	Scenario    string `json:"scenario"`
	GeneratedAt string `json:"generatedAt"`
	RunDigest   string `json:"runDigest"`
	Components  struct {
		MMI             MMIComponent      `json:"mmi"`
		SEI             SEIComponent      `json:"sei"`
		SCN001          SCNComponent      `json:"scn001"`
		ReviewArtifact  ArtifactComponent `json:"reviewArtifact"`
		PublicationGate GateComponent     `json:"publicationGate"`
	} `json:"components"`
	Passed                bool     `json:"passed"`
	Synthetic             bool     `json:"synthetic"`
	RealProductsConnected bool     `json:"realProductsConnected"`
	HumanReviewed         bool     `json:"humanReviewed"`
	AuthorityVerified     bool     `json:"authorityVerified"`
	ProvisionalApproved   bool     `json:"provisionalApproved"`
	PublicationApproved   bool     `json:"publicationApproved"`
	PublicationAllowed    bool     `json:"publicationAllowed"`
	PublicationBlockers   []string `json:"publicationBlockers"`
	ReviewRequired        bool     `json:"reviewRequired"`
	ReviewTrigger         string   `json:"reviewTrigger,omitempty"`
	Published             bool     `json:"published"`
	Notes                 []string `json:"notes"`
}

func goRunOutput(ctx context.Context, dir string, args ...string) ([]byte, error) {
	cmd := exec.CommandContext(ctx, "go", args...)
	cmd.Dir = dir
	output, err := cmd.CombinedOutput()
	if err != nil {
		return output, fmt.Errorf("go %s in %s: %w: %s", strings.Join(args, " "), dir, err, strings.TrimSpace(string(output)))
	}
	return output, nil
}

func goRunAllowExit(ctx context.Context, dir string, args ...string) ([]byte, error) {
	cmd := exec.CommandContext(ctx, "go", args...)
	cmd.Dir = dir
	output, err := cmd.Output()
	if err != nil {
		if exitErr, ok := err.(*exec.ExitError); ok && exitErr.ExitCode() == 1 {
			return output, nil
		}
		return output, fmt.Errorf("go %s in %s: %w", strings.Join(args, " "), dir, err)
	}
	return output, nil
}

func goRun(ctx context.Context, dir string, args ...string) error {
	cmd := exec.CommandContext(ctx, "go", args...)
	cmd.Dir = dir
	output, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("go %s in %s: %w: %s", strings.Join(args, " "), dir, err, strings.TrimSpace(string(output)))
	}
	return nil
}

func readJSON(path string, target any) error {
	raw, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	return json.Unmarshal(raw, target)
}

func digestJSON(value any) (string, error) {
	raw, err := json.Marshal(value)
	if err != nil {
		return "", err
	}
	sum := sha256.Sum256(raw)
	return "sha256:" + hex.EncodeToString(sum[:]), nil
}

type OwnerQuestion struct {
	ID         string `json:"id"`
	Question   string `json:"question"`
	WhyBlocked string `json:"whyBlocked"`
}

type OwnerPacket struct {
	Schema               string          `json:"schema"`
	Scenario             string          `json:"scenario"`
	Status               string          `json:"status"`
	RunDigest            string          `json:"runDigest"`
	ReviewArtifactDigest string          `json:"reviewArtifactDigest,omitempty"`
	ReviewArtifactStatus string          `json:"reviewArtifactStatus,omitempty"`
	Evidence             []string        `json:"evidence"`
	Questions            []OwnerQuestion `json:"questions"`
	ProvisionalApproved  bool            `json:"provisionalApproved"`
	ReviewTrigger        string          `json:"reviewTrigger,omitempty"`
	Approved             bool            `json:"approved"`
	HumanReviewed        bool            `json:"humanReviewed"`
	AuthorityVerified    bool            `json:"authorityVerified"`
	PublicationApproved  bool            `json:"publicationApproved"`
	Notes                []string        `json:"notes"`
}

func BuildOwnerPacket(receipt RunReceipt) (OwnerPacket, error) {
	if verification := Verify(receipt); !verification.Passed {
		return OwnerPacket{}, fmt.Errorf("run receipt is not verifiable: %s", verification.Reason)
	}
	return OwnerPacket{
		Schema: "tai.reference.scn001-owner-packet/v0", Scenario: receipt.Scenario,
		Status: "awaiting-owner", RunDigest: receipt.RunDigest,
		ReviewArtifactDigest: receipt.Components.ReviewArtifact.ArtifactDigest,
		ReviewArtifactStatus: receipt.Components.ReviewArtifact.Status,
		Evidence: []string{
			"tools/reference-scn001-run/README.md",
			"tools/reference-scn001/README.md",
			"tools/reference-scn001-render/README.md",
			"tools/reference-mmi-readonly/README.md",
			"tools/reference-sei-decision/README.md",
			"evaluations/artifacts/SCN-001-D-04-provisional.md",
			"evaluations/records/SCN-001-run-2026-10-26.json",
			"evaluations/SCN-001-real-object-review.md",
		},
		Questions: []OwnerQuestion{
			{ID: "Q-01", Question: "SCN-001の案内文を公開する権限者は誰か。", WhyBlocked: "authority:unknownのままでは公開・外部作用へ進めない。"},
			{ID: "Q-02", Question: "個人・組織・社会の主体規模比較（P-06）を初回に含めるか。", WhyBlocked: "P-06はnot-runで、人間の比較判断が必要。"},
			{ID: "Q-03", Question: "EKIの限定委任（N-05）を初回の範囲に含めるか。", WhyBlocked: "委任の利益と独立確認が未検証。"},
			{ID: "Q-04", Question: "この合成fixtureと参照接続の範囲を、SCN-001の初回実証として受理するか。", WhyBlocked: "合成試験の成功は利用者価値・実運用の証明ではない。"},
		},
		ProvisionalApproved: receipt.ProvisionalApproved,
		ReviewTrigger:       receipt.ReviewTrigger,
		Approved:            false, HumanReviewed: false, AuthorityVerified: false, PublicationApproved: false,
		Notes: []string{
			"このpacketはOwner判断を求めるための入力であり、承認ではない。",
			"development-review-onlyの仮承認は記録済みだが、公開承認ではない。実物ベースの再レビューを要する。",
			"runDigestは参照実行の内部整合だけを示し、署名・実行者・Authorityを証明しない。",
			"P-06とN-05はnot-runであり、知的機能の受入合格ではない。",
		},
	}, nil
}

type Verification struct {
	Schema    string `json:"schema"`
	Passed    bool   `json:"passed"`
	Reason    string `json:"reason,omitempty"`
	RunDigest string `json:"runDigest,omitempty"`
}

func Verify(receipt RunReceipt) Verification {
	verification := Verification{Schema: "tai.reference.scn001-run-verification/v0", RunDigest: receipt.RunDigest}
	if receipt.Schema != "tai.reference.scn001-run/v0" {
		verification.Reason = "unexpected run schema"
		return verification
	}
	if receipt.HumanReviewed || receipt.AuthorityVerified || receipt.Published {
		verification.Reason = "run receipt claims human review, authority, or publication"
		return verification
	}
	mmi := receipt.Components.MMI
	sei := receipt.Components.SEI
	scn := receipt.Components.SCN001
	artifact := receipt.Components.ReviewArtifact
	// A successful synthetic evaluation must agree with its individual case results.
	// A component digest alone cannot establish that agreement.
	if scn.Passed {
		required := map[string]string{
			"P-01": "pass", "P-02": "pass", "P-03": "pass", "P-04": "pass",
			"P-05": "pass", "P-06": "not-run", "P-07": "pass",
			"N-01": "pass", "N-02": "pass", "N-03": "pass", "N-04": "pass",
			"N-05": "not-run", "N-06": "pass", "N-07": "pass",
		}
		if len(scn.Cases) != len(required) {
			verification.Reason = "SCN-001 case count does not match the successful reference evaluation"
			return verification
		}
		seen := map[string]bool{}
		for _, item := range scn.Cases {
			status, ok := required[item.ID]
			if !ok || seen[item.ID] || item.Status != status {
				verification.Reason = "SCN-001 case status is inconsistent with the successful reference evaluation"
				return verification
			}
			seen[item.ID] = true
		}
	}
	if receipt.Passed != (mmi.Passed && sei.Passed && scn.Passed && artifact.Passed) {
		verification.Reason = "overall pass does not match component outcomes"
		return verification
	}
	if artifact.Passed && (artifact.Status != "provisional" || artifact.DraftID != "D-04" ||
		artifact.ArtifactDigest == "" || !artifact.ProvisionalApproved || artifact.PublicationApproved ||
		!artifact.ReviewRequired || artifact.ReviewTrigger != "real-object" || artifact.AuthorityVerified) {
		verification.Reason = "review artifact component is incomplete"
		return verification
	}
	gate := receipt.Components.PublicationGate
	if gate.Allowed && len(gate.Blockers) != 0 {
		verification.Reason = "publication gate is allowed but has blockers"
		return verification
	}
	if !gate.Allowed && len(gate.Blockers) == 0 {
		verification.Reason = "publication gate is blocked without a blocker"
		return verification
	}
	if receipt.PublicationAllowed != gate.Allowed {
		verification.Reason = "publication allowed does not match the gate"
		return verification
	}
	if mmi.Passed && (mmi.Server == "" || mmi.ProtocolVersion != "2024-11-05" ||
		mmi.SelectedRows != 3 || !mmi.ConflictPreserved || !mmi.BoundaryRejected ||
		!mmi.MissingSourceRejected || mmi.SourceDigestBefore == "" ||
		mmi.SourceDigestBefore != mmi.SourceDigestAfter) {
		verification.Reason = "MMI component is incomplete"
		return verification
	}
	if sei.Passed && (sei.SeiCommit == "" || sei.RecordCount != 3 || sei.Decision.ID != "dec-01" ||
		sei.ProvisionalDecision.ID != "dec-02" || !sei.ProvisionalApproved || sei.ReviewTrigger != "real-object" ||
		!sei.ReadOnlyProjection || sei.AuthorityVerified || sei.HumanReviewed || sei.Published) {
		verification.Reason = "SEI component is incomplete"
		return verification
	}
	if scn.Passed && (scn.ObservationSource != "mmi-reference" || !scn.RealProductsConnected ||
		!scn.Synthetic || scn.HumanReviewed || scn.AuthorityVerified ||
		!scn.ProvisionalApproved || scn.PublicationApproved || !scn.ReviewRequired || scn.ReviewTrigger != "real-object") {
		verification.Reason = "SCN-001 component is incomplete"
		return verification
	}
	if receipt.PublicationApproved || !receipt.ReviewRequired && receipt.ProvisionalApproved {
		verification.Reason = "provisional approval was reported as publication"
		return verification
	}
	if receipt.ProvisionalApproved && !(sei.ProvisionalApproved && scn.ProvisionalApproved) {
		verification.Reason = "provisional approval is not supported by the components"
		return verification
	}
	if receipt.ProvisionalApproved && receipt.ReviewTrigger != "real-object" {
		verification.Reason = "provisional approval lacks the real-object review trigger"
		return verification
	}
	if receipt.Passed && (!mmi.Passed || !sei.Passed || !scn.Passed || !artifact.Passed) {
		verification.Reason = "overall pass does not match the components"
		return verification
	}
	if receipt.RealProductsConnected && !(mmi.Passed && sei.Passed && scn.RealProductsConnected) {
		verification.Reason = "real product connection is not supported by all components"
		return verification
	}
	digest, err := digestJSON(receipt.Components)
	if err != nil {
		verification.Reason = err.Error()
		return verification
	}
	if receipt.RunDigest == "" || receipt.RunDigest != digest {
		verification.Reason = "run digest does not match the components"
		return verification
	}
	verification.Passed = true
	return verification
}

func Run(ctx context.Context, root string) (RunReceipt, error) {
	receipt := RunReceipt{Schema: "tai.reference.scn001-run/v0", Scenario: "SCN-001", Synthetic: true}
	tools := filepath.Join(root, "tools")
	mmiTool := filepath.Join(tools, "reference-mmi-readonly")
	seiTool := filepath.Join(tools, "reference-sei-decision")
	scnTool := filepath.Join(tools, "reference-scn001")
	renderTool := filepath.Join(tools, "reference-scn001-render")
	gateTool := filepath.Join(tools, "reference-publication-gate")
	for _, dir := range []string{mmiTool, seiTool, scnTool, renderTool, gateTool} {
		if info, err := os.Stat(dir); err != nil || !info.IsDir() {
			return receipt, fmt.Errorf("tool directory is unavailable: %s", dir)
		}
	}
	work, err := os.MkdirTemp("", "tai-scn001-run-")
	if err != nil {
		return receipt, err
	}
	defer os.RemoveAll(work)
	mmiPath := filepath.Join(work, "mmi.json")
	seiPath := filepath.Join(work, "sei.json")
	scnPath := filepath.Join(work, "scn001.json")
	resolvedFixturePath := filepath.Join(work, "resolved-scn001.json")
	artifactPath := filepath.Join(work, "d04.md")

	if err := goRun(ctx, mmiTool, "run", ".", "-workspace", "testdata/workspace", "-out", mmiPath); err != nil {
		return receipt, err
	}
	if err := goRun(ctx, seiTool, "run", ".", "-out", seiPath); err != nil {
		return receipt, err
	}
	if err := goRun(ctx, scnTool, "run", ".", "-fixture", "testdata/scn001.json",
		"-mmi-receipt", mmiPath, "-out-fixture", resolvedFixturePath, "-out", scnPath); err != nil {
		return receipt, err
	}
	renderOutput, err := goRunOutput(ctx, renderTool, "run", ".", "-fixture", resolvedFixturePath, "-out", artifactPath)
	if err != nil {
		return receipt, err
	}
	if err := json.Unmarshal(renderOutput, &receipt.Components.ReviewArtifact); err != nil {
		return receipt, fmt.Errorf("review artifact receipt is invalid: %w", err)
	}
	gateOutput, err := goRunAllowExit(ctx, gateTool, "run", ".", "-status", "../../evaluations/SCN-001-review-status.json")
	if err != nil {
		return receipt, err
	}
	if err := json.Unmarshal(gateOutput, &receipt.Components.PublicationGate); err != nil {
		return receipt, fmt.Errorf("publication gate receipt is invalid: %w", err)
	}
	// The renderer's digest must match the bytes written for this run, not merely exist.
	artifactBytes, err := os.ReadFile(artifactPath)
	if err != nil {
		return receipt, fmt.Errorf("reading rendered D-04: %w", err)
	}
	artifactHash := sha256.Sum256(artifactBytes)
	if receipt.Components.ReviewArtifact.ArtifactDigest != "sha256:"+hex.EncodeToString(artifactHash[:]) {
		return receipt, fmt.Errorf("D-04 artifact bytes do not match the renderer receipt")
	}
	if err := readJSON(mmiPath, &receipt.Components.MMI); err != nil {
		return receipt, err
	}
	if err := readJSON(seiPath, &receipt.Components.SEI); err != nil {
		return receipt, err
	}
	if err := readJSON(scnPath, &receipt.Components.SCN001); err != nil {
		return receipt, err
	}
	receipt.GeneratedAt = time.Now().UTC().Format(time.RFC3339)
	receipt.RealProductsConnected = receipt.Components.MMI.Passed && receipt.Components.MMI.SourceDigestBefore != "" &&
		receipt.Components.SEI.Passed && receipt.Components.SCN001.RealProductsConnected
	receipt.Passed = receipt.Components.MMI.Passed && receipt.Components.SEI.Passed &&
		receipt.Components.SCN001.Passed && receipt.Components.ReviewArtifact.Passed
	receipt.HumanReviewed = false
	receipt.AuthorityVerified = false
	receipt.Published = false
	receipt.ProvisionalApproved = receipt.Components.SEI.ProvisionalApproved && receipt.Components.SCN001.ProvisionalApproved
	receipt.ReviewRequired = receipt.ProvisionalApproved
	receipt.ReviewTrigger = "real-object"
	receipt.PublicationApproved = false
	receipt.PublicationAllowed = receipt.Components.PublicationGate.Allowed
	receipt.PublicationBlockers = receipt.Components.PublicationGate.Blockers
	receipt.Notes = []string{
		"MMIの読み取り専用観測とSEIのdecision-memory projection、SCN-001合成評価を1回の参照実行に束ねた。",
		"Draft・仮説・判断・revisionは合成fixtureであり、人間の判断ではない。",
		"SEIの一時storeは参照用で、実在の規程・権限・公開ではない。",
		"仮承認はdevelopment-review-onlyで、公開承認ではなく、実物ベースの再レビューを要する。",
		"D-04の内部レビュー用Markdownを生成し、そのdigestをreviewArtifactへ記録した。公開用ではない。",
		"publicationGateは実物レビューR-01〜R-07の状態を読み、公開可否だけを判定する。",
		"P-06とN-05はnot-runであり、全体の知的機能の合格ではない。",
	}
	digest, err := digestJSON(receipt.Components)
	if err != nil {
		return receipt, err
	}
	receipt.RunDigest = digest
	return receipt, nil
}

func main() {
	root := flag.String("root", "", "TAI checkout root (default: ../..)")
	verifyPath := flag.String("verify", "", "verify an existing run receipt instead of running")
	ownerPacketPath := flag.String("owner-packet", "", "build an owner decision packet from an existing run receipt")
	outPath := flag.String("out", "", "write receipt JSON to this file")
	flag.Parse()
	if *ownerPacketPath != "" {
		raw, err := os.ReadFile(*ownerPacketPath)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
		var receipt RunReceipt
		if err := json.Unmarshal(raw, &receipt); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
		packet, err := BuildOwnerPacket(receipt)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		encoded, err := json.MarshalIndent(packet, "", "  ")
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
		return
	}
	if *verifyPath != "" {
		raw, err := os.ReadFile(*verifyPath)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
		var receipt RunReceipt
		if err := json.Unmarshal(raw, &receipt); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
		verification := Verify(receipt)
		encoded, err := json.MarshalIndent(verification, "", "  ")
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
		os.Stdout.Write(append(encoded, '\n'))
		if !verification.Passed {
			os.Exit(1)
		}
		return
	}
	if *root == "" {
		*root = filepath.Clean(filepath.Join("..", ".."))
	}
	ctx, cancel := context.WithTimeout(context.Background(), 180*time.Second)
	defer cancel()
	receipt, err := Run(ctx, *root)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
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
