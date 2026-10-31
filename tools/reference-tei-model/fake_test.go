package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

// fakeTEIScenario controls a fake TEI CLI. Its output shapes were measured against
// the real CLI (57f09a7 and 490dd20); passing against this fake says nothing about
// the real product.
type fakeTEIScenario struct {
	TextOut  string `json:"textOut,omitempty"` // "-" prints nothing; default "ok\n"
	TextExit int    `json:"textExit,omitempty"`
	JSONOut  string `json:"jsonOut,omitempty"` // default: the honest report
	JSONExit int    `json:"jsonExit,omitempty"`
	// Catalog variations.
	CatalogOut    string `json:"catalogOut,omitempty"`    // replaces the whole stdout
	CatalogExit   int    `json:"catalogExit,omitempty"`   //
	CatalogOmit   string `json:"catalogOmit,omitempty"`   // data symbol left out
	CatalogDrop   string `json:"catalogDrop,omitempty"`   // "Observation.sourceVersion" left out
	CatalogRetype string `json:"catalogRetype,omitempty"` // "Observation.text=std.code"
	CatalogExtra  string `json:"catalogExtra,omitempty"`  // "Observation.extra" added
	Effect        string `json:"effect,omitempty"`
	// Writes. WriteOn is the call that writes: text (default), json or catalog.
	WriteOn            string `json:"writeOn,omitempty"`
	WriteWorkspace     string `json:"writeWorkspace,omitempty"`     // new file in the workspace
	OverwriteWorkspace string `json:"overwriteWorkspace,omitempty"` // same-length rewrite of an existing workspace file
	AppendTracked      string `json:"appendTracked,omitempty"`      // appended to a tracked file of the TEI checkout (cwd)
	WriteUntracked     string `json:"writeUntracked,omitempty"`     // new untracked file in the TEI checkout (cwd)
	LogPath            string `json:"logPath,omitempty"`
}

const honestValidateJSON = `{"schemaVersion":"tei.cli.validate/v0","ok":true,"diagnostics":[]}` + "\n"

func honestCatalog(scenario fakeTEIScenario) string {
	type subject = map[string]string
	entries := []map[string]any{
		{"subject": subject{"kind": "semantic", "id": "scn001"}, "sourceStatus": "indexed"},
	}
	for _, data := range declaredModel {
		if data.Symbol == scenario.CatalogOmit {
			continue
		}
		dataID := "scn001." + strings.ToLower(data.Symbol)
		entries = append(entries, map[string]any{
			"subject": subject{"kind": "semantic-data", "id": dataID}, "parent": subject{"kind": "semantic", "id": "scn001"},
			"symbol": data.Symbol, "sourceStatus": "indexed",
		})
		for name, typeRef := range data.Attributes {
			if scenario.CatalogDrop == data.Symbol+"."+name {
				continue
			}
			if want, ok := strings.CutPrefix(scenario.CatalogRetype, data.Symbol+"."+name+"="); ok {
				typeRef = want
			}
			entries = append(entries, map[string]any{
				"subject": subject{"kind": "semantic-attribute", "id": dataID + "." + name}, "parent": subject{"kind": "semantic-data", "id": dataID},
				"symbol": name, "detail": typeRef, "sourceStatus": "indexed",
			})
		}
		if symbol, name, ok := strings.Cut(scenario.CatalogExtra, "."); ok && symbol == data.Symbol {
			entries = append(entries, map[string]any{
				"subject": subject{"kind": "semantic-attribute", "id": dataID + "." + name}, "parent": subject{"kind": "semantic-data", "id": dataID},
				"symbol": name, "detail": "std.text", "sourceStatus": "indexed",
			})
		}
	}
	effect := "read-only"
	if scenario.Effect != "" {
		effect = scenario.Effect
	}
	raw, _ := json.Marshal(map[string]any{
		"schemaVersion": "tei.cli.model/v0", "ok": true,
		"result": map[string]any{
			"schemaVersion": "tei.operations.model-catalog/v0", "effect": effect,
			"worldFingerprint":       "sha256:" + strings.Repeat("1", 64),
			"sourceIndexFingerprint": "sha256:" + strings.Repeat("2", 64),
			"modelRevision":          "sha256:" + strings.Repeat("3", 64),
			"entries":                entries,
			"authorityLimits":        []string{"catalog-is-a-derived-read-only-projection"},
		},
	})
	return string(raw) + "\n"
}

// TestFakeTEIProcess is the fake TEI CLI. It does nothing in a normal test run.
func TestFakeTEIProcess(t *testing.T) {
	if os.Getenv("TAI_FAKE_TEI_PROCESS") != "1" {
		return
	}
	var scenario fakeTEIScenario
	if err := json.Unmarshal([]byte(os.Getenv("TAI_FAKE_TEI_SCENARIO")), &scenario); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(3)
	}
	var args []string
	if err := json.Unmarshal([]byte(os.Getenv("TAI_FAKE_TEI_ARGS")), &args); err != nil {
		os.Exit(3)
	}
	if scenario.LogPath != "" {
		if file, err := os.OpenFile(scenario.LogPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o600); err == nil {
			fmt.Fprintln(file, strings.Join(args, " "))
			file.Close()
		}
	}
	workspace := ""
	for index, arg := range args {
		if arg == "-workspace" && index+1 < len(args) {
			workspace = args[index+1]
		}
	}
	call := "text"
	switch {
	case len(args) > 0 && args[0] == "model":
		call = "catalog"
	case len(args) > 0 && args[len(args)-1] == "-json":
		call = "json"
	}
	writeOn := scenario.WriteOn
	if writeOn == "" {
		writeOn = "text"
	}
	if call == writeOn {
		if scenario.WriteWorkspace != "" {
			_ = os.WriteFile(filepath.Join(workspace, scenario.WriteWorkspace), []byte("written by the fake TEI\n"), 0o600)
		}
		if scenario.OverwriteWorkspace != "" {
			path := filepath.Join(workspace, scenario.OverwriteWorkspace)
			if existing, err := os.ReadFile(path); err == nil {
				_ = os.WriteFile(path, []byte(strings.Repeat("Z", len(existing))), 0o600)
			}
		}
		if scenario.AppendTracked != "" {
			if file, err := os.OpenFile("README.md", os.O_APPEND|os.O_WRONLY, 0); err == nil {
				fmt.Fprint(file, scenario.AppendTracked)
				file.Close()
			}
		}
		if scenario.WriteUntracked != "" {
			_ = os.WriteFile(scenario.WriteUntracked, []byte("written by the fake TEI\n"), 0o600)
		}
	}
	switch call {
	case "text":
		out := scenario.TextOut
		switch out {
		case "":
			out = "ok\n"
		case "-":
			out = ""
		}
		fmt.Print(out)
		os.Exit(scenario.TextExit)
	case "json":
		out := scenario.JSONOut
		if out == "" {
			out = honestValidateJSON
		}
		fmt.Print(out)
		os.Exit(scenario.JSONExit)
	default:
		out := scenario.CatalogOut
		if out == "" {
			out = honestCatalog(scenario)
		}
		fmt.Print(out)
		os.Exit(scenario.CatalogExit)
	}
}

const fakeGoVersion = "go version go1.26.9 linux/amd64"

// useFakeTEI replaces the build step (and the go probe, so these tests need no go
// binary and no TEI checkout) for one test. The returned counter says how many times
// a TEI CLI was prepared, which is zero when a pin failed before any TEI code ran.
func useFakeTEI(t *testing.T, scenario fakeTEIScenario) *int {
	t.Helper()
	launches := 0
	previousProbe := probeToolchain
	probeToolchain = func(_ context.Context, _ string, pinned bool) (string, Toolchain) {
		tool := Toolchain{GoVersionToken: "go1.26.9", GoToolchainEnv: "local", Enforced: []string{}, Build: "not-run"}
		if pinned {
			tool.Enforced = append([]string{}, pinnedGoEnv...)
		}
		return fakeGoVersion, tool
	}
	t.Cleanup(func() { probeToolchain = previousProbe })
	previous := prepareTEI
	prepareTEI = func(_ context.Context, teiRoot string, _ bool) (teiTool, error) {
		launches++
		raw, err := json.Marshal(scenario)
		if err != nil {
			return teiTool{}, err
		}
		return teiTool{
			command: func(ctx context.Context, args ...string) *exec.Cmd {
				rawArgs, _ := json.Marshal(args)
				cmd := exec.CommandContext(ctx, os.Args[0], "-test.run=^TestFakeTEIProcess$")
				cmd.Dir = teiRoot
				cmd.Env = append(os.Environ(), "TAI_FAKE_TEI_PROCESS=1", "TAI_FAKE_TEI_SCENARIO="+string(raw), "TAI_FAKE_TEI_ARGS="+string(rawArgs))
				return cmd
			},
			cleanup: func() {},
		}, nil
	}
	t.Cleanup(func() { prepareTEI = previous })
	return &launches
}

// newWorkspace writes LF content so digests do not depend on the checkout's
// line-ending conversion (testdata/workspace is CRLF in a Windows working tree).
func newWorkspace(t *testing.T) string {
	t.Helper()
	dir := t.TempDir()
	if err := os.MkdirAll(filepath.Join(dir, "semantic"), 0o755); err != nil {
		t.Fatal(err)
	}
	files := map[string]string{
		"tei.workspace.yaml":    "workspace: scn001\nsources:\n  - semantic\n",
		"semantic/guidance.tei": "namespace scn001\n",
	}
	for name, content := range files {
		if err := os.WriteFile(filepath.Join(dir, filepath.FromSlash(name)), []byte(content), 0o600); err != nil {
			t.Fatal(err)
		}
	}
	return dir
}

func readLog(t *testing.T, path string) []string {
	t.Helper()
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	return strings.Split(strings.TrimSpace(string(raw)), "\n")
}
