package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

type Receipt struct {
	Schema          string   `json:"schema"`
	TeiCommit       string   `json:"teiCommit"`
	GoVersion       string   `json:"goVersion"`
	WorkspaceDigest string   `json:"workspaceDigest"`
	Validation      string   `json:"validation"`
	ReadOnly        bool     `json:"readOnly"`
	Synthetic       bool     `json:"synthetic"`
	EvidenceKind    string   `json:"evidenceKind"`
	Passed          bool     `json:"passed"`
	Reason          string   `json:"reason,omitempty"`
	Notes           []string `json:"notes"`
}

func digestWorkspace(root string) (string, error) {
	var files []string
	err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() {
			return nil
		}
		relative, err := filepath.Rel(root, path)
		if err != nil {
			return err
		}
		files = append(files, relative)
		return nil
	})
	if err != nil {
		return "", err
	}
	sort.Strings(files)
	hash := sha256.New()
	for _, relative := range files {
		content, err := os.ReadFile(filepath.Join(root, relative))
		if err != nil {
			return "", err
		}
		hash.Write([]byte(relative))
		hash.Write([]byte{0})
		hash.Write(content)
		hash.Write([]byte{0})
	}
	return "sha256:" + hex.EncodeToString(hash.Sum(nil)), nil
}

func commandOutput(ctx context.Context, dir, name string, args ...string) string {
	cmd := exec.CommandContext(ctx, name, args...)
	cmd.Dir = dir
	output, err := cmd.Output()
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(output))
}

func Run(ctx context.Context, teiRoot, workspace string) Receipt {
	receipt := Receipt{
		Schema: "tai.reference.tei-model/v0", ReadOnly: true,
		Notes: []string{
			"TEIのvalidateだけを実行する読み取り専用接続。",
			"SCN-001のObservation/RuleCandidateの型宣言を検証するが、実データ・意味・Authorityは検証しない。",
		},
	}
	absWorkspace, err := filepath.Abs(workspace)
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	if _, err := os.Stat(filepath.Join(absWorkspace, "tei.workspace.yaml")); err != nil {
		receipt.Reason = "TEI workspace manifest is unavailable: " + err.Error()
		return receipt
	}
	if _, err := os.Stat(filepath.Join(teiRoot, "cmd", "tei")); err != nil {
		receipt.Reason = "TEI runtime is unavailable: " + err.Error()
		return receipt
	}
	if _, err := exec.LookPath("go"); err != nil {
		receipt.Reason = "go is unavailable: " + err.Error()
		return receipt
	}
	before, err := digestWorkspace(absWorkspace)
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	receipt.WorkspaceDigest = before
	receipt.TeiCommit = commandOutput(ctx, teiRoot, "git", "rev-parse", "HEAD")
	receipt.GoVersion = commandOutput(ctx, teiRoot, "go", "version")
	cmd := exec.CommandContext(ctx, "go", "run", "./cmd/tei", "validate", "-workspace", absWorkspace)
	cmd.Dir = teiRoot
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	if err := cmd.Run(); err != nil {
		receipt.Reason = fmt.Sprintf("TEI validate failed: %v: %s", err, strings.TrimSpace(stderr.String()))
		return receipt
	}
	receipt.Validation = strings.TrimSpace(stdout.String())
	if receipt.Validation != "ok" {
		receipt.Reason = "TEI validate did not report ok: " + receipt.Validation
		return receipt
	}
	after, err := digestWorkspace(absWorkspace)
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	if before != after {
		receipt.Reason = "TEI validate changed the workspace"
		return receipt
	}
	receipt.Passed = true
	return receipt
}

func main() {
	teiRoot := flag.String("tei-root", "", "TEI checkout root (default: TEI_ROOT or ../../../tei-platform)")
	workspace := flag.String("workspace", "testdata/workspace", "TEI workspace")
	synthetic := flag.Bool("synthetic", false, "mark the workspace as synthetic verification input")
	outPath := flag.String("out", "", "write receipt JSON to this file")
	flag.Parse()
	root := *teiRoot
	if root == "" {
		root = os.Getenv("TEI_ROOT")
	}
	if root == "" {
		root = filepath.Clean(filepath.Join("..", "..", "..", "tei-platform"))
	}
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	defer cancel()
	receipt := Run(ctx, root, *workspace)
	if *synthetic {
		receipt.Synthetic = true
		receipt.EvidenceKind = "synthetic"
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
