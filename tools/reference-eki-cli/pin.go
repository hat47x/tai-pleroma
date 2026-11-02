package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
)

// Options carries opt-in expectations. The zero value means "record only".
// Any non-empty field turns the run into a pinned run, and a pinned run needs
// ExpectCommit: the Go version says nothing about which EKI checkout was run.
type Options struct {
	ExpectCommit    string // 40-hex (or 64-hex) git object id of the EKI checkout HEAD
	ExpectGoVersion string // the version token of `go version`, e.g. go1.26.9 (no OS/arch)
	BuildOut        string // optional directory (outside the checkout) that keeps the built binaries
}

func (o Options) specified() bool {
	return o.ExpectCommit != "" || o.ExpectGoVersion != ""
}

type PinItem struct {
	Status   string `json:"status"` // not-checked | match | mismatch | unavailable
	Expected string `json:"expected,omitempty"`
	Actual   string `json:"actual,omitempty"`
}

// SourceTree describes tracked file content, plus the untracked or ignored files the
// Go toolchain may compile. "clean" says nothing about other untracked files, other
// ignored files, //go:embed files or anything outside the checkout.
type SourceTree struct {
	Status               string `json:"status"` // not-checked | clean | tracked-changes | untracked-build-inputs | unavailable
	TrackedChanges       int    `json:"trackedChanges"`
	UntrackedFiles       int    `json:"untrackedFiles"`
	UntrackedBuildInputs int    `json:"untrackedBuildInputs"` // untracked or ignored files the Go toolchain may compile or be steered by
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
	commitPattern    = regexp.MustCompile(`^(?:[0-9a-f]{40}|[0-9a-f]{64})$`)
	goVersionPattern = regexp.MustCompile(`^go[0-9]+\.[0-9]+(?:\.[0-9]+)?(?:(?:rc|beta)[0-9]+)?$`)
)

func digestBytes(content []byte) string {
	sum := sha256.Sum256(content)
	return "sha256:" + hex.EncodeToString(sum[:])
}

// gitRedirectingEnv are variables that make git look at another repository, work
// tree, index or object store than the checkout directory. A git hook sets some
// of them; they must not redirect these queries.
var gitRedirectingEnv = []string{
	"GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
	"GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
}

// gitCommand builds a git query for the checkout in dir. --no-replace-objects
// keeps a refs/replace entry from making `diff HEAD` compare against another tree
// than the one the recorded HEAD commit has.
func gitCommand(ctx context.Context, dir string, args ...string) *exec.Cmd {
	cmd := exec.CommandContext(ctx, "git", append([]string{"--no-replace-objects"}, args...)...)
	cmd.Dir = dir
	for _, entry := range os.Environ() {
		name, _, _ := strings.Cut(entry, "=")
		redirects := false
		for _, blocked := range gitRedirectingEnv {
			if name == blocked {
				redirects = true
				break
			}
		}
		if !redirects {
			cmd.Env = append(cmd.Env, entry)
		}
	}
	return cmd
}

// copyIndex copies the checkout's real .git/index into a private temporary
// directory. `git diff` refreshes stat information and rewrites the index it is
// given even with --no-optional-locks, so every index-reading query runs against
// this copy (GIT_INDEX_FILE) and the shared EKI checkout's .git stays untouched.
//
// The copy gets the original index file's modification time. git trusts an entry
// whose stat data matches the file unless the entry is not older than the index
// file ("racily clean"), in which case it reads the content. A copy stamped with
// the time of copying would make every entry look older than the index and hide a
// same-size edit made in the second the index was written.
func copyIndex(ctx context.Context, ekiRoot string) (string, func(), error) {
	out, err := gitCommand(ctx, ekiRoot, "rev-parse", "--git-path", "index").Output()
	if err != nil {
		return "", nil, err
	}
	source := strings.TrimSpace(string(out))
	if !filepath.IsAbs(source) {
		source = filepath.Join(ekiRoot, source)
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
	dir, err := os.MkdirTemp("", "tai-eki-index-")
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

// ekiFacts is what can be said about the EKI checkout without modifying it.
type ekiFacts struct {
	Commit            string
	TreeStatus        string // clean | tracked-changes | untracked-build-inputs | unavailable
	Tracked           int
	Untracked         int
	BuildInputs       int    // untracked or ignored files the Go toolchain may compile or be steered by
	Hidden            int    // tracked files git is told not to look at
	TrackedDigest     string // sha256 of `git diff --binary HEAD`: also sees a further edit of an already modified file
	UntrackedDigest   string // sha256 of the NUL separated untracked file names
	BuildInputsDigest string // sha256 of the untracked and ignored build input names
}

// buildInputExtensions are the file types `go build` compiles or links: Go, assembly,
// C, C++, Objective-C, Fortran and SWIG sources, headers, and prebuilt .syso objects.
var buildInputExtensions = map[string]bool{
	".go": true, ".s": true, ".S": true, ".sx": true,
	".c": true, ".h": true, ".cc": true, ".cpp": true, ".cxx": true, ".hh": true, ".hpp": true, ".hxx": true,
	".m": true, ".f": true, ".F": true, ".for": true, ".f90": true,
	".swig": true, ".swigcxx": true, ".syso": true,
}

// isGoBuildInput reports whether a path (git prints slash separated, relative to the
// checkout root) can change what `go build` produces: a source file of any kind the
// toolchain compiles, a go.mod / go.sum / go.work* file at any depth (a nested go.mod
// removes its directory from the module), or anything under the root vendor/.
// It does not see files pulled in by //go:embed, which can have any name.
func isGoBuildInput(name string) bool {
	base := name[strings.LastIndex(name, "/")+1:]
	switch {
	case base == "go.mod" || base == "go.sum" || strings.HasPrefix(base, "go.work"):
		return true
	case strings.HasPrefix(name, "vendor/"):
		return true
	}
	if dot := strings.LastIndex(base, "."); dot >= 0 {
		return buildInputExtensions[base[dot:]]
	}
	return false
}

// buildInputs returns the NUL separated git output filtered to build input names.
func buildInputs(output []byte) []string {
	var names []string
	for _, entry := range bytes.Split(output, []byte{0}) {
		if name := string(entry); name != "" && isGoBuildInput(name) {
			names = append(names, name)
		}
	}
	return names
}

// gatherFacts does not modify the EKI checkout: git rev-parse, a copy of the
// index for diff/ls-files. A subdirectory of another repository is "unavailable".
func gatherFacts(ctx context.Context, ekiRoot string) ekiFacts {
	facts := ekiFacts{TreeStatus: "unavailable"}
	// `git rev-parse HEAD` inside a plain subdirectory of another repository would
	// report that outer repository's commit. Require ekiRoot to be the top level.
	top, err := gitCommand(ctx, ekiRoot, "--no-optional-locks", "rev-parse", "--show-toplevel").Output()
	if err != nil {
		return facts
	}
	topInfo, topErr := os.Stat(strings.TrimSpace(string(top)))
	rootInfo, rootErr := os.Stat(ekiRoot)
	if topErr != nil || rootErr != nil || !os.SameFile(topInfo, rootInfo) {
		return facts
	}
	head, err := gitCommand(ctx, ekiRoot, "rev-parse", "HEAD").Output()
	if err != nil {
		return facts
	}
	facts.Commit = strings.TrimSpace(string(head))
	indexCopy, cleanup, err := copyIndex(ctx, ekiRoot)
	if err != nil {
		return facts
	}
	defer cleanup()
	onCopy := func(args ...string) *exec.Cmd {
		cmd := gitCommand(ctx, ekiRoot, append([]string{"--no-optional-locks"}, args...)...)
		cmd.Env = append(cmd.Env, "GIT_INDEX_FILE="+indexCopy)
		return cmd
	}
	// Tracked changes are judged by content (`diff HEAD` covers staged, unstaged and
	// deleted files). `git status` reports a CRLF working copy of an LF blob as
	// modified when the index stat was taken before the rewrite, and `diff` refreshes
	// the index it reads, hence the copy.
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
	// skip-worktree flag, so an edit can hide behind it. Count those files: lower
	// case tags are assume-unchanged, `S` is skip-worktree.
	flagged, err := onCopy("ls-files", "-v", "-z").Output()
	if err != nil {
		return facts
	}
	// A pinned commit says which tracked files are compiled. An untracked or ignored
	// file the toolchain picks up (a .go file in cmd/eki-control, a nested go.mod, ...) builds
	// a different program without changing HEAD or any tracked file, and git status
	// never lists an ignored one: ask for both.
	ignored, err := onCopy("ls-files", "--others", "--ignored", "--exclude-standard", "-z").Output()
	if err != nil {
		return facts
	}
	inputs := append(buildInputs(untracked), buildInputs(ignored)...)
	facts.Tracked = countNUL(changed)
	facts.Untracked = countNUL(untracked)
	facts.BuildInputs = len(inputs)
	facts.Hidden = countHiddenFlags(flagged)
	facts.TrackedDigest = digestBytes(patch)
	facts.UntrackedDigest = digestBytes(untracked)
	facts.BuildInputsDigest = digestBytes([]byte(strings.Join(inputs, "\x00")))
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

// countHiddenFlags counts `git ls-files -v -z` entries whose tag marks the file
// as assume-unchanged (lower case) or skip-worktree (S).
func countHiddenFlags(output []byte) int {
	count := 0
	for _, entry := range bytes.Split(output, []byte{0}) {
		if len(entry) > 1 && (entry[0] == 'S' || (entry[0] >= 'a' && entry[0] <= 'z')) {
			count++
		}
	}
	return count
}

// countNUL counts the non-empty entries of NUL-separated git output.
func countNUL(output []byte) int {
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

// evaluatePin returns the recorded pin state and the reasons it fails (none when
// no expectation was supplied: record-only).
func evaluatePin(options Options, facts ekiFacts, tool Toolchain) (PinCheck, []string) {
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
		{"expected commit", options.ExpectCommit, commitPattern},
		{"expected go version", options.ExpectGoVersion, goVersionPattern},
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
	}{{"eki commit", pin.Commit}, {"go version", pin.GoVersion}} {
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
		reasons = append(reasons, fmt.Sprintf("pin mismatch: EKI source tree has %d tracked change(s)", facts.Tracked))
	}
	if facts.BuildInputs > 0 {
		result = "mismatch"
		reasons = append(reasons, fmt.Sprintf("pin mismatch: EKI checkout has %d untracked or ignored Go build input file(s)", facts.BuildInputs))
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
		reasons = append(reasons, "pin unavailable: EKI source tree state could not be determined")
	}
	// Flags that redirect go.mod or overlay source files make the commit say
	// nothing about what is compiled.
	for _, flag := range []string{"-modfile", "-overlay"} {
		if strings.Contains(tool.GoFlags, flag) {
			if result == "match" {
				result = "unavailable"
			}
			reasons = append(reasons, fmt.Sprintf("pin unavailable: GOFLAGS contains %s, which can change what is compiled", flag))
		}
	}
	pin.Result = result
	return pin, reasons
}
