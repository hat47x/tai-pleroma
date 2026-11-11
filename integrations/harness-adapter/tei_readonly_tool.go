package harnessadapter

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

// TEIReadOnlyTool projects TEI's existing read-only CLI into a ToolOffer plus a
// deterministic invoker.
//
// This is a projection of an existing product surface, not a new API. The
// command allowlist is derived from `tei commands` (the CLI's own advertised
// read-only catalog) so a command that the CLI would reject is never offered,
// and a command the CLI advertises is never silently dropped. Write-capable
// commands are out of scope for this projection by construction.
type TEIReadOnlyTool struct {
	// Binary is the path to a built tei executable. Empty means resolve "tei"
	// on PATH.
	Binary string
	// WorkspaceRoot is the TEI workspace directory. It is also the only root
	// this tool is allowed to name.
	WorkspaceRoot string
	// Namespace restricts `model catalog` when non-empty.
	Namespace string
	// Timeout bounds one invocation.
	Timeout time.Duration
	// Clock is injectable for tests.
	Clock func() time.Time
	// Runner executes the product CLI. Production uses ProcessRunner; tests
	// substitute a fake so the contract tests need no TEI binary.
	Runner Runner
}

// TEIReadOnlyCommands are the commands this projection may offer. They are the
// read-only subset of TEI's advertised catalog (see tei-platform
// cmd/tei/cli_commands.go, scope "selected-read-only-commands"). Anything not
// listed here is not offered, even though the CLI dispatches more.
var TEIReadOnlyCommands = []string{
	"version",
	"model catalog",
	"model overview",
	"model locate",
	"workspace-files",
	"inspect",
	"trace",
	"source-index",
	"knowledge-context",
	"validate",
}

// NewTEIReadOnlyTool builds the projection with production defaults.
func NewTEIReadOnlyTool(binary, workspaceRoot string) *TEIReadOnlyTool {
	return &TEIReadOnlyTool{
		Binary:        binary,
		WorkspaceRoot: workspaceRoot,
		Timeout:       2 * time.Minute,
		Clock:         time.Now,
		Runner:        ProcessRunner{},
	}
}

// Name implements the ToolOffer naming convention "<product>.<command>".
func (t *TEIReadOnlyTool) Name(command string) string {
	return "tei." + strings.ReplaceAll(command, " ", "-")
}

// Offers returns the tool offers for every allowlisted command that this
// projection can actually build. A command whose required flags the projection
// cannot fill is not offered, and the gap is returned so the caller can record
// it instead of advertising a tool that cannot run.
func (t *TEIReadOnlyTool) Offers() (offers []ToolOffer, unsupported []string) {
	for _, cmd := range TEIReadOnlyCommands {
		argv, ok := t.argvFor(cmd)
		if !ok {
			unsupported = append(unsupported, "tei."+strings.ReplaceAll(cmd, " ", "-")+":missing-required-input")
			continue
		}
		offers = append(offers, ToolOffer{
			Name:         t.Name(cmd),
			Description:  "TEI read-only CLI: " + cmd,
			ReadOnly:     true,
			AllowedRoots: []string{"tei-workspace"},
			Command:      argv,
			InputSchema:  json.RawMessage(`{"type":"object","additionalProperties":false,"properties":{}}`),
		})
	}
	sort.Slice(offers, func(i, j int) bool { return offers[i].Name < offers[j].Name })
	return offers, unsupported
}

// argvFor builds the exact argv for one command. The second return is false
// when the command needs an input the projection does not carry (for example
// inspect needs a subject id), which is why such commands are not offered.
func (t *TEIReadOnlyTool) argvFor(command string) ([]string, bool) {
	exe := t.Binary
	if exe == "" {
		exe = "tei"
	}
	ws := t.WorkspaceRoot
	switch command {
	case "version":
		return []string{exe, "version"}, true
	case "model catalog":
		if ws == "" {
			return nil, false
		}
		argv := []string{exe, "model", "catalog", "-workspace", ws}
		if t.Namespace != "" {
			argv = append(argv, "-namespace", t.Namespace)
		}
		return argv, true
	case "model overview":
		if ws == "" {
			return nil, false
		}
		return []string{exe, "model", "overview", "-workspace", ws}, true
	case "workspace-files":
		if ws == "" {
			return nil, false
		}
		return []string{exe, "workspace-files", "-workspace", ws}, true
	case "source-index":
		if ws == "" {
			return nil, false
		}
		return []string{exe, "source-index", "-workspace", ws}, true
	case "validate":
		if ws == "" {
			return nil, false
		}
		return []string{exe, "validate", "-workspace", ws, "-json"}, true
	case "inspect", "model locate", "trace", "knowledge-context":
		// These need a subject reference the projection does not own. They stay
		// in the allowlist for documentation and are reported as not offered.
		return nil, false
	}
	return nil, false
}

// Invoke runs one offered command and returns a product verdict plus the raw
// envelope. The verdict keeps operation completion and validation success
// separate, matching ADR-0048 §2.4.
func (t *TEIReadOnlyTool) Invoke(ctx context.Context, command string) (*ToolCallRecord, error) {
	argv, ok := t.argvFor(command)
	if !ok {
		return nil, fmt.Errorf("tei read-only tool: command %q is not offered by this projection", command)
	}
	if ctx == nil {
		ctx = context.Background()
	}
	runner := t.Runner
	if runner == nil {
		runner = ProcessRunner{}
	}
	start := t.Clock()
	execRes, err := runner.Exec(ctx, ExecSpec{
		Argv:    argv,
		Dir:     t.WorkspaceRoot,
		Timeout: t.Timeout,
	})
	elapsed := t.Clock().Sub(start)
	if err != nil {
		return nil, fmt.Errorf("tei read-only tool: %w", err)
	}
	if execRes.LaunchError != "" {
		return nil, fmt.Errorf("tei read-only tool: %s", execRes.LaunchError)
	}
	code := execRes.ExitCode
	stdout, stderr := execRes.Stdout, execRes.Stderr
	rec := &ToolCallRecord{
		CallID:      "tei-" + strings.ReplaceAll(command, " ", "-"),
		Tool:        t.Name(command),
		InputJSON:   "{}",
		ExitCode:    &code,
		ResultBytes: int64(len(stdout)),
		ResultText:  string(stdout),
		Note:        "product CLI invocation; no harness involved",
	}
	verdict, diags := decodeProductEnvelope(stdout)
	rec.ProductVerdict = verdict
	if len(stderr) > 0 {
		diags = append(diags, Diagnostic{Severity: "warning", Code: "tei-stderr", Message: firstLine(stderr), Source: t.Name(command)})
	}
	rec.Note += fmt.Sprintf("; elapsed=%s; product-diagnostics=%d", elapsed.Round(time.Millisecond), len(diags))
	return rec, nil
}

// DigestWorkspace reports a digest over the workspace root's immediate file
// names and sizes, plus the file count and total bytes. It is an observation
// about a directory listing, not a claim that every file was parsed, read or
// validated.
func DigestWorkspace(root string) (digest string, files int, bytes int64, err error) {
	if root == "" {
		return "", 0, 0, fmt.Errorf("workspace root is empty")
	}
	entries, err := os.ReadDir(root)
	if err != nil {
		return "", 0, 0, err
	}
	h := sha256.New()
	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		info, err := e.Info()
		if err != nil {
			return "", 0, 0, err
		}
		files++
		bytes += info.Size()
		fmt.Fprintf(h, "%s\t%d\n", e.Name(), info.Size())
	}
	return "sha256:" + hex.EncodeToString(h.Sum(nil)), files, bytes, nil
}

// ResolveBinary resolves the tei executable, preferring an explicit path and
// falling back to PATH. It returns the resolved path so the evidence can name
// the exact executable that ran.
func (t *TEIReadOnlyTool) ResolveBinary() (string, error) {
	if t.Binary != "" {
		if _, err := os.Stat(t.Binary); err != nil {
			return "", fmt.Errorf("tei binary %q: %w", t.Binary, err)
		}
		return filepath.Clean(t.Binary), nil
	}
	return exec.LookPath("tei")
}
