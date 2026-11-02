package main

import (
	"context"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

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
	Root, Head string
}

// newFakeTEI builds a throwaway git repository shaped like the TEI checkout:
// cmd/tei, go.mod, go.sum and a README.
func newFakeTEI(t *testing.T) fakeRepo {
	t.Helper()
	if _, err := exec.LookPath("git"); err != nil {
		t.Skip("git is not available")
	}
	root := t.TempDir()
	return commitFakeTEI(t, root)
}

func commitFakeTEI(t *testing.T, root string) fakeRepo {
	t.Helper()
	git(t, root, "init", "-q")
	git(t, root, "config", "core.autocrlf", "false")
	writeFakeTEIFiles(t, root)
	git(t, root, "add", "-A")
	git(t, root, "commit", "-q", "-m", "fixture")
	return fakeRepo{Root: root, Head: git(t, root, "rev-parse", "HEAD")}
}

func writeFakeTEIFiles(t *testing.T, root string) {
	t.Helper()
	files := map[string]string{
		filepath.Join("cmd", "tei", "main.go"): "package main\n\nfunc main() {}\n",
		"go.mod":                               "module tei\n\ngo 1.21\n",
		"go.sum":                               "",
		"README.md":                            "stub\n",
	}
	for path, content := range files {
		full := filepath.Join(root, path)
		if err := os.MkdirAll(filepath.Dir(full), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(full, []byte(content), 0o644); err != nil {
			t.Fatal(err)
		}
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

func assertFailsClosed(t *testing.T, receipt Receipt, reasonContains string) {
	t.Helper()
	if receipt.Passed {
		t.Fatalf("expected a failed receipt, got passed=true: %+v", receipt)
	}
	if !strings.Contains(receipt.Reason, reasonContains) {
		t.Fatalf("reason %q does not contain %q", receipt.Reason, reasonContains)
	}
}

func TestUnpinnedRunRecordsAndDoesNotCheckThePin(t *testing.T) {
	workspace := newWorkspace(t)
	repo := newFakeTEI(t)
	log := filepath.Join(t.TempDir(), "log")
	useFakeTEI(t, fakeTEIScenario{LogPath: log})
	receipt := Run(context.Background(), repo.Root, workspace)
	if !receipt.Passed || !receipt.ReadOnly || receipt.Validation != "ok" || receipt.Reason != "" {
		t.Fatalf("unpinned run should pass against the honest fake: %+v", receipt)
	}
	if receipt.Schema != "tai.reference.tei-model/v0" || receipt.TeiCommit != repo.Head || receipt.GoVersion != fakeGoVersion {
		t.Fatalf("existing fields: %+v", receipt)
	}
	if receipt.Pin.Checked || receipt.Pin.Result != "not-checked" || receipt.Pin.Commit.Status != "not-checked" || receipt.Pin.Commit.Actual != repo.Head || receipt.Pin.GoVersion.Actual != "go1.26.9" {
		t.Fatalf("pin must be recorded but not checked: %+v", receipt.Pin)
	}
	if receipt.Pin.SourceTree.Status != "not-checked" {
		t.Fatalf("an unpinned run does not judge the tree: %+v", receipt.Pin.SourceTree)
	}
	if receipt.ValidateJSON.Status != "consistent" || receipt.ModelBinding.Status != "bound" || receipt.Checkout.Status != "unchanged" {
		t.Fatalf("honest fake: json=%+v binding=%+v checkout=%+v", receipt.ValidateJSON, receipt.ModelBinding, receipt.Checkout)
	}
	if receipt.WorkspaceTree.DigestBefore == "" || receipt.WorkspaceTree.DigestBefore != receipt.WorkspaceTree.DigestAfter || receipt.WorkspaceTree.Entries < 3 {
		t.Fatalf("workspace tree digests: %+v", receipt.WorkspaceTree)
	}
	legacy, err := legacyDigestWorkspace(workspace)
	if err != nil || legacy != receipt.WorkspaceDigest {
		t.Fatalf("workspaceDigest must stay what it was (%s): %s %v", legacy, receipt.WorkspaceDigest, err)
	}
	var sawNote bool
	for _, note := range receipt.Notes {
		sawNote = sawNote || strings.Contains(note, "版固定の期待値が指定されていない")
	}
	if !sawNote {
		t.Fatalf("an unpinned receipt must say the pin was not checked: %v", receipt.Notes)
	}
	var runs []string
	for _, line := range readLog(t, log) {
		runs = append(runs, strings.Fields(line)[0])
	}
	if strings.Join(runs, ",") != "validate,validate,model" {
		t.Fatalf("TEI must receive exactly validate, validate -json and model catalog: %v", runs)
	}
}

func TestPinMatchPassesAndRecordsExpectations(t *testing.T) {
	repo := newFakeTEI(t)
	useFakeTEI(t, fakeTEIScenario{})
	receipt := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head, ExpectGoVersion: "go1.26.9"})
	if !receipt.Passed || receipt.Pin.Result != "match" || receipt.Pin.SourceTree.Status != "clean" || !receipt.Pin.Checked {
		t.Fatalf("matching pin should pass: %+v", receipt)
	}
	if receipt.Pin.Commit.Status != "match" || receipt.Pin.GoVersion.Status != "match" {
		t.Fatalf("every supplied expectation must be recorded as matched: %+v", receipt.Pin)
	}
	if strings.Join(receipt.Toolchain.Enforced, ",") != "GOTOOLCHAIN=local,GOWORK=off,GOFLAGS=-mod=readonly" {
		t.Fatalf("a pinned run constrains the go toolchain: %+v", receipt.Toolchain)
	}
	commitOnly := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
	if !commitOnly.Passed || commitOnly.Pin.Commit.Status != "match" || commitOnly.Pin.GoVersion.Status != "not-checked" {
		t.Fatalf("the commit alone is a valid pin: %+v", commitOnly.Pin)
	}
}

func TestPinMismatchFailsBeforeAnyTEICodeRuns(t *testing.T) {
	other := strings.Repeat("0", 40)
	cases := map[string]struct {
		options  func(r fakeRepo) Options
		prepare  func(t *testing.T, r fakeRepo)
		contains string
		result   string
	}{
		"commit mismatch": {func(fakeRepo) Options { return Options{ExpectCommit: other} }, nil,
			"pin mismatch: tei commit expected " + other, "mismatch"},
		"go version mismatch": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head, ExpectGoVersion: "go1.24.0"} }, nil,
			"pin mismatch: go version expected go1.24.0, got go1.26.9", "mismatch"},
		"dirty tracked file": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head} },
			func(t *testing.T, r fakeRepo) { appendFile(t, filepath.Join(r.Root, "README.md"), "local edit\n") },
			"1 tracked change(s)", "mismatch"},
		"staged change": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head} },
			func(t *testing.T, r fakeRepo) {
				appendFile(t, filepath.Join(r.Root, "README.md"), "staged edit\n")
				git(t, r.Root, "add", "README.md")
			}, "1 tracked change(s)", "mismatch"},
		"go.mod edited": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head} },
			func(t *testing.T, r fakeRepo) { appendFile(t, filepath.Join(r.Root, "go.mod"), "// edited\n") },
			"1 tracked change(s)", "mismatch"},
		"tracked file deleted": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head} },
			func(t *testing.T, r fakeRepo) {
				if err := os.Remove(filepath.Join(r.Root, "README.md")); err != nil {
					t.Fatal(err)
				}
			}, "1 tracked change(s)", "mismatch"},
		"edited file hidden by assume-unchanged": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head} },
			func(t *testing.T, r fakeRepo) {
				appendFile(t, filepath.Join(r.Root, "README.md"), "hidden edit\n")
				git(t, r.Root, "update-index", "--assume-unchanged", "README.md")
			}, "assume-unchanged or skip-worktree", "unavailable"},
		"edited file hidden by skip-worktree": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head} },
			func(t *testing.T, r fakeRepo) {
				appendFile(t, filepath.Join(r.Root, "README.md"), "hidden edit\n")
				git(t, r.Root, "update-index", "--skip-worktree", "README.md")
			}, "assume-unchanged or skip-worktree", "unavailable"},
		"short commit is an invalid expectation": {func(fakeRepo) Options { return Options{ExpectCommit: "490dd20"} }, nil,
			"invalid pin expectation: expected commit", "invalid-expectation"},
		"63 hex digits is an invalid expectation": {func(fakeRepo) Options { return Options{ExpectCommit: strings.Repeat("a", 63)} }, nil,
			"invalid pin expectation: expected commit", "invalid-expectation"},
		"non-hex commit is an invalid expectation": {func(fakeRepo) Options { return Options{ExpectCommit: strings.Repeat("g", 40)} }, nil,
			"invalid pin expectation: expected commit", "invalid-expectation"},
		"commit with a trailing space is invalid": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head + " "} }, nil,
			"invalid pin expectation: expected commit", "invalid-expectation"},
		"go version with os and arch is invalid": {func(r fakeRepo) Options {
			return Options{ExpectCommit: r.Head, ExpectGoVersion: "go1.26.9 linux/amd64"}
		}, nil,
			"invalid pin expectation: expected go version", "invalid-expectation"},
		"go version without the go prefix is invalid": {func(r fakeRepo) Options { return Options{ExpectCommit: r.Head, ExpectGoVersion: "1.26.9"} }, nil,
			"invalid pin expectation: expected go version", "invalid-expectation"},
		// The Go version says nothing about which TEI checkout runs.
		"go version alone does not pin a version": {func(fakeRepo) Options { return Options{ExpectGoVersion: "go1.26.9"} }, nil,
			"expected commit is required", "invalid-expectation"},
	}
	for name, test := range cases {
		t.Run(name, func(t *testing.T) {
			repo := newFakeTEI(t)
			if test.prepare != nil {
				test.prepare(t, repo)
			}
			launches := useFakeTEI(t, fakeTEIScenario{})
			receipt := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), test.options(repo))
			assertFailsClosed(t, receipt, test.contains)
			if receipt.Pin.Result != test.result || !receipt.Pin.Checked {
				t.Fatalf("pin result %q checked=%t, want %q checked: %+v", receipt.Pin.Result, receipt.Pin.Checked, test.result, receipt.Pin)
			}
			if *launches != 0 || receipt.Validation != "" {
				t.Fatal("TEI code was executed although the pin did not hold")
			}
		})
	}
}

func TestPinnedRunRefusesGoFlagsThatChangeWhatIsCompiled(t *testing.T) {
	for _, flag := range []string{"-modfile=/elsewhere/go.mod", "-overlay=/elsewhere/overlay.json"} {
		repo := newFakeTEI(t)
		launches := useFakeTEI(t, fakeTEIScenario{})
		previous := probeToolchain
		probeToolchain = func(ctx context.Context, root string, pinned bool) (string, Toolchain) {
			full, tool := previous(ctx, root, pinned)
			tool.GoFlags = "-count=1 " + flag
			return full, tool
		}
		receipt := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
		assertFailsClosed(t, receipt, "GOFLAGS contains "+flag[:strings.Index(flag, "=")])
		if receipt.Pin.Result != "unavailable" || *launches != 0 {
			t.Fatalf("%s: pin=%+v launches=%d", flag, receipt.Pin, *launches)
		}
		unpinned := Run(context.Background(), repo.Root, newWorkspace(t))
		if !unpinned.Passed || !strings.Contains(unpinned.Toolchain.GoFlags, flag) {
			t.Fatalf("a record-only run records GOFLAGS and passes: %+v", unpinned.Toolchain)
		}
		probeToolchain = previous
	}
}

func TestUntrackedFilesAreCountedButDoNotFailThePin(t *testing.T) {
	repo := newFakeTEI(t)
	if err := os.WriteFile(filepath.Join(repo.Root, "scratch_tmp.txt"), []byte("x\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	useFakeTEI(t, fakeTEIScenario{})
	receipt := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
	if !receipt.Passed || receipt.Pin.SourceTree.UntrackedFiles != 1 || receipt.Pin.SourceTree.TrackedChanges != 0 || receipt.Pin.SourceTree.Status != "clean" {
		t.Fatalf("untracked scratch files are recorded, not rejected: %+v", receipt.Pin)
	}
	if receipt.Checkout.Before.UntrackedFiles != 1 || receipt.Checkout.After.UntrackedFiles != 1 || receipt.Checkout.Status != "unchanged" {
		t.Fatalf("checkout: %+v", receipt.Checkout)
	}
}

// The default run must keep passing on a dirty checkout at any commit: it records.
func TestUnpinnedRunDoesNotFailOnADirtyOrDifferentCheckout(t *testing.T) {
	repo := newFakeTEI(t)
	appendFile(t, filepath.Join(repo.Root, "README.md"), "local edit\n")
	useFakeTEI(t, fakeTEIScenario{})
	receipt := Run(context.Background(), repo.Root, newWorkspace(t))
	if !receipt.Passed || receipt.Pin.Checked || receipt.Pin.SourceTree.TrackedChanges != 1 || receipt.Checkout.Before.TrackedChanges != 1 || receipt.Checkout.Status != "unchanged" {
		t.Fatalf("default behaviour must stay record-only: %+v", receipt)
	}
}

// The preconditions keep the reasons they had before the version pin existed.
func TestPreconditionReasonsAreUnchanged(t *testing.T) {
	root := t.TempDir()
	if err := os.MkdirAll(filepath.Join(root, "cmd", "tei"), 0o755); err != nil {
		t.Fatal(err)
	}
	noManifest := Run(context.Background(), root, t.TempDir())
	assertFailsClosed(t, noManifest, "TEI workspace manifest is unavailable:")
	noRuntime := Run(context.Background(), t.TempDir(), newWorkspace(t))
	assertFailsClosed(t, noRuntime, "TEI runtime is unavailable:")
	t.Setenv("PATH", t.TempDir()) // no go and no git on PATH; the real build step reports it
	noGo := Run(context.Background(), root, newWorkspace(t))
	assertFailsClosed(t, noGo, "go is unavailable:")
	if noGo.Toolchain.Build != "failed" || noGo.Validation != "" || noGo.TeiCommit != "" {
		t.Fatalf("%+v", noGo)
	}
}

func TestGitUnavailable(t *testing.T) {
	repo := newFakeTEI(t)
	launches := useFakeTEI(t, fakeTEIScenario{})
	t.Setenv("PATH", t.TempDir()) // no git on PATH
	unpinned := Run(context.Background(), repo.Root, newWorkspace(t))
	if !unpinned.Passed || unpinned.TeiCommit != "" || unpinned.Checkout.Status != "unavailable" || unpinned.Pin.Commit.Status != "not-checked" {
		t.Fatalf("a record-only run records the missing commit and passes: %+v", unpinned)
	}
	pinned := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
	assertFailsClosed(t, pinned, "pin unavailable: tei commit could not be determined")
	if pinned.Pin.Result != "unavailable" || pinned.Pin.Commit.Status != "unavailable" || *launches != 1 {
		t.Fatalf("pin: %+v launches=%d (only the unpinned run may start TEI)", pinned.Pin, *launches)
	}
}

// `git rev-parse HEAD` in a subdirectory of another repository reports the outer
// repository's commit: that is not the commit of this TEI checkout.
func TestTEIRootInsideAnotherRepositoryHasNoCommit(t *testing.T) {
	outer := newFakeTEI(t)
	inner := filepath.Join(outer.Root, "vendor", "tei")
	if err := os.MkdirAll(filepath.Join(inner, "cmd", "tei"), 0o755); err != nil {
		t.Fatal(err)
	}
	launches := useFakeTEI(t, fakeTEIScenario{})
	unpinned := Run(context.Background(), inner, newWorkspace(t))
	if !unpinned.Passed || unpinned.TeiCommit != "" || unpinned.Pin.Commit.Actual != "" || unpinned.Checkout.Status != "unavailable" {
		t.Fatalf("a subdirectory must not borrow the outer commit: %+v", unpinned)
	}
	pinned := RunWithOptions(context.Background(), inner, newWorkspace(t), Options{ExpectCommit: outer.Head})
	assertFailsClosed(t, pinned, "pin unavailable: tei commit could not be determined")
	if *launches != 1 {
		t.Fatalf("launches=%d: only the unpinned run may start TEI", *launches)
	}
}

func TestTEIRootThatIsNotAGitRepository(t *testing.T) {
	root := t.TempDir()
	writeFakeTEIFiles(t, root)
	useFakeTEI(t, fakeTEIScenario{})
	unpinned := Run(context.Background(), root, newWorkspace(t))
	if !unpinned.Passed || unpinned.TeiCommit != "" || unpinned.Checkout.Status != "unavailable" {
		t.Fatalf("record-only: %+v", unpinned)
	}
	pinned := RunWithOptions(context.Background(), root, newWorkspace(t), Options{ExpectCommit: strings.Repeat("a", 40)})
	assertFailsClosed(t, pinned, "pin unavailable")
}

func TestValidateOutputThatIsNotExactlyOkFails(t *testing.T) {
	cases := map[string]fakeTEIScenario{
		"a warning before ok":  {TextOut: "warning\tSOME_CODE\ta finding\nok\n"},
		"empty output":         {TextOut: "-"},
		"ok followed by more":  {TextOut: "ok\nextra\n"},
		"something else":       {TextOut: "fine\n"},
		"a finding and no ok":  {TextOut: "semantic/a.tei:1:1\terror\tPARSE_ERROR\tbad\n"},
		"uppercase ok":         {TextOut: "OK\n"},
		"ok then a nonzero rc": {TextOut: "ok\n", TextExit: 1},
	}
	for name, scenario := range cases {
		t.Run(name, func(t *testing.T) {
			repo := newFakeTEI(t)
			useFakeTEI(t, scenario)
			receipt := Run(context.Background(), repo.Root, newWorkspace(t))
			want := "TEI validate did not report ok"
			if scenario.TextExit != 0 {
				want = "TEI validate failed"
			}
			assertFailsClosed(t, receipt, want)
			if receipt.ValidateJSON.Status != "not-run" || receipt.ModelBinding.Status != "not-run" {
				t.Fatalf("nothing is derived from a failed validate: %+v %+v", receipt.ValidateJSON, receipt.ModelBinding)
			}
		})
	}
}

func TestValidateJSONEvidence(t *testing.T) {
	cases := map[string]struct {
		scenario  fakeTEIScenario
		inconsist bool   // fails even without a pin: TEI contradicts itself
		status    string // validateJson.status
	}{
		"ok false although the text said ok": {fakeTEIScenario{JSONOut: `{"schemaVersion":"tei.cli.validate/v0","ok":false,"diagnostics":[]}` + "\n"}, true, "inconsistent"},
		"an error diagnostic":                {fakeTEIScenario{JSONOut: `{"schemaVersion":"tei.cli.validate/v0","ok":true,"diagnostics":[{"diagnostic":{"code":"X","severity":"error","message":"m"}}]}` + "\n"}, true, "inconsistent"},
		"an error object":                    {fakeTEIScenario{JSONOut: `{"schemaVersion":"tei.cli.validate/v0","ok":true,"diagnostics":[],"error":{"code":"WORKSPACE_LOAD_FAILED","message":"m"}}` + "\n"}, true, "inconsistent"},
		"json exit code 1":                   {fakeTEIScenario{JSONExit: 1}, true, "inconsistent"},
		"not json":                           {fakeTEIScenario{JSONOut: "ok\n"}, false, "unavailable"},
		"empty":                              {fakeTEIScenario{JSONOut: "{}"}, false, "unavailable"},
		"another schema version":             {fakeTEIScenario{JSONOut: `{"schemaVersion":"tei.cli.validate/v1","ok":true,"diagnostics":[]}` + "\n"}, false, "unavailable"},
	}
	for name, test := range cases {
		t.Run(name, func(t *testing.T) {
			repo := newFakeTEI(t)
			useFakeTEI(t, test.scenario)
			unpinned := Run(context.Background(), repo.Root, newWorkspace(t))
			if test.inconsist {
				assertFailsClosed(t, unpinned, "contradicts the text output")
			} else if !unpinned.Passed {
				t.Fatalf("a record-only run records an unusable -json and passes: %+v", unpinned)
			}
			if unpinned.ValidateJSON.Status != test.status {
				t.Fatalf("status %q, want %q: %+v", unpinned.ValidateJSON.Status, test.status, unpinned.ValidateJSON)
			}
			pinned := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
			if pinned.Passed {
				t.Fatalf("a pinned run needs a consistent -json: %+v", pinned)
			}
		})
	}
	t.Run("warnings are counted and do not contradict ok", func(t *testing.T) {
		repo := newFakeTEI(t)
		useFakeTEI(t, fakeTEIScenario{JSONOut: `{"schemaVersion":"tei.cli.validate/v0","ok":true,"diagnostics":[{"diagnostic":{"code":"W","severity":"warning","message":"m"}}]}` + "\n"})
		receipt := Run(context.Background(), repo.Root, newWorkspace(t))
		if !receipt.Passed || receipt.ValidateJSON.Diagnostics.Warnings != 1 || receipt.ValidateJSON.Diagnostics.Total != 1 || receipt.ValidateJSON.Diagnostics.Errors != 0 {
			t.Fatalf("%+v", receipt.ValidateJSON)
		}
	})
}

func TestModelBinding(t *testing.T) {
	cases := map[string]struct {
		scenario fakeTEIScenario
		status   string
		contains string
	}{
		"a declared data type is missing":      {fakeTEIScenario{CatalogOmit: "RuleCandidate"}, "mismatch", "RuleCandidate: 0 data entries"},
		"a declared attribute is missing":      {fakeTEIScenario{CatalogDrop: "Observation.sourceVersion"}, "mismatch", "Observation.sourceVersion is missing"},
		"an attribute has another type":        {fakeTEIScenario{CatalogRetype: "Observation.text=std.code"}, "mismatch", "Observation.text has type std.code, declared std.text"},
		"TEI reports an attribute TAI did not": {fakeTEIScenario{CatalogExtra: "Observation.extra"}, "mismatch", "Observation.extra is not declared by TAI"},
		"the catalog is not read-only":         {fakeTEIScenario{Effect: "write"}, "mismatch", "effect is not read-only"},
		"the command fails":                    {fakeTEIScenario{CatalogOut: "-", CatalogExit: 2}, "unavailable", ""},
		"the output is not json":               {fakeTEIScenario{CatalogOut: "unknown command\n"}, "unavailable", ""},
		"an error envelope":                    {fakeTEIScenario{CatalogOut: `{"schemaVersion":"tei.cli.model/v0","ok":false,"error":{"code":"WORKSPACE_LOAD_FAILED","message":"m"}}` + "\n", CatalogExit: 2}, "unavailable", ""},
		"another schema version":               {fakeTEIScenario{CatalogOut: `{"schemaVersion":"tei.cli.model/v1","ok":true,"result":{"schemaVersion":"tei.operations.model-catalog/v0","entries":[]}}` + "\n"}, "unavailable", ""},
	}
	for name, test := range cases {
		t.Run(name, func(t *testing.T) {
			repo := newFakeTEI(t)
			useFakeTEI(t, test.scenario)
			unpinned := Run(context.Background(), repo.Root, newWorkspace(t))
			if !unpinned.Passed || unpinned.ModelBinding.Status != test.status {
				t.Fatalf("a record-only run records the binding (%s) and passes: %+v", test.status, unpinned)
			}
			if test.contains != "" && !strings.Contains(strings.Join(unpinned.ModelBinding.Differences, "|"), test.contains) {
				t.Fatalf("differences %v do not contain %q", unpinned.ModelBinding.Differences, test.contains)
			}
			if unpinned.ModelBinding.Status == "unavailable" && unpinned.ModelBinding.WorldFingerprint != "" {
				t.Fatalf("an unusable catalog yields no fingerprints: %+v", unpinned.ModelBinding)
			}
			pinned := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: repo.Head})
			assertFailsClosed(t, pinned, "pinned run requires the TEI model catalog to bind")
			if pinned.Pin.Result != "match" {
				t.Fatalf("the pin itself matched; the binding is what failed: %+v", pinned.Pin)
			}
		})
	}
	t.Run("an honest catalog binds and records TEI's fingerprints", func(t *testing.T) {
		repo := newFakeTEI(t)
		useFakeTEI(t, fakeTEIScenario{})
		receipt := Run(context.Background(), repo.Root, newWorkspace(t))
		binding := receipt.ModelBinding
		if binding.Status != "bound" || binding.Effect != "read-only" || len(binding.Differences) != 0 ||
			binding.WorldFingerprint == "" || binding.SourceIndexFingerprint == "" || binding.ModelRevision == "" ||
			strings.Join(binding.Declared, ",") != "Observation,RuleCandidate" {
			t.Fatalf("%+v", binding)
		}
	})
}

// A TEI CLI that writes must be seen: in the workspace (a new file, or a rewrite of
// an existing file to bytes of the same length) and in the TEI checkout (a tracked
// file, a new untracked file, or a further edit of an already modified file).
func TestAWriteByTEIIsDetected(t *testing.T) {
	cases := map[string]struct {
		scenario fakeTEIScenario
		prepare  func(t *testing.T, r fakeRepo)
		contains string
		checkout string // expected checkout.status
	}{
		"a new file in the workspace":              {fakeTEIScenario{WriteWorkspace: "ledger.json"}, nil, "TEI validate changed the workspace", "unchanged"},
		"a same-length rewrite in the workspace":   {fakeTEIScenario{OverwriteWorkspace: filepath.Join("semantic", "guidance.tei")}, nil, "TEI validate changed the workspace", "unchanged"},
		"a write during the json call":             {fakeTEIScenario{WriteWorkspace: "late.json", WriteOn: "json"}, nil, "TEI validate changed the workspace", "unchanged"},
		"a write during the catalog call":          {fakeTEIScenario{WriteWorkspace: "late.json", WriteOn: "catalog"}, nil, "TEI validate changed the workspace", "unchanged"},
		"an edit of a tracked TEI file":            {fakeTEIScenario{AppendTracked: "edited by TEI\n"}, nil, "tracked changes 0->1", "changed"},
		"a new untracked file in the TEI checkout": {fakeTEIScenario{WriteUntracked: "generated.out"}, nil, "untracked files 0->1", "changed"},
		"a further edit of an already modified file": {fakeTEIScenario{AppendTracked: "more\n"},
			func(t *testing.T, r fakeRepo) {
				appendFile(t, filepath.Join(r.Root, "README.md"), "first local edit\n")
			},
			"tracked changes 1->1", "changed"},
	}
	for name, test := range cases {
		for _, pinned := range []bool{false, true} {
			t.Run(fmt.Sprintf("%s pinned=%t", name, pinned), func(t *testing.T) {
				repo := newFakeTEI(t)
				if test.prepare != nil {
					test.prepare(t, repo)
				}
				useFakeTEI(t, test.scenario)
				options := Options{}
				if pinned {
					if test.prepare != nil {
						t.Skip("a dirty checkout cannot be pinned")
					}
					options = Options{ExpectCommit: repo.Head}
				}
				receipt := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), options)
				assertFailsClosed(t, receipt, test.contains)
				if receipt.ReadOnly || receipt.Checkout.Status != test.checkout {
					t.Fatalf("readOnly=%t checkout=%+v", receipt.ReadOnly, receipt.Checkout)
				}
			})
		}
	}
}

func TestAWriteIsReportedAlongsideAFailedValidate(t *testing.T) {
	repo := newFakeTEI(t)
	useFakeTEI(t, fakeTEIScenario{TextOut: "fine\n", WriteUntracked: "generated.out"})
	receipt := Run(context.Background(), repo.Root, newWorkspace(t))
	assertFailsClosed(t, receipt, "untracked files 0->1")
	assertFailsClosed(t, receipt, "TEI validate did not report ok")
	if receipt.ReadOnly {
		t.Fatal("a write is a write even when validation failed")
	}
}
