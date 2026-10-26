package main

import (
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

type Receipt struct {
	Schema            string   `json:"schema"`
	EkiCommit         string   `json:"ekiCommit"`
	GoVersion         string   `json:"goVersion"`
	ControlVersion    string   `json:"controlVersion"`
	AgentVersion      string   `json:"agentVersion"`
	ReadOnly          bool     `json:"readOnly"`
	TaskDelegated     bool     `json:"taskDelegated"`
	AuthorityVerified bool     `json:"authorityVerified"`
	Passed            bool     `json:"passed"`
	Reason            string   `json:"reason,omitempty"`
	Notes             []string `json:"notes"`
}

func commandOutput(ctx context.Context, dir, name string, args ...string) (string, error) {
	cmd := exec.CommandContext(ctx, name, args...)
	cmd.Dir = dir
	output, err := cmd.Output()
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(output)), nil
}

func Run(ctx context.Context, ekiRoot string) Receipt {
	receipt := Receipt{
		Schema: "tai.reference.eki-cli/v0", ReadOnly: true,
		Notes: []string{
			"EKIの`eki-control`/`eki-agent`のversion表示だけを確認する。",
			"Taskの委任・Worker・Authority・結果検証は未実施。",
		},
	}
	if _, err := os.Stat(filepath.Join(ekiRoot, "cmd", "eki-control")); err != nil {
		receipt.Reason = "EKI control command is unavailable: " + err.Error()
		return receipt
	}
	if _, err := exec.LookPath("go"); err != nil {
		receipt.Reason = "go is unavailable: " + err.Error()
		return receipt
	}
	receipt.EkiCommit, _ = commandOutput(ctx, ekiRoot, "git", "rev-parse", "HEAD")
	receipt.GoVersion, _ = commandOutput(ctx, ekiRoot, "go", "version")
	control, err := commandOutput(ctx, ekiRoot, "go", "run", "./cmd/eki-control", "--version")
	if err != nil {
		receipt.Reason = "eki-control --version failed: " + err.Error()
		return receipt
	}
	agent, err := commandOutput(ctx, ekiRoot, "go", "run", "./cmd/eki-agent", "--version")
	if err != nil {
		receipt.Reason = "eki-agent --version failed: " + err.Error()
		return receipt
	}
	receipt.ControlVersion = control
	receipt.AgentVersion = agent
	if control == "" || agent == "" {
		receipt.Reason = "EKI version output is empty"
		return receipt
	}
	receipt.Passed = true
	return receipt
}

func main() {
	ekiRoot := flag.String("eki-root", "", "EKI checkout root (default: EKI_ROOT or ../../../eki-fabric)")
	outPath := flag.String("out", "", "write receipt JSON")
	flag.Parse()
	root := *ekiRoot
	if root == "" {
		root = os.Getenv("EKI_ROOT")
	}
	if root == "" {
		root = filepath.Clean(filepath.Join("..", "..", "..", "eki-fabric"))
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
