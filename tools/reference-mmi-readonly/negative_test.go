package main

import (
	"bytes"
	"context"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"unicode"
)

func intp(v int) *int    { return &v }
func boolp(v bool) *bool { return &v }

func gitEnv() []string {
	env := []string{}
	for _, entry := range os.Environ() {
		if strings.HasPrefix(entry, "GIT_") {
			continue
		}
		env = append(env, entry)
	}
	return append(env, "GIT_CONFIG_NOSYSTEM=1", "GIT_CONFIG_GLOBAL="+os.DevNull)
}

func git(t *testing.T, dir string, args ...string) string {
	t.Helper()
	cmd := exec.Command("git", append([]string{"-c", "user.name=tai-test", "-c", "user.email=tai-test@example.invalid", "-c", "commit.gpgsign=false"}, args...)...)
	cmd.Dir = dir
	cmd.Env = gitEnv()
	output, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("git %v: %v: %s", args, err, output)
	}
	return strings.TrimSpace(string(output))
}

type fakeRepo struct {
	Root, Head, LockDigest string
}

// newFakeMMI builds a throwaway git repository shaped like the MMI checkout.
func newFakeMMI(t *testing.T, autocrlf bool) fakeRepo {
	return newFakeMMIWith(t, autocrlf, true)
}

func newFakeMMIWith(t *testing.T, autocrlf, withLock bool) fakeRepo {
	t.Helper()
	if _, err := exec.LookPath("git"); err != nil {
		t.Skip("git is not available")
	}
	root := t.TempDir()
	git(t, root, "init", "-q")
	git(t, root, "config", "core.autocrlf", map[bool]string{true: "true", false: "false"}[autocrlf])
	lock := []byte("{\n  \"lockfileVersion\": 3\n}\n")
	files := map[string][]byte{
		filepath.Join("03_Implement", "src", "cli", "mcp.ts"): []byte("// stub\n"),
		"README.md": []byte("stub\n"),
	}
	if withLock {
		files[filepath.Join("03_Implement", "package-lock.json")] = lock
	}
	for path, content := range files {
		full := filepath.Join(root, path)
		if err := os.MkdirAll(filepath.Dir(full), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(full, content, 0o644); err != nil {
			t.Fatal(err)
		}
	}
	git(t, root, "add", "-A")
	git(t, root, "commit", "-q", "-m", "fixture")
	return fakeRepo{Root: root, Head: git(t, root, "rev-parse", "HEAD"), LockDigest: digestBytes(lock)}
}

func assertFailsClosed(t *testing.T, receipt Receipt, reasonContains string) {
	t.Helper()
	if receipt.Passed || receipt.RealProductConnected {
		t.Fatalf("expected a failed receipt, got passed=%t realProductConnected=%t", receipt.Passed, receipt.RealProductConnected)
	}
	if !strings.Contains(receipt.Reason, reasonContains) {
		t.Fatalf("reason %q does not contain %q", receipt.Reason, reasonContains)
	}
}

func TestUnpinnedRunRecordsAndDoesNotCheckThePin(t *testing.T) {
	workspace := newWorkspace(t)
	repo := newFakeMMI(t, false)
	log := filepath.Join(t.TempDir(), "log")
	useFakeMCP(t, fakeScenario{LogPath: log})
	receipt := Run(context.Background(), repo.Root, workspace)
	if !receipt.Passed || !receipt.RealProductConnected || !receipt.ReadOnly {
		t.Fatalf("unpinned run should pass against the honest fake: %+v", receipt)
	}
	if receipt.Pin.Checked || receipt.Pin.Result != "not-checked" || receipt.Pin.Commit.Status != "not-checked" || receipt.Pin.Commit.Actual != repo.Head {
		t.Fatalf("pin must be recorded but not checked: %+v", receipt.Pin)
	}
	if receipt.Binding.SourceDigest != "match" || receipt.Binding.FingerprintCrossCheck != "match" || receipt.Binding.Rows.Status != "complete" {
		t.Fatalf("honest fake should bind: %+v", receipt.Binding)
	}
	if receipt.CandidateCount != 1 || receipt.RejectionKind.Boundary != "outside-workspace" || receipt.RejectionKind.Missing != "not-found" {
		t.Fatalf("counts or rejection kinds: %+v", receipt)
	}
	if strings.Join(receipt.ToolSurface.CalledByTAI, ",") != "inspect,select" {
		t.Fatalf("TAI must call only inspect and select: %+v", receipt.ToolSurface)
	}
	for _, line := range readLog(t, log) {
		if strings.HasPrefix(line, "tools/call ") && line != "tools/call inspect" && line != "tools/call select" {
			t.Fatalf("server saw an unexpected call: %s", line)
		}
	}
	if receipt.WorkspaceTree.DigestBefore == "" || receipt.WorkspaceTree.DigestBefore != receipt.WorkspaceTree.DigestAfter {
		t.Fatalf("workspace tree digests: %+v", receipt.WorkspaceTree)
	}
}

func TestPinMatchPassesAndRecordsExpectations(t *testing.T) {
	workspace := newWorkspace(t)
	repo := newFakeMMI(t, false)
	useFakeMCP(t, fakeScenario{})
	receipt := RunWithOptions(context.Background(), repo.Root, workspace, Options{ExpectCommit: repo.Head, ExpectLockDigest: repo.LockDigest, ExpectNodeMajor: "20"})
	if !receipt.Passed || receipt.Pin.Result != "match" || receipt.Pin.SourceTree.Status != "clean" || !receipt.Pin.Checked {
		t.Fatalf("matching pin should pass: %+v", receipt)
	}
	if receipt.Pin.Commit.Status != "match" || receipt.Pin.PackageLock.Status != "match" || receipt.Pin.NodeMajor.Status != "match" {
		t.Fatalf("every supplied expectation must be recorded as matched: %+v", receipt.Pin)
	}
	commitOnly := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
	if !commitOnly.Passed || commitOnly.Pin.Commit.Status != "match" || commitOnly.Pin.PackageLock.Status != "not-checked" {
		t.Fatalf("the commit alone is a valid pin: %+v", commitOnly.Pin)
	}
}

func TestPinMismatchFailsBeforeAnyMMICodeRuns(t *testing.T) {
	other := strings.Repeat("0", 40)
	otherLock := "sha256:" + strings.Repeat("0", 64)
	cases := map[string]struct {
		options  func(r fakeRepo) Options
		prepare  func(t *testing.T, r fakeRepo)
		contains string
		result   string
		noLock   bool
	}{
		"commit mismatch": {func(fakeRepo) Options { return Options{ExpectCommit: other} }, nil,
			"pin mismatch: mmi commit expected " + other, "mismatch", false},
		"lock digest mismatch": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head, ExpectLockDigest: otherLock} }, nil,
			"pin mismatch: package-lock digest", "mismatch", false},
		"node major mismatch": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head, ExpectNodeMajor: "1"} }, nil,
			"pin mismatch: node major expected 1", "mismatch", false},
		"dirty tracked file": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head, ExpectLockDigest: r.LockDigest} },
			func(t *testing.T, r fakeRepo) {
				appendFile(t, filepath.Join(r.Root, "03_Implement", "src", "cli", "mcp.ts"), "// local edit\n")
			}, "1 tracked change(s)", "mismatch", false},
		"edited file hidden by assume-unchanged": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head, ExpectLockDigest: r.LockDigest} },
			func(t *testing.T, r fakeRepo) {
				path := filepath.Join(r.Root, "03_Implement", "src", "cli", "mcp.ts")
				appendFile(t, path, "// hidden edit\n")
				git(t, r.Root, "update-index", "--assume-unchanged", "03_Implement/src/cli/mcp.ts")
			}, "assume-unchanged or skip-worktree", "unavailable", false},
		"edited file hidden by skip-worktree": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head, ExpectLockDigest: r.LockDigest} },
			func(t *testing.T, r fakeRepo) {
				path := filepath.Join(r.Root, "03_Implement", "src", "cli", "mcp.ts")
				appendFile(t, path, "// hidden edit\n")
				git(t, r.Root, "update-index", "--skip-worktree", "03_Implement/src/cli/mcp.ts")
			}, "assume-unchanged or skip-worktree", "unavailable", false},
		"package-lock.json deleted from the working tree": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head, ExpectLockDigest: r.LockDigest} },
			func(t *testing.T, r fakeRepo) {
				if err := os.Remove(filepath.Join(r.Root, "03_Implement", "package-lock.json")); err != nil {
					t.Fatal(err)
				}
			}, "pin unavailable: package-lock digest", "mismatch", false},
		"package-lock.json never committed": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head, ExpectLockDigest: otherLock} },
			nil, "pin unavailable: package-lock digest", "unavailable", true},
		"short commit is an invalid expectation": {func(fakeRepo) Options { return Options{ExpectCommit: "a8addd1"} }, nil,
			"invalid pin expectation", "invalid-expectation", false},
		// The lock file is identical across many MMI commits and the Node major says
		// nothing about the checkout, so neither may stand in for the commit.
		"lock digest alone does not pin a version": {func(r fakeRepo) Options { return Options{ExpectLockDigest: r.LockDigest} }, nil,
			"expected commit is required", "invalid-expectation", false},
		"node major alone does not pin a version": {func(fakeRepo) Options { return Options{ExpectNodeMajor: "20"} }, nil,
			"expected commit is required", "invalid-expectation", false},
	}
	for name, test := range cases {
		t.Run(name, func(t *testing.T) {
			repo := newFakeMMIWith(t, false, !test.noLock)
			if test.prepare != nil {
				test.prepare(t, repo)
			}
			launches := useFakeMCP(t, fakeScenario{})
			receipt := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), test.options(repo))
			assertFailsClosed(t, receipt, test.contains)
			if receipt.Pin.Result != test.result || !receipt.Pin.Checked {
				t.Fatalf("pin result %q checked=%t, want %q checked: %+v", receipt.Pin.Result, receipt.Pin.Checked, test.result, receipt.Pin)
			}
			if *launches != 0 {
				t.Fatal("MMI code was executed although the pin did not hold")
			}
		})
	}
}

func appendFile(t *testing.T, path, text string) {
	t.Helper()
	file, err := os.OpenFile(path, os.O_APPEND|os.O_WRONLY, 0)
	if err != nil {
		t.Fatal(err)
	}
	defer file.Close()
	if _, err := file.WriteString(text); err != nil {
		t.Fatal(err)
	}
}

func TestUntrackedFilesAreCountedButDoNotFailThePin(t *testing.T) {
	workspace := newWorkspace(t)
	repo := newFakeMMI(t, false)
	if err := os.WriteFile(filepath.Join(repo.Root, "03_Implement", "scratch_tmp.mjs"), []byte("//\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	useFakeMCP(t, fakeScenario{})
	receipt := RunWithOptions(context.Background(), repo.Root, workspace, Options{ExpectCommit: repo.Head})
	if !receipt.Passed || receipt.Pin.SourceTree.UntrackedFiles != 1 || receipt.Pin.SourceTree.TrackedChanges != 0 || receipt.Pin.SourceTree.Status != "clean" {
		t.Fatalf("untracked scratch files are recorded, not rejected: %+v", receipt.Pin)
	}
}

func TestUnpinnedRunDoesNotFailOnADirtyOrDifferentCheckout(t *testing.T) {
	workspace := newWorkspace(t)
	repo := newFakeMMI(t, false)
	appendFile(t, filepath.Join(repo.Root, "03_Implement", "src", "cli", "mcp.ts"), "// local edit\n")
	useFakeMCP(t, fakeScenario{})
	receipt := Run(context.Background(), repo.Root, workspace)
	if !receipt.Passed || receipt.Pin.Checked || receipt.Pin.SourceTree.TrackedChanges != 1 {
		t.Fatalf("default behaviour must stay record-only: %+v", receipt)
	}
}

func TestCRLFWorkingTreeIsCleanAndLockDigestIsLFNormalised(t *testing.T) {
	workspace := newWorkspace(t)
	repo := newFakeMMI(t, true) // like a Windows checkout with core.autocrlf=true
	lockPath := filepath.Join(repo.Root, "03_Implement", "package-lock.json")
	crlf := bytes.ReplaceAll([]byte("{\n  \"lockfileVersion\": 3\n}\n"), []byte("\n"), []byte("\r\n"))
	if err := os.WriteFile(lockPath, crlf, 0o644); err != nil {
		t.Fatal(err)
	}
	useFakeMCP(t, fakeScenario{})
	receipt := RunWithOptions(context.Background(), repo.Root, workspace, Options{ExpectCommit: repo.Head, ExpectLockDigest: repo.LockDigest})
	if !receipt.Passed || receipt.Pin.SourceTree.Status != "clean" {
		t.Fatalf("CRLF working copy of an LF blob is not a change: %+v", receipt)
	}
	if receipt.PackageLockDigest == repo.LockDigest {
		t.Fatalf("the raw digest is expected to stay platform dependent: %s", receipt.PackageLockDigest)
	}
}

func TestSubdirectoryOfAnotherRepositoryDoesNotBorrowItsCommit(t *testing.T) {
	workspace := newWorkspace(t)
	repo := newFakeMMI(t, false)
	sub := filepath.Join(repo.Root, "vendored")
	if err := os.MkdirAll(filepath.Join(sub, "03_Implement"), 0o755); err != nil {
		t.Fatal(err)
	}
	useFakeMCP(t, fakeScenario{})
	receipt := RunWithOptions(context.Background(), sub, workspace, Options{ExpectCommit: repo.Head})
	assertFailsClosed(t, receipt, "pin unavailable: mmi commit")
}

func TestBindingFailures(t *testing.T) {
	cases := map[string]struct {
		scenario fakeScenario
		contains string
	}{
		"MMI sourceDigest differs from the TAI digest": {fakeScenario{SourceDigest: "sha256:" + strings.Repeat("a", 64)}, "differs from the TAI-computed CSV digest"},
		"shown differs from ofTotal":                   {fakeScenario{Shown: intp(3), OfTotal: intp(4)}, "select rows are incomplete"},
		"exact is false":                               {fakeScenario{Exact: boolp(false)}, "select rows are incomplete"},
		"preview truncated against shown":              {fakeScenario{Shown: intp(8), OfTotal: intp(8), PreviewRows: intp(5)}, "select rows are incomplete"},
		"inspect has an empty candidates array":        {fakeScenario{EmptyCandidates: true}, "zero candidates"},
		"inspect has no candidates key":                {fakeScenario{OmitCandidates: true}, "candidates array"},
		"select fingerprint differs from inspect":      {fakeScenario{SelectFinger: "sha256:" + strings.Repeat("b", 64)}, "fingerprint differs"},
	}
	for name, test := range cases {
		t.Run(name, func(t *testing.T) {
			useFakeMCP(t, test.scenario)
			receipt := Run(context.Background(), t.TempDir(), newWorkspace(t))
			assertFailsClosed(t, receipt, test.contains)
		})
	}
}

func TestMissingMMIValuesAreUnavailableNotFailures(t *testing.T) {
	cases := map[string]fakeScenario{
		"no rows object":            {OmitRows: true},
		"no sourceDigest":           {SourceDigest: "-"},
		"sourceDigest other format": {SourceDigest: "md5:abc"},
	}
	for name, scenario := range cases {
		t.Run(name, func(t *testing.T) {
			useFakeMCP(t, scenario)
			receipt := Run(context.Background(), t.TempDir(), newWorkspace(t))
			if !receipt.Passed {
				t.Fatalf("an absent or differently formatted MMI value is recorded, not failed: %+v", receipt)
			}
			if receipt.Binding.SourceDigest == "match" && scenario.SourceDigest != "" {
				t.Fatalf("must not claim a binding it could not make: %+v", receipt.Binding)
			}
			if scenario.OmitRows && receipt.Binding.Rows.Status != "unavailable" {
				t.Fatalf("rows status: %+v", receipt.Binding.Rows)
			}
		})
	}
}

func TestRejectionReasonKinds(t *testing.T) {
	cases := map[string]struct {
		scenario fakeScenario
		options  Options
		contains string
	}{
		"boundary request reached the filesystem": {fakeScenario{BoundaryText: "mmi: ENOENT: no such file or directory, open '/x/outside.csv'"}, Options{}, "ENOENT"},
		"boundary request was not an error":       {fakeScenario{BoundaryOK: true}, Options{}, "was not rejected"},
		"missing source reported as outside":      {fakeScenario{MissingText: `mmi: Argument "source" is outside the MCP workspace root.`}, Options{}, "outside the workspace"},
		"missing source was not an error":         {fakeScenario{MissingOK: true}, Options{}, "was not rejected"},
	}
	for name, test := range cases {
		t.Run(name, func(t *testing.T) {
			useFakeMCP(t, test.scenario)
			receipt := RunWithOptions(context.Background(), t.TempDir(), newWorkspace(t), test.options)
			assertFailsClosed(t, receipt, test.contains)
		})
	}
	t.Run("unrecognised wording is recorded when unpinned and fails when pinned", func(t *testing.T) {
		repo := newFakeMMI(t, false)
		scenario := fakeScenario{BoundaryText: "mmi: rejected for reasons"}
		useFakeMCP(t, scenario)
		unpinned := Run(context.Background(), repo.Root, newWorkspace(t))
		if !unpinned.Passed || unpinned.RejectionKind.Boundary != "other" {
			t.Fatalf("unpinned: %+v", unpinned)
		}
		pinned := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
		assertFailsClosed(t, pinned, "unrecognised reason")
	})
}

func TestToolSurface(t *testing.T) {
	t.Run("write-capable name is recorded when unpinned and fails when pinned", func(t *testing.T) {
		repo := newFakeMMI(t, false)
		useFakeMCP(t, fakeScenario{Tools: append([]string{"html-commit"}, defaultFakeTools...)})
		unpinned := Run(context.Background(), repo.Root, newWorkspace(t))
		if !unpinned.Passed || strings.Join(unpinned.ToolSurface.WriteCapable, ",") != "html-commit" {
			t.Fatalf("an unpinned run must not fail on a tool name heuristic, only record it: %+v", unpinned.ToolSurface)
		}
		if !strings.Contains(strings.Join(unpinned.Notes, "\n"), "html-commit") {
			t.Fatalf("the write-capable name must be noted: %v", unpinned.Notes)
		}
		pinned := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
		assertFailsClosed(t, pinned, "write-capable")
		if pinned.ReadOnly {
			t.Fatal("readOnly must be false when a pinned run lists a write-capable tool")
		}
	})
	t.Run("unmeasured tool is recorded unpinned and fails pinned", func(t *testing.T) {
		repo := newFakeMMI(t, false)
		useFakeMCP(t, fakeScenario{Tools: append([]string{"frobnicate"}, defaultFakeTools...)})
		unpinned := Run(context.Background(), repo.Root, newWorkspace(t))
		if !unpinned.Passed || strings.Join(unpinned.ToolSurface.Unmeasured, ",") != "frobnicate" {
			t.Fatalf("unpinned: %+v", unpinned.ToolSurface)
		}
		pinned := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
		assertFailsClosed(t, pinned, "measured tools")
	})
	t.Run("TAI refuses to call anything but inspect and select", func(t *testing.T) {
		client := &mcpClient{}
		if _, _, err := client.callTool("render", map[string]any{}); err == nil {
			t.Fatal("render must be refused before any request is written")
		}
	})
	t.Run("measured tool names are not write-capable", func(t *testing.T) {
		for _, name := range append([]string{"html-audit"}, defaultFakeTools...) {
			if writeCapable(name) {
				t.Fatalf("%s was measured as read-only", name)
			}
		}
		for _, name := range []string{"html-commit", "write-ledger", "apply_patch", "import"} {
			if !writeCapable(name) {
				t.Fatalf("%s should be treated as write-capable", name)
			}
		}
	})
}

// A pinned run is stricter than a record-only run: the values it records as
// "unavailable" must all be present, because the measured versions provide them.
func TestPinnedRunRequiresTheBinding(t *testing.T) {
	cases := map[string]fakeScenario{
		"no rows object":            {OmitRows: true},
		"no sourceDigest":           {SourceDigest: "-"},
		"sourceDigest other format": {SourceDigest: "md5:abc"},
	}
	for name, scenario := range cases {
		t.Run(name, func(t *testing.T) {
			repo := newFakeMMI(t, false)
			useFakeMCP(t, scenario)
			unpinned := Run(context.Background(), repo.Root, newWorkspace(t))
			if !unpinned.Passed {
				t.Fatalf("the same run is only recorded when unpinned: %+v", unpinned)
			}
			pinned := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
			assertFailsClosed(t, pinned, "pinned run requires")
		})
	}
}

// A fingerprint that cannot be matched to an inspect candidate stays
// "unavailable" for a record-only run and fails a pinned run.
func TestPinnedRunRequiresTheFingerprintCrossCheck(t *testing.T) {
	repo := newFakeMMI(t, false)
	useFakeMCP(t, fakeScenario{SelectFinger: "-"})
	unpinned := Run(context.Background(), repo.Root, newWorkspace(t))
	if !unpinned.Passed || unpinned.Binding.FingerprintCrossCheck != "unavailable" {
		t.Fatalf("record-only: %+v", unpinned.Binding)
	}
	pinned := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
	assertFailsClosed(t, pinned, "pinned run requires")
}

func TestNodeVersionProbeCanBeUnavailable(t *testing.T) {
	repo := newFakeMMI(t, false)
	launches := useFakeMCP(t, fakeScenario{})
	nodeVersionOf = func(context.Context) string { return "" } // restored by useFakeMCP's cleanup
	unpinned := Run(context.Background(), repo.Root, newWorkspace(t))
	if !unpinned.Passed || unpinned.NodeVersion != "" {
		t.Fatalf("a missing node probe must not fail a record-only run: %+v", unpinned)
	}
	*launches = 0
	pinned := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head, ExpectNodeMajor: "20"})
	assertFailsClosed(t, pinned, "pin unavailable: node major")
	if *launches != 0 {
		t.Fatal("MMI code was executed without a node version to compare")
	}
}

func TestFailureReasonDoesNotCarryMMIErrorText(t *testing.T) {
	secret := "/home/someone/private/observations.csv"
	useFakeMCP(t, fakeScenario{InspectError: "mmi: ENOENT: no such file or directory, open '" + secret + "'"})
	receipt := Run(context.Background(), t.TempDir(), newWorkspace(t))
	assertFailsClosed(t, receipt, "inspect returned isError")
	raw, err := json.Marshal(receipt)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(raw), "someone") || strings.Contains(string(raw), "ENOENT") {
		t.Fatalf("the MMI error text (with a local path) leaked into the receipt: %s", raw)
	}
}

func TestChildStderrIsReportedWhenTheServerDies(t *testing.T) {
	useFakeMCP(t, fakeScenario{CrashOnInit: "tsx exploded"})
	receipt := Run(context.Background(), t.TempDir(), newWorkspace(t))
	assertFailsClosed(t, receipt, "reading MCP response")
	if !strings.Contains(receipt.Reason, "tsx exploded") {
		t.Fatalf("stderr must be read after the process exits: %q", receipt.Reason)
	}
}

func TestWholeWorkspaceDigestSeesWritesToOtherFiles(t *testing.T) {
	workspace := newWorkspace(t)
	useFakeMCP(t, fakeScenario{WriteOnSelect: "ledger.json"})
	receipt := Run(context.Background(), t.TempDir(), workspace)
	assertFailsClosed(t, receipt, "changed the workspace")
	if receipt.ReadOnly {
		t.Fatal("readOnly must be false after a workspace write")
	}
	if receipt.SourceDigestBefore != receipt.SourceDigestAfter || receipt.GuideDigestBefore != receipt.GuideDigestAfter {
		t.Fatal("the CSV and guide digests alone cannot see this write; that is the point of the tree digest")
	}
}

// The server may write while it shuts down, so the after-digests must be taken
// once the process is gone, not while it is still running.
func TestWriteDuringShutdownIsObserved(t *testing.T) {
	useFakeMCP(t, fakeScenario{WriteOnExit: "ledger.json"})
	receipt := Run(context.Background(), t.TempDir(), newWorkspace(t))
	assertFailsClosed(t, receipt, "changed the workspace")
	if receipt.ReadOnly {
		t.Fatal("readOnly must be false after a write during shutdown")
	}
}

func TestDigestTree(t *testing.T) {
	dir := t.TempDir()
	if err := os.WriteFile(filepath.Join(dir, "a.txt"), []byte("a"), 0o600); err != nil {
		t.Fatal(err)
	}
	base, entries, err := digestTree(dir)
	if err != nil || entries != 2 {
		t.Fatalf("%d %v", entries, err)
	}
	again, _, _ := digestTree(dir)
	if again != base {
		t.Fatal("digest must be deterministic")
	}
	if err := os.Mkdir(filepath.Join(dir, "empty"), 0o700); err != nil {
		t.Fatal(err)
	}
	withDir, _, _ := digestTree(dir)
	if withDir == base {
		t.Fatal("a new empty directory must change the digest")
	}
	if err := os.Rename(filepath.Join(dir, "a.txt"), filepath.Join(dir, "b.txt")); err != nil {
		t.Fatal(err)
	}
	renamed, _, _ := digestTree(dir)
	if renamed == withDir {
		t.Fatal("a rename must change the digest")
	}
}

func TestReceiptKeepsExistingKeysAndHasNoAmbiguousNames(t *testing.T) {
	useFakeMCP(t, fakeScenario{})
	receipt := Run(context.Background(), t.TempDir(), newWorkspace(t))
	raw, err := json.Marshal(receipt)
	if err != nil {
		t.Fatal(err)
	}
	var generic map[string]json.RawMessage
	if err := json.Unmarshal(raw, &generic); err != nil {
		t.Fatal(err)
	}
	for _, key := range []string{"schema", "server", "protocolVersion", "mmiCommit", "packageLockDigest", "nodeVersion", "tool", "candidateCount", "selectedRows", "observedIds", "selected", "conflictPreserved", "sourceDigestBefore", "sourceDigestAfter", "guideDigestBefore", "guideDigestAfter", "boundaryRejected", "missingSourceRejected", "readOnly", "realProductConnected", "passed", "notes"} {
		if _, ok := generic[key]; !ok && key != "mmiCommit" && key != "packageLockDigest" && key != "nodeVersion" {
			t.Fatalf("existing key %q disappeared", key)
		}
	}
	if string(generic["schema"]) != `"tai.reference.mmi-readonly/v0"` {
		t.Fatalf("schema string changed: %s", generic["schema"])
	}
	// reference-scn001-run rejects JSON objects whose keys collide after Unicode
	// case folding. Check every object in the new receipt the same way.
	decoder := json.NewDecoder(bytes.NewReader(raw))
	var walk func() error
	walk = func() error {
		token, err := decoder.Token()
		if err != nil {
			return err
		}
		switch token {
		case json.Delim('{'):
			seen := map[string]bool{}
			for decoder.More() {
				keyToken, _ := decoder.Token()
				folded := strings.Map(unicode.ToLower, keyToken.(string))
				if seen[folded] {
					t.Fatalf("keys collide after case folding: %s", keyToken)
				}
				seen[folded] = true
				if err := walk(); err != nil {
					return err
				}
			}
			_, err = decoder.Token()
			return err
		case json.Delim('['):
			for decoder.More() {
				if err := walk(); err != nil {
					return err
				}
			}
			_, err = decoder.Token()
			return err
		}
		return nil
	}
	if err := walk(); err != nil {
		t.Fatal(err)
	}
}
