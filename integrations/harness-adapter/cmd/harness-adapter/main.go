// Command harness-adapter runs one pinned Task through one or more registered
// harness adapters and writes a pilot report.
//
// The report is an observation record. It contains no PASS verdict, because no
// observation in this package can qualify a harness: a session id, a tool
// status and a process exit code are recorded separately from product
// acceptance, permission and effect.
//
// Usage:
//
//	harness-adapter -task task.json -out report.json [-adapters dsh-headless,direct-control]
//
// With -real, the command performs real connections to external harnesses.
// Without it, only adapters that need no external process are run and the
// report marks the rest not-run/ineligible. There is no mode that fakes a
// connection.
package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/hat47x/tai-pleroma/integrations/harness-adapter"
)

func main() {
	var (
		taskPath = flag.String("task", "", "path to a Task JSON file")
		outPath  = flag.String("out", "", "path to write the pilot report JSON")
		names    = flag.String("adapters", "direct-control", "comma-separated adapter names")
		real     = flag.Bool("real", false, "allow real connections to external harnesses")
		timeout  = flag.Duration("timeout", 20*time.Minute, "overall timeout")
		dshProf  = flag.String("dsh-profile", "headless", "DSH profile to boot")
		dshCLI   = flag.String("dsh-cli", "dsh", "DSH executable")
		dshMode  = flag.String("dsh-permission-mode", "", "DSH --permission-mode (empty: harness default)")
		dshAppr  = flag.String("dsh-approval-policy", "", "DSH --approval-policy")
		dshDirs  = flag.String("dsh-add-dir", "", "comma-separated --add-dir values")
		dshPatch = flag.String("dsh-patch", "", "comma-separated --patch overlays")
		codexCLI     = flag.String("codex-cli", "codex", "Codex CLI executable for codex-exec")
		codexVersion = flag.String("codex-version", "", "exact output of codex --version; empty permits unqualified version")
		ccCLI    = flag.String("claude-cli", "claude", "Claude Code executable")
		ccTools  = flag.String("claude-tools", "", "Claude Code --tools value")
		ccMode   = flag.String("claude-permission-mode", "", "Claude Code --permission-mode")
		ccPrompt = flag.String("claude-permission-prompts", "none", "Claude Code --permission-prompts")
		ccDirs   = flag.String("claude-add-dir", "", "comma-separated --add-dir values")
		ccMCP    = flag.String("claude-mcp-config", "", "comma-separated --mcp-config values")
	)
	flag.Parse()

	if *taskPath == "" {
		fmt.Fprintln(os.Stderr, "harness-adapter: -task is required")
		os.Exit(2)
	}
	raw, err := os.ReadFile(*taskPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "harness-adapter: read task: %v\n", err)
		os.Exit(2)
	}
	var task harnessadapter.Task
	if err := json.Unmarshal(raw, &task); err != nil {
		fmt.Fprintf(os.Stderr, "harness-adapter: parse task: %v\n", err)
		os.Exit(2)
	}

	ctx, cancel := context.WithTimeout(context.Background(), *timeout)
	defer cancel()

	reg := harnessadapter.NewRegistry()
	reg.Register(harnessadapter.NewDirectControlAdapter())
	for _, name := range splitList(*names) {
		if name == "direct-control" {
			continue
		}
		if !*real {
			fmt.Fprintf(os.Stderr, "harness-adapter: adapter %q needs a real connection; rerun with -real\n", name)
			continue
		}
		switch name {
		case "dsh-headless":
			a := harnessadapter.NewDSHHeadlessAdapter(*dshProf, task.WorkDirHint())
			a.CLI = *dshCLI
			a.PermissionMode = *dshMode
			a.ApprovalPolicy = *dshAppr
			a.AddDirs = splitList(*dshDirs)
			a.PatchFiles = splitList(*dshPatch)
			reg.Register(a)
		case "codex-exec":
			a := harnessadapter.NewCodexExecAdapter(task.WorkDirHint())
			a.CLI = *codexCLI
			a.ExpectedVersion = *codexVersion
			reg.Register(a)
		case "claude-code":
			a := harnessadapter.NewClaudeCodeAdapter(task.WorkDirHint())
			a.CLI = *ccCLI
			a.Tools = *ccTools
			a.PermissionMode = *ccMode
			a.PermissionPrompts = *ccPrompt
			a.AddDirs = splitList(*ccDirs)
			a.MCPConfigs = splitList(*ccMCP)
			reg.Register(a)
		default:
			fmt.Fprintf(os.Stderr, "harness-adapter: unknown adapter %q\n", name)
			os.Exit(2)
		}
	}

	adapters := make([]harnessadapter.Adapter, 0, len(reg.Names()))
	for _, name := range reg.Names() {
		a, ok := reg.Get(name)
		if !ok {
			continue
		}
		adapters = append(adapters, a)
	}
	rep := harnessadapter.Pilot(ctx, adapters, task, nil)
	fmt.Print(rep.Summary())
	if *outPath != "" {
		b, err := rep.JSON()
		if err != nil {
			fmt.Fprintf(os.Stderr, "harness-adapter: marshal report: %v\n", err)
			os.Exit(1)
		}
		if err := os.WriteFile(*outPath, b, 0o644); err != nil {
			fmt.Fprintf(os.Stderr, "harness-adapter: write report: %v\n", err)
			os.Exit(1)
		}
	}
	// A report is an observation, so the process exit is not a verdict either.
	// It is non-zero only when the report could not be produced.
}

// splitList parses a comma-separated flag value.
func splitList(v string) []string {
	var out []string
	for _, p := range strings.Split(v, ",") {
		p = strings.TrimSpace(p)
		if p != "" {
			out = append(out, p)
		}
	}
	return out
}
