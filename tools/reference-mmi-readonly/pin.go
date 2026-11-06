package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
)

const (
	defaultTable        = "Sheet1!A1:E4"
	defaultExpectedRows = 3
)

// Options carries opt-in expectations. The zero value of the Expect* fields means "record only"; Table and
// ExpectedRows only choose the selected range.
// Any non-empty field turns the run into a pinned run, and a pinned run needs
// ExpectCommit: package-lock.json is byte-identical across many MMI commits and
// the Node major says nothing about the checkout, so neither can stand in for it.
type Options struct {
	Table            string // MMI table range to select; empty means defaultTable
	ExpectedRows     int    // expected selected row count (with Table)
	ExpectCommit     string // 40-hex (or 64-hex) git object id of the MMI checkout HEAD
	ExpectLockDigest string // sha256:<64 hex> of package-lock.json after CRLF->LF normalisation
	ExpectNodeMajor  string // decimal major of `node --version`
}

func (o Options) specified() bool {
	return o.ExpectCommit != "" || o.ExpectLockDigest != "" || o.ExpectNodeMajor != ""
}

type PinItem struct {
	Status   string `json:"status"` // not-checked | match | mismatch | unavailable
	Expected string `json:"expected,omitempty"`
	Actual   string `json:"actual,omitempty"`
}

// SourceTree describes tracked file content only. "clean" says nothing about
// untracked files, ignored files (node_modules) or anything outside the checkout.
type SourceTree struct {
	Status             string `json:"status"` // not-checked | clean | tracked-changes | unavailable
	TrackedChanges     int    `json:"trackedChanges"`
	UntrackedFiles     int    `json:"untrackedFiles"`
	HiddenFlaggedFiles int    `json:"hiddenFlaggedFiles"` // tracked files marked assume-unchanged or skip-worktree
}

type PinCheck struct {
	Checked     bool       `json:"checked"`
	Result      string     `json:"result"` // not-checked | match | mismatch | unavailable | invalid-expectation
	Commit      PinItem    `json:"commit"`
	PackageLock PinItem    `json:"packageLock"`
	NodeMajor   PinItem    `json:"nodeMajor"`
	SourceTree  SourceTree `json:"sourceTree"`
}

var (
	commitPattern = regexp.MustCompile(`^(?:[0-9a-f]{40}|[0-9a-f]{64})$`)
	digestPattern = regexp.MustCompile(`^sha256:[0-9a-f]{64}$`)
	majorPattern  = regexp.MustCompile(`^[0-9]{1,3}$`)
	nodePattern   = regexp.MustCompile(`^v([0-9]+)\.`)
)

func digestBytes(content []byte) string {
	sum := sha256.Sum256(content)
	return "sha256:" + hex.EncodeToString(sum[:])
}

// digestFileLF hashes a file after CRLF->LF normalisation. package-lock.json is
// LF in git, but a Windows checkout with core.autocrlf=true holds CRLF, so the
// raw digest is platform dependent while this one equals the committed blob.
func digestFileLF(path string) (string, error) {
	content, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	return digestBytes(bytes.ReplaceAll(content, []byte("\r\n"), []byte("\n"))), nil
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
// this copy (GIT_INDEX_FILE) and the shared MMI checkout's .git stays untouched.
// The copy keeps the original's modification time.
func copyIndex(ctx context.Context, mmiRoot string) (string, func(), error) {
	out, err := gitCommand(ctx, mmiRoot, "rev-parse", "--git-path", "index").Output()
	if err != nil {
		return "", nil, err
	}
	source := strings.TrimSpace(string(out))
	if !filepath.IsAbs(source) {
		source = filepath.Join(mmiRoot, source)
	}
	info, err := os.Stat(source)
	if err != nil {
		return "", nil, err
	}
	content, err := os.ReadFile(source)
	if err != nil {
		return "", nil, err
	}
	dir, err := os.MkdirTemp("", "tai-mmi-index-")
	if err != nil {
		return "", nil, err
	}
	cleanup := func() { _ = os.RemoveAll(dir) }
	copyPath := filepath.Join(dir, "index")
	if err := os.WriteFile(copyPath, content, 0o600); err != nil {
		cleanup()
		return "", nil, err
	}
	// git treats an entry whose mtime is not older than the index file's mtime as
	// possibly stale and compares its content (racy-git protection). The copy must
	// carry the original's mtime, or a same-size edit made in the second the index was
	// written would look unchanged. If the mtime cannot be set the state is unknown.
	if err := os.Chtimes(copyPath, info.ModTime(), info.ModTime()); err != nil {
		cleanup()
		return "", nil, err
	}
	return copyPath, cleanup, nil
}

type mmiFacts struct {
	Commit     string
	LockLF     string
	NodeMajor  string
	TreeStatus string // clean | tracked-changes | unavailable
	Tracked    int
	Untracked  int
	Hidden     int // tracked files git is told not to look at
}

// gatherFacts does not modify the MMI checkout: git rev-parse, a copy of the
// index for diff/ls-files, and a file read.
func gatherFacts(ctx context.Context, mmiRoot, nodeVersion string) mmiFacts {
	facts := mmiFacts{TreeStatus: "unavailable"}
	if match := nodePattern.FindStringSubmatch(nodeVersion); match != nil {
		facts.NodeMajor = match[1]
	}
	if lock, err := digestFileLF(filepath.Join(mmiRoot, "03_Implement", "package-lock.json")); err == nil {
		facts.LockLF = lock
	}
	// `git rev-parse HEAD` inside a plain subdirectory of another repository would
	// report that outer repository's commit. Require mmiRoot to be the top level.
	top, err := gitCommand(ctx, mmiRoot, "--no-optional-locks", "rev-parse", "--show-toplevel").Output()
	if err != nil {
		return facts
	}
	topInfo, topErr := os.Stat(strings.TrimSpace(string(top)))
	rootInfo, rootErr := os.Stat(mmiRoot)
	if topErr != nil || rootErr != nil || !os.SameFile(topInfo, rootInfo) {
		return facts
	}
	head, err := gitCommand(ctx, mmiRoot, "rev-parse", "HEAD").Output()
	if err != nil {
		return facts
	}
	facts.Commit = strings.TrimSpace(string(head))
	indexCopy, cleanup, err := copyIndex(ctx, mmiRoot)
	if err != nil {
		return facts
	}
	defer cleanup()
	onCopy := func(args ...string) *exec.Cmd {
		cmd := gitCommand(ctx, mmiRoot, append([]string{"--no-optional-locks"}, args...)...)
		cmd.Env = append(cmd.Env, "GIT_INDEX_FILE="+indexCopy)
		return cmd
	}
	// Tracked changes are judged by content (`diff HEAD` covers staged, unstaged and
	// deleted files). `git status` reports a CRLF working copy of an LF blob as
	// modified when the index stat was taken before the rewrite, and `diff` refreshes
	// the index it reads, hence the copy.
	changed, err := onCopy("diff", "--name-only", "-z", "HEAD", "--").Output()
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
	facts.Tracked = countNUL(changed)
	facts.Untracked = countNUL(untracked)
	facts.Hidden = countHiddenFlags(flagged)
	switch {
	case facts.Tracked > 0:
		facts.TreeStatus = "tracked-changes"
	case facts.Hidden > 0:
		facts.TreeStatus = "unavailable"
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
func evaluatePin(options Options, facts mmiFacts) (PinCheck, []string) {
	pin := PinCheck{
		Result:      "not-checked",
		Commit:      pinItem("", facts.Commit),
		PackageLock: pinItem("", facts.LockLF),
		NodeMajor:   pinItem("", facts.NodeMajor),
		SourceTree:  SourceTree{Status: "not-checked", TrackedChanges: facts.Tracked, UntrackedFiles: facts.Untracked, HiddenFlaggedFiles: facts.Hidden},
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
		{"expected package-lock digest", options.ExpectLockDigest, digestPattern},
		{"expected node major", options.ExpectNodeMajor, majorPattern},
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
	pin.PackageLock = pinItem(options.ExpectLockDigest, facts.LockLF)
	pin.NodeMajor = pinItem(options.ExpectNodeMajor, facts.NodeMajor)
	pin.SourceTree.Status = facts.TreeStatus
	result := "match"
	for _, item := range []struct {
		name string
		item PinItem
	}{{"mmi commit", pin.Commit}, {"package-lock digest", pin.PackageLock}, {"node major", pin.NodeMajor}} {
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
		reasons = append(reasons, fmt.Sprintf("pin mismatch: MMI source tree has %d tracked change(s)", facts.Tracked))
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
		reasons = append(reasons, "pin unavailable: MMI source tree state could not be determined")
	}
	pin.Result = result
	return pin, reasons
}

// WorkspaceTree is a content digest of every entry below the MMI workspace.
type WorkspaceTree struct {
	DigestBefore string `json:"digestBefore"`
	DigestAfter  string `json:"digestAfter"`
	Entries      int    `json:"entries"`
}

// digestTree hashes entry kind, relative path, size and content in lexical
// order. A symlink below the root is not followed (its target is hashed), but a
// root that is itself a symlink is resolved first: WalkDir would otherwise stop
// at the link and see one entry. Modification times are ignored on purpose.
func digestTree(root string) (string, int, error) {
	resolved, err := filepath.EvalSymlinks(root)
	if err != nil {
		return "", 0, err
	}
	root = resolved
	hash := sha256.New()
	entries := 0
	err = filepath.WalkDir(root, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		relative, err := filepath.Rel(root, path)
		if err != nil {
			return err
		}
		relative = filepath.ToSlash(relative)
		entries++
		switch {
		case entry.IsDir():
			fmt.Fprintf(hash, "d\x00%s\n", relative)
		case entry.Type()&fs.ModeSymlink != 0:
			target, err := os.Readlink(path)
			if err != nil {
				return err
			}
			fmt.Fprintf(hash, "l\x00%s\x00%s\n", relative, target)
		case entry.Type().IsRegular():
			content, err := os.ReadFile(path)
			if err != nil {
				return err
			}
			fmt.Fprintf(hash, "f\x00%s\x00%d\x00%s\n", relative, len(content), digestBytes(content))
		default:
			fmt.Fprintf(hash, "o\x00%s\n", relative)
		}
		return nil
	})
	if err != nil {
		return "", 0, err
	}
	return "sha256:" + hex.EncodeToString(hash.Sum(nil)), entries, nil
}
