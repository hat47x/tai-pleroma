package main

import (
	"bytes"
	"context"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
	"testing"
)

func teiRootForTest(t *testing.T) string {
	t.Helper()
	if _, err := exec.LookPath("go"); err != nil {
		t.Skip("go is not available")
	}
	// No sibling-directory fallback here: the command line keeps its default, but a
	// test that builds and runs TEI must be pointed at a checkout on purpose (a
	// private clone, not a checkout other sessions are editing).
	root := os.Getenv("TEI_ROOT")
	if root == "" {
		t.Skip("TEI_ROOT is not set")
	}
	if _, err := os.Stat(filepath.Join(root, "cmd", "tei")); err != nil {
		t.Skip("TEI runtime is not available")
	}
	return root
}

func TestMissingWorkspaceManifestIsRejected(t *testing.T) {
	receipt := Run(context.Background(), filepath.Join(t.TempDir(), "tei"), t.TempDir())
	if receipt.Passed || !strings.Contains(receipt.Reason, "manifest") {
		t.Fatalf("missing manifest was not rejected: %+v", receipt)
	}
}

// Real TEI: skipped without a TEI checkout. The pin expectations come only from
// the environment (TAI_TEI_EXPECT_COMMIT, TAI_TEI_EXPECT_GO_VERSION); without them
// this records the checkout and asserts nothing about its commit or tree.
// Use a private clone: another session editing a shared checkout while TEI runs
// is reported as a write by the checkout comparison.
func TestTEIWorkspaceValidation(t *testing.T) {
	root := teiRootForTest(t)
	config, err := parseConfig(nil, os.Getenv)
	if err != nil {
		t.Fatal(err)
	}
	receipt := RunWithOptions(context.Background(), root, filepath.Join("testdata", "workspace"), config.Options)
	if !receipt.Passed {
		t.Fatalf("TEI validation failed: %+v", receipt)
	}
	if !receipt.ReadOnly || receipt.Validation != "ok" || receipt.WorkspaceDigest == "" {
		t.Fatalf("receipt is incomplete: %+v", receipt)
	}
	if receipt.TeiCommit == "" || receipt.GoVersion == "" {
		t.Fatalf("version evidence is missing: %+v", receipt)
	}
	if receipt.ValidateJSON.Status != "consistent" || receipt.ModelBinding.Status != "bound" || receipt.Checkout.Status != "unchanged" {
		t.Fatalf("structured evidence: json=%+v binding=%+v checkout=%+v", receipt.ValidateJSON, receipt.ModelBinding, receipt.Checkout)
	}
	if config.Options.specified() && (!receipt.Pin.Checked || receipt.Pin.Result != "match") {
		t.Fatalf("an expectation was given and must match: %+v", receipt.Pin)
	}
	t.Logf("tei commit %s, %s, pin checked=%t result=%s, tree=%+v", receipt.TeiCommit, receipt.Toolchain.GoVersionToken, receipt.Pin.Checked, receipt.Pin.Result, receipt.Pin.SourceTree)
}

// declaredModel is a copy of what testdata/workspace/semantic/guidance.tei
// declares. The test keeps the copy honest so the binding compares with the file.
func TestDeclaredModelMatchesTheWorkspaceFile(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("testdata", "workspace", "semantic", "guidance.tei"))
	if err != nil {
		t.Fatal(err)
	}
	text := strings.ReplaceAll(string(raw), "\r\n", "\n")
	if !strings.Contains(text, "namespace "+declaredNamespace+"\n") {
		t.Fatalf("namespace %s is not declared", declaredNamespace)
	}
	blocks := regexp.MustCompile(`(?s)data (\w+) \{(.*?)\n\}`).FindAllStringSubmatch(text, -1)
	if len(blocks) != len(declaredModel) {
		t.Fatalf("the file declares %d data types, declaredModel has %d", len(blocks), len(declaredModel))
	}
	attribute := regexp.MustCompile(`attribute (\w+) type ([\w.]+)`)
	for index, block := range blocks {
		want := declaredModel[index]
		got := map[string]string{}
		for _, match := range attribute.FindAllStringSubmatch(block[2], -1) {
			got[match[1]] = match[2]
		}
		if block[1] != want.Symbol || fmt.Sprint(got) != fmt.Sprint(want.Attributes) {
			t.Fatalf("%s: file %v, declaredModel %s %v", block[1], got, want.Symbol, want.Attributes)
		}
	}
}

// tinyTEIMain is a stdlib-only stand-in for cmd/tei that answers the three calls
// this tool makes. It is real Go that the default launcher builds and runs, so it
// exercises `go build`, the child environment and the checkout comparison.
func tinyTEIMain(catalog string, extra string) string {
	return fmt.Sprintf(`package main

import (
	"fmt"
	"os"
)

const catalog = %q

func main() {
	%s
	switch {
	case len(os.Args) > 1 && os.Args[1] == "model":
		fmt.Print(catalog)
	case os.Args[len(os.Args)-1] == "-json":
		fmt.Print(%q)
	default:
		fmt.Println("ok")
	}
}
`, catalog, extra, honestValidateJSON)
}

func newTinyTEI(t *testing.T, extra string) fakeRepo {
	t.Helper()
	if _, err := exec.LookPath("go"); err != nil {
		t.Skip("go is not available")
	}
	repo := newFakeTEI(t)
	source := tinyTEIMain(honestCatalog(fakeTEIScenario{}), extra)
	if err := os.WriteFile(filepath.Join(repo.Root, "cmd", "tei", "main.go"), []byte(source), 0o644); err != nil {
		t.Fatal(err)
	}
	git(t, repo.Root, "add", "-A")
	git(t, repo.Root, "commit", "-q", "-m", "tiny tei")
	repo.Head = git(t, repo.Root, "rev-parse", "HEAD")
	return repo
}

func TestDefaultLauncherBuildsAndRunsTheCLIOutsideTheCheckout(t *testing.T) {
	repo := newTinyTEI(t, "")
	// A plain `go build` runs `git status` in the checkout (measured), which rewrites a
	// stale .git/index; -buildvcs=false and the index copy must keep it byte-identical.
	touchTrackedFiles(t, repo)
	index := filepath.Join(repo.Root, ".git", "index")
	indexBefore := mustRead(t, index)
	workspace := newWorkspace(t)
	scratch := t.TempDir() // every temporary directory the run creates must be gone afterwards
	for _, name := range []string{"TMPDIR", "TMP", "TEMP"} {
		t.Setenv(name, scratch)
	}
	receipt := RunWithOptions(context.Background(), repo.Root, workspace, Options{ExpectCommit: repo.Head})
	if !receipt.Passed || receipt.Toolchain.Build != "built" || receipt.ValidateJSON.Status != "consistent" || receipt.ModelBinding.Status != "bound" {
		t.Fatalf("%+v", receipt)
	}
	if !bytes.Equal(indexBefore, mustRead(t, index)) {
		t.Fatal("building TEI rewrote the TEI checkout's .git/index")
	}
	if !strings.HasPrefix(receipt.GoVersion, "go version go") || receipt.Toolchain.GoVersionToken == "" {
		t.Fatalf("go version evidence: %q %+v", receipt.GoVersion, receipt.Toolchain)
	}
	if strings.Join(receipt.Toolchain.BuildFlags, " ") != "-mod=readonly -buildvcs=false" || strings.Join(receipt.Toolchain.Enforced, ",") != "GOTOOLCHAIN=local,GOWORK=off,GOFLAGS=-mod=readonly" {
		t.Fatalf("build constraints: %+v", receipt.Toolchain)
	}
	if status := git(t, repo.Root, "status", "--porcelain"); status != "" {
		t.Fatalf("go build left something in the TEI checkout: %q", status)
	}
	if _, err := os.Stat(filepath.Join(repo.Root, "tei")); err == nil {
		t.Fatal("the TEI binary must not be built inside the checkout")
	}
	if leftovers, _ := os.ReadDir(scratch); len(leftovers) != 0 {
		t.Fatalf("the private build directory or the index copy was not removed: %v", leftovers)
	}
}

// A TEI CLI that rewrites a tracked file of its checkout (here go.mod) is caught
// by the checkout comparison with the real launcher too.
func TestDefaultLauncherDetectsATEIThatRewritesItsCheckout(t *testing.T) {
	repo := newTinyTEI(t, `if len(os.Args) > 1 && os.Args[1] == "validate" && os.Args[len(os.Args)-1] != "-json" { f, _ := os.OpenFile("go.mod", os.O_APPEND|os.O_WRONLY, 0); fmt.Fprintln(f, "// by tei"); f.Close() }`)
	receipt := Run(context.Background(), repo.Root, newWorkspace(t))
	assertFailsClosed(t, receipt, "tracked changes 0->1")
	if receipt.ReadOnly || receipt.Checkout.Status != "changed" {
		t.Fatalf("%+v", receipt.Checkout)
	}
}

// A pinned run never lets go switch toolchains: with go.mod asking for a Go that is
// not installed, GOTOOLCHAIN=auto would try to download one. The pinned run forces
// local and fails; the record-only run inherits auto and is left to the environment.
func TestPinnedRunNeverSwitchesTheGoToolchain(t *testing.T) {
	repo := newTinyTEI(t, "")
	if err := os.WriteFile(filepath.Join(repo.Root, "go.mod"), []byte("module tei\n\ngo 1.99\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	git(t, repo.Root, "add", "-A")
	git(t, repo.Root, "commit", "-q", "-m", "needs a newer go")
	head := git(t, repo.Root, "rev-parse", "HEAD")
	t.Setenv("GOTOOLCHAIN", "auto")
	t.Setenv("GOPROXY", "off") // nothing may reach the network from this test
	pinned := RunWithOptions(context.Background(), repo.Root, newWorkspace(t), Options{ExpectCommit: head})
	assertFailsClosed(t, pinned, "TEI build failed")
	if !strings.Contains(pinned.Reason, "GOTOOLCHAIN=local") || pinned.Toolchain.Build != "failed" || pinned.Validation != "" {
		t.Fatalf("a pinned run must stop on the local toolchain: %+v", pinned)
	}
	unpinned := Run(context.Background(), repo.Root, newWorkspace(t))
	if unpinned.Passed || strings.Contains(unpinned.Reason, "GOTOOLCHAIN=local") {
		t.Fatalf("a record-only run keeps the caller's GOTOOLCHAIN=auto: %+v", unpinned)
	}
	if unpinned.Toolchain.GoToolchainEnv != "auto" {
		t.Fatalf("the effective GOTOOLCHAIN is recorded: %+v", unpinned.Toolchain)
	}
}
