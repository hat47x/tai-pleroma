package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"runtime"
	"sort"
	"strings"
	"time"
)

// PinReport holds the additive receipt fields. It is embedded in every receipt of this
// tool; the names pin, checkout, toolchain and binary are new, so a consumer that
// decodes the older fields only is unaffected.
type PinReport struct {
	Pin       PinCheck      `json:"pin"`
	Checkout  CheckoutCheck `json:"checkout"`
	Toolchain Toolchain     `json:"toolchain"`
	Binary    BinaryInfo    `json:"binary"`
}

// Toolchain records the Go toolchain SEI is built with and how a pinned run kept it from
// changing. GoToolchainEnv, GoFlagNames and GoWork are what the caller's environment says
// (what an unpinned run builds with); Enforced lists the values a pinned run puts in their
// place for every go command it starts. No value of GOFLAGS or GOWORK and no path is kept.
type Toolchain struct {
	GoVersionToken    string   `json:"goVersionToken"`    // go1.26.9, from `go version` run in runtime/go
	GoToolchainEnv    string   `json:"goToolchainEnv"`    // inherited GOTOOLCHAIN (local | auto | go1.x ...)
	GoFlagNames       []string `json:"goFlagNames"`       // names of the flags in the inherited GOFLAGS, never their values
	GoWork            string   `json:"goWork"`            // inherited GOWORK: "" or off when no go.work applies, present when one does
	GoDirective       string   `json:"goDirective"`       // the go directive of runtime/go/go.mod (number only), "" when not read
	InheritedSettings []string `json:"inheritedSettings"` // names (never values) of inherited settings that a pinned run does not constrain
	Enforced          []string `json:"enforced"`          // NAME=value set for the go commands because the run is pinned
	Build             string   `json:"build"`             // not-run | built | failed
	BuildFlags        []string `json:"buildFlags,omitempty"`
	Unsupported       []string `json:"-"` // settings that make a pinned run unavailable; named in the failure reason
}

// ReportedCommit says whether `sei version` names a commit and whether it is HEAD. A
// plain build prints commit "unknown" (measured), so this is normally "not-reported".
type ReportedCommit struct {
	Status string `json:"status"` // not-run | not-reported | match | mismatch
}

type VersionLine struct {
	Version string `json:"version"`
	Commit  string `json:"commit"`
	Target  string `json:"target"`
}

// BinaryInfo describes the sei this tool built outside the checkout for a pinned run.
// The digest is of that file; it is not a statement about any other build.
type BinaryInfo struct {
	Status         string         `json:"status"` // not-built | built | failed
	Sha256         string         `json:"sha256"`
	VersionLine    VersionLine    `json:"versionLine"`
	ReportedCommit ReportedCommit `json:"reportedCommit"`
	KeptAt         string         `json:"keptAt"` // "build-out" when -build-out kept the file; never a path
}

// CheckoutFacts is the SEI checkout state at one moment.
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

// CheckoutCheck compares the SEI checkout before and after the SEI commands ran.
type CheckoutCheck struct {
	Status string        `json:"status"` // not-checked | unchanged | changed | unavailable
	Before CheckoutFacts `json:"before"`
	After  CheckoutFacts `json:"after"`
}

func pinCheckoutFacts(facts pinFacts) CheckoutFacts {
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

func newPinReport() PinReport {
	return PinReport{
		Pin:       PinCheck{Result: "not-checked", Commit: PinItem{Status: "not-checked"}, GoVersion: PinItem{Status: "not-checked"}, SourceTree: SourceTree{Status: "not-checked"}},
		Checkout:  CheckoutCheck{Status: "not-checked"},
		Toolchain: Toolchain{GoFlagNames: []string{}, InheritedSettings: []string{}, Enforced: []string{}, Build: "not-run"},
		Binary:    BinaryInfo{Status: "not-built", ReportedCommit: ReportedCommit{Status: "not-run"}},
	}
}

// pinnedGoEnv is what a pinned run puts in the environment of every go command it
// starts, in place of what the caller has:
//   - GOTOOLCHAIN=local: no download of another Go chosen by GOTOOLCHAIN=auto from
//     SEI's go.mod, so the Go that is checked is the Go that compiles;
//   - GOWORK=off: no go.work file outside the checkout chooses the module versions;
//   - GOFLAGS=-mod=readonly: an inherited GOFLAGS (-tags, -ldflags, -gcflags, -modfile,
//     -overlay ...) would change the program that is built without changing a file of the
//     checkout. It is replaced, not merged, so those flags have no effect on a pinned
//     build; the receipt keeps only their names. The value has to be non-empty: an empty
//     GOFLAGS in the environment does not replace what a go env file sets.
//
// GOEXPERIMENT, CGO_ENABLED, GOOS/GOARCH, CC and GOENV are not constrained; their names
// are recorded when set. GOTOOLDIR, GOCACHEPROG and a GOROOT that is not the go
// command's own make a pinned run unavailable.
var pinnedGoEnv = []string{"GOTOOLCHAIN=local", "GOWORK=off", "GOFLAGS=-mod=readonly"}

var pinBuildFlags = []string{"-mod=readonly", "-buildvcs=false", "-trimpath"}

func pinGoEnv(pinned bool) (env []string, enforced []string) {
	env = os.Environ()
	if pinned {
		enforced = append([]string{}, pinnedGoEnv...)
		env = append(env, enforced...)
	}
	return env, enforced
}

func pinCommandOutput(ctx context.Context, dir string, env []string, name string, args ...string) string {
	cmd := exec.CommandContext(ctx, name, args...)
	cmd.Dir = dir
	cmd.Env = env
	output, err := cmd.Output()
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(output))
}

var pinDirectivePattern = regexp.MustCompile(`(?m)^go[ \t]+([0-9]+\.[0-9]+(?:\.[0-9]+)?)[ \t]*\r?$`)

// pinInheritedSettings are settings that change what the compiler produces and that a
// pinned run does not constrain; the receipt names the ones that are set.
var pinInheritedSettings = []string{"CC", "CGO_ENABLED", "CXX", "GOARCH", "GOENV", "GOEXPERIMENT", "GOOS"}

// pinProbeToolchain asks the go command which toolchain runs from runtime/go and how the
// caller's environment configures it.
func pinProbeToolchain(ctx context.Context, runtimeDir string, pinned bool) (string, Toolchain) {
	env, enforced := pinGoEnv(pinned)
	tool := Toolchain{GoFlagNames: []string{}, InheritedSettings: []string{}, Enforced: append([]string{}, enforced...), Build: "not-run"}
	full := pinCommandOutput(ctx, runtimeDir, env, "go", "version")
	if fields := strings.Fields(full); len(fields) >= 3 && fields[0] == "go" && fields[1] == "version" && strings.HasPrefix(fields[2], "go") {
		tool.GoVersionToken = fields[2]
	}
	if raw, err := os.ReadFile(filepath.Join(runtimeDir, "go.mod")); err == nil {
		if match := pinDirectivePattern.FindSubmatch(raw); match != nil {
			tool.GoDirective = string(match[1])
		}
	}
	// What the caller's environment says, read with that environment. GOTOOLCHAIN and
	// GOFLAGS do not depend on the module, so they are read from a neutral directory;
	// GOWORK depends on the directory and is read in runtime/go with the switch off.
	inherited := os.Environ()
	var goenv, workenv, rootenv map[string]string
	if raw := pinCommandOutput(ctx, os.TempDir(), inherited, "go", "env", "-json", "GOTOOLCHAIN", "GOFLAGS", "GOROOT"); raw != "" {
		_ = json.Unmarshal([]byte(raw), &goenv)
	}
	if raw := pinCommandOutput(ctx, runtimeDir, append(append([]string{}, inherited...), "GOTOOLCHAIN=local"), "go", "env", "-json", "GOWORK"); raw != "" {
		_ = json.Unmarshal([]byte(raw), &workenv)
	}
	if raw := pinCommandOutput(ctx, os.TempDir(), pinStripEnv(inherited, "GOROOT"), "go", "env", "-json", "GOROOT"); raw != "" {
		_ = json.Unmarshal([]byte(raw), &rootenv)
	}
	tool.GoToolchainEnv = goenv["GOTOOLCHAIN"]
	// Only the names of the flags: their values may be paths (-modfile=...).
	for _, field := range strings.Fields(goenv["GOFLAGS"]) {
		name, _, _ := strings.Cut(field, "=")
		if strings.HasPrefix(name, "-") {
			tool.GoFlagNames = append(tool.GoFlagNames, name)
		}
	}
	switch work := workenv["GOWORK"]; work {
	case "", "off":
		tool.GoWork = work
	default:
		tool.GoWork = "present"
	}
	for _, name := range pinInheritedSettings {
		if os.Getenv(name) != "" {
			tool.InheritedSettings = append(tool.InheritedSettings, name)
		}
	}
	sort.Strings(tool.InheritedSettings)
	for _, name := range []string{"GOTOOLDIR", "GOCACHEPROG"} {
		if os.Getenv(name) != "" {
			tool.Unsupported = append(tool.Unsupported, name)
		}
	}
	if os.Getenv("GOROOT") != "" && rootenv["GOROOT"] != "" && filepath.Clean(os.Getenv("GOROOT")) != filepath.Clean(rootenv["GOROOT"]) {
		tool.Unsupported = append(tool.Unsupported, "GOROOT")
	}
	return full, tool
}

func pinResolveLoose(path string) (string, error) {
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

// pinOutsideCheckout is false when dir is the checkout or below it (after symlinks), and
// also when either path cannot be resolved.
func pinOutsideCheckout(root, dir string) bool {
	checkout, err1 := pinResolveLoose(root)
	target, err2 := pinResolveLoose(dir)
	if err1 != nil || err2 != nil {
		return false
	}
	relative, err := filepath.Rel(checkout, target)
	if err != nil {
		return true
	}
	return relative == ".." || strings.HasPrefix(relative, ".."+string(filepath.Separator))
}

// pinnedSEI is what a pinned context carries: the sei built outside the checkout, the
// empty working directory it runs in, and what the git and go queries of the old code
// path answer. A non-empty refusal makes every command fail before any SEI code starts.
type pinnedSEI struct {
	bin, work, commit, goFull, refusal string
}

type pinContextKey struct{}

func pinnedFrom(ctx context.Context) (*pinnedSEI, bool) {
	p, ok := ctx.Value(pinContextKey{}).(*pinnedSEI)
	return p, ok
}

// run answers run()/runOutput() for a pinned context. It never starts `go run`: a call
// that does not have the `run ./cmd/sei <subcommand>` shape fails instead of falling
// back to an unpinned SEI. Only standard output is returned; standard error is dropped,
// so a tool message cannot be mixed into a JSON document.
func (p *pinnedSEI) run(ctx context.Context, args []string) ([]byte, error) {
	if p.refusal != "" {
		return nil, errors.New(p.refusal)
	}
	if len(args) < 3 || args[0] != "run" || args[1] != "./cmd/sei" {
		return nil, errors.New("pinned run refused: unsupported go command")
	}
	cmd := exec.CommandContext(ctx, p.bin, args[2:]...)
	cmd.Dir = p.work
	cmd.Env = pinStripEnv(os.Environ(), append(append([]string{}, pinGitRedirectingEnv...), "SEI_DATA_ROOT")...)
	var stdout bytes.Buffer
	cmd.Stdout = &stdout
	if err := cmd.Run(); err != nil {
		return nil, fmt.Errorf("sei %s failed", args[2])
	}
	return stdout.Bytes(), nil
}

// output answers the git and go queries of the old code path from the facts measured
// before the run (git with GIT_* removed, an index copy), never from a second query.
func (p *pinnedSEI) output(name string) string {
	switch name {
	case "git":
		return p.commit
	case "go":
		return p.goFull
	}
	return ""
}

type pinSession struct {
	root     string
	options  Options
	pinned   bool
	report   PinReport
	refusal  string
	state    *pinnedSEI
	before   pinFacts
	cleanups []func()
}

func (s *pinSession) refuse(reason string) {
	if s.refusal == "" {
		s.refusal = reason
	}
}

func (s *pinSession) close() {
	for _, cleanup := range s.cleanups {
		cleanup()
	}
	s.cleanups = nil
}

func pinSuffix() string {
	if runtime.GOOS == "windows" {
		return ".exe"
	}
	return ""
}

var pinHexPattern = regexp.MustCompile(`(?:^|[^0-9a-f])([0-9a-f]{64}|[0-9a-f]{40})(?:[^0-9a-f]|$)`)

// pinReportedCommit compares any commit `sei version` names with HEAD.
func pinReportedCommit(head string, values ...string) string {
	status := "not-reported"
	for _, value := range values {
		for _, match := range pinHexPattern.FindAllStringSubmatch(strings.ToLower(value), -1) {
			if match[1] != head {
				return "mismatch"
			}
			status = "match"
		}
	}
	return status
}

var pinShortHexPattern = regexp.MustCompile(`^[0-9a-f]{7,39}$`)

// pinShortCommit judges an abbreviated commit (7 to 39 hex digits) in the `commit` field of
// `sei version` as a prefix of HEAD. "" means the field is not an abbreviated hash.
func pinShortCommit(head, commit string) string {
	value := strings.ToLower(strings.TrimSpace(commit))
	if !pinShortHexPattern.MatchString(value) {
		return ""
	}
	if strings.HasPrefix(head, value) {
		return "match"
	}
	return "mismatch"
}

// build compiles cmd/sei outside the checkout, runs `sei version` in an empty directory
// and returns the state of the pinned context. A non-empty reason is a refusal.
func (s *pinSession) build(ctx context.Context, runtimeDir, goPath string, head string) (*pinnedSEI, string) {
	dir, keptAt := s.options.BuildOut, ""
	if dir != "" {
		if err := os.MkdirAll(dir, 0o755); err != nil {
			return nil, "build-out cannot be created"
		}
		keptAt = "build-out"
	} else {
		var err error
		if dir, err = os.MkdirTemp("", "tai-sei-bin-"); err != nil {
			return nil, "temporary directory cannot be created"
		}
		s.cleanups = append(s.cleanups, func() { _ = os.RemoveAll(dir) })
	}
	work, err := os.MkdirTemp("", "tai-sei-run-")
	if err != nil {
		return nil, "temporary directory cannot be created"
	}
	s.cleanups = append(s.cleanups, func() { _ = os.RemoveAll(work) })
	bin := filepath.Join(dir, "sei"+pinSuffix())
	env, _ := pinGoEnv(true)
	build := exec.CommandContext(ctx, goPath, append(append([]string{"build"}, pinBuildFlags...), "-o", bin, "./cmd/sei")...)
	build.Dir = runtimeDir
	build.Env = env
	if err := build.Run(); err != nil {
		s.report.Toolchain.Build = "failed"
		s.report.Binary.Status = "failed"
		directive, local := s.report.Toolchain.GoDirective, s.report.Toolchain.GoVersionToken
		if directive == "" {
			directive = "unknown"
		}
		if local == "" {
			local = "unknown"
		}
		return nil, fmt.Sprintf("SEI build failed (go.mod go directive %s, local go %s)", directive, local)
	}
	s.report.Toolchain.Build = "built"
	s.report.Toolchain.BuildFlags = append([]string{}, pinBuildFlags...)
	s.report.Binary.Status = "built"
	s.report.Binary.KeptAt = keptAt
	if raw, err := os.ReadFile(bin); err == nil {
		s.report.Binary.Sha256 = pinDigest(raw)
	}
	state := &pinnedSEI{bin: bin, work: work, commit: head, goFull: ""}
	versionCtx, cancel := context.WithTimeout(ctx, 60*time.Second)
	defer cancel()
	out, err := state.run(versionCtx, []string{"run", "./cmd/sei", "version"})
	if err != nil {
		return nil, "sei version failed"
	}
	var line struct {
		Version string `json:"version"`
		Commit  string `json:"commit"`
		Target  string `json:"target"`
	}
	if json.Unmarshal(bytes.TrimSpace(out), &line) != nil || line.Version == "" {
		return nil, "sei version output is invalid"
	}
	s.report.Binary.VersionLine = VersionLine{Version: line.Version, Commit: line.Commit, Target: line.Target}
	status := pinReportedCommit(head, line.Commit, line.Version)
	switch pinShortCommit(head, line.Commit) {
	case "mismatch":
		status = "mismatch"
	case "match":
		if status == "not-reported" {
			status = "match"
		}
	}
	s.report.Binary.ReportedCommit.Status = status
	if status == "mismatch" {
		return nil, "pin mismatch: sei version reports a commit that differs from HEAD"
	}
	return state, ""
}

// beginPin gathers the facts and, for a pinned run, checks every expectation and builds
// sei before any SEI code is started. The returned context routes run()/runOutput()/
// output() to the pinned sei (or to a refusal). An unpinned run gets ctx back unchanged
// and keeps the old `go run` path; only facts are recorded.
func beginPin(ctx context.Context, root string, options Options) (context.Context, *pinSession) {
	// go build runs in runtime/go, so a relative build-out would land inside the checkout
	// although it looks outside relative to the caller's directory: decide on the absolute path.
	if options.BuildOut != "" {
		if absolute, err := filepath.Abs(options.BuildOut); err == nil {
			options.BuildOut = absolute
		}
	}
	s := &pinSession{root: root, options: options, pinned: options.specified(), report: newPinReport()}
	runtimeDir := filepath.Join(root, "runtime", "go")
	_, statErr := os.Stat(filepath.Join(runtimeDir, "cmd", "sei"))
	goPath, goErr := exec.LookPath("go")
	full := ""
	if statErr == nil && goErr == nil {
		var tool Toolchain
		full, tool = pinProbeToolchain(ctx, runtimeDir, s.pinned)
		s.report.Toolchain = tool
	}
	s.before = gatherFacts(ctx, root)
	s.report.Checkout.Before = pinCheckoutFacts(s.before)
	pin, reasons := evaluatePin(options, s.before, s.report.Toolchain)
	s.report.Pin = pin
	switch {
	case options.BuildOut != "" && !s.pinned:
		s.refuse("invalid pin expectation: -build-out is only used together with an expected commit")
	case !s.pinned:
	case statErr != nil:
		s.refuse("SEI runtime is unavailable")
	case goErr != nil:
		s.refuse("go is unavailable")
	case len(reasons) > 0:
		s.refuse(strings.Join(reasons, "; "))
	case options.BuildOut != "" && !pinOutsideCheckout(root, options.BuildOut):
		s.refuse("build-out must be outside the SEI checkout")
	default:
		buildCtx, cancel := context.WithTimeout(ctx, 10*time.Minute)
		state, reason := s.build(buildCtx, runtimeDir, goPath, s.before.Commit)
		cancel()
		if reason != "" {
			s.refuse(reason)
		} else {
			state.goFull = full
			s.state = state
		}
	}
	if s.refusal != "" {
		s.state = &pinnedSEI{refusal: s.refusal, commit: s.before.Commit, goFull: full}
	}
	if s.state == nil {
		return ctx, s
	}
	return context.WithValue(ctx, pinContextKey{}, s.state), s
}

// finish takes the after-state of the checkout and returns the report and the reasons the
// run failed because of the pin (none for an unpinned run: record only).
func (s *pinSession) finish(ctx context.Context) (PinReport, []string) {
	defer s.close()
	if s.refusal != "" {
		return s.report, []string{s.refusal}
	}
	var failures []string
	after := gatherFacts(ctx, s.root)
	s.report.Checkout.After = pinCheckoutFacts(after)
	queried := func(facts pinFacts) bool { return facts.Commit != "" && facts.TrackedDigest != "" }
	switch {
	case !queried(s.before):
		s.report.Checkout.Status = "unavailable"
	case !queried(after):
		s.report.Checkout.Status = "changed"
		failures = append(failures, "SEI commands changed the SEI checkout (its git state can no longer be read)")
	default:
		if changed := s.report.Checkout.Before.changedFields(s.report.Checkout.After); len(changed) > 0 {
			s.report.Checkout.Status = "changed"
			failures = append(failures, "SEI commands changed the SEI checkout ("+strings.Join(changed, ", ")+")")
		} else {
			s.report.Checkout.Status = "unchanged"
		}
	}
	if s.state != nil {
		if entries, err := os.ReadDir(s.state.work); err != nil || len(entries) > 0 {
			failures = append(failures, "sei wrote outside the store (its working directory is not empty)")
		}
	}
	if !s.pinned {
		// Default: record only. A changed checkout is visible in checkout.status.
		return s.report, nil
	}
	return s.report, failures
}

const (
	pinNoteRecordOnly = "版固定の期待値が指定されていないため、SEIのcommit・Go versionは記録のみで照合していない。実行前後のcheckoutの変化もcheckout.statusに記録するだけで、passedは変えない。"
	pinNotePinned     = "版固定の一致が示すのは、checkoutのHEAD・追跡内容・Go toolchainが期待と合ったことだけである（バイナリのsha256は記録するだけで照合しない）。GOEXPERIMENT・CGO_ENABLED・GOOS/GOARCH・CCなど、toolchainの他の設定は拘束せず、名前だけを記録する。SEIの正しさ・決定の意味・Authorityは示さない。`sei version`は`commit: unknown`を出すため、版の証明にならない。"
)

// pinScrub replaces a reason that names a local path with a fixed sentence.
func pinScrub(reason, root string) string {
	candidates := []string{root, os.TempDir()}
	if home, err := os.UserHomeDir(); err == nil {
		candidates = append(candidates, home)
	}
	for _, candidate := range candidates {
		if candidate != "" && candidate != "." && candidate != string(filepath.Separator) && strings.Contains(reason, candidate) {
			return "SEI run failed"
		}
	}
	return reason
}

// RunWithOptions runs the fixture of the named variant ("" is the SCN-001 decision
// fixture). The old Run, RunApproval, RunRejection and RunVariant are unchanged.
func RunWithOptions(ctx context.Context, root, variant string, options Options) Receipt {
	pctx, session := beginPin(ctx, root, options)
	var receipt Receipt
	switch variant {
	case "":
		receipt = Run(pctx, root)
	case "scn002-approvals":
		receipt = RunApproval(pctx, root)
	case "scn002-rejections":
		receipt = RunRejection(pctx, root)
	default:
		receipt = RunVariant(pctx, root, variant)
	}
	report, failures := session.finish(ctx)
	receipt.PinReport = &report
	if receipt.Schema != "" {
		note := pinNotePinned
		if !session.pinned {
			note = pinNoteRecordOnly
		}
		receipt.Notes = append(receipt.Notes, note)
	}
	if len(failures) > 0 {
		receipt.Passed = false
		if session.refusal != "" {
			receipt.Reason = session.refusal
		} else {
			receipt.Reason = strings.Join(failures, "; ")
		}
	}
	if session.pinned && !receipt.Passed {
		receipt.Reason = pinScrub(receipt.Reason, root)
	}
	return receipt
}

func inspectBasisPinned(ctx context.Context, root, path string, options Options) (BasisInspection, error) {
	pctx, session := beginPin(ctx, root, options)
	result, err := inspectBasis(pctx, root, path)
	report, failures := session.finish(ctx)
	if err == nil && len(failures) > 0 {
		err = errors.New(strings.Join(failures, "; "))
	}
	result.PinReport = &report
	return result, err
}

func inspectValidityPinned(ctx context.Context, root, path, targetPath string, names []string, options Options) (ValidityInspection, error) {
	pctx, session := beginPin(ctx, root, options)
	result, err := inspectValidity(pctx, root, path, targetPath, names)
	report, failures := session.finish(ctx)
	if err == nil && len(failures) > 0 {
		err = errors.New(strings.Join(failures, "; "))
	}
	result.PinReport = &report
	return result, err
}

// runValidityPinned is runValidity with the pin: same exit codes, no report when the pin
// failed.
func runValidityPinned(ctx context.Context, root, bundlePath, targetPath string, names []string, outPath string, options Options, stdout, stderr io.Writer) int {
	inspection, err := inspectValidityPinned(ctx, root, bundlePath, targetPath, names, options)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	return emitValidity(inspection, outPath, stdout, stderr)
}
