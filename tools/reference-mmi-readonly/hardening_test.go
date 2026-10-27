package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
	"time"
)

func mustRead(t *testing.T, path string) []byte {
	t.Helper()
	content, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	return content
}

// touchTrackedFiles advances the modification time of tracked files without
// changing their content. The index then holds stale stat data, which is what
// makes a plain `git diff` refresh (rewrite) .git/index.
func touchTrackedFiles(t *testing.T, repo fakeRepo) {
	t.Helper()
	future := time.Now().Add(2 * time.Hour)
	for _, relative := range []string{"README.md", filepath.Join("03_Implement", "package-lock.json"), filepath.Join("03_Implement", "src", "cli", "mcp.ts")} {
		if err := os.Chtimes(filepath.Join(repo.Root, relative), future, future); err != nil {
			t.Fatal(err)
		}
	}
}

// The MMI checkout is shared with other sessions. Reading it must not rewrite its
// .git/index (git diff does, even with --no-optional-locks) or leave files behind.
func TestGatherFactsLeavesTheCheckoutGitDirAlone(t *testing.T) {
	repo := newFakeMMI(t, false)
	index := filepath.Join(repo.Root, ".git", "index")
	touchTrackedFiles(t, repo)
	before := mustRead(t, index)
	scratch := t.TempDir()
	for _, name := range []string{"TMPDIR", "TMP", "TEMP"} {
		t.Setenv(name, scratch)
	}
	facts := gatherFacts(context.Background(), repo.Root, "v20.18.0")
	if facts.TreeStatus != "clean" || facts.Tracked != 0 {
		t.Fatalf("a file that was only touched is not a tracked change: %+v", facts)
	}
	if !bytes.Equal(before, mustRead(t, index)) {
		t.Fatal("gatherFacts rewrote the MMI checkout's .git/index")
	}
	if _, err := os.Stat(filepath.Join(repo.Root, ".git", "index.lock")); err == nil {
		t.Fatal("an index.lock was left in the MMI checkout")
	}
	if leftovers, _ := os.ReadDir(scratch); len(leftovers) != 0 {
		t.Fatalf("the temporary index copy was not removed: %v", leftovers)
	}

	useFakeMCP(t, fakeScenario{})
	receipt := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
	if !receipt.Passed {
		t.Fatalf("pinned run should pass on a touched but unchanged checkout: %+v", receipt)
	}
	if !bytes.Equal(before, mustRead(t, index)) {
		t.Fatal("a pinned run rewrote the MMI checkout's .git/index")
	}
}

// A refs/replace entry makes plain `git diff HEAD` compare against another tree
// than the recorded HEAD commit has, so an edit would not be seen.
func TestReplaceRefCannotHideATrackedEdit(t *testing.T) {
	repo := newFakeMMI(t, false)
	appendFile(t, filepath.Join(repo.Root, "README.md"), "edited\n")
	git(t, repo.Root, "add", "-A")
	git(t, repo.Root, "commit", "-q", "-m", "edited")
	edited := git(t, repo.Root, "rev-parse", "HEAD")
	git(t, repo.Root, "reset", "-q", "--hard", repo.Head)
	appendFile(t, filepath.Join(repo.Root, "README.md"), "edited\n")
	git(t, repo.Root, "replace", repo.Head, edited)
	if got := git(t, repo.Root, "diff", "--name-only", "HEAD"); got != "" {
		t.Fatalf("the fixture must hide the edit from a plain git diff, got %q", got)
	}
	if got := git(t, repo.Root, "--no-replace-objects", "diff", "--name-only", "HEAD"); got != "README.md" {
		t.Fatalf("the fixture's edit must be visible without the replace ref, got %q", got)
	}
	launches := useFakeMCP(t, fakeScenario{})
	receipt := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
	assertFailsClosed(t, receipt, "1 tracked change(s)")
	if receipt.Pin.SourceTree.Status != "tracked-changes" || *launches != 0 {
		t.Fatalf("pin: %+v launches=%d", receipt.Pin, *launches)
	}
}

// When git cannot tell whether the tree is clean, a pinned run fails instead of
// passing on a default.
func TestPinFailsClosedWhenTheTreeStateCannotBeRead(t *testing.T) {
	cases := map[string]func(t *testing.T, repo fakeRepo){
		"corrupt index": func(t *testing.T, repo fakeRepo) {
			if err := os.WriteFile(filepath.Join(repo.Root, ".git", "index"), []byte("not an index"), 0o644); err != nil {
				t.Fatal(err)
			}
		},
		"missing index": func(t *testing.T, repo fakeRepo) {
			if err := os.Remove(filepath.Join(repo.Root, ".git", "index")); err != nil {
				t.Fatal(err)
			}
		},
	}
	for name, damage := range cases {
		t.Run(name, func(t *testing.T) {
			repo := newFakeMMI(t, false)
			damage(t, repo)
			launches := useFakeMCP(t, fakeScenario{})
			receipt := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
			assertFailsClosed(t, receipt, "pin unavailable: MMI source tree state could not be determined")
			if receipt.Pin.Result != "unavailable" || receipt.Pin.SourceTree.Status != "unavailable" || *launches != 0 {
				t.Fatalf("pin: %+v launches=%d", receipt.Pin, *launches)
			}
			if receipt.Pin.Commit.Status != "match" {
				t.Fatalf("HEAD is still readable and must be recorded: %+v", receipt.Pin.Commit)
			}
		})
	}
}

// A git hook exports GIT_DIR, GIT_WORK_TREE and GIT_INDEX_FILE for its own repository.
func TestGitEnvironmentCannotRedirectTheQueries(t *testing.T) {
	repo := newFakeMMI(t, false)
	other := newFakeMMI(t, false)
	if err := os.WriteFile(filepath.Join(other.Root, "extra.txt"), []byte("x\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	git(t, other.Root, "add", "-A")
	git(t, other.Root, "commit", "-q", "-m", "another commit")
	otherHead := git(t, other.Root, "rev-parse", "HEAD")
	if otherHead == repo.Head {
		t.Fatal("the fixtures must differ")
	}
	t.Setenv("GIT_DIR", filepath.Join(other.Root, ".git"))
	t.Setenv("GIT_WORK_TREE", other.Root)
	t.Setenv("GIT_INDEX_FILE", filepath.Join(other.Root, ".git", "index"))
	facts := gatherFacts(context.Background(), repo.Root, "v20.18.0")
	if facts.Commit != repo.Head || facts.TreeStatus != "clean" {
		t.Fatalf("the inherited GIT_* variables redirected the query (got %q, want %q): %+v", facts.Commit, repo.Head, facts)
	}
}

// A version manager's shim picks the Node version by the working directory, so the
// version must be asked in the directory MMI is started in.
func TestNodeVersionIsProbedWhereMMIStarts(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("the shim is a POSIX shell script")
	}
	shim := t.TempDir()
	script := "#!/bin/sh\nif [ -f .node-version ]; then echo v22.23.2; else echo v18.0.0; fi\n"
	if err := os.WriteFile(filepath.Join(shim, "node"), []byte(script), 0o755); err != nil {
		t.Fatal(err)
	}
	t.Setenv("PATH", shim)
	root := t.TempDir()
	implement := filepath.Join(root, "03_Implement")
	if err := os.MkdirAll(implement, 0o755); err != nil {
		t.Fatal(err)
	}
	if got := defaultNodeVersionOf(context.Background(), root); got != "v18.0.0" {
		t.Fatalf("shim sanity (no .node-version in 03_Implement): %q", got)
	}
	if err := os.WriteFile(filepath.Join(implement, ".node-version"), []byte("22.23.2\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if got := defaultNodeVersionOf(context.Background(), root); got != "v22.23.2" {
		t.Fatalf("the version was not asked in 03_Implement, where MMI starts: %q", got)
	}
}

// filepath.WalkDir does not descend into a root that is a symlink, which made the
// whole-workspace digest see one entry and report "unchanged".
func TestSymlinkedWorkspaceIsStillDigested(t *testing.T) {
	real := newWorkspace(t)
	link := filepath.Join(t.TempDir(), "workspace-link")
	if err := os.Symlink(real, link); err != nil {
		t.Skipf("symlinks are not available: %v", err)
	}
	viaLink, linkEntries, err := digestTree(link)
	if err != nil {
		t.Fatal(err)
	}
	viaReal, realEntries, err := digestTree(real)
	if err != nil || viaLink != viaReal || linkEntries != realEntries || linkEntries < 3 {
		t.Fatalf("link: %s/%d real: %s/%d err: %v", viaLink, linkEntries, viaReal, realEntries, err)
	}
	useFakeMCP(t, fakeScenario{WriteOnSelect: "ledger.json"})
	receipt := Run(context.Background(), t.TempDir(), link)
	assertFailsClosed(t, receipt, "changed the workspace")
	if receipt.ReadOnly {
		t.Fatal("readOnly must be false after a write through a symlinked workspace")
	}
	if _, err := os.Stat(filepath.Join(real, "ledger.json")); err != nil {
		t.Fatalf("the fixture should have written into the real directory: %v", err)
	}
}

func TestWorkspaceDigestSeesRewrittenContentOfAnExistingFile(t *testing.T) {
	workspace := newWorkspace(t)
	if err := os.WriteFile(filepath.Join(workspace, "ledger.json"), []byte("0123456789\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	useFakeMCP(t, fakeScenario{OverwriteOnSelect: "ledger.json"})
	receipt := Run(context.Background(), t.TempDir(), workspace)
	assertFailsClosed(t, receipt, "changed the workspace")
	if receipt.ReadOnly || receipt.SourceDigestBefore != receipt.SourceDigestAfter || receipt.GuideDigestBefore != receipt.GuideDigestAfter {
		t.Fatalf("only the whole-workspace digest can see a same-size rewrite of another file: %+v", receipt)
	}
}

func TestDigestTreeSeesContentAndSymlinkTargets(t *testing.T) {
	dir := t.TempDir()
	file := filepath.Join(dir, "a.txt")
	if err := os.WriteFile(file, []byte("aaaa"), 0o600); err != nil {
		t.Fatal(err)
	}
	first, _, err := digestTree(dir)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(file, []byte("bbbb"), 0o600); err != nil {
		t.Fatal(err)
	}
	second, _, err := digestTree(dir)
	if err != nil || second == first {
		t.Fatalf("a same-size content rewrite must change the digest (err %v)", err)
	}
	t.Run("symlink target", func(t *testing.T) {
		link := filepath.Join(dir, "link")
		if err := os.Symlink("one", link); err != nil {
			t.Skipf("symlinks are not available: %v", err)
		}
		toOne, _, err := digestTree(dir)
		if err != nil {
			t.Fatal(err)
		}
		if err := os.Remove(link); err != nil {
			t.Fatal(err)
		}
		if err := os.Symlink("two", link); err != nil {
			t.Fatal(err)
		}
		toTwo, _, err := digestTree(dir)
		if err != nil || toTwo == toOne {
			t.Fatalf("re-pointing a symlink must change the digest (err %v)", err)
		}
	})
}

// A tools/list that cannot show the whole surface proves nothing about it.
func TestToolsListThatCannotProveAnythingFailsAPinnedRun(t *testing.T) {
	cases := map[string]fakeScenario{
		"another page follows (nextCursor)": {NextCursor: "page-2"},
		"empty list":                        {EmptyTools: true},
	}
	for name, scenario := range cases {
		t.Run(name, func(t *testing.T) {
			repo := newFakeMMI(t, false)
			useFakeMCP(t, scenario)
			unpinned := Run(context.Background(), repo.Root, newWorkspace(t))
			if !unpinned.Passed || unpinned.ToolSurface.Status != "unavailable" || len(unpinned.ToolSurface.Tools) != 0 {
				t.Fatalf("a record-only run records the surface as unavailable: %+v", unpinned.ToolSurface)
			}
			pinned := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
			assertFailsClosed(t, pinned, "status=unavailable")
		})
	}
}

func TestPinnedRunRejectsAnUnrecognisedMissingSourceReason(t *testing.T) {
	repo := newFakeMMI(t, false)
	useFakeMCP(t, fakeScenario{MissingText: "mmi: rejected for reasons"})
	unpinned := Run(context.Background(), repo.Root, newWorkspace(t))
	if !unpinned.Passed || unpinned.RejectionKind.Missing != "other" || !unpinned.MissingSourceRejected {
		t.Fatalf("unpinned: %+v", unpinned)
	}
	pinned := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
	assertFailsClosed(t, pinned, "missing source was rejected for an unrecognised reason")
}

// The fingerprint select returns is compared with the inspect candidate of the
// same sheet and range, not with whichever candidate comes first.
func TestFingerprintIsComparedWithTheCandidateOfTheSameTable(t *testing.T) {
	useFakeMCP(t, fakeScenario{ExtraCandidate: true})
	receipt := Run(context.Background(), t.TempDir(), newWorkspace(t))
	if !receipt.Passed || receipt.CandidateCount != 2 || receipt.Binding.FingerprintCrossCheck != "match" || receipt.Binding.SourceDigest != "match" {
		t.Fatalf("a second candidate for another range must not decide the cross-check: %+v", receipt)
	}
}

func configEnv(values map[string]string) func(string) string {
	return func(name string) string { return values[name] }
}

// The expectation flags and their environment variables are the only way to ask
// for a pinned run; a broken wiring would silently produce a record-only run.
func TestParseConfigWiresEveryExpectation(t *testing.T) {
	lower := strings.Repeat("a", 40)
	digest := "sha256:" + strings.Repeat("b", 64)
	cases := map[string]struct {
		args    []string
		env     map[string]string
		want    Options
		wantErr bool
	}{
		"nothing given is record-only": {},
		"flags": {
			args: []string{"-expect-commit", lower, "-expect-lock-digest", digest, "-expect-node-major", "22"},
			want: Options{ExpectCommit: lower, ExpectLockDigest: digest, ExpectNodeMajor: "22"},
		},
		"environment variables": {
			env:  map[string]string{"TAI_MMI_EXPECT_COMMIT": lower, "TAI_MMI_EXPECT_PACKAGE_LOCK_DIGEST": digest, "TAI_MMI_EXPECT_NODE_MAJOR": "22"},
			want: Options{ExpectCommit: lower, ExpectLockDigest: digest, ExpectNodeMajor: "22"},
		},
		"a flag wins over the environment": {
			args: []string{"-expect-commit", lower},
			env:  map[string]string{"TAI_MMI_EXPECT_COMMIT": strings.Repeat("c", 40), "TAI_MMI_EXPECT_NODE_MAJOR": "20"},
			want: Options{ExpectCommit: lower, ExpectNodeMajor: "20"},
		},
		"an explicitly empty flag means no expectation": {
			args: []string{"-expect-commit="},
			env:  map[string]string{"TAI_MMI_EXPECT_COMMIT": lower},
			want: Options{},
		},
		"upper-case commit and digest are lower-cased": {
			args: []string{"-expect-commit", strings.ToUpper(lower), "-expect-lock-digest", strings.ToUpper(digest)},
			want: Options{ExpectCommit: lower, ExpectLockDigest: "sha256:" + strings.Repeat("b", 64)},
		},
		"an unknown flag is an error": {args: []string{"-expect-comit", lower}, wantErr: true},
	}
	for name, test := range cases {
		t.Run(name, func(t *testing.T) {
			config, err := parseConfig(test.args, configEnv(test.env))
			if (err != nil) != test.wantErr {
				t.Fatalf("error = %v, wantErr %t", err, test.wantErr)
			}
			if err == nil && config.Options != test.want {
				t.Fatalf("options = %+v, want %+v", config.Options, test.want)
			}
		})
	}
	t.Run("paths", func(t *testing.T) {
		config, err := parseConfig(nil, configEnv(nil))
		if err != nil || config.Workspace != "testdata/workspace" || config.OutPath != "" || config.MMIRoot != filepath.Clean(filepath.Join("..", "..", "..", "markdown-matrix-injector")) {
			t.Fatalf("defaults: %+v %v", config, err)
		}
		config, _ = parseConfig(nil, configEnv(map[string]string{"MMI_ROOT": "/from/env"}))
		if config.MMIRoot != "/from/env" {
			t.Fatalf("MMI_ROOT: %+v", config)
		}
		config, _ = parseConfig([]string{"-mmi-root", "/from/flag", "-workspace", "ws", "-out", "receipt.json"}, configEnv(map[string]string{"MMI_ROOT": "/from/env"}))
		if config.MMIRoot != "/from/flag" || config.Workspace != "ws" || config.OutPath != "receipt.json" {
			t.Fatalf("flags: %+v", config)
		}
	})
}

// TestMainProcess runs main() inside a re-executed test binary. It does nothing
// in a normal test run.
func TestMainProcess(t *testing.T) {
	if os.Getenv("TAI_MAIN_PROCESS") != "1" {
		return
	}
	var args []string
	if err := json.Unmarshal([]byte(os.Getenv("TAI_MAIN_ARGS")), &args); err != nil {
		os.Exit(3)
	}
	os.Args = append([]string{"reference-mmi-readonly"}, args...)
	main()
}

// main() is the only entry users have, so run it for real: the expectation reaches
// RunWithOptions (flag or environment variable), a failed pin exits 1, and -out
// receives the same receipt as stdout. Each case fails at the pin, before any MMI
// code would start.
func TestMainTurnsExpectationsIntoAFailedPinnedRun(t *testing.T) {
	repo := newFakeMMI(t, false)
	zeros, ones := strings.Repeat("0", 40), strings.Repeat("1", 40)
	cases := map[string]struct {
		args     []string
		env      map[string]string
		result   string
		expected string // pin.commit.expected
	}{
		"flag":                  {[]string{"-expect-commit", zeros}, nil, "mismatch", zeros},
		"environment variable":  {nil, map[string]string{"TAI_MMI_EXPECT_COMMIT": zeros}, "mismatch", zeros},
		"flag over environment": {[]string{"-expect-commit", ones}, map[string]string{"TAI_MMI_EXPECT_COMMIT": zeros}, "mismatch", ones},
		"upper-case commit":     {[]string{"-expect-commit", strings.ToUpper(zeros[:39]) + "A"}, nil, "mismatch", zeros[:39] + "a"},
		"lock digest alone":     {nil, map[string]string{"TAI_MMI_EXPECT_PACKAGE_LOCK_DIGEST": "sha256:" + strings.Repeat("0", 64)}, "invalid-expectation", ""},
		"node major alone":      {nil, map[string]string{"TAI_MMI_EXPECT_NODE_MAJOR": "20"}, "invalid-expectation", ""},
	}
	for name, test := range cases {
		t.Run(name, func(t *testing.T) {
			outPath := filepath.Join(t.TempDir(), "receipt.json")
			args := append([]string{"-mmi-root", repo.Root, "-workspace", newWorkspace(t), "-out", outPath}, test.args...)
			rawArgs, _ := json.Marshal(args)
			cmd := exec.Command(os.Args[0], "-test.run=^TestMainProcess$")
			for _, entry := range os.Environ() {
				if !strings.HasPrefix(entry, "TAI_MMI_EXPECT_") && !strings.HasPrefix(entry, "MMI_ROOT=") {
					cmd.Env = append(cmd.Env, entry)
				}
			}
			cmd.Env = append(cmd.Env, "TAI_MAIN_PROCESS=1", "TAI_MAIN_ARGS="+string(rawArgs))
			for key, value := range test.env {
				cmd.Env = append(cmd.Env, key+"="+value)
			}
			var stdout bytes.Buffer
			cmd.Stdout = &stdout
			err := cmd.Run()
			var exitErr *exec.ExitError
			if !errors.As(err, &exitErr) || exitErr.ExitCode() != 1 {
				t.Fatalf("a failed pinned run must exit 1, got %v\n%s", err, stdout.String())
			}
			var receipt Receipt
			if err := json.Unmarshal(stdout.Bytes(), &receipt); err != nil {
				t.Fatalf("stdout is not a receipt: %v\n%s", err, stdout.String())
			}
			if receipt.Passed || !receipt.Pin.Checked || receipt.Pin.Result != test.result || receipt.Pin.Commit.Expected != test.expected {
				t.Fatalf("the expectation did not reach the run: %+v", receipt.Pin)
			}
			if !bytes.Equal(bytes.TrimSpace(mustRead(t, outPath)), bytes.TrimSpace(stdout.Bytes())) {
				t.Fatal("-out must hold the receipt that was printed")
			}
		})
	}
}
