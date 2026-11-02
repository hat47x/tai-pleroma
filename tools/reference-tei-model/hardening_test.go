package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"os"
	"os/exec"
	"path/filepath"
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
	for _, relative := range []string{"README.md", "go.mod", filepath.Join("cmd", "tei", "main.go")} {
		if err := os.Chtimes(filepath.Join(repo.Root, relative), future, future); err != nil {
			t.Fatal(err)
		}
	}
}

// The TEI checkout is shared with other sessions. Reading it must not rewrite its
// .git/index (git diff does, even with --no-optional-locks) or leave files behind.
func TestGatherFactsLeavesTheCheckoutGitDirAlone(t *testing.T) {
	repo := newFakeTEI(t)
	index := filepath.Join(repo.Root, ".git", "index")
	touchTrackedFiles(t, repo)
	before := mustRead(t, index)
	scratch := t.TempDir()
	for _, name := range []string{"TMPDIR", "TMP", "TEMP"} {
		t.Setenv(name, scratch)
	}
	facts := gatherFacts(context.Background(), repo.Root)
	if facts.TreeStatus != "clean" || facts.Tracked != 0 {
		t.Fatalf("a file that was only touched is not a tracked change: %+v", facts)
	}
	if !bytes.Equal(before, mustRead(t, index)) {
		t.Fatal("gatherFacts rewrote the TEI checkout's .git/index")
	}
	if _, err := os.Stat(filepath.Join(repo.Root, ".git", "index.lock")); err == nil {
		t.Fatal("an index.lock was left in the TEI checkout")
	}
	if leftovers, _ := os.ReadDir(scratch); len(leftovers) != 0 {
		t.Fatalf("the temporary index copy was not removed: %v", leftovers)
	}

	useFakeTEI(t, fakeTEIScenario{})
	receipt := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
	if !receipt.Passed {
		t.Fatalf("pinned run should pass on a touched but unchanged checkout: %+v", receipt)
	}
	if !bytes.Equal(before, mustRead(t, index)) {
		t.Fatal("a pinned run rewrote the TEI checkout's .git/index")
	}
}

// A refs/replace entry makes plain `git diff HEAD` compare against another tree
// than the recorded HEAD commit has, so an edit would not be seen.
func TestReplaceRefCannotHideATrackedEdit(t *testing.T) {
	repo := newFakeTEI(t)
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
	launches := useFakeTEI(t, fakeTEIScenario{})
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
			repo := newFakeTEI(t)
			damage(t, repo)
			launches := useFakeTEI(t, fakeTEIScenario{})
			receipt := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
			assertFailsClosed(t, receipt, "pin unavailable: TEI source tree state could not be determined")
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
	repo := newFakeTEI(t)
	other := newFakeTEI(t)
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
	facts := gatherFacts(context.Background(), repo.Root)
	if facts.Commit != repo.Head || facts.TreeStatus != "clean" {
		t.Fatalf("the inherited GIT_* variables redirected the query (got %q, want %q): %+v", facts.Commit, repo.Head, facts)
	}
}

// filepath.WalkDir does not descend into a root that is a symlink, which made a
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
}

func TestDigestTreeSeesContentAndEmptyDirectories(t *testing.T) {
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
	legacyBefore, err := digestWorkspace(dir)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.Mkdir(filepath.Join(dir, "empty"), 0o755); err != nil {
		t.Fatal(err)
	}
	legacyAfter, err := digestWorkspace(dir)
	third, _, _ := digestTree(dir)
	if err != nil || legacyAfter != legacyBefore || third == second {
		t.Fatal("the legacy workspaceDigest ignores empty directories (kept as is); the tree digest sees them")
	}
}

func configEnv(values map[string]string) func(string) string {
	return func(name string) string { return values[name] }
}

// The expectation flags and their environment variables are the only way to ask
// for a pinned run; a broken wiring would silently produce a record-only run.
func TestParseConfigWiresEveryExpectation(t *testing.T) {
	lower := strings.Repeat("a", 40)
	cases := map[string]struct {
		args    []string
		env     map[string]string
		want    Options
		wantErr bool
	}{
		"nothing given is record-only": {},
		"flags": {
			args: []string{"-expect-commit", lower, "-expect-go-version", "go1.26.9"},
			want: Options{ExpectCommit: lower, ExpectGoVersion: "go1.26.9"},
		},
		"environment variables": {
			env:  map[string]string{"TAI_TEI_EXPECT_COMMIT": lower, "TAI_TEI_EXPECT_GO_VERSION": "go1.26.9"},
			want: Options{ExpectCommit: lower, ExpectGoVersion: "go1.26.9"},
		},
		"a flag wins over the environment": {
			args: []string{"-expect-commit", lower},
			env:  map[string]string{"TAI_TEI_EXPECT_COMMIT": strings.Repeat("c", 40), "TAI_TEI_EXPECT_GO_VERSION": "go1.25.0"},
			want: Options{ExpectCommit: lower, ExpectGoVersion: "go1.25.0"},
		},
		"an explicitly empty flag means no expectation": {
			args: []string{"-expect-commit="},
			env:  map[string]string{"TAI_TEI_EXPECT_COMMIT": lower},
			want: Options{},
		},
		"upper-case commit is lower-cased": {
			args: []string{"-expect-commit", strings.ToUpper(lower)},
			want: Options{ExpectCommit: lower},
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
		if err != nil || config.Workspace != "testdata/workspace" || config.OutPath != "" || config.TEIRoot != filepath.Clean(filepath.Join("..", "..", "..", "tei-platform")) {
			t.Fatalf("defaults: %+v %v", config, err)
		}
		config, _ = parseConfig(nil, configEnv(map[string]string{"TEI_ROOT": "/from/env"}))
		if config.TEIRoot != "/from/env" {
			t.Fatalf("TEI_ROOT: %+v", config)
		}
		config, _ = parseConfig([]string{"-tei-root", "/from/flag", "-workspace", "ws", "-out", "receipt.json"}, configEnv(map[string]string{"TEI_ROOT": "/from/env"}))
		if config.TEIRoot != "/from/flag" || config.Workspace != "ws" || config.OutPath != "receipt.json" {
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
	os.Args = append([]string{"reference-tei-model"}, args...)
	main()
}

// main() is the only entry users have, so run it for real: the expectation reaches
// RunWithOptions (flag or environment variable), a failed pin exits 1, and -out
// receives the same receipt as stdout. Each case fails at the pin, before any TEI
// code would be built.
func TestMainTurnsExpectationsIntoAFailedPinnedRun(t *testing.T) {
	repo := newFakeTEI(t)
	zeros, ones := strings.Repeat("0", 40), strings.Repeat("1", 40)
	cases := map[string]struct {
		args     []string
		env      map[string]string
		result   string
		expected string // pin.commit.expected
	}{
		"flag":                  {[]string{"-expect-commit", zeros}, nil, "mismatch", zeros},
		"environment variable":  {nil, map[string]string{"TAI_TEI_EXPECT_COMMIT": zeros}, "mismatch", zeros},
		"flag over environment": {[]string{"-expect-commit", ones}, map[string]string{"TAI_TEI_EXPECT_COMMIT": zeros}, "mismatch", ones},
		"upper-case commit":     {[]string{"-expect-commit", strings.ToUpper(zeros[:39]) + "A"}, nil, "mismatch", zeros[:39] + "a"},
		"go version alone":      {nil, map[string]string{"TAI_TEI_EXPECT_GO_VERSION": "go1.26.9"}, "invalid-expectation", ""},
		"malformed go version":  {[]string{"-expect-commit", zeros, "-expect-go-version", "1.26"}, nil, "invalid-expectation", ""},
	}
	for name, test := range cases {
		t.Run(name, func(t *testing.T) {
			outPath := filepath.Join(t.TempDir(), "receipt.json")
			args := append([]string{"-tei-root", repo.Root, "-workspace", newWorkspace(t), "-out", outPath}, test.args...)
			rawArgs, _ := json.Marshal(args)
			cmd := exec.Command(os.Args[0], "-test.run=^TestMainProcess$")
			for _, entry := range os.Environ() {
				if !strings.HasPrefix(entry, "TAI_TEI_EXPECT_") && !strings.HasPrefix(entry, "TEI_ROOT=") {
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

// The receipt keeps its v0 fields: a consumer written against the first nine keys
// must still find them.
func TestReceiptKeepsTheV0Fields(t *testing.T) {
	repo := newFakeTEI(t)
	useFakeTEI(t, fakeTEIScenario{})
	receipt := Run(context.Background(), repo.Root, newWorkspace(t))
	raw, err := json.Marshal(receipt)
	if err != nil {
		t.Fatal(err)
	}
	var fields map[string]json.RawMessage
	if err := json.Unmarshal(raw, &fields); err != nil {
		t.Fatal(err)
	}
	for _, key := range []string{"schema", "teiCommit", "goVersion", "workspaceDigest", "validation", "readOnly", "passed", "notes"} {
		if _, ok := fields[key]; !ok {
			t.Fatalf("v0 field %q is missing from %s", key, raw)
		}
	}
	var schema string
	_ = json.Unmarshal(fields["schema"], &schema)
	if schema != "tai.reference.tei-model/v0" {
		t.Fatalf("the schema string must not change: %q", schema)
	}
	var legacy struct {
		Schema          string   `json:"schema"`
		TeiCommit       string   `json:"teiCommit"`
		GoVersion       string   `json:"goVersion"`
		WorkspaceDigest string   `json:"workspaceDigest"`
		Validation      string   `json:"validation"`
		ReadOnly        bool     `json:"readOnly"`
		Passed          bool     `json:"passed"`
		Reason          string   `json:"reason,omitempty"`
		Notes           []string `json:"notes"`
	}
	if err := json.Unmarshal(raw, &legacy); err != nil || !legacy.Passed || legacy.TeiCommit != repo.Head || legacy.Validation != "ok" {
		t.Fatalf("a v0 consumer misreads the receipt: %+v %v", legacy, err)
	}
}
