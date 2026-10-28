package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"sort"
	"strings"
	"time"
)

// Receipt keeps the first nine fields and their meaning from tai.reference.tei-model/v0.
// The fields after Notes are additive: a consumer that decodes the receipt without
// DisallowUnknownFields is unaffected.
type Receipt struct {
	Schema          string   `json:"schema"`
	TeiCommit       string   `json:"teiCommit"`
	GoVersion       string   `json:"goVersion"`
	WorkspaceDigest string   `json:"workspaceDigest"`
	Validation      string   `json:"validation"`
	ReadOnly        bool     `json:"readOnly"`
	Passed          bool     `json:"passed"`
	Reason          string   `json:"reason,omitempty"`
	Notes           []string `json:"notes"`
	// Additive fields.
	Pin           PinCheck      `json:"pin"`
	Checkout      CheckoutCheck `json:"checkout"`
	Toolchain     Toolchain     `json:"toolchain"`
	ValidateJSON  ValidateJSON  `json:"validateJson"`
	ModelBinding  ModelBinding  `json:"modelBinding"`
	WorkspaceTree WorkspaceTree `json:"workspaceTree"`
}

// Toolchain records the Go toolchain the TEI CLI is built with and how it was kept
// from changing under a pinned run. GoToolchainEnv, GoFlags and GoWork are what the
// caller's environment says (what an unpinned run builds with); Enforced lists the
// values a pinned run puts in their place for every go command it starts.
type Toolchain struct {
	GoVersionToken string   `json:"goVersionToken"`       // go1.26.9, from `go version` run in the TEI checkout
	GoToolchainEnv string   `json:"goToolchainEnv"`       // inherited GOTOOLCHAIN (local | auto | go1.x ...)
	GoFlags        string   `json:"goFlags"`              // inherited GOFLAGS
	GoWork         string   `json:"goWork"`               // inherited GOWORK ("" or off when no go.work applies)
	Enforced       []string `json:"enforced"`             // NAME=value set for the go commands because the run is pinned
	Build          string   `json:"build"`                // not-run | built | failed
	BuildFlags     []string `json:"buildFlags,omitempty"` // explicit flags given to go build
}

// CheckoutFacts is the TEI checkout state at one moment.
type CheckoutFacts struct {
	Commit               string `json:"commit"`
	TrackedChanges       int    `json:"trackedChanges"`
	UntrackedFiles       int    `json:"untrackedFiles"`
	UntrackedBuildInputs int    `json:"untrackedBuildInputs"`
	HiddenFlaggedFiles   int    `json:"hiddenFlaggedFiles"`
	TrackedDigest        string `json:"trackedDigest,omitempty"`
	UntrackedDigest      string `json:"untrackedDigest,omitempty"`
	BuildInputsDigest    string `json:"buildInputsDigest,omitempty"`
}

// CheckoutCheck compares the TEI checkout before and after the TEI CLI ran.
type CheckoutCheck struct {
	Status string        `json:"status"` // not-checked | unchanged | changed | unavailable
	Before CheckoutFacts `json:"before"`
	After  CheckoutFacts `json:"after"`
}

func checkoutFactsOf(facts teiFacts) CheckoutFacts {
	return CheckoutFacts{
		Commit: facts.Commit, TrackedChanges: facts.Tracked, UntrackedFiles: facts.Untracked, UntrackedBuildInputs: facts.BuildInputs, HiddenFlaggedFiles: facts.Hidden,
		TrackedDigest: facts.TrackedDigest, UntrackedDigest: facts.UntrackedDigest, BuildInputsDigest: facts.BuildInputsDigest,
	}
}

// changedFields names what differs, never the content.
func (before CheckoutFacts) changedFields(after CheckoutFacts) []string {
	var changed []string
	if before.Commit != after.Commit {
		changed = append(changed, "HEAD")
	}
	if before.TrackedChanges != after.TrackedChanges || before.TrackedDigest != after.TrackedDigest {
		changed = append(changed, fmt.Sprintf("tracked changes %d->%d", before.TrackedChanges, after.TrackedChanges))
	}
	if before.UntrackedFiles != after.UntrackedFiles || before.UntrackedDigest != after.UntrackedDigest {
		changed = append(changed, fmt.Sprintf("untracked files %d->%d", before.UntrackedFiles, after.UntrackedFiles))
	}
	if before.UntrackedBuildInputs != after.UntrackedBuildInputs || before.BuildInputsDigest != after.BuildInputsDigest {
		changed = append(changed, fmt.Sprintf("untracked build inputs %d->%d", before.UntrackedBuildInputs, after.UntrackedBuildInputs))
	}
	if before.HiddenFlaggedFiles != after.HiddenFlaggedFiles {
		changed = append(changed, fmt.Sprintf("hidden-flagged files %d->%d", before.HiddenFlaggedFiles, after.HiddenFlaggedFiles))
	}
	return changed
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

func commandOutput(ctx context.Context, dir string, env []string, name string, args ...string) string {
	cmd := exec.CommandContext(ctx, name, args...)
	cmd.Dir = dir
	cmd.Env = env
	output, err := cmd.Output()
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(output))
}

// pinnedGoEnv is what a pinned run puts in the environment of every go command it
// starts, in place of what the caller has:
//   - GOTOOLCHAIN=local: no download of another Go chosen by GOTOOLCHAIN=auto from
//     TEI's go.mod, so the Go that is checked is the Go that compiles;
//   - GOWORK=off: no go.work file outside the checkout chooses the module versions;
//   - GOFLAGS=-mod=readonly: flags such as -tags, -ldflags, -gcflags or -modfile
//     change the program that is built without changing a file of the checkout.
//     The value has to be non-empty: an empty GOFLAGS in the environment does not
//     replace what a go env file sets, a non-empty one does.
//
// GOEXPERIMENT, CGO_ENABLED, GOOS/GOARCH, CC and the like are not constrained.
var pinnedGoEnv = []string{"GOTOOLCHAIN=local", "GOWORK=off", "GOFLAGS=-mod=readonly"}

// goChildEnv is the environment of every go command this tool starts. An unpinned run
// inherits the environment unchanged and records it.
func goChildEnv(pinned bool) (env []string, enforced []string) {
	env = os.Environ()
	if pinned {
		enforced = append([]string{}, pinnedGoEnv...)
		env = append(env, enforced...)
	}
	return env, enforced
}

// probeToolchain asks the go command which toolchain runs from the TEI checkout and
// how the caller's environment configures it. Tests replace it so they need no go
// binary.
var probeToolchain = defaultProbeToolchain

func defaultProbeToolchain(ctx context.Context, teiRoot string, pinned bool) (string, Toolchain) {
	env, enforced := goChildEnv(pinned)
	tool := Toolchain{Enforced: append([]string{}, enforced...), Build: "not-run"}
	full := commandOutput(ctx, teiRoot, env, "go", "version")
	if fields := strings.Fields(full); len(fields) >= 3 && fields[0] == "go" && fields[1] == "version" && strings.HasPrefix(fields[2], "go") {
		tool.GoVersionToken = fields[2]
	}
	// What the caller's environment says, read with that environment (a pinned run
	// replaces it for the build; see Enforced). GOTOOLCHAIN and GOFLAGS do not depend
	// on the module, so they are read from a neutral directory: asked inside the TEI
	// checkout, `go env` would first try the toolchain switch that go.mod asks for
	// and report nothing when that fails. GOWORK depends on the directory; it is read
	// in the checkout with the switch off.
	inherited := os.Environ()
	var goenv, workenv map[string]string
	if raw := commandOutput(ctx, os.TempDir(), inherited, "go", "env", "-json", "GOTOOLCHAIN", "GOFLAGS"); raw != "" {
		_ = json.Unmarshal([]byte(raw), &goenv)
	}
	if raw := commandOutput(ctx, teiRoot, append(append([]string{}, inherited...), "GOTOOLCHAIN=local"), "go", "env", "-json", "GOWORK"); raw != "" {
		_ = json.Unmarshal([]byte(raw), &workenv)
	}
	tool.GoToolchainEnv, tool.GoFlags, tool.GoWork = goenv["GOTOOLCHAIN"], goenv["GOFLAGS"], workenv["GOWORK"]
	return full, tool
}

// teiTool starts the TEI CLI that prepareTEI made ready.
type teiTool struct {
	command func(ctx context.Context, args ...string) *exec.Cmd
	cleanup func()
}

var buildFlags = []string{"-mod=readonly", "-buildvcs=false"}

// prepareTEI builds cmd/tei once into a private directory outside the TEI
// checkout, so the validate, validate -json and model catalog runs use one binary and
// no `go run` links TEI three times (measured at about 30 seconds each).
// -mod=readonly stops go from rewriting go.mod/go.sum; -buildvcs=false stops it
// from running git status in the checkout. Tests replace it with a fake TEI.
var prepareTEI = defaultPrepareTEI

func defaultPrepareTEI(ctx context.Context, teiRoot string, pinned bool) (teiTool, error) {
	goPath, err := exec.LookPath("go")
	if err != nil {
		return teiTool{}, fmt.Errorf("go is unavailable: %w", err)
	}
	dir, err := os.MkdirTemp("", "tai-tei-bin-")
	if err != nil {
		return teiTool{}, err
	}
	cleanup := func() { _ = os.RemoveAll(dir) }
	binary := filepath.Join(dir, "tei")
	if runtime.GOOS == "windows" {
		binary += ".exe"
	}
	env, _ := goChildEnv(pinned)
	build := exec.CommandContext(ctx, goPath, append(append([]string{"build"}, buildFlags...), "-o", binary, "./cmd/tei")...)
	build.Dir = teiRoot
	build.Env = env
	var stderr bytes.Buffer
	build.Stderr = &stderr
	if err := build.Run(); err != nil {
		cleanup()
		return teiTool{}, fmt.Errorf("TEI build failed: %v: %s", err, truncate(strings.TrimSpace(stderr.String())))
	}
	return teiTool{
		command: func(ctx context.Context, args ...string) *exec.Cmd {
			cmd := exec.CommandContext(ctx, binary, args...)
			cmd.Dir = teiRoot
			return cmd
		},
		cleanup: cleanup,
	}, nil
}

func truncate(text string) string {
	const limit = 2000
	if len(text) > limit {
		return text[:limit] + "...(truncated)"
	}
	return text
}

type teiResult struct {
	Stdout, Stderr string
	ExitCode       int
	Err            error // the process could not be started or was killed; a non-zero exit is not an Err
}

func (tool teiTool) run(ctx context.Context, args ...string) teiResult {
	runCtx, cancel := context.WithTimeout(ctx, runTimeout)
	defer cancel()
	cmd := tool.command(runCtx, args...)
	var stdout, stderr bytes.Buffer
	cmd.Stdout, cmd.Stderr = &stdout, &stderr
	result := teiResult{}
	if err := cmd.Run(); err != nil {
		var exit *exec.ExitError
		if errors.As(err, &exit) {
			result.ExitCode = exit.ExitCode()
		} else {
			result.ExitCode = -1
		}
		result.Err = err
	}
	result.Stdout, result.Stderr = stdout.String(), stderr.String()
	return result
}

// buildTimeout covers a cold build of TEI (measured above four minutes with an empty
// build cache); runTimeout covers one invocation of the built CLI.
const (
	buildTimeout = 15 * time.Minute
	runTimeout   = 60 * time.Second
)

// Run keeps the record-only behaviour when options carry no expectation.
func Run(ctx context.Context, teiRoot, workspace string) Receipt {
	return RunWithOptions(ctx, teiRoot, workspace, Options{})
}

func newReceipt() Receipt {
	return Receipt{
		Schema: "tai.reference.tei-model/v0", ReadOnly: true,
		Notes: []string{
			"TEIのvalidate（テキストと-json）とmodel catalogだけを実行する読み取り専用接続。",
			"SCN-001のObservation/RuleCandidateの型宣言を検証するが、実データ・意味・Authorityは検証しない。",
		},
		Pin:          PinCheck{Result: "not-checked", Commit: PinItem{Status: "not-checked"}, GoVersion: PinItem{Status: "not-checked"}, SourceTree: SourceTree{Status: "not-checked"}},
		Checkout:     CheckoutCheck{Status: "not-checked"},
		Toolchain:    Toolchain{Enforced: []string{}, Build: "not-run"},
		ValidateJSON: ValidateJSON{Status: "not-run"},
		ModelBinding: ModelBinding{Status: "not-run", Declared: declaredNames(), Differences: []string{}},
	}
}

func fail(receipt Receipt, reason string) Receipt {
	receipt.Reason = reason
	return receipt
}

func RunWithOptions(ctx context.Context, teiRoot, workspace string, options Options) Receipt {
	receipt := newReceipt()
	absWorkspace, err := filepath.Abs(workspace)
	if err != nil {
		return fail(receipt, err.Error())
	}
	if _, err := os.Stat(filepath.Join(absWorkspace, "tei.workspace.yaml")); err != nil {
		return fail(receipt, "TEI workspace manifest is unavailable: "+err.Error())
	}
	if _, err := os.Stat(filepath.Join(teiRoot, "cmd", "tei")); err != nil {
		return fail(receipt, "TEI runtime is unavailable: "+err.Error())
	}
	before, err := digestWorkspace(absWorkspace)
	if err != nil {
		return fail(receipt, err.Error())
	}
	beforeTree, entries, err := digestTree(absWorkspace)
	if err != nil {
		return fail(receipt, err.Error())
	}
	receipt.WorkspaceDigest = before
	receipt.WorkspaceTree = WorkspaceTree{DigestBefore: beforeTree, Entries: entries}

	probeCtx, cancelProbe := context.WithTimeout(ctx, buildTimeout)
	full, tool := probeToolchain(probeCtx, teiRoot, options.specified())
	cancelProbe()
	receipt.GoVersion = full
	receipt.Toolchain = tool
	factsBefore := gatherFacts(ctx, teiRoot)
	receipt.TeiCommit = factsBefore.Commit
	pin, pinReasons := evaluatePin(options, factsBefore, tool)
	receipt.Pin = pin
	receipt.Checkout.Before = checkoutFactsOf(factsBefore)
	if len(pinReasons) > 0 {
		// Fail before executing any TEI code that is not the expected version.
		return fail(receipt, joinReasons(pinReasons))
	}
	strict := pin.Checked
	if !strict {
		receipt.Notes = append(receipt.Notes, "版固定の期待値が指定されていないため、TEIのcommit・Go versionは記録のみで照合していない。")
	}

	buildCtx, cancelBuild := context.WithTimeout(ctx, buildTimeout)
	defer cancelBuild()
	tei, err := prepareTEI(buildCtx, teiRoot, strict)
	if err != nil {
		receipt.Toolchain.Build = "failed"
		return finish(ctx, receipt, teiRoot, absWorkspace, factsBefore, before, beforeTree, err.Error())
	}
	defer tei.cleanup()
	receipt.Toolchain.Build = "built"
	receipt.Toolchain.BuildFlags = append([]string{}, buildFlags...)

	reason := runChecks(ctx, &receipt, tei, absWorkspace, strict)
	return finish(ctx, receipt, teiRoot, absWorkspace, factsBefore, before, beforeTree, reason)
}

// runChecks runs the TEI CLI and returns the first failure reason ("" when every
// check that applies passed). It never decides write detection; finish does.
func runChecks(ctx context.Context, receipt *Receipt, tei teiTool, absWorkspace string, strict bool) string {
	text := tei.run(ctx, "validate", "-workspace", absWorkspace)
	if text.Err != nil {
		return fmt.Sprintf("TEI validate failed: %v: %s", text.Err, truncate(strings.TrimSpace(text.Stderr)))
	}
	receipt.Validation = strings.TrimSpace(text.Stdout)
	if receipt.Validation != "ok" {
		return "TEI validate did not report ok: " + receipt.Validation
	}
	structured := tei.run(ctx, "validate", "-workspace", absWorkspace, "-json")
	receipt.ValidateJSON = parseValidateJSON(structured.Stdout, structured.ExitCode, true)
	switch {
	case receipt.ValidateJSON.Status == "inconsistent":
		return "TEI validate -json contradicts the text output that reported ok"
	case strict && receipt.ValidateJSON.Status != "consistent":
		return "pinned run requires TEI validate -json to be consistent with the text output (status=" + receipt.ValidateJSON.Status + ")"
	case receipt.ValidateJSON.Status == "unavailable":
		receipt.Notes = append(receipt.Notes, "validate -jsonから比較できる値を得られなかった（版固定なしのため記録のみ）。")
	}
	catalog := tei.run(ctx, "model", "catalog", "-workspace", absWorkspace)
	receipt.ModelBinding = bindModel(catalog.Stdout, catalog.ExitCode)
	if receipt.ModelBinding.Status != "bound" {
		if strict {
			return fmt.Sprintf("pinned run requires the TEI model catalog to bind to the declared types (status=%s, differences=%s)",
				receipt.ModelBinding.Status, strings.Join(receipt.ModelBinding.Differences, ", "))
		}
		receipt.Notes = append(receipt.Notes, "TEIのmodel catalogが宣言した型と結び付かなかった（版固定なしのため記録のみ）。status="+receipt.ModelBinding.Status)
	}
	return ""
}

// finish takes the after-state, flags any write by TEI, and settles passed. It runs
// whenever the TEI CLI was started, so a write is seen even when validation failed.
func finish(ctx context.Context, receipt Receipt, teiRoot, absWorkspace string, factsBefore teiFacts, before, beforeTree string, reason string) Receipt {
	var writes []string
	after, afterErr := digestWorkspace(absWorkspace)
	afterTree, _, treeErr := digestTree(absWorkspace)
	receipt.WorkspaceTree.DigestAfter = afterTree
	switch {
	case afterErr != nil || treeErr != nil:
		writes = append(writes, "the workspace could not be read after the TEI CLI ran")
	case after != before || afterTree != beforeTree:
		writes = append(writes, "TEI validate changed the workspace")
	}
	factsAfter := gatherFacts(ctx, teiRoot)
	receipt.Checkout.After = checkoutFactsOf(factsAfter)
	queried := func(facts teiFacts) bool { return facts.Commit != "" && facts.TrackedDigest != "" }
	switch {
	case !queried(factsBefore):
		receipt.Checkout.Status = "unavailable"
	case !queried(factsAfter):
		receipt.Checkout.Status = "changed"
		writes = append(writes, "TEI validate changed the TEI checkout (its git state can no longer be read)")
	default:
		if changed := receipt.Checkout.Before.changedFields(receipt.Checkout.After); len(changed) > 0 {
			receipt.Checkout.Status = "changed"
			writes = append(writes, "TEI validate changed the TEI checkout ("+strings.Join(changed, ", ")+")")
		} else {
			receipt.Checkout.Status = "unchanged"
		}
	}
	if len(writes) > 0 {
		receipt.ReadOnly = false
		if reason != "" {
			writes = append(writes, reason)
		}
		return fail(receipt, joinReasons(writes))
	}
	if reason != "" {
		return fail(receipt, reason)
	}
	receipt.Passed = true
	return receipt
}

// cliConfig is what main passes on: where TEI and the workspace are, and the
// opt-in pin expectations.
type cliConfig struct {
	TEIRoot   string
	Workspace string
	OutPath   string
	Options   Options
}

// parseConfig reads the command line, with environment variables as the default
// of each expectation flag (a flag given on the command line wins, an empty value
// means "no expectation"). main is a thin wrapper, so the only way to give an
// expectation is tested here and not in an untested flag block.
func parseConfig(args []string, getenv func(string) string) (cliConfig, error) {
	flags := flag.NewFlagSet("reference-tei-model", flag.ContinueOnError)
	teiRoot := flags.String("tei-root", "", "TEI checkout root (default: TEI_ROOT or ../../../tei-platform)")
	workspace := flags.String("workspace", "testdata/workspace", "TEI workspace")
	outPath := flags.String("out", "", "write receipt JSON to this file")
	expectCommit := flags.String("expect-commit", getenv("TAI_TEI_EXPECT_COMMIT"), "fail unless the TEI checkout HEAD equals this commit (env TAI_TEI_EXPECT_COMMIT)")
	expectGo := flags.String("expect-go-version", getenv("TAI_TEI_EXPECT_GO_VERSION"), "fail unless `go version` reports this version token, e.g. go1.26.9 (env TAI_TEI_EXPECT_GO_VERSION)")
	if err := flags.Parse(args); err != nil {
		return cliConfig{}, err
	}
	root := *teiRoot
	if root == "" {
		root = getenv("TEI_ROOT")
	}
	if root == "" {
		root = filepath.Clean(filepath.Join("..", "..", "..", "tei-platform"))
	}
	return cliConfig{
		TEIRoot: root, Workspace: *workspace, OutPath: *outPath,
		Options: Options{ExpectCommit: strings.ToLower(*expectCommit), ExpectGoVersion: *expectGo},
	}, nil
}

func main() {
	config, err := parseConfig(os.Args[1:], os.Getenv)
	if err != nil {
		if errors.Is(err, flag.ErrHelp) {
			os.Exit(0)
		}
		os.Exit(2)
	}
	receipt := RunWithOptions(context.Background(), config.TEIRoot, config.Workspace, config.Options)
	encoded, err := json.MarshalIndent(receipt, "", "  ")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	encoded = append(encoded, '\n')
	if config.OutPath != "" {
		if err := os.WriteFile(config.OutPath, encoded, 0o644); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
	}
	os.Stdout.Write(encoded)
	if !receipt.Passed {
		os.Exit(1)
	}
}
