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
	Passed             bool         `json:"passed"`
	SeiCommit          string       `json:"seiCommit,omitempty"`
	GoVersion          string       `json:"goVersion,omitempty"`
	BundleID           string       `json:"bundleId,omitempty"`
	RecordCount        int          `json:"recordCount"`
	Decision           DecisionView `json:"decision"`
	AuthorityVerified  bool         `json:"authorityVerified"`
	HumanReviewed      bool         `json:"humanReviewed"`
	Published          bool         `json:"published"`
	ReadOnlyProjection bool         `json:"readOnlyProjection"`
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
	Cases                 []CaseResult `json:"cases"`
}

type RunReceipt struct {
	Schema      string `json:"schema"`
	Scenario    string `json:"scenario"`
	GeneratedAt string `json:"generatedAt"`
	RunDigest   string `json:"runDigest"`
	Components  struct {
		MMI    MMIComponent `json:"mmi"`
		SEI    SEIComponent `json:"sei"`
		SCN001 SCNComponent `json:"scn001"`
	} `json:"components"`
	Passed                bool     `json:"passed"`
	Synthetic             bool     `json:"synthetic"`
	RealProductsConnected bool     `json:"realProductsConnected"`
	HumanReviewed         bool     `json:"humanReviewed"`
	AuthorityVerified     bool     `json:"authorityVerified"`
	Published             bool     `json:"published"`
	Notes                 []string `json:"notes"`
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
	for _, dir := range []string{mmiTool, seiTool, scnTool} {
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

	if err := goRun(ctx, mmiTool, "run", ".", "-workspace", "testdata/workspace", "-out", mmiPath); err != nil {
		return receipt, err
	}
	if err := goRun(ctx, seiTool, "run", ".", "-out", seiPath); err != nil {
		return receipt, err
	}
	if err := goRun(ctx, scnTool, "run", ".", "-fixture", "testdata/scn001.json", "-mmi-receipt", mmiPath, "-out", scnPath); err != nil {
		return receipt, err
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
	receipt.Passed = receipt.Components.MMI.Passed && receipt.Components.SEI.Passed && receipt.Components.SCN001.Passed
	receipt.HumanReviewed = false
	receipt.AuthorityVerified = false
	receipt.Published = false
	receipt.Notes = []string{
		"MMIの読み取り専用観測とSEIのdecision-memory projection、SCN-001合成評価を1回の参照実行に束ねた。",
		"Draft・仮説・判断・revisionは合成fixtureであり、人間の判断ではない。",
		"SEIの一時storeは参照用で、実在の規程・権限・公開ではない。",
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
	outPath := flag.String("out", "", "write run receipt JSON to this file")
	flag.Parse()
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
