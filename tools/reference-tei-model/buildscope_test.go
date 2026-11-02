package main

import (
	"context"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

// These tests cover what a pinned run says is compiled: tracked content read through
// a copy of the index that keeps git's "racy" protection, no untracked or ignored
// Go build input, and a go command environment that the caller cannot steer.

func writeFile(t *testing.T, path, content string) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
}

// commitIgnoreRules commits a .gitignore so that ignored paths exist in the fixture.
func commitIgnoreRules(t *testing.T, repo *fakeRepo, rules string) {
	t.Helper()
	writeFile(t, filepath.Join(repo.Root, ".gitignore"), rules)
	git(t, repo.Root, "add", ".gitignore")
	git(t, repo.Root, "commit", "-q", "-m", "ignore rules")
	repo.Head = git(t, repo.Root, "rev-parse", "HEAD")
}

// git compares an index entry with the file by stat data (seconds, size, inode) and,
// when the entry is not older than the index file itself, by content ("racily
// clean"). A same-size edit made in the second the index was written is therefore
// found only if the index that git reads carries the original index file's
// modification time. A copy made with a fresh modification time loses that and
// reports the edit as clean, which let a pinned run pass on an edited checkout.
func TestRacyEditInTheSecondOfTheIndexWriteIsSeen(t *testing.T) {
	repo := newFakeTEI(t)
	// ctime cannot be set from a test. With the default, the edit below would change
	// ctime and git would read the content for that reason, which hides the racy case.
	git(t, repo.Root, "config", "core.trustctime", "false")
	readme := filepath.Join(repo.Root, "README.md")
	index := filepath.Join(repo.Root, ".git", "index")
	moment := time.Now().Add(-48 * time.Hour).Truncate(time.Second)
	if err := os.Chtimes(readme, moment, moment); err != nil {
		t.Fatal(err)
	}
	git(t, repo.Root, "update-index", "--refresh")
	if got := git(t, repo.Root, "ls-files", "--debug", "README.md"); !strings.Contains(got, fmt.Sprintf("mtime: %d:", moment.Unix())) {
		t.Fatalf("fixture: the index entry does not carry the file's modification time: %q", got)
	}
	if err := os.Chtimes(index, moment, moment); err != nil {
		t.Fatal(err)
	}
	// Same size ("stub\n" -> "STUB\n"), same inode, same modification time.
	if err := os.WriteFile(readme, []byte("STUB\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.Chtimes(readme, moment, moment); err != nil {
		t.Fatal(err)
	}
	// Check the fixture on copies, never on the real index (git rewrites what it reads,
	// which would smudge the racy entry): the edit is visible through a copy that keeps
	// the index file's modification time, and invisible through one that does not.
	realIndex := mustRead(t, index)
	diffNames := func(keepMtime bool) string {
		copyPath := filepath.Join(t.TempDir(), "index")
		if err := os.WriteFile(copyPath, realIndex, 0o600); err != nil {
			t.Fatal(err)
		}
		if keepMtime {
			if err := os.Chtimes(copyPath, moment, moment); err != nil {
				t.Fatal(err)
			}
		}
		cmd := exec.Command("git", "--no-optional-locks", "diff", "--name-only", "HEAD", "--")
		cmd.Dir = repo.Root
		cmd.Env = append(gitEnv(), "GIT_INDEX_FILE="+copyPath)
		out, err := cmd.Output()
		if err != nil {
			t.Fatal(err)
		}
		return strings.TrimSpace(string(out))
	}
	if got := diffNames(true); got != "README.md" {
		t.Fatalf("fixture: git must see the racy edit through an index that keeps its modification time, got %q", got)
	}
	if got := diffNames(false); got != "" {
		t.Skipf("this git already reads the content of a racily clean entry (diff saw %q): nothing to test", got)
	}

	facts := gatherFacts(context.Background(), repo.Root)
	if facts.Tracked != 1 || facts.TreeStatus != "tracked-changes" {
		t.Fatalf("a same-size edit in the second of the index write was not seen: %+v", facts)
	}
	launches := useFakeTEI(t, fakeTEIScenario{})
	receipt := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
	assertFailsClosed(t, receipt, "1 tracked change(s)")
	if receipt.Pin.Result != "mismatch" || *launches != 0 {
		t.Fatalf("pin=%+v launches=%d", receipt.Pin, *launches)
	}
}

// Files the Go toolchain compiles or that change what it compiles: an untracked or
// ignored one is a different program than the pinned commit, but it is neither a
// tracked change nor a different HEAD.
func TestPinnedRunRefusesUntrackedOrIgnoredGoBuildInputs(t *testing.T) {
	cases := map[string]struct {
		path    string
		ignored bool
	}{
		"an untracked go file next to main":       {filepath.Join("cmd", "tei", "zz_extra.go"), false},
		"an untracked go file in another package": {filepath.Join("internal", "x", "x.go"), false},
		"an untracked test file":                  {filepath.Join("cmd", "tei", "zz_extra_test.go"), false},
		"an untracked assembly file":              {filepath.Join("cmd", "tei", "zz.s"), false},
		"an untracked upper-case assembly file":   {filepath.Join("cmd", "tei", "zz.S"), false},
		"an untracked C file":                     {filepath.Join("cmd", "tei", "zz.c"), false},
		"an untracked C header":                   {filepath.Join("cmd", "tei", "zz.h"), false},
		"an untracked syso object":                {filepath.Join("cmd", "tei", "zz.syso"), false},
		"an untracked nested go.mod":              {filepath.Join("internal", "nested", "go.mod"), false},
		"an untracked nested go.sum":              {filepath.Join("internal", "nested", "go.sum"), false},
		"an untracked go.work":                    {"go.work", false},
		"an untracked go.work.sum":                {"go.work.sum", false},
		"an untracked vendor directory":           {filepath.Join("vendor", "modules.txt"), false},
		"an ignored go file":                      {filepath.Join("ignored", "x.go"), true},
		"an ignored generated go file":            {filepath.Join("cmd", "tei", "x.gen.go"), true},
		"an ignored go.mod":                       {filepath.Join("ignored", "go.mod"), true},
	}
	for name, test := range cases {
		t.Run(name, func(t *testing.T) {
			repo := newFakeTEI(t)
			commitIgnoreRules(t, &repo, "ignored/\n*.gen.go\n")
			writeFile(t, filepath.Join(repo.Root, test.path), "package x\n")
			launches := useFakeTEI(t, fakeTEIScenario{})
			receipt := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
			assertFailsClosed(t, receipt, "pin mismatch: TEI checkout has 1 untracked or ignored Go build input file(s)")
			if !receipt.Pin.Checked || receipt.Pin.Result != "mismatch" || receipt.Pin.SourceTree.UntrackedBuildInputs != 1 || receipt.Pin.SourceTree.Status != "untracked-build-inputs" {
				t.Fatalf("pin: %+v", receipt.Pin)
			}
			if receipt.Pin.Commit.Status != "match" || receipt.Pin.SourceTree.TrackedChanges != 0 {
				t.Fatalf("the commit and the tracked files are fine; the build input is what fails: %+v", receipt.Pin)
			}
			if *launches != 0 || receipt.Validation != "" {
				t.Fatal("TEI code was executed although a build input is not in the pinned commit")
			}
			// The default run keeps passing and records the count.
			unpinned := Run(context.Background(), repo.Root, newWorkspace(t))
			if !unpinned.Passed || unpinned.Pin.Checked || unpinned.Pin.SourceTree.UntrackedBuildInputs != 1 || unpinned.Checkout.Before.UntrackedBuildInputs != 1 || unpinned.Checkout.Status != "unchanged" {
				t.Fatalf("a record-only run records the build input and passes: %+v", unpinned)
			}
		})
	}
}

// Everything else untracked stays what it was: counted, not rejected.
func TestUntrackedFilesThatAreNotBuildInputsStayCountedOnly(t *testing.T) {
	repo := newFakeTEI(t)
	for _, name := range []string{"notes.txt", filepath.Join("docs", "new.md"), filepath.Join("data", "x.json"), filepath.Join("testdata", "blob.bin"), "Makefile", "goreleaser.yaml"} {
		writeFile(t, filepath.Join(repo.Root, name), "x\n")
	}
	useFakeTEI(t, fakeTEIScenario{})
	receipt := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
	if !receipt.Passed || receipt.Pin.SourceTree.UntrackedFiles != 6 || receipt.Pin.SourceTree.UntrackedBuildInputs != 0 || receipt.Pin.SourceTree.Status != "clean" {
		t.Fatalf("%+v", receipt.Pin)
	}
}

// An ignored build input that appears while TEI runs is a write, though git status
// never lists it.
func TestAnIgnoredBuildInputCreatedByTEIIsAWrite(t *testing.T) {
	repo := newFakeTEI(t)
	commitIgnoreRules(t, &repo, "ignored/\n")
	if err := os.MkdirAll(filepath.Join(repo.Root, "ignored"), 0o755); err != nil {
		t.Fatal(err)
	}
	useFakeTEI(t, fakeTEIScenario{WriteUntracked: filepath.Join("ignored", "generated.go")})
	receipt := Run(context.Background(), repo.Root, newWorkspace(t))
	assertFailsClosed(t, receipt, "untracked build inputs 0->1")
	if receipt.ReadOnly || receipt.Checkout.Status != "changed" {
		t.Fatalf("readOnly=%t checkout=%+v", receipt.ReadOnly, receipt.Checkout)
	}
}

func lastEnvValue(env []string, name string) (string, bool) {
	value, found := "", false
	for _, entry := range env {
		if key, v, ok := strings.Cut(entry, "="); ok && key == name {
			value, found = v, true
		}
	}
	return value, found
}

// A pinned run replaces the caller's GOFLAGS (and, because an empty value does not
// replace what a go env file sets, with a non-empty one). Flags such as -tags or
// -ldflags change the program that is built without changing any file of the
// checkout.
func TestPinnedGoEnvironmentReplacesInheritedGoFlags(t *testing.T) {
	t.Setenv("GOFLAGS", "-tags=taitag -ldflags=-X=main.v=1")
	env, enforced := goChildEnv(true)
	if got, _ := lastEnvValue(env, "GOFLAGS"); got != "-mod=readonly" {
		t.Fatalf("a pinned run must not build with the inherited GOFLAGS, got %q", got)
	}
	if strings.Join(enforced, ",") != "GOTOOLCHAIN=local,GOWORK=off,GOFLAGS=-mod=readonly" {
		t.Fatalf("enforced: %v", enforced)
	}
	env, enforced = goChildEnv(false)
	if got, _ := lastEnvValue(env, "GOFLAGS"); got != "-tags=taitag -ldflags=-X=main.v=1" || len(enforced) != 0 {
		t.Fatalf("a record-only run inherits the environment unchanged: %q %v", got, enforced)
	}
}

// tagSensitiveTEI is a tiny real TEI whose output depends on a build tag.
func newTagSensitiveTEI(t *testing.T) fakeRepo {
	t.Helper()
	if _, err := exec.LookPath("go"); err != nil {
		t.Skip("go is not available")
	}
	repo := newTinyTEI(t, `if variant != "" { fmt.Println("ok" + variant); return }`)
	writeFile(t, filepath.Join(repo.Root, "cmd", "tei", "variant_default.go"), "//go:build !taitag\n\npackage main\n\nconst variant = \"\"\n")
	writeFile(t, filepath.Join(repo.Root, "cmd", "tei", "variant_tag.go"), "//go:build taitag\n\npackage main\n\nconst variant = \"x\"\n")
	git(t, repo.Root, "add", "-A")
	git(t, repo.Root, "commit", "-q", "-m", "tag sensitive tei")
	repo.Head = git(t, repo.Root, "rev-parse", "HEAD")
	return repo
}

func TestPinnedRunIgnoresInheritedGoFlagsThatChangeTheBuild(t *testing.T) {
	sources := map[string]func(t *testing.T){
		"environment variable": func(t *testing.T) { t.Setenv("GOFLAGS", "-tags=taitag") },
		// An empty GOFLAGS in the environment does not override this file, so the
		// replacement has to be a non-empty value.
		"go env file": func(t *testing.T) {
			file := filepath.Join(t.TempDir(), "env")
			writeFile(t, file, "GOFLAGS=-tags=taitag\n")
			t.Setenv("GOENV", file)
			t.Setenv("GOFLAGS", "")
			_ = os.Unsetenv("GOFLAGS")
		},
	}
	for name, inherit := range sources {
		t.Run(name, func(t *testing.T) {
			repo := newTagSensitiveTEI(t)
			inherit(t)
			pinned := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
			if !pinned.Passed || pinned.Validation != "ok" {
				t.Fatalf("the pinned run must build the pinned commit without the inherited -tags: %+v", pinned)
			}
			if pinned.Toolchain.GoFlags != "-tags=taitag" || !strings.Contains(strings.Join(pinned.Toolchain.Enforced, ","), "GOFLAGS=-mod=readonly") {
				t.Fatalf("the inherited value is recorded and the replacement is listed: %+v", pinned.Toolchain)
			}
			if name != "environment variable" {
				return // the control below is slow (a second real build); once is enough
			}
			// Without a pin the caller's environment is kept, so the tag is built in: the
			// flag really changes the program, which is what the pinned run must not allow.
			unpinned := Run(context.Background(), repo.Root, newWorkspace(t))
			assertFailsClosed(t, unpinned, "TEI validate did not report ok: okx")
		})
	}
}

// A real build, not a fake: an untracked Go file in cmd/tei is compiled into the
// binary, so the pinned run must stop before building and nothing may run.
func TestPinnedRunNeverBuildsAnUntrackedGoFile(t *testing.T) {
	repo := newTinyTEI(t, "")
	writeFile(t, filepath.Join(repo.Root, "cmd", "tei", "zz_extra.go"),
		"package main\n\nimport \"os\"\n\nfunc init() { _ = os.WriteFile(\"marker.txt\", []byte(\"ran\"), 0o644) }\n")
	pinned := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
	assertFailsClosed(t, pinned, "untracked or ignored Go build input")
	if _, err := os.Stat(filepath.Join(repo.Root, "marker.txt")); err == nil {
		t.Fatal("the untracked Go file was compiled and run by a pinned run")
	}
	if pinned.Toolchain.Build != "not-run" || pinned.Validation != "" {
		t.Fatalf("a pinned run must stop before building: %+v", pinned)
	}
	// The record-only run does build it, and the checkout comparison sees the write.
	unpinned := Run(context.Background(), repo.Root, newWorkspace(t))
	assertFailsClosed(t, unpinned, "untracked files 1->2")
	if unpinned.ReadOnly {
		t.Fatalf("%+v", unpinned.Checkout)
	}
}

func TestReceiptNotesSayWhatTheConnectionRuns(t *testing.T) {
	repo := newFakeTEI(t)
	useFakeTEI(t, fakeTEIScenario{})
	receipt := Run(context.Background(), repo.Root, newWorkspace(t))
	notes := strings.Join(receipt.Notes, "\n")
	if strings.Contains(notes, "validateだけを実行") || !strings.Contains(notes, "validate（テキストと-json）とmodel catalogだけを実行する読み取り専用接続") {
		t.Fatalf("the receipt must not understate what is run: %v", receipt.Notes)
	}
}
