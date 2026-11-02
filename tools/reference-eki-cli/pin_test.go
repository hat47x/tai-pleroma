package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func TestUnpinnedRunRecordsAndDoesNotCheckThePin(t *testing.T) {
	repo := newFakeEKI(t)
	receipt := Run(t.Context(), repo.Root)
	if !receipt.Passed || !receipt.ReadOnly || receipt.Reason != "" {
		t.Fatalf("unpinned run should pass against the honest fake: %+v", receipt)
	}
	if receipt.Schema != "tai.reference.eki-cli/v0" || receipt.EkiCommit != repo.Head || !strings.HasPrefix(receipt.GoVersion, "go version go") {
		t.Fatalf("existing fields: %+v", receipt)
	}
	if receipt.ControlVersion != "eki-control dev" || receipt.AgentVersion != "eki-agent dev" {
		t.Fatalf("version lines: %q %q", receipt.ControlVersion, receipt.AgentVersion)
	}
	if receipt.Pin.Checked || receipt.Pin.Result != "not-checked" || receipt.Pin.Commit.Status != "not-checked" || receipt.Pin.Commit.Actual != repo.Head {
		t.Fatalf("pin must be recorded but not checked: %+v", receipt.Pin)
	}
	if receipt.Pin.SourceTree.Status != "not-checked" || receipt.Checkout.Status != "unchanged" || receipt.Toolchain.Build != "built" {
		t.Fatalf("unpinned run: %+v %+v %+v", receipt.Pin.SourceTree, receipt.Checkout, receipt.Toolchain)
	}
	if len(receipt.Toolchain.Enforced) != 0 {
		t.Fatalf("an unpinned run must not constrain the go toolchain: %+v", receipt.Toolchain)
	}
	if !strings.HasPrefix(receipt.Binaries.ControlSha256, "sha256:") || len(receipt.Binaries.ControlSha256) != 71 || len(receipt.Binaries.AgentSha256) != 71 {
		t.Fatalf("binary digests: %+v", receipt.Binaries)
	}
	if receipt.Binaries.VersionAgreement != "agree" || receipt.Binaries.ReportedCommit.Status != "not-reported" {
		t.Fatalf("binaries: %+v", receipt.Binaries)
	}
	noted := false
	for _, note := range receipt.Notes[2:] {
		noted = noted || strings.Contains(note, "版固定の期待値が指定されていない")
	}
	if !noted {
		t.Fatalf("an unpinned receipt must say the pin was not checked: %v", receipt.Notes)
	}
}

func TestPinMatchPassesAndRecordsExpectations(t *testing.T) {
	repo := newFakeEKI(t)
	token := Run(t.Context(), repo.Root).Toolchain.GoVersionToken
	if token == "" {
		t.Fatal("go version token was not recorded")
	}
	receipt := run(t, repo.Root, Options{ExpectCommit: repo.Head, ExpectGoVersion: token})
	if !receipt.Passed || receipt.Pin.Result != "match" || receipt.Pin.SourceTree.Status != "clean" || !receipt.Pin.Checked {
		t.Fatalf("matching pin should pass: %+v", receipt)
	}
	if receipt.Pin.Commit.Status != "match" || receipt.Pin.GoVersion.Status != "match" || receipt.Checkout.Status != "unchanged" {
		t.Fatalf("every supplied expectation must be recorded as matched: %+v", receipt.Pin)
	}
	if strings.Join(receipt.Toolchain.Enforced, ",") != "GOTOOLCHAIN=local,GOWORK=off,GOFLAGS=-mod=readonly" {
		t.Fatalf("a pinned run constrains the go toolchain: %+v", receipt.Toolchain)
	}
	if strings.Join(receipt.Toolchain.BuildFlags, " ") != "-mod=readonly -buildvcs=false -trimpath" {
		t.Fatalf("build flags: %+v", receipt.Toolchain.BuildFlags)
	}
	if receipt.TaskDelegated || receipt.AuthorityVerified || !receipt.ReadOnly {
		t.Fatalf("a pin match must not claim more: %+v", receipt)
	}
	said := false
	for _, note := range receipt.Notes {
		said = said || strings.Contains(note, "EKIの正しさ") && strings.Contains(note, "dev")
	}
	if !said {
		t.Fatalf("notes must say a match is not proof of EKI correctness or of the version: %v", receipt.Notes)
	}
	commitOnly := run(t, repo.Root, Options{ExpectCommit: repo.Head})
	if !commitOnly.Passed || commitOnly.Pin.GoVersion.Status != "not-checked" {
		t.Fatalf("the commit alone is a valid pin: %+v", commitOnly.Pin)
	}
	same := run(t, repo.Root, Options{ExpectCommit: repo.Head})
	if same.Binaries.ControlSha256 != commitOnly.Binaries.ControlSha256 {
		t.Fatalf("two builds of the same checkout differ: %s %s", same.Binaries.ControlSha256, commitOnly.Binaries.ControlSha256)
	}
}

func TestPinMismatchFailsBeforeAnyEkiCodeRuns(t *testing.T) {
	other := strings.Repeat("0", 40)
	head := func(r fakeRepo) Options { return Options{ExpectCommit: r.Head} }
	cases := map[string]struct {
		options  func(r fakeRepo) Options
		prepare  func(t *testing.T, r fakeRepo)
		contains string
		result   string
	}{
		"commit mismatch": {func(fakeRepo) Options { return Options{ExpectCommit: other} }, nil,
			"pin mismatch: eki commit expected " + other, "mismatch"},
		"go version mismatch": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head, ExpectGoVersion: "go1.2.3"} }, nil,
			"pin mismatch: go version expected go1.2.3", "mismatch"},
		"dirty tracked file": {head,
			func(t *testing.T, r fakeRepo) { appendFile(t, filepath.Join(r.Root, "README.md"), "local edit\n") },
			"1 tracked change(s)", "mismatch"},
		"staged change": {head,
			func(t *testing.T, r fakeRepo) {
				appendFile(t, filepath.Join(r.Root, "README.md"), "staged edit\n")
				git(t, r.Root, "add", "README.md")
			}, "1 tracked change(s)", "mismatch"},
		"go.mod edited": {head,
			func(t *testing.T, r fakeRepo) { appendFile(t, filepath.Join(r.Root, "go.mod"), "// edited\n") },
			"1 tracked change(s)", "mismatch"},
		"tracked source edited": {head,
			func(t *testing.T, r fakeRepo) {
				appendFile(t, filepath.Join(r.Root, "internal", "core", "core.go"), "// edited\n")
			}, "1 tracked change(s)", "mismatch"},
		"tracked file deleted": {head,
			func(t *testing.T, r fakeRepo) {
				if err := os.Remove(filepath.Join(r.Root, "README.md")); err != nil {
					t.Fatal(err)
				}
			}, "1 tracked change(s)", "mismatch"},
		"edited file hidden by assume-unchanged": {head,
			func(t *testing.T, r fakeRepo) {
				appendFile(t, filepath.Join(r.Root, "README.md"), "hidden edit\n")
				git(t, r.Root, "update-index", "--assume-unchanged", "README.md")
			}, "assume-unchanged or skip-worktree", "unavailable"},
		"edited file hidden by skip-worktree": {head,
			func(t *testing.T, r fakeRepo) {
				appendFile(t, filepath.Join(r.Root, "README.md"), "hidden edit\n")
				git(t, r.Root, "update-index", "--skip-worktree", "README.md")
			}, "assume-unchanged or skip-worktree", "unavailable"},
		"untracked go file next to the command": {head,
			func(t *testing.T, r fakeRepo) {
				writeFiles(t, r.Root, map[string]string{"cmd/eki-control/extra.go": "package main\n\nfunc init() {}\n"})
			}, "1 untracked or ignored Go build input", "mismatch"},
		"untracked go file under internal": {head,
			func(t *testing.T, r fakeRepo) {
				writeFiles(t, r.Root, map[string]string{"internal/core/extra.go": "package core\n"})
			}, "1 untracked or ignored Go build input", "mismatch"},
		"untracked nested go.mod": {head,
			func(t *testing.T, r fakeRepo) {
				writeFiles(t, r.Root, map[string]string{"internal/core/go.mod": "module x\n"})
			},
			"1 untracked or ignored Go build input", "mismatch"},
		"untracked vendor file that is not a go file": {head,
			func(t *testing.T, r fakeRepo) {
				writeFiles(t, r.Root, map[string]string{"vendor/modules.txt": "# eki\n"})
			},
			"1 untracked or ignored Go build input", "mismatch"},
		"untracked go.work": {head,
			func(t *testing.T, r fakeRepo) {
				writeFiles(t, r.Root, map[string]string{"go.work": "go 1.21\n"})
			},
			"1 untracked or ignored Go build input", "mismatch"},
		"untracked go.work.sum": {head,
			func(t *testing.T, r fakeRepo) {
				writeFiles(t, r.Root, map[string]string{"go.work.sum": "\n"})
			},
			"1 untracked or ignored Go build input", "mismatch"},
		"ignored go file": {head,
			func(t *testing.T, r fakeRepo) {
				writeFiles(t, r.Root, map[string]string{".git/info/exclude": "*.go.local\nhidden.go\n", "cmd/eki-agent/hidden.go": "package main\n"})
			}, "1 untracked or ignored Go build input", "mismatch"},
		"short commit is an invalid expectation": {func(fakeRepo) Options { return Options{ExpectCommit: "559e789"} }, nil,
			"invalid pin expectation: expected commit", "invalid-expectation"},
		"63 hex digits is an invalid expectation": {func(fakeRepo) Options { return Options{ExpectCommit: strings.Repeat("a", 63)} }, nil,
			"invalid pin expectation: expected commit", "invalid-expectation"},
		"commit with a trailing space is invalid": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head + " "} }, nil,
			"invalid pin expectation: expected commit", "invalid-expectation"},
		"go version with os and arch is invalid": {func(r fakeRepo) Options {
			return Options{ExpectCommit: r.Head, ExpectGoVersion: "go1.26.9 linux/amd64"}
		}, nil, "invalid pin expectation: expected go version", "invalid-expectation"},
		"go version without the go prefix is invalid": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head, ExpectGoVersion: "1.26.9"} }, nil,
			"invalid pin expectation: expected go version", "invalid-expectation"},
		"go version alone does not pin a version": {func(fakeRepo) Options { return Options{ExpectGoVersion: "go1.26.9"} }, nil,
			"expected commit is required", "invalid-expectation"},
	}
	for name, test := range cases {
		t.Run(name, func(t *testing.T) {
			repo := newFakeEKI(t)
			if test.prepare != nil {
				test.prepare(t, repo)
			}
			marker := armMarker(t)
			receipt := run(t, repo.Root, test.options(repo))
			assertFailsClosed(t, receipt, test.contains)
			if receipt.Pin.Result != test.result || !receipt.Pin.Checked {
				t.Fatalf("pin result %q checked=%t, want %q checked: %+v", receipt.Pin.Result, receipt.Pin.Checked, test.result, receipt.Pin)
			}
			if wasStarted(marker) || receipt.Toolchain.Build != "not-run" || receipt.Binaries.ControlSha256 != "" {
				t.Fatalf("EKI code was built or executed although the pin did not hold: %+v", receipt)
			}
			assertNoLocalText(t, receipt, repo.Root)
		})
	}
}

func TestUntrackedNonBuildFilesDoNotFailThePin(t *testing.T) {
	repo := newFakeEKI(t)
	writeFiles(t, repo.Root, map[string]string{"NOTES.md": "x\n", "scratch.txt": "y\n"})
	receipt := run(t, repo.Root, Options{ExpectCommit: repo.Head})
	if !receipt.Passed || receipt.Pin.SourceTree.UntrackedFiles != 2 || receipt.Pin.SourceTree.UntrackedBuildInputs != 0 || receipt.Pin.SourceTree.Status != "clean" {
		t.Fatalf("untracked non-Go files are counted, not failed: %+v", receipt.Pin.SourceTree)
	}
}

func TestUnpinnedRunDoesNotFailOnADirtyOrDifferentCheckout(t *testing.T) {
	repo := newFakeEKI(t)
	appendFile(t, filepath.Join(repo.Root, "README.md"), "edit\n")
	writeFiles(t, repo.Root, map[string]string{"internal/core/extra.go": "package core\n"})
	receipt := Run(t.Context(), repo.Root)
	if !receipt.Passed || receipt.Pin.Checked || receipt.Pin.SourceTree.TrackedChanges != 1 || receipt.Pin.SourceTree.UntrackedBuildInputs != 1 {
		t.Fatalf("record only by default: %+v", receipt)
	}
}

func TestSubdirectoryOfAnotherRepoDoesNotBorrowItsCommit(t *testing.T) {
	repo := newFakeEKI(t)
	// A copy of the fake EKI placed below the repository: the outer HEAD is not its commit.
	sub := filepath.Join(repo.Root, "nested")
	writeFiles(t, sub, map[string]string{
		"cmd/eki-control/main.go": strings.Replace(strings.Replace(fakeCommandSource, "NAME", "eki-control", 1), "UPPER", "CONTROL", -1),
		"cmd/eki-agent/main.go":   strings.Replace(strings.Replace(fakeCommandSource, "NAME", "eki-agent", 1), "UPPER", "AGENT", -1),
		"go.mod":                  "module nested\n\ngo 1.21\n",
	})
	unpinned := Run(t.Context(), sub)
	if unpinned.EkiCommit != "" || unpinned.Pin.Commit.Status != "not-checked" {
		t.Fatalf("a subdirectory must not report the outer commit: %+v", unpinned)
	}
	pinned := run(t, sub, Options{ExpectCommit: repo.Head})
	assertFailsClosed(t, pinned, "pin unavailable: eki commit could not be determined")
	if pinned.Pin.Result != "unavailable" {
		t.Fatalf("pin: %+v", pinned.Pin)
	}
}

func TestIndexCopyKeepsTheOriginalMtime(t *testing.T) {
	// A same-size edit made in the second the index was written ("racily clean"):
	// git only sees it when the index copy carries the original index mtime.
	repo := newFakeEKI(t)
	readme := filepath.Join(repo.Root, "README.md")
	stamp := time.Now().Add(-time.Hour).Truncate(time.Second)
	must := func(err error) {
		t.Helper()
		if err != nil {
			t.Fatal(err)
		}
	}
	must(os.Chtimes(readme, stamp, stamp))
	git(t, repo.Root, "update-index", "--really-refresh")
	must(os.Chtimes(filepath.Join(repo.Root, ".git", "index"), stamp, stamp))
	file, err := os.OpenFile(readme, os.O_WRONLY, 0)
	must(err)
	_, err = file.WriteString("STUB\n")
	must(err)
	must(file.Close())
	must(os.Chtimes(readme, stamp, stamp))
	receipt := run(t, repo.Root, Options{ExpectCommit: repo.Head})
	assertFailsClosed(t, receipt, "1 tracked change(s)")
}

func TestGitEnvironmentCannotRedirectTheQueries(t *testing.T) {
	repo := newFakeEKI(t)
	appendFile(t, filepath.Join(repo.Root, "README.md"), "edit\n")
	other := newFakeEKI(t)
	t.Setenv("GIT_DIR", filepath.Join(other.Root, ".git"))
	t.Setenv("GIT_WORK_TREE", other.Root)
	t.Setenv("GIT_INDEX_FILE", filepath.Join(other.Root, ".git", "index"))
	receipt := run(t, repo.Root, Options{ExpectCommit: repo.Head})
	assertFailsClosed(t, receipt, "1 tracked change(s)")
	if receipt.EkiCommit != repo.Head {
		t.Fatalf("GIT_DIR must not choose the repository: %+v", receipt)
	}
}

func TestReplaceRefCannotHideATrackedEdit(t *testing.T) {
	repo := newFakeEKI(t)
	readme := filepath.Join(repo.Root, "README.md")
	appendFile(t, readme, "edit\n")
	git(t, repo.Root, "add", "README.md")
	git(t, repo.Root, "commit", "-q", "-m", "edited")
	edited := git(t, repo.Root, "rev-parse", "HEAD")
	git(t, repo.Root, "reset", "-q", "--hard", repo.Head)
	appendFile(t, readme, "edit\n") // the work tree now equals the edited commit's tree
	git(t, repo.Root, "replace", repo.Head, edited)
	receipt := run(t, repo.Root, Options{ExpectCommit: repo.Head})
	assertFailsClosed(t, receipt, "1 tracked change(s)")
}

func TestGatherFactsLeavesTheCheckoutGitDirAlone(t *testing.T) {
	repo := newFakeEKI(t)
	index := filepath.Join(repo.Root, ".git", "index")
	before, err := os.ReadFile(index)
	if err != nil {
		t.Fatal(err)
	}
	statBefore, _ := os.Stat(index)
	facts := gatherFacts(t.Context(), repo.Root)
	if facts.Commit != repo.Head || facts.TreeStatus != "clean" {
		t.Fatalf("facts: %+v", facts)
	}
	after, _ := os.ReadFile(index)
	statAfter, _ := os.Stat(index)
	if string(before) != string(after) || !statBefore.ModTime().Equal(statAfter.ModTime()) {
		t.Fatal("gatherFacts changed the real index")
	}
}

func TestGitUnavailableOrNotARepository(t *testing.T) {
	needTools(t)
	plain := t.TempDir()
	writeFiles(t, plain, map[string]string{"cmd/eki-control/main.go": "package main\n\nfunc main() {}\n"})
	unpinned := Run(t.Context(), plain)
	if unpinned.EkiCommit != "" || unpinned.Pin.Commit.Status != "not-checked" {
		t.Fatalf("a plain directory has no commit: %+v", unpinned.Pin)
	}
	pinned := run(t, plain, Options{ExpectCommit: strings.Repeat("a", 40)})
	if pinned.Passed || pinned.Pin.Result != "unavailable" {
		t.Fatalf("pinned run on a non-repository: %+v", pinned)
	}
}

// The commit can be read while the tracked state cannot (the index is unreadable): a
// pinned run must not treat "could not look" as "clean".
func TestUnreadableIndexFailsClosedWhileTheCommitIsKnown(t *testing.T) {
	repo := newFakeEKI(t)
	if err := os.WriteFile(filepath.Join(repo.Root, ".git", "index"), []byte("not an index"), 0o644); err != nil {
		t.Fatal(err)
	}
	marker := armMarker(t)
	receipt := run(t, repo.Root, Options{ExpectCommit: repo.Head})
	assertFailsClosed(t, receipt, "source tree state could not be determined")
	if receipt.Pin.Commit.Status != "match" || receipt.Pin.Result != "unavailable" || wasStarted(marker) {
		t.Fatalf("unreadable index: %+v", receipt.Pin)
	}
	if unpinned := Run(t.Context(), repo.Root); unpinned.Pin.Checked {
		t.Fatalf("an unpinned run only records: %+v", unpinned.Pin)
	}
}
