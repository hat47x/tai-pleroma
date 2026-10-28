package main

import (
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"runtime"
	"strings"
	"time"
)

// Receipt keeps the first eleven fields and their meaning from tai.reference.eki-cli/v0.
// The fields after Notes are additive: a consumer that decodes the receipt without
// DisallowUnknownFields is unaffected.
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
	// Additive fields.
	Pin       PinCheck      `json:"pin"`
	Checkout  CheckoutCheck `json:"checkout"`
	Toolchain Toolchain     `json:"toolchain"`
	Binaries  Binaries      `json:"binaries"`
}

// Toolchain records the Go toolchain the EKI commands are built with and how it was
// kept from changing under a pinned run. GoToolchainEnv, GoFlags and GoWork are what
// the caller's environment says (what an unpinned run builds with); Enforced lists the
// values a pinned run puts in their place for every go command it starts.
type Toolchain struct {
	GoVersionToken string   `json:"goVersionToken"`       // go1.26.9, from `go version` run in the EKI checkout
	GoToolchainEnv string   `json:"goToolchainEnv"`       // inherited GOTOOLCHAIN (local | auto | go1.x ...)
	GoFlags        string   `json:"goFlags"`              // inherited GOFLAGS
	GoWork         string   `json:"goWork"`               // inherited GOWORK ("" or off when no go.work applies)
	Enforced       []string `json:"enforced"`             // NAME=value set for the go commands because the run is pinned
	Build          string   `json:"build"`                // not-run | built | failed
	BuildFlags     []string `json:"buildFlags,omitempty"` // explicit flags given to go build
}

// ReportedCommit says whether the --version output names a commit and whether it is HEAD.
// The EKI commands print only `<name> dev` (measured), so this is normally "not-reported".
type ReportedCommit struct {
	Status string `json:"status"` // not-run | not-reported | match | mismatch
}

// Binaries describes what the built commands printed. The digest is of the file this
// tool built outside the checkout; it is not a statement about any other build.
type Binaries struct {
	ControlSha256    string         `json:"controlSha256"`
	AgentSha256      string         `json:"agentSha256"`
	ControlLine      string         `json:"controlLine"`
	AgentLine        string         `json:"agentLine"`
	VersionAgreement string         `json:"versionAgreement"` // agree | disagree | not-run
	ReportedCommit   ReportedCommit `json:"reportedCommit"`
	KeptAt           string         `json:"keptAt"` // "build-out" when -build-out kept the files; never a path
}

// CheckoutFacts is the EKI checkout state at one moment.
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

// CheckoutCheck compares the EKI checkout before and after the EKI commands ran.
type CheckoutCheck struct {
	Status string        `json:"status"` // not-checked | unchanged | changed | unavailable
	Before CheckoutFacts `json:"before"`
	After  CheckoutFacts `json:"after"`
}

func checkoutFactsOf(facts ekiFacts) CheckoutFacts {
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
//     EKI's go.mod, so the Go that is checked is the Go that compiles;
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

// probeToolchain asks the go command which toolchain runs from the EKI checkout and
// how the caller's environment configures it.
func probeToolchain(ctx context.Context, ekiRoot string, pinned bool) (string, Toolchain) {
	env, enforced := goChildEnv(pinned)
	tool := Toolchain{Enforced: append([]string{}, enforced...), Build: "not-run"}
	full := commandOutput(ctx, ekiRoot, env, "go", "version")
	if fields := strings.Fields(full); len(fields) >= 3 && fields[0] == "go" && fields[1] == "version" && strings.HasPrefix(fields[2], "go") {
		tool.GoVersionToken = fields[2]
	}
	// What the caller's environment says, read with that environment. GOTOOLCHAIN and
	// GOFLAGS do not depend on the module, so they are read from a neutral directory:
	// asked inside the checkout, `go env` would first try the toolchain switch that
	// go.mod asks for and report nothing when that fails. GOWORK depends on the
	// directory; it is read in the checkout with the switch off.
	inherited := os.Environ()
	var goenv, workenv map[string]string
	if raw := commandOutput(ctx, os.TempDir(), inherited, "go", "env", "-json", "GOTOOLCHAIN", "GOFLAGS"); raw != "" {
		_ = json.Unmarshal([]byte(raw), &goenv)
	}
	if raw := commandOutput(ctx, ekiRoot, append(append([]string{}, inherited...), "GOTOOLCHAIN=local"), "go", "env", "-json", "GOWORK"); raw != "" {
		_ = json.Unmarshal([]byte(raw), &workenv)
	}
	tool.GoToolchainEnv, tool.GoFlags, tool.GoWork = goenv["GOTOOLCHAIN"], goenv["GOFLAGS"], workenv["GOWORK"]
	return full, tool
}

// buildFlags are given to every go build. -mod=readonly stops go from rewriting
// go.mod/go.sum; -buildvcs=false stops it from running git in the checkout (and from
// embedding the commit in the binary); -trimpath keeps the build directory out of it.
var buildFlags = []string{"-mod=readonly", "-buildvcs=false", "-trimpath"}

const (
	// buildTimeout covers a cold build of both commands (about 53 seconds measured with
	// the module download; far longer is possible on a cold cache).
	buildTimeout = 15 * time.Minute
	runTimeout   = 60 * time.Second
)

type ekiBinaries struct {
	control, agent string
	keptAt         string
	cleanup        func()
}

// resolveLoose resolves symlinks in the longest existing prefix of path.
func resolveLoose(path string) (string, error) {
	absolute, err := filepath.Abs(path)
	if err != nil {
		return "", err
	}
	rest, current := "", absolute
	for {
		if resolved, err := filepath.EvalSymlinks(current); err == nil {
			return filepath.Join(resolved, rest), nil
		}
		parent := filepath.Dir(current)
		if parent == current {
			return "", errors.New("path cannot be resolved")
		}
		rest = filepath.Join(filepath.Base(current), rest)
		current = parent
	}
}

// outsideCheckout is false when dir is the checkout or below it (after symlinks), and
// also when either path cannot be resolved.
func outsideCheckout(ekiRoot, dir string) bool {
	root, err1 := resolveLoose(ekiRoot)
	target, err2 := resolveLoose(dir)
	if err1 != nil || err2 != nil {
		return false
	}
	relative, err := filepath.Rel(root, target)
	if err != nil {
		return true
	}
	return relative == ".." || strings.HasPrefix(relative, ".."+string(filepath.Separator))
}

func fileDigest(path string) string {
	raw, err := os.ReadFile(path)
	if err != nil {
		return ""
	}
	return digestBytes(raw)
}

// prepareEKI builds cmd/eki-control and cmd/eki-agent once, outside the checkout, so
// no `go run` links into or writes below it.
func prepareEKI(ctx context.Context, ekiRoot string, pinned bool, buildOut string) (ekiBinaries, error) {
	goPath, err := exec.LookPath("go")
	if err != nil {
		return ekiBinaries{}, errors.New("go is unavailable")
	}
	dir, cleanup := buildOut, func() {}
	keptAt := ""
	if buildOut != "" {
		if err := os.MkdirAll(buildOut, 0o755); err != nil {
			return ekiBinaries{}, errors.New("build-out cannot be created")
		}
		keptAt = "build-out"
	} else {
		dir, err = os.MkdirTemp("", "tai-eki-bin-")
		if err != nil {
			return ekiBinaries{}, errors.New("temporary directory cannot be created")
		}
		cleanup = func() { _ = os.RemoveAll(dir) }
	}
	suffix := ""
	if runtime.GOOS == "windows" {
		suffix = ".exe"
	}
	env, _ := goChildEnv(pinned)
	result := ekiBinaries{keptAt: keptAt, cleanup: cleanup}
	for _, name := range []string{"eki-control", "eki-agent"} {
		out := filepath.Join(dir, name+suffix)
		build := exec.CommandContext(ctx, goPath, append(append([]string{"build"}, buildFlags...), "-o", out, "./cmd/"+name)...)
		build.Dir = ekiRoot
		build.Env = env
		if err := build.Run(); err != nil {
			cleanup()
			return ekiBinaries{}, errors.New("EKI build failed")
		}
		if name == "eki-control" {
			result.control = out
		} else {
			result.agent = out
		}
	}
	return result, nil
}

// versionLine is `<name> <token>`, optionally followed by a reported commit.
var (
	versionLine = regexp.MustCompile(`^(eki-control|eki-agent) (\S+)(?: (?:commit=)?(?:[0-9a-f]{40}|[0-9a-f]{64}))?$`)
	reportedHex = regexp.MustCompile(`(?:^|[^0-9a-f])([0-9a-f]{64}|[0-9a-f]{40})(?:[^0-9a-f]|$)`)
)

// reportedCommit compares any commit the output names with HEAD.
func reportedCommit(head string, lines ...string) string {
	status := "not-reported"
	for _, line := range lines {
		for _, match := range reportedHex.FindAllStringSubmatch(strings.ToLower(line), -1) {
			if match[1] != head {
				return "mismatch"
			}
			status = "match"
		}
	}
	return status
}

// versionsAgree needs both lines in the `<name> <token>` form, each from the command it
// belongs to, with the same token.
func versionsAgree(control, agent string) bool {
	c, a := versionLine.FindStringSubmatch(control), versionLine.FindStringSubmatch(agent)
	return c != nil && a != nil && c[1] == "eki-control" && a[1] == "eki-agent" && c[2] == a[2]
}

func runVersion(ctx context.Context, binary, dir string) (string, error) {
	runCtx, cancel := context.WithTimeout(ctx, runTimeout)
	defer cancel()
	cmd := exec.CommandContext(runCtx, binary, "--version")
	cmd.Dir = dir
	cmd.Env = os.Environ()
	output, err := cmd.Output()
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(output)), nil
}

// Run keeps the record-only behaviour when options carry no expectation.
func Run(ctx context.Context, ekiRoot string) Receipt {
	return RunWithOptions(ctx, ekiRoot, Options{})
}

func newReceipt() Receipt {
	return Receipt{
		Schema: "tai.reference.eki-cli/v0", ReadOnly: true,
		Notes: []string{
			"EKIの`eki-control`/`eki-agent`のversion表示だけを確認する。",
			"Taskの委任・Worker・Authority・結果検証は未実施。",
			"版固定の一致が示すのは、checkoutのHEAD・追跡内容・Go toolchainと、そこから作ったバイナリのsha256が期待と合ったことだけである。EKIの正しさ・実行結果・Authorityは示さない。`--version`は`dev`だけを出し、版の証明にならない。",
		},
		Pin:       PinCheck{Result: "not-checked", Commit: PinItem{Status: "not-checked"}, GoVersion: PinItem{Status: "not-checked"}, SourceTree: SourceTree{Status: "not-checked"}},
		Checkout:  CheckoutCheck{Status: "not-checked"},
		Toolchain: Toolchain{Enforced: []string{}, Build: "not-run"},
		Binaries:  Binaries{VersionAgreement: "not-run", ReportedCommit: ReportedCommit{Status: "not-run"}},
	}
}

func fail(receipt Receipt, reason string) Receipt {
	receipt.Reason = reason
	return receipt
}

func joinReasons(reasons []string) string { return strings.Join(reasons, "; ") }

// RunWithOptions fails before building or executing any EKI code when a pin
// expectation does not hold. Only the check of the printed versions needs the built
// commands, so it runs afterwards.
func RunWithOptions(ctx context.Context, ekiRoot string, options Options) Receipt {
	receipt := newReceipt()
	if _, err := os.Stat(filepath.Join(ekiRoot, "cmd", "eki-control")); err != nil {
		return fail(receipt, "EKI control command is unavailable")
	}
	if _, err := exec.LookPath("go"); err != nil {
		return fail(receipt, "go is unavailable")
	}
	if options.BuildOut != "" && !outsideCheckout(ekiRoot, options.BuildOut) {
		return fail(receipt, "build-out must be outside the EKI checkout")
	}
	probeCtx, cancelProbe := context.WithTimeout(ctx, buildTimeout)
	full, tool := probeToolchain(probeCtx, ekiRoot, options.specified())
	cancelProbe()
	receipt.GoVersion = full
	receipt.Toolchain = tool
	factsBefore := gatherFacts(ctx, ekiRoot)
	receipt.EkiCommit = factsBefore.Commit
	pin, pinReasons := evaluatePin(options, factsBefore, tool)
	receipt.Pin = pin
	receipt.Checkout.Before = checkoutFactsOf(factsBefore)
	if len(pinReasons) > 0 {
		return fail(receipt, joinReasons(pinReasons))
	}
	strict := pin.Checked
	if !strict {
		receipt.Notes = append(receipt.Notes, "版固定の期待値が指定されていないため、EKIのcommit・Go versionは記録のみで照合していない。")
	}

	buildCtx, cancelBuild := context.WithTimeout(ctx, buildTimeout)
	defer cancelBuild()
	binaries, err := prepareEKI(buildCtx, ekiRoot, strict, options.BuildOut)
	if err != nil {
		receipt.Toolchain.Build = "failed"
		return finish(ctx, receipt, ekiRoot, factsBefore, err.Error())
	}
	defer binaries.cleanup()
	receipt.Toolchain.Build = "built"
	receipt.Toolchain.BuildFlags = append([]string{}, buildFlags...)
	receipt.Binaries.KeptAt = binaries.keptAt
	receipt.Binaries.ControlSha256 = fileDigest(binaries.control)
	receipt.Binaries.AgentSha256 = fileDigest(binaries.agent)

	reason := runChecks(ctx, &receipt, binaries, factsBefore.Commit, strict)
	return finish(ctx, receipt, ekiRoot, factsBefore, reason)
}

// runChecks starts the built commands and returns the first failure reason ("" when
// every check that applies passed). The commands run in an empty temporary directory,
// not in the checkout. It never decides write detection; finish does.
func runChecks(ctx context.Context, receipt *Receipt, binaries ekiBinaries, head string, strict bool) string {
	work, err := os.MkdirTemp("", "tai-eki-run-")
	if err != nil {
		return "temporary directory cannot be created"
	}
	defer os.RemoveAll(work)
	control, err := runVersion(ctx, binaries.control, work)
	if err != nil {
		return "eki-control --version failed"
	}
	agent, err := runVersion(ctx, binaries.agent, work)
	if err != nil {
		return "eki-agent --version failed"
	}
	receipt.ControlVersion, receipt.AgentVersion = control, agent
	receipt.Binaries.ControlLine, receipt.Binaries.AgentLine = control, agent
	if control == "" || agent == "" {
		return "EKI version output is empty"
	}
	receipt.Binaries.ReportedCommit.Status = reportedCommit(head, control, agent)
	receipt.Binaries.VersionAgreement = "disagree"
	if versionsAgree(control, agent) {
		receipt.Binaries.VersionAgreement = "agree"
	}
	if !strict {
		return ""
	}
	var reasons []string
	if receipt.Binaries.ReportedCommit.Status == "mismatch" {
		reasons = append(reasons, "pin mismatch: version output reports commit that differs from HEAD")
	}
	if receipt.Binaries.VersionAgreement != "agree" {
		reasons = append(reasons, "pin mismatch: version output of eki-control and eki-agent disagree")
	}
	return joinReasons(reasons)
}

// finish takes the after-state, flags any write by the EKI commands, and settles
// passed. It runs whenever EKI code was built or started, so a write is seen even
// when the version check failed.
func finish(ctx context.Context, receipt Receipt, ekiRoot string, factsBefore ekiFacts, reason string) Receipt {
	var writes []string
	factsAfter := gatherFacts(ctx, ekiRoot)
	receipt.Checkout.After = checkoutFactsOf(factsAfter)
	queried := func(facts ekiFacts) bool { return facts.Commit != "" && facts.TrackedDigest != "" }
	switch {
	case !queried(factsBefore):
		receipt.Checkout.Status = "unavailable"
	case !queried(factsAfter):
		receipt.Checkout.Status = "changed"
		writes = append(writes, "EKI commands changed the EKI checkout (its git state can no longer be read)")
	default:
		if changed := receipt.Checkout.Before.changedFields(receipt.Checkout.After); len(changed) > 0 {
			receipt.Checkout.Status = "changed"
			writes = append(writes, "EKI commands changed the EKI checkout ("+strings.Join(changed, ", ")+")")
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

type cliConfig struct {
	EkiRoot string
	OutPath string
	Options Options
}

// parseConfig reads the command line, with environment variables as the default of
// each expectation flag (a flag given on the command line wins, an empty value means
// "no expectation"). main is a thin wrapper, so the only way to give an expectation is
// tested here.
func parseConfig(args []string, getenv func(string) string) (cliConfig, error) {
	flags := flag.NewFlagSet("reference-eki-cli", flag.ContinueOnError)
	flags.SetOutput(io.Discard)
	ekiRoot := flags.String("eki-root", "", "EKI checkout root (default: EKI_ROOT or ../../../eki-fabric)")
	outPath := flags.String("out", "", "write receipt JSON")
	expectCommit := flags.String("expect-commit", getenv("TAI_EKI_EXPECT_COMMIT"), "fail unless the EKI checkout HEAD equals this commit (env TAI_EKI_EXPECT_COMMIT)")
	expectGo := flags.String("expect-go-version", getenv("TAI_EKI_EXPECT_GO_VERSION"), "fail unless `go version` reports this version token, e.g. go1.27.3 (env TAI_EKI_EXPECT_GO_VERSION)")
	buildOut := flags.String("build-out", "", "keep the built eki-control and eki-agent in this directory (must be outside the checkout)")
	if err := flags.Parse(args); err != nil {
		return cliConfig{}, err
	}
	root := *ekiRoot
	if root == "" {
		root = getenv("EKI_ROOT")
	}
	if root == "" {
		root = filepath.Clean(filepath.Join("..", "..", "..", "eki-fabric"))
	}
	return cliConfig{
		EkiRoot: root, OutPath: *outPath,
		Options: Options{ExpectCommit: strings.ToLower(*expectCommit), ExpectGoVersion: *expectGo, BuildOut: *buildOut},
	}, nil
}

func realMain(args []string, getenv func(string) string, stdout, stderr io.Writer) int {
	config, err := parseConfig(args, getenv)
	if err != nil {
		if errors.Is(err, flag.ErrHelp) {
			return 0
		}
		fmt.Fprintln(stderr, err)
		return 2
	}
	ctx, cancel := context.WithTimeout(context.Background(), buildTimeout+2*runTimeout+time.Minute)
	defer cancel()
	receipt := RunWithOptions(ctx, config.EkiRoot, config.Options)
	encoded, err := json.MarshalIndent(receipt, "", "  ")
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 2
	}
	encoded = append(encoded, '\n')
	if config.OutPath != "" {
		if err := os.WriteFile(config.OutPath, encoded, 0o644); err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
	}
	_, _ = stdout.Write(encoded)
	if !receipt.Passed {
		return 1
	}
	return 0
}

func main() {
	os.Exit(realMain(os.Args[1:], os.Getenv, os.Stdout, os.Stderr))
}
