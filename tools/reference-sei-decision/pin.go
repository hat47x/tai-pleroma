package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
)

// Options carries opt-in expectations. The zero value means "record only".
// Any non-empty expectation turns the run into a pinned run, and a pinned run needs
// ExpectCommit: the Go version says nothing about which SEI checkout was run.
type Options struct {
	ExpectCommit    string // 40-hex (or 64-hex) git object id of the SEI checkout HEAD
	ExpectGoVersion string // the version token of `go version`, e.g. go1.26.9 (no OS/arch)
	BuildOut        string // optional directory (outside the checkout) that keeps the built sei
}

func (o Options) specified() bool {
	return o.ExpectCommit != "" || o.ExpectGoVersion != ""
}

type PinItem struct {
	Status   string `json:"status"` // not-checked | match | mismatch | unavailable
	Expected string `json:"expected,omitempty"`
	Actual   string `json:"actual,omitempty"`
}

// SourceTree describes tracked file content, plus the untracked or ignored files the Go
// toolchain may compile under runtime/go. "clean" says nothing about other untracked
// files, other ignored files, //go:embed files or anything outside the checkout.
type SourceTree struct {
	Status               string `json:"status"` // not-checked | clean | tracked-changes | untracked-build-inputs | unavailable
	TrackedChanges       int    `json:"trackedChanges"`
	UntrackedFiles       int    `json:"untrackedFiles"`
	UntrackedBuildInputs int    `json:"untrackedBuildInputs"` // untracked or ignored files under runtime/go that go build may compile or be steered by
	HiddenFlaggedFiles   int    `json:"hiddenFlaggedFiles"`   // tracked files marked assume-unchanged or skip-worktree
}

type PinCheck struct {
	Checked    bool       `json:"checked"`
	Result     string     `json:"result"` // not-checked | match | mismatch | unavailable | invalid-expectation
	Commit     PinItem    `json:"commit"`
	GoVersion  PinItem    `json:"goVersion"`
	SourceTree SourceTree `json:"sourceTree"`
}

var (
	pinCommitPattern    = regexp.MustCompile(`^(?:[0-9a-f]{40}|[0-9a-f]{64})$`)
	pinGoVersionPattern = regexp.MustCompile(`^go[0-9]+\.[0-9]+(?:\.[0-9]+)?(?:(?:rc|beta)[0-9]+)?$`)
)

func pinDigest(content []byte) string {
	sum := sha256.Sum256(content)
	return "sha256:" + hex.EncodeToString(sum[:])
}

// pinGitRedirectingEnv are variables that make git look at another repository, work
// tree, index or object store than the checkout directory.
var pinGitRedirectingEnv = []string{
	"GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
	"GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
}

// pinStripEnv returns env without the named variables.
func pinStripEnv(env []string, names ...string) []string {
	var kept []string
	for _, entry := range env {
		name, _, _ := strings.Cut(entry, "=")
		drop := false
		for _, blocked := range names {
			if name == blocked {
				drop = true
				break
			}
		}
		if !drop {
			kept = append(kept, entry)
		}
	}
	return kept
}

// pinGitCommand builds a git query for the checkout in dir. --no-replace-objects keeps
// a refs/replace entry from making `diff HEAD` compare against another tree than the
// one the recorded HEAD commit has.
func pinGitCommand(ctx context.Context, dir string, args ...string) *exec.Cmd {
	cmd := exec.CommandContext(ctx, "git", append([]string{"--no-replace-objects"}, args...)...)
	cmd.Dir = dir
	cmd.Env = pinStripEnv(os.Environ(), pinGitRedirectingEnv...)
	return cmd
}

// pinCopyIndex copies the checkout's real index into a private temporary directory.
// `git diff` refreshes stat information and rewrites the index it is given even with
// --no-optional-locks, so every index-reading query runs against this copy
// (GIT_INDEX_FILE) and the shared SEI checkout's .git stays untouched.
//
// The copy gets the original index file's modification time. git trusts an entry whose
// stat data matches the file unless the entry is not older than the index file
// ("racily clean"), in which case it reads the content. A copy stamped with the time of
// copying would make every entry look older than the index and hide a same-size edit
// made in the second the index was written.
func pinCopyIndex(ctx context.Context, root string) (string, func(), error) {
	out, err := pinGitCommand(ctx, root, "rev-parse", "--git-path", "index").Output()
	if err != nil {
		return "", nil, err
	}
	source := strings.TrimSpace(string(out))
	if !filepath.IsAbs(source) {
		source = filepath.Join(root, source)
	}
	statBefore, err := os.Stat(source)
	if err != nil {
		return "", nil, err
	}
	content, err := os.ReadFile(source)
	if err != nil {
		return "", nil, err
	}
	statAfter, err := os.Stat(source)
	if err != nil {
		return "", nil, err
	}
	if !statBefore.ModTime().Equal(statAfter.ModTime()) || statBefore.Size() != statAfter.Size() || int64(len(content)) != statAfter.Size() {
		return "", nil, errors.New("the index changed while it was copied")
	}
	dir, err := os.MkdirTemp("", "tai-sei-index-")
	if err != nil {
		return "", nil, err
	}
	cleanup := func() { _ = os.RemoveAll(dir) }
	copyPath := filepath.Join(dir, "index")
	if err := os.WriteFile(copyPath, content, 0o600); err != nil {
		cleanup()
		return "", nil, err
	}
	if err := os.Chtimes(copyPath, statBefore.ModTime(), statBefore.ModTime()); err != nil {
		cleanup()
		return "", nil, err
	}
	return copyPath, cleanup, nil
}

// pinFacts is what can be said about the SEI checkout without modifying it.
type pinFacts struct {
	Commit            string
	TreeStatus        string // clean | tracked-changes | untracked-build-inputs | unavailable
	Tracked           int
	Untracked         int
	BuildInputs       int    // untracked or ignored files under runtime/go that the Go toolchain may compile or be steered by
	Hidden            int    // tracked files git is told not to look at
	TrackedDigest     string // sha256 of `git diff --binary HEAD`: also sees a further edit of an already modified file
	UntrackedDigest   string // sha256 of the NUL separated untracked file names
	BuildInputsDigest string // sha256 of the untracked and ignored build input names
}

// pinModuleDir is where the Go module of SEI lives, relative to the checkout root.
const pinModuleDir = "runtime/go/"

var pinBuildInputExtensions = map[string]bool{
	".go": true, ".s": true, ".S": true, ".sx": true,
	".c": true, ".h": true, ".cc": true, ".cpp": true, ".cxx": true, ".hh": true, ".hpp": true, ".hxx": true,
	".m": true, ".f": true, ".F": true, ".for": true, ".f90": true,
	".swig": true, ".swigcxx": true, ".syso": true,
}

// isGoBuildInput reports whether a path (git prints it slash separated, relative to the
// checkout root) can change what `go build` produces in runtime/go: a source file the
// toolchain compiles, a go.mod / go.sum / go.work* file at any depth below runtime/go (a
// nested go.mod removes its directory from the module), or anything under
// runtime/go/vendor/. Files outside runtime/go are not inputs of this build. It does not
// see files pulled in by //go:embed, which can have any name.
func isGoBuildInput(name string) bool {
	if !strings.HasPrefix(name, pinModuleDir) {
		return false
	}
	rel := strings.TrimPrefix(name, pinModuleDir)
	base := rel[strings.LastIndex(rel, "/")+1:]
	switch {
	case base == "go.mod" || base == "go.sum" || strings.HasPrefix(base, "go.work"):
		return true
	case strings.HasPrefix(rel, "vendor/"):
		return true
	}
	if dot := strings.LastIndex(base, "."); dot >= 0 {
		return pinBuildInputExtensions[base[dot:]]
	}
	return false
}

// isNestedRepository reports an entry that git lists as one directory (trailing slash)
// because it holds a repository of its own, when that directory is or contains part of the
// module directory. git does not list the files inside it, so their names cannot be
// judged: such a directory is counted as a build input (fail closed).
func isNestedRepository(name string) bool {
	return strings.HasSuffix(name, "/") && (strings.HasPrefix(name, pinModuleDir) || strings.HasPrefix(pinModuleDir, name))
}

func pinBuildInputs(output []byte) []string {
	var names []string
	for _, entry := range bytes.Split(output, []byte{0}) {
		if name := string(entry); name != "" && (isGoBuildInput(name) || isNestedRepository(name)) {
			names = append(names, name)
		}
	}
	return names
}

// gatherFacts does not modify the SEI checkout: git rev-parse, a copy of the index for
// diff/ls-files. A subdirectory of another repository is "unavailable".
func gatherFacts(ctx context.Context, root string) pinFacts {
	facts := pinFacts{TreeStatus: "unavailable"}
	// `git rev-parse HEAD` inside a plain subdirectory of another repository would
	// report that outer repository's commit. Require root to be the top level.
	top, err := pinGitCommand(ctx, root, "--no-optional-locks", "rev-parse", "--show-toplevel").Output()
	if err != nil {
		return facts
	}
	topInfo, topErr := os.Stat(strings.TrimSpace(string(top)))
	rootInfo, rootErr := os.Stat(root)
	if topErr != nil || rootErr != nil || !os.SameFile(topInfo, rootInfo) {
		return facts
	}
	head, err := pinGitCommand(ctx, root, "rev-parse", "HEAD").Output()
	if err != nil {
		return facts
	}
	facts.Commit = strings.TrimSpace(string(head))
	indexCopy, cleanup, err := pinCopyIndex(ctx, root)
	if err != nil {
		return facts
	}
	defer cleanup()
	onCopy := func(args ...string) *exec.Cmd {
		cmd := pinGitCommand(ctx, root, append([]string{"--no-optional-locks"}, args...)...)
		cmd.Env = append(cmd.Env, "GIT_INDEX_FILE="+indexCopy)
		return cmd
	}
	// Tracked changes are judged by content (`diff HEAD` covers staged, unstaged and
	// deleted files) over the whole checkout.
	changed, err := onCopy("diff", "--name-only", "--no-ext-diff", "-z", "HEAD", "--").Output()
	if err != nil {
		return facts
	}
	patch, err := onCopy("diff", "--binary", "--no-ext-diff", "--no-textconv", "HEAD", "--").Output()
	if err != nil {
		return facts
	}
	untracked, err := onCopy("ls-files", "--others", "--exclude-standard", "-z").Output()
	if err != nil {
		return facts
	}
	// `diff HEAD` does not see a tracked file that carries the assume-unchanged or
	// skip-worktree flag, so an edit can hide behind it.
	flagged, err := onCopy("ls-files", "-v", "-z").Output()
	if err != nil {
		return facts
	}
	// An untracked or ignored file the toolchain picks up builds a different program
	// without changing HEAD or any tracked file, and git status never lists an ignored
	// one: ask for both, limited to the module directory.
	ignored, err := onCopy("ls-files", "--others", "--ignored", "--exclude-standard", "-z", "--", "runtime/go").Output()
	if err != nil {
		return facts
	}
	inputs := append(pinBuildInputs(untracked), pinBuildInputs(ignored)...)
	facts.Tracked = pinCountNUL(changed)
	facts.Untracked = pinCountNUL(untracked)
	facts.BuildInputs = len(inputs)
	facts.Hidden = pinCountHidden(flagged)
	facts.TrackedDigest = pinDigest(patch)
	facts.UntrackedDigest = pinDigest(untracked)
	facts.BuildInputsDigest = pinDigest([]byte(strings.Join(inputs, "\x00")))
	switch {
	case facts.Tracked > 0:
		facts.TreeStatus = "tracked-changes"
	case facts.Hidden > 0:
		facts.TreeStatus = "unavailable"
	case facts.BuildInputs > 0:
		facts.TreeStatus = "untracked-build-inputs"
	default:
		facts.TreeStatus = "clean"
	}
	return facts
}

// pinCountHidden counts `git ls-files -v -z` entries whose tag marks the file as
// assume-unchanged (lower case) or skip-worktree (S).
func pinCountHidden(output []byte) int {
	count := 0
	for _, entry := range bytes.Split(output, []byte{0}) {
		if len(entry) > 1 && (entry[0] == 'S' || (entry[0] >= 'a' && entry[0] <= 'z')) {
			count++
		}
	}
	return count
}

func pinCountNUL(output []byte) int {
	count := 0
	for _, entry := range bytes.Split(output, []byte{0}) {
		if len(entry) > 0 {
			count++
		}
	}
	return count
}

func pinItem(expected, actual string) PinItem {
	switch {
	case expected == "":
		return PinItem{Status: "not-checked", Actual: actual}
	case actual == "":
		return PinItem{Status: "unavailable", Expected: expected}
	case expected == actual:
		return PinItem{Status: "match", Expected: expected, Actual: actual}
	default:
		return PinItem{Status: "mismatch", Expected: expected, Actual: actual}
	}
}

// evaluatePin returns the recorded pin state and the reasons it fails (none when no
// expectation was supplied: record-only). Reasons are fixed sentences plus the expected
// and measured hash or version token; they carry no path and no tool error text.
func evaluatePin(options Options, facts pinFacts, tool Toolchain) (PinCheck, []string) {
	pin := PinCheck{
		Result:     "not-checked",
		Commit:     pinItem("", facts.Commit),
		GoVersion:  pinItem("", tool.GoVersionToken),
		SourceTree: SourceTree{Status: "not-checked", TrackedChanges: facts.Tracked, UntrackedFiles: facts.Untracked, UntrackedBuildInputs: facts.BuildInputs, HiddenFlaggedFiles: facts.Hidden},
	}
	if !options.specified() {
		return pin, nil
	}
	pin.Checked = true
	var reasons []string
	for _, check := range []struct {
		name, value string
		pattern     *regexp.Regexp
	}{
		{"expected commit", options.ExpectCommit, pinCommitPattern},
		{"expected go version", options.ExpectGoVersion, pinGoVersionPattern},
	} {
		if check.value != "" && !check.pattern.MatchString(check.value) {
			reasons = append(reasons, fmt.Sprintf("invalid pin expectation: %s", check.name))
		}
	}
	if options.ExpectCommit == "" {
		reasons = append(reasons, "invalid pin expectation: expected commit is required when any pin expectation is given")
	}
	if len(reasons) > 0 {
		pin.Result = "invalid-expectation"
		return pin, reasons
	}
	pin.Commit = pinItem(options.ExpectCommit, facts.Commit)
	pin.GoVersion = pinItem(options.ExpectGoVersion, tool.GoVersionToken)
	pin.SourceTree.Status = facts.TreeStatus
	result := "match"
	for _, item := range []struct {
		name string
		item PinItem
	}{{"sei commit", pin.Commit}, {"go version", pin.GoVersion}} {
		switch item.item.Status {
		case "mismatch":
			result = "mismatch"
			reasons = append(reasons, fmt.Sprintf("pin mismatch: %s expected %s, got %s", item.name, item.item.Expected, item.item.Actual))
		case "unavailable":
			if result == "match" {
				result = "unavailable"
			}
			reasons = append(reasons, fmt.Sprintf("pin unavailable: %s could not be determined", item.name))
		}
	}
	if facts.TreeStatus == "tracked-changes" {
		result = "mismatch"
		reasons = append(reasons, fmt.Sprintf("pin mismatch: SEI source tree has %d tracked change(s)", facts.Tracked))
	}
	if facts.BuildInputs > 0 {
		result = "mismatch"
		reasons = append(reasons, fmt.Sprintf("pin mismatch: SEI checkout has %d untracked or ignored Go build input file(s) under runtime/go", facts.BuildInputs))
	}
	if facts.Hidden > 0 {
		if result == "match" {
			result = "unavailable"
		}
		reasons = append(reasons, fmt.Sprintf("pin unavailable: %d tracked file(s) are marked assume-unchanged or skip-worktree, so edits to them cannot be seen", facts.Hidden))
	}
	if facts.TreeStatus == "unavailable" && facts.Hidden == 0 {
		if result == "match" {
			result = "unavailable"
		}
		reasons = append(reasons, "pin unavailable: SEI source tree state could not be determined")
	}
	// Settings that replace the compiler or its cache change what is compiled without
	// changing the version line that `go version` prints.
	for _, name := range tool.Unsupported {
		if result == "match" {
			result = "unavailable"
		}
		reasons = append(reasons, fmt.Sprintf("pin unavailable: %s is set, which can change what is compiled", name))
	}
	pin.Result = result
	return pin, reasons
}

// registerPinFlags adds the opt-in flags to fs. The values are read by resolvePinOptions
// after fs is parsed.
func registerPinFlags(fs *flag.FlagSet) {
	fs.String("expect-commit", "", "fail unless the SEI checkout HEAD equals this commit (env TAI_SEI_EXPECT_COMMIT)")
	fs.String("expect-go-version", "", "fail unless `go version` reports this version token, e.g. go1.26.9 (env TAI_SEI_EXPECT_GO_VERSION)")
	fs.String("build-out", "", "keep the sei built for a pinned run in this directory (must be outside the checkout)")
}

// resolvePinOptions reads the pin flags from a parsed fs, with environment variables as
// the default of each expectation (a flag given on the command line wins, and an empty
// flag value means "no expectation").
func resolvePinOptions(fs *flag.FlagSet, getenv func(string) string) Options {
	set := map[string]bool{}
	fs.Visit(func(f *flag.Flag) { set[f.Name] = true })
	value := func(name, env string) string {
		if set[name] {
			return fs.Lookup(name).Value.String()
		}
		if env != "" {
			return getenv(env)
		}
		return ""
	}
	return Options{
		ExpectCommit:    strings.ToLower(value("expect-commit", "TAI_SEI_EXPECT_COMMIT")),
		ExpectGoVersion: value("expect-go-version", "TAI_SEI_EXPECT_GO_VERSION"),
		BuildOut:        value("build-out", ""),
	}
}

func init() { registerPinFlags(flag.CommandLine) }

// pinOptions is what main uses: the pin flags of flag.CommandLine plus the environment.
func pinOptions() Options { return resolvePinOptions(flag.CommandLine, os.Getenv) }
