package main

import (
	"context"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
)

// pinFakeSEI is a stand-in for the sei command line, only as far as this tool uses it:
// init, add, resume --json, verify --input and version. Its environment variables switch
// misbehaviour on. A pass with it shows that the build and inspection path works; it
// says nothing about SEI itself.
const pinFakeSEI = `package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

func values(args []string, name string) []string {
	var out []string
	for i := 0; i+1 < len(args); i++ {
		if args[i] == name {
			out = append(out, args[i+1])
		}
	}
	return out
}

func first(args []string, name string) string {
	if v := values(args, name); len(v) > 0 {
		return v[0]
	}
	return ""
}

func main() {
	args := os.Args[1:]
	if len(args) == 0 {
		os.Exit(2)
	}
	sub := args[0]
	if path := os.Getenv("FAKE_SEI_MARKER"); path != "" {
		if f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o600); err == nil {
			fmt.Fprintln(f, strings.Join(args[:min(2, len(args))], " "))
			f.Close()
		}
	}
	if os.Getenv("FAKE_SEI_FAIL") == sub {
		fmt.Fprintln(os.Stderr, "fake failure at /secret/path")
		os.Exit(1)
	}
	if noise := os.Getenv("FAKE_SEI_STDERR"); noise != "" {
		fmt.Fprintln(os.Stderr, noise)
	}
	if sub == "init" {
		if p := os.Getenv("FAKE_SEI_WRITE_CHECKOUT"); p != "" {
			_ = os.WriteFile(p, []byte("written by the product"), 0o644)
		}
		if p := os.Getenv("FAKE_SEI_APPEND_TRACKED"); p != "" {
			if f, err := os.OpenFile(p, os.O_APPEND|os.O_WRONLY, 0); err == nil {
				f.WriteString("appended\n")
				f.Close()
			}
		}
		if p := os.Getenv("FAKE_SEI_SWAP"); p != "" {
			if from, to, ok := strings.Cut(p, "|"); ok {
				_ = os.Remove(from)
				_ = os.WriteFile(to, []byte("package main\n"), 0o644)
			}
		}
		if os.Getenv("FAKE_SEI_WRITE_CWD") != "" {
			_ = os.WriteFile(".sei", []byte("x"), 0o644)
		}
	}
	root := first(args, "--data-root")
	switch sub {
	case "init":
		_ = os.MkdirAll(root, 0o755)
		_ = os.WriteFile(filepath.Join(root, "bundle"), []byte(first(args, "--bundle-id")), 0o644)
	case "add":
		rec := map[string]any{"kind": args[1], "id": first(args, "--id"), "statement": first(args, "--statement"),
			"unresolved": values(args, "--unresolved"), "recommendation": values(args, "--recommendation"), "responsible": values(args, "--responsible")}
		line, _ := json.Marshal(rec)
		f, err := os.OpenFile(filepath.Join(root, "records.jsonl"), os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
		if err != nil {
			os.Exit(1)
		}
		f.Write(append(line, '\n'))
		f.Close()
	case "resume":
		if os.Getenv("FAKE_SEI_BREAK_RESUME") != "" {
			fmt.Println("not json")
			return
		}
		bundle, _ := os.ReadFile(filepath.Join(root, "bundle"))
		raw, _ := os.ReadFile(filepath.Join(root, "records.jsonl"))
		decisions := []map[string]any{}
		unresolved := []map[string]any{}
		count := 0
		for _, line := range strings.Split(strings.TrimSpace(string(raw)), "\n") {
			var rec struct {
				Kind, ID, Statement                string
				Unresolved, Recommendation, Responsible []string
			}
			if json.Unmarshal([]byte(line), &rec) != nil {
				continue
			}
			count++
			if rec.Kind != "decision" {
				continue
			}
			recs := []string{}
			for _, r := range rec.Recommendation {
				recs = append(recs, "recommendation:"+r)
			}
			decisions = append(decisions, map[string]any{"id": rec.ID, "statement": rec.Statement, "recommendations": recs, "responsible": rec.Responsible})
			for _, u := range rec.Unresolved {
				unresolved = append(unresolved, map[string]any{"ref": u, "left_open_by_decision": rec.ID})
			}
		}
		json.NewEncoder(os.Stdout).Encode(map[string]any{"bundle_id": string(bundle), "record_count": count, "decisions": decisions,
			"unresolved": unresolved, "not_verified_record_count": 0, "recommendations_not_yet_relied_on": []any{}, "recommendations_relied_on": []any{}})
	case "verify":
		raw, err := os.ReadFile(first(args, "--input"))
		if err != nil {
			os.Exit(1)
		}
		var bundle map[string]json.RawMessage
		var id string
		var records []json.RawMessage
		if json.Unmarshal(raw, &bundle) != nil || json.Unmarshal(bundle["bundle_id"], &id) != nil || json.Unmarshal(bundle["records"], &records) != nil {
			os.Exit(1)
		}
		json.NewEncoder(os.Stdout).Encode(map[string]any{"bundle_id": id, "record_count": len(records), "validated_count": len(records), "not_verified_count": 0})
	case "version":
		if v := os.Getenv("FAKE_SEI_VERSION_OUT"); v != "" {
			fmt.Print(v)
			return
		}
		fmt.Println("{\"commit\":\"unknown\",\"target\":\"unknown\",\"version\":\"dev\"}")
	default:
		os.Exit(2)
	}
}
`

// pinShimSource logs every `go run` and delegates everything else to the real go; with
// SHIM_DENY set, `go run` fails.
const pinShimSource = `#!/bin/sh
if [ "$1" = run ]; then
  echo "$*" >> "$SHIM_LOG"
  if [ -n "$SHIM_DENY" ]; then exit 97; fi
fi
exec "%s" "$@"
`

type pinEnv struct {
	runLog string // file that lists every `go run` the shim saw
}

// pinSetup makes the environment of the fake tests reproducible: local toolchain, no
// inherited GOFLAGS/GOWORK, no git redirection, no user git configuration. With shim,
// `go` on PATH is a script that records (and, when deny, refuses) `go run`; without git,
// git is not on PATH.
func pinSetup(t *testing.T, shim, deny, withGit bool) pinEnv {
	t.Helper()
	goPath, err := exec.LookPath("go")
	if err != nil {
		t.Skip("go is not available")
	}
	gitPath, err := exec.LookPath("git")
	if err != nil {
		t.Skip("git is not available")
	}
	t.Setenv("GOTOOLCHAIN", "local")
	t.Setenv("GOFLAGS", "")
	t.Setenv("GOWORK", "")
	t.Setenv("GIT_CONFIG_GLOBAL", os.DevNull)
	t.Setenv("GIT_CONFIG_NOSYSTEM", "1")
	for _, name := range append(append([]string{}, pinGitRedirectingEnv...), "TAI_SEI_EXPECT_COMMIT", "TAI_SEI_EXPECT_GO_VERSION", "SEI_DATA_ROOT",
		"GOTOOLDIR", "GOCACHEPROG", "GOROOT", "FAKE_SEI_MARKER", "FAKE_SEI_FAIL", "FAKE_SEI_STDERR", "FAKE_SEI_WRITE_CHECKOUT", "FAKE_SEI_APPEND_TRACKED",
		"FAKE_SEI_WRITE_CWD", "FAKE_SEI_BREAK_RESUME", "FAKE_SEI_VERSION_OUT", "FAKE_SEI_SWAP") {
		old, had := os.LookupEnv(name)
		os.Unsetenv(name)
		if had {
			name, old := name, old
			t.Cleanup(func() { os.Setenv(name, old) })
		}
	}
	env := pinEnv{}
	if shim {
		if runtime.GOOS == "windows" {
			t.Skip("the go shim is a shell script")
		}
		dir := t.TempDir()
		env.runLog = filepath.Join(dir, "go-run.log")
		script := strings.Replace(pinShimSource, "%s", goPath, 1)
		if err := os.WriteFile(filepath.Join(dir, "go"), []byte(script), 0o755); err != nil {
			t.Fatal(err)
		}
		t.Setenv("SHIM_LOG", env.runLog)
		if deny {
			t.Setenv("SHIM_DENY", "1")
		}
		path := dir
		if withGit {
			path += string(os.PathListSeparator) + filepath.Dir(gitPath) + string(os.PathListSeparator) + os.Getenv("PATH")
		}
		t.Setenv("PATH", path)
	}
	return env
}

func (e pinEnv) goRuns(t *testing.T) string {
	t.Helper()
	raw, _ := os.ReadFile(e.runLog)
	return string(raw)
}

func pinGit(t *testing.T, dir string, args ...string) string {
	t.Helper()
	cmd := exec.Command("git", args...)
	cmd.Dir = dir
	out, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("git %v: %v: %s", args, err, out)
	}
	return strings.TrimSpace(string(out))
}

// pinFakeRepo makes a git checkout whose runtime/go holds the fake sei, and returns its
// root and HEAD. extra replaces or adds files (path relative to the root, slash separated).
func pinFakeRepo(t *testing.T, extra map[string]string) (string, string) {
	t.Helper()
	root := t.TempDir()
	if resolved, err := filepath.EvalSymlinks(root); err == nil {
		root = resolved
	}
	files := map[string]string{
		"README.md":                  "# fake sei\n",
		"runtime/go/go.mod":          "module fakesei\n\ngo 1.21\n",
		"runtime/go/cmd/sei/main.go": pinFakeSEI,
		"runtime/go/notes.txt":       "not a build input\n",
	}
	for name, content := range extra {
		files[name] = content
	}
	for name, content := range files {
		path := filepath.Join(root, filepath.FromSlash(name))
		if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	pinGit(t, root, "init", "-q")
	pinGit(t, root, "config", "core.autocrlf", "false")
	pinGit(t, root, "add", "-A")
	pinGit(t, root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false", "commit", "-q", "-m", "fake")
	return root, pinGit(t, root, "rev-parse", "HEAD")
}

func pinGoToken(t *testing.T) string {
	t.Helper()
	fields := strings.Fields(pinCommandOutput(context.Background(), os.TempDir(), os.Environ(), "go", "version"))
	if len(fields) < 3 {
		t.Skip("go version cannot be read")
	}
	return fields[2]
}

func pinMarker(t *testing.T) string {
	t.Helper()
	path := filepath.Join(t.TempDir(), "marker")
	t.Setenv("FAKE_SEI_MARKER", path)
	return path
}

func pinStarted(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}

func pinRun(t *testing.T, root string, options Options) Receipt {
	t.Helper()
	return RunWithOptions(context.Background(), root, "", options)
}

func pinJSON(t *testing.T, value any) string {
	t.Helper()
	raw, err := json.Marshal(value)
	if err != nil {
		t.Fatal(err)
	}
	return string(raw)
}

func TestPinFakeUnpinnedRecordsAndDoesNotCheck(t *testing.T) {
	pinSetup(t, false, false, true)
	root, head := pinFakeRepo(t, nil)
	// A dirty checkout and an unrelated expectation-free run: nothing is enforced.
	if err := os.WriteFile(filepath.Join(root, "README.md"), []byte("dirty\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	receipt := pinRun(t, root, Options{})
	if !receipt.Passed || receipt.Pin.Checked || receipt.Pin.Result != "not-checked" || receipt.Binary.Status != "not-built" {
		t.Fatalf("an unpinned run only records: %+v", receipt)
	}
	if receipt.Pin.Commit.Actual != head || receipt.Pin.SourceTree.TrackedChanges != 1 || receipt.Checkout.Before.TrackedChanges != 1 || receipt.Checkout.Status != "unchanged" {
		t.Fatalf("facts are recorded: %+v", receipt.PinReport)
	}
	if receipt.SeiCommit != head || receipt.RecordCount != 3 || !receipt.ProvisionalApproved {
		t.Fatalf("unpinned behaviour changed: %+v", receipt)
	}
}

func TestPinFakeMatchPassesAndRecordsExpectations(t *testing.T) {
	env := pinSetup(t, true, true, true)
	root, head := pinFakeRepo(t, nil)
	receipt := pinRun(t, root, Options{ExpectCommit: head, ExpectGoVersion: pinGoToken(t)})
	if !receipt.Passed || receipt.Pin.Result != "match" || !receipt.Pin.Checked || receipt.Checkout.Status != "unchanged" {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
	if receipt.Binary.Status != "built" || !strings.HasPrefix(receipt.Binary.Sha256, "sha256:") || receipt.Binary.ReportedCommit.Status != "not-reported" ||
		receipt.Binary.VersionLine.Version != "dev" || len(receipt.Toolchain.Enforced) != 3 || receipt.Toolchain.Build != "built" ||
		receipt.Toolchain.GoDirective != "1.21" || receipt.Binary.KeptAt != "" {
		t.Fatalf("%s", pinJSON(t, receipt.PinReport))
	}
	if receipt.SeiCommit != head || receipt.RecordCount != 3 || receipt.GoVersion == "" {
		t.Fatalf("%+v", receipt)
	}
	if runs := env.goRuns(t); runs != "" {
		t.Fatalf("a pinned run must never use go run: %s", runs)
	}
}

func TestPinFakeCommitMismatchFailsBeforeAnySEICodeRuns(t *testing.T) {
	env := pinSetup(t, true, true, true)
	root, head := pinFakeRepo(t, nil)
	marker := pinMarker(t)
	wrong := strings.Repeat("0", 40)
	receipt := pinRun(t, root, Options{ExpectCommit: wrong})
	if receipt.Passed || receipt.Pin.Result != "mismatch" || receipt.Binary.Status != "not-built" || receipt.Toolchain.Build != "not-run" {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
	if pinStarted(marker) || env.goRuns(t) != "" {
		t.Fatal("SEI code started although the pin did not match")
	}
	if !strings.Contains(receipt.Reason, wrong) || !strings.Contains(receipt.Reason, head) || strings.Contains(receipt.Reason, root) {
		t.Fatalf("the reason names the expected and measured hash only: %q", receipt.Reason)
	}
}

func TestPinFakeGoVersionMismatchFailsBeforeBuild(t *testing.T) {
	pinSetup(t, true, true, true)
	root, head := pinFakeRepo(t, nil)
	marker := pinMarker(t)
	receipt := pinRun(t, root, Options{ExpectCommit: head, ExpectGoVersion: "go1.1.1"})
	if receipt.Passed || receipt.Pin.Result != "mismatch" || receipt.Pin.GoVersion.Status != "mismatch" || receipt.Toolchain.Build != "not-run" || pinStarted(marker) {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
}

func TestPinFakeTrackedChangeKinds(t *testing.T) {
	cases := map[string]func(t *testing.T, root string){
		"unstaged edit": func(t *testing.T, root string) {
			os.WriteFile(filepath.Join(root, "README.md"), []byte("edited and longer\n"), 0o644)
		},
		"staged edit": func(t *testing.T, root string) {
			os.WriteFile(filepath.Join(root, "README.md"), []byte("edited and longer\n"), 0o644)
			pinGit(t, root, "add", "README.md")
		},
		"deleted file": func(t *testing.T, root string) { os.Remove(filepath.Join(root, "README.md")) },
		"same-size edit right after the commit": func(t *testing.T, root string) {
			os.WriteFile(filepath.Join(root, "README.md"), []byte("# fake SEI\n"), 0o644)
		},
		"edit of a source file under runtime/go": func(t *testing.T, root string) {
			f, _ := os.OpenFile(filepath.Join(root, "runtime", "go", "cmd", "sei", "main.go"), os.O_APPEND|os.O_WRONLY, 0)
			f.WriteString("\n// edited\n")
			f.Close()
		},
	}
	for name, edit := range cases {
		t.Run(name, func(t *testing.T) {
			pinSetup(t, true, true, true)
			root, head := pinFakeRepo(t, nil)
			marker := pinMarker(t)
			edit(t, root)
			receipt := pinRun(t, root, Options{ExpectCommit: head})
			if receipt.Passed || receipt.Pin.Result != "mismatch" || receipt.Pin.SourceTree.Status != "tracked-changes" || receipt.Pin.SourceTree.TrackedChanges != 1 || pinStarted(marker) {
				t.Fatalf("%s", pinJSON(t, receipt))
			}
		})
	}
}

func TestPinFakeUntrackedGoInputsUnderRuntimeGoFail(t *testing.T) {
	cases := map[string]func(t *testing.T, root string){
		"untracked go file": func(t *testing.T, root string) {
			os.WriteFile(filepath.Join(root, "runtime", "go", "cmd", "sei", "extra.go"), []byte("package main\n"), 0o644)
		},
		"nested go.mod": func(t *testing.T, root string) {
			os.MkdirAll(filepath.Join(root, "runtime", "go", "cmd", "sub"), 0o755)
			os.WriteFile(filepath.Join(root, "runtime", "go", "cmd", "sub", "go.mod"), []byte("module x\n"), 0o644)
		},
		"vendor directory": func(t *testing.T, root string) {
			os.MkdirAll(filepath.Join(root, "runtime", "go", "vendor", "x"), 0o755)
			os.WriteFile(filepath.Join(root, "runtime", "go", "vendor", "x", "x.txt"), []byte("x"), 0o644)
		},
		"ignored go file": func(t *testing.T, root string) {
			os.WriteFile(filepath.Join(root, ".git", "info", "exclude"), []byte("hidden_*.go\n"), 0o644)
			os.WriteFile(filepath.Join(root, "runtime", "go", "cmd", "sei", "hidden_x.go"), []byte("package main\n"), 0o644)
		},
	}
	for name, add := range cases {
		t.Run(name, func(t *testing.T) {
			pinSetup(t, true, true, true)
			root, head := pinFakeRepo(t, nil)
			marker := pinMarker(t)
			add(t, root)
			receipt := pinRun(t, root, Options{ExpectCommit: head})
			if receipt.Passed || receipt.Pin.Result != "mismatch" || receipt.Pin.SourceTree.Status != "untracked-build-inputs" || receipt.Pin.SourceTree.UntrackedBuildInputs < 1 || pinStarted(marker) {
				t.Fatalf("%s", pinJSON(t, receipt))
			}
		})
	}
}

func TestPinFakeUntrackedNonInputsAndFilesOutsideRuntimeGoDoNotFail(t *testing.T) {
	pinSetup(t, true, true, true)
	root, head := pinFakeRepo(t, nil)
	os.WriteFile(filepath.Join(root, "runtime", "go", "scratch.txt"), []byte("x"), 0o644)
	os.WriteFile(filepath.Join(root, "tool.py"), []byte("x"), 0o644)
	os.WriteFile(filepath.Join(root, "outside.go"), []byte("package outside\n"), 0o644) // not in the module
	os.WriteFile(filepath.Join(root, ".git", "info", "exclude"), []byte("cache/\n"), 0o644)
	os.MkdirAll(filepath.Join(root, "cache"), 0o755)
	os.WriteFile(filepath.Join(root, "cache", "x.pyc"), []byte("x"), 0o644)
	receipt := pinRun(t, root, Options{ExpectCommit: head})
	if !receipt.Passed || receipt.Pin.Result != "match" || receipt.Pin.SourceTree.UntrackedBuildInputs != 0 || receipt.Pin.SourceTree.UntrackedFiles < 3 {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
}

func TestPinFakeHiddenFlagsMakeThePinUnavailable(t *testing.T) {
	for _, flag := range []string{"--assume-unchanged", "--skip-worktree"} {
		t.Run(flag, func(t *testing.T) {
			pinSetup(t, true, true, true)
			root, head := pinFakeRepo(t, nil)
			marker := pinMarker(t)
			pinGit(t, root, "update-index", flag, "README.md")
			os.WriteFile(filepath.Join(root, "README.md"), []byte("hidden edit\n"), 0o644)
			receipt := pinRun(t, root, Options{ExpectCommit: head})
			if receipt.Passed || receipt.Pin.Result != "unavailable" || receipt.Pin.SourceTree.HiddenFlaggedFiles != 1 || pinStarted(marker) {
				t.Fatalf("%s", pinJSON(t, receipt))
			}
		})
	}
}

func TestPinFakeGoEnvironmentIsEnforcedAndOnlyFlagNamesAreRecorded(t *testing.T) {
	pinSetup(t, true, true, true)
	root, head := pinFakeRepo(t, nil)
	other := t.TempDir()
	flags := "-tags=other -modfile=" + filepath.Join(other, "evil.mod") + " -overlay=" + filepath.Join(other, "overlay.json")
	t.Setenv("GOFLAGS", flags)
	t.Setenv("GOTOOLCHAIN", "auto")
	t.Setenv("GOWORK", filepath.Join(other, "go.work"))
	t.Setenv("CGO_ENABLED", "0")
	receipt := pinRun(t, root, Options{ExpectCommit: head})
	if !receipt.Passed {
		t.Fatalf("an inherited GOFLAGS is replaced by the pinned value, not a reason to fail: %s", pinJSON(t, receipt))
	}
	tool := receipt.Toolchain
	if tool.GoToolchainEnv != "auto" || strings.Join(tool.GoFlagNames, " ") != "-tags -modfile -overlay" || len(tool.Enforced) != 3 ||
		len(tool.InheritedSettings) != 1 || tool.InheritedSettings[0] != "CGO_ENABLED" {
		t.Fatalf("%s", pinJSON(t, tool))
	}
	encoded := pinJSON(t, receipt)
	for _, leak := range []string{other, "evil.mod", "overlay.json", "go.work", root, "tai-sei-"} {
		if strings.Contains(encoded, leak) {
			t.Fatalf("the receipt leaks %q: %s", leak, encoded)
		}
	}
}

func TestPinFakeUnsupportedCompilerSettingsMakeThePinUnavailable(t *testing.T) {
	for _, name := range []string{"GOTOOLDIR", "GOCACHEPROG"} {
		t.Run(name, func(t *testing.T) {
			pinSetup(t, true, true, true)
			root, head := pinFakeRepo(t, nil)
			marker := pinMarker(t)
			t.Setenv(name, filepath.Join(t.TempDir(), "x"))
			receipt := pinRun(t, root, Options{ExpectCommit: head})
			if receipt.Passed || receipt.Pin.Result != "unavailable" || !strings.Contains(receipt.Reason, name) || pinStarted(marker) || strings.Contains(pinJSON(t, receipt), os.Getenv(name)) {
				t.Fatalf("%s", pinJSON(t, receipt))
			}
		})
	}
}

func TestPinFakeBuildFailureNamesTheGoDirectiveOnly(t *testing.T) {
	pinSetup(t, true, true, true)
	root, head := pinFakeRepo(t, map[string]string{"runtime/go/go.mod": "module fakesei\n\ngo 1.99\n"})
	marker := pinMarker(t)
	receipt := pinRun(t, root, Options{ExpectCommit: head})
	if receipt.Passed || receipt.Toolchain.Build != "failed" || receipt.Binary.Status != "failed" || pinStarted(marker) ||
		!strings.Contains(receipt.Reason, "go directive 1.99") || strings.Contains(pinJSON(t, receipt), root) {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
}

func TestPinFakeVersionDisagreementFailsPinnedOnly(t *testing.T) {
	cases := map[string]string{
		"another commit": `{"commit":"` + strings.Repeat("a", 40) + `","target":"t","version":"dev"}`,
		"not json":       "dev",
		"no version key": `{"commit":"unknown"}`,
	}
	for name, out := range cases {
		t.Run(name, func(t *testing.T) {
			pinSetup(t, true, true, true)
			root, head := pinFakeRepo(t, nil)
			marker := pinMarker(t)
			t.Setenv("FAKE_SEI_VERSION_OUT", out)
			receipt := pinRun(t, root, Options{ExpectCommit: head})
			raw, _ := os.ReadFile(marker)
			if receipt.Passed || strings.Contains(string(raw), "init") {
				t.Fatalf("a disagreeing version must stop the run before init: %s", pinJSON(t, receipt))
			}
		})
	}
	t.Run("commit that equals HEAD", func(t *testing.T) {
		pinSetup(t, true, true, true)
		root, head := pinFakeRepo(t, nil)
		t.Setenv("FAKE_SEI_VERSION_OUT", `{"commit":"`+head+`","target":"t","version":"dev"}`)
		receipt := pinRun(t, root, Options{ExpectCommit: head})
		if !receipt.Passed || receipt.Binary.ReportedCommit.Status != "match" {
			t.Fatalf("%s", pinJSON(t, receipt))
		}
	})
	t.Run("unpinned never calls version", func(t *testing.T) {
		pinSetup(t, false, false, true)
		root, _ := pinFakeRepo(t, nil)
		marker := pinMarker(t)
		t.Setenv("FAKE_SEI_VERSION_OUT", "garbage")
		receipt := pinRun(t, root, Options{})
		raw, _ := os.ReadFile(marker)
		if !receipt.Passed || strings.Contains(string(raw), "version") {
			t.Fatalf("%s", pinJSON(t, receipt))
		}
	})
}

func TestPinFakeProductWritingIntoTheCheckoutIsDetected(t *testing.T) {
	cases := map[string]func(root string){
		"new file":            func(root string) { t.Setenv("FAKE_SEI_WRITE_CHECKOUT", filepath.Join(root, "created.txt")) },
		"append to a tracked": func(root string) { t.Setenv("FAKE_SEI_APPEND_TRACKED", filepath.Join(root, "README.md")) },
	}
	for name, arm := range cases {
		t.Run(name+" pinned", func(t *testing.T) {
			pinSetup(t, true, true, true)
			root, head := pinFakeRepo(t, nil)
			arm(root)
			receipt := pinRun(t, root, Options{ExpectCommit: head})
			if receipt.Passed || receipt.Checkout.Status != "changed" || !strings.Contains(receipt.Reason, "changed the SEI checkout") || strings.Contains(receipt.Reason, root) {
				t.Fatalf("%s", pinJSON(t, receipt))
			}
		})
		t.Run(name+" unpinned only records", func(t *testing.T) {
			pinSetup(t, false, false, true)
			root, _ := pinFakeRepo(t, nil)
			arm(root)
			receipt := pinRun(t, root, Options{})
			if !receipt.Passed || receipt.Checkout.Status != "changed" {
				t.Fatalf("a default run records the change and keeps passed: %s", pinJSON(t, receipt))
			}
		})
	}
}

func TestPinFakeProductWritingOutsideTheStoreFailsPinned(t *testing.T) {
	pinSetup(t, true, true, true)
	root, head := pinFakeRepo(t, nil)
	t.Setenv("FAKE_SEI_WRITE_CWD", "1")
	receipt := pinRun(t, root, Options{ExpectCommit: head})
	if receipt.Passed || !strings.Contains(receipt.Reason, "wrote outside the store") {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
}

func TestPinFakeBuildOutRejectsCheckoutAndSymlink(t *testing.T) {
	pinSetup(t, true, true, true)
	root, head := pinFakeRepo(t, nil)
	marker := pinMarker(t)
	link := filepath.Join(t.TempDir(), "link")
	if err := os.Symlink(filepath.Join(root, "runtime"), link); err != nil {
		t.Skip("symlinks are not available")
	}
	for _, dir := range []string{filepath.Join(root, "bin"), link, filepath.Join(link, "x")} {
		receipt := pinRun(t, root, Options{ExpectCommit: head, BuildOut: dir})
		if receipt.Passed || !strings.Contains(receipt.Reason, "build-out must be outside") || pinStarted(marker) {
			t.Fatalf("%s: %s", dir, pinJSON(t, receipt))
		}
	}
	if status := pinGit(t, root, "status", "--porcelain", "--ignored"); status != "" {
		t.Fatalf("the checkout was written: %s", status)
	}
	out := filepath.Join(t.TempDir(), "kept")
	receipt := pinRun(t, root, Options{ExpectCommit: head, BuildOut: out})
	if !receipt.Passed || receipt.Binary.KeptAt != "build-out" || strings.Contains(pinJSON(t, receipt), out) {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
	if _, err := os.Stat(filepath.Join(out, "sei"+pinSuffix())); err != nil {
		t.Fatalf("the built sei is kept in build-out: %v", err)
	}
	if status := pinGit(t, root, "status", "--porcelain", "--ignored"); status != "" {
		t.Fatalf("the checkout was written: %s", status)
	}
	// build-out is meaningless without an expectation
	if receipt := pinRun(t, root, Options{BuildOut: out}); receipt.Passed {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
}

func TestPinFakeFailureReceiptsKeepPassedFalseAndNoLocalText(t *testing.T) {
	cases := map[string]func(t *testing.T){
		"sei init fails":     func(t *testing.T) { t.Setenv("FAKE_SEI_FAIL", "init") },
		"sei resume fails":   func(t *testing.T) { t.Setenv("FAKE_SEI_FAIL", "resume") },
		"sei add fails":      func(t *testing.T) { t.Setenv("FAKE_SEI_FAIL", "add") },
		"resume is not json": func(t *testing.T) { t.Setenv("FAKE_SEI_BREAK_RESUME", "1") },
	}
	for name, arm := range cases {
		t.Run(name, func(t *testing.T) {
			pinSetup(t, true, true, true)
			root, head := pinFakeRepo(t, nil)
			arm(t)
			receipt := pinRun(t, root, Options{ExpectCommit: head})
			encoded := pinJSON(t, receipt)
			if receipt.Passed || receipt.Reason == "" {
				t.Fatalf("%s", encoded)
			}
			for _, leak := range []string{root, os.TempDir(), "tai-sei-", "/secret/path", "fake failure"} {
				if strings.Contains(encoded, leak) {
					t.Fatalf("the failure receipt leaks %q: %s", leak, encoded)
				}
			}
		})
	}
	t.Run("runtime is missing", func(t *testing.T) {
		pinSetup(t, true, true, true)
		receipt := pinRun(t, t.TempDir(), Options{ExpectCommit: strings.Repeat("1", 40)})
		if receipt.Passed || receipt.Reason != "SEI runtime is unavailable" {
			t.Fatalf("%s", pinJSON(t, receipt))
		}
	})
}

func TestPinFakeStdoutOnlyIsParsed(t *testing.T) {
	pinSetup(t, true, true, true)
	root, head := pinFakeRepo(t, nil)
	t.Setenv("FAKE_SEI_STDERR", "go: downloading example.invalid/x v1.0.0")
	receipt := pinRun(t, root, Options{ExpectCommit: head})
	if !receipt.Passed {
		t.Fatalf("noise on standard error must not reach the JSON: %s", pinJSON(t, receipt))
	}
}

func TestPinFakeGitEnvironmentCannotRedirectTheQueries(t *testing.T) {
	pinSetup(t, true, true, true)
	root, head := pinFakeRepo(t, nil)
	other, otherHead := pinFakeRepo(t, map[string]string{"other.txt": "other\n"})
	if other == root || otherHead == head {
		t.Fatal("the two repositories must differ")
	}
	t.Setenv("GIT_DIR", filepath.Join(other, ".git"))
	t.Setenv("GIT_WORK_TREE", other)
	t.Setenv("GIT_INDEX_FILE", filepath.Join(other, ".git", "index"))
	t.Setenv("GIT_COMMON_DIR", filepath.Join(other, ".git"))
	receipt := pinRun(t, root, Options{ExpectCommit: head})
	if !receipt.Passed || receipt.SeiCommit != head {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
}

func TestPinFakeReplaceRefsCannotHideATrackedEdit(t *testing.T) {
	pinSetup(t, true, true, true)
	root, head := pinFakeRepo(t, nil)
	marker := pinMarker(t)
	// Make a commit that has the edited README, and let refs/replace swap it for HEAD.
	os.WriteFile(filepath.Join(root, "README.md"), []byte("replaced\n"), 0o644)
	pinGit(t, root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false", "commit", "-q", "-a", "-m", "edit")
	edited := pinGit(t, root, "rev-parse", "HEAD")
	pinGit(t, root, "reset", "-q", "--hard", head)
	pinGit(t, root, "replace", head, edited)
	// The work tree now shows the replacement's tree through ordinary git commands.
	if got := pinGit(t, root, "show", "HEAD:README.md"); got != "replaced" {
		t.Skipf("refs/replace did not take effect: %q", got)
	}
	os.WriteFile(filepath.Join(root, "README.md"), []byte("replaced\n"), 0o644)
	receipt := pinRun(t, root, Options{ExpectCommit: head})
	if receipt.Passed || receipt.Pin.SourceTree.TrackedChanges < 1 || pinStarted(marker) {
		t.Fatalf("--no-replace-objects must keep the edit visible: %s", pinJSON(t, receipt))
	}
}

func TestPinFakeSubdirectoryOfAnotherRepositoryAndNoGitAreUnavailable(t *testing.T) {
	t.Run("subdirectory", func(t *testing.T) {
		pinSetup(t, true, false, true)
		outer := t.TempDir()
		pinGit(t, outer, "init", "-q")
		inner := filepath.Join(outer, "sei")
		for name, content := range map[string]string{"runtime/go/go.mod": "module fakesei\n\ngo 1.21\n", "runtime/go/cmd/sei/main.go": pinFakeSEI} {
			path := filepath.Join(inner, filepath.FromSlash(name))
			os.MkdirAll(filepath.Dir(path), 0o755)
			os.WriteFile(path, []byte(content), 0o644)
		}
		pinGit(t, outer, "add", "-A")
		pinGit(t, outer, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false", "commit", "-q", "-m", "outer")
		outerHead := pinGit(t, outer, "rev-parse", "HEAD")
		marker := pinMarker(t)
		receipt := pinRun(t, inner, Options{ExpectCommit: outerHead})
		if receipt.Passed || receipt.Pin.Result != "unavailable" || receipt.Pin.Commit.Actual != "" || pinStarted(marker) {
			t.Fatalf("an outer repository's commit must not be borrowed: %s", pinJSON(t, receipt))
		}
		// default: recorded as unavailable, the run goes on
		receipt = pinRun(t, inner, Options{})
		if !receipt.Passed || receipt.Checkout.Status != "unavailable" {
			t.Fatalf("%s", pinJSON(t, receipt))
		}
	})
	t.Run("git is not on PATH", func(t *testing.T) {
		pinSetup(t, true, false, false)
		root := t.TempDir()
		for name, content := range map[string]string{"runtime/go/go.mod": "module fakesei\n\ngo 1.21\n", "runtime/go/cmd/sei/main.go": pinFakeSEI} {
			path := filepath.Join(root, filepath.FromSlash(name))
			os.MkdirAll(filepath.Dir(path), 0o755)
			os.WriteFile(path, []byte(content), 0o644)
		}
		receipt := pinRun(t, root, Options{ExpectCommit: strings.Repeat("2", 40)})
		if receipt.Passed || receipt.Pin.Result != "unavailable" {
			t.Fatalf("%s", pinJSON(t, receipt))
		}
		receipt = pinRun(t, root, Options{})
		if !receipt.Passed || receipt.Checkout.Status != "unavailable" || receipt.Pin.Result != "not-checked" {
			t.Fatalf("a default run goes on without git: %s", pinJSON(t, receipt))
		}
	})
}

func TestPinFakeGatherFactsLeavesTheCheckoutGitDirAlone(t *testing.T) {
	pinSetup(t, false, false, true)
	root, _ := pinFakeRepo(t, nil)
	index := filepath.Join(root, ".git", "index")
	beforeBytes, _ := os.ReadFile(index)
	beforeInfo, _ := os.Stat(index)
	// make the stat data of the work tree stale so that a refresh would rewrite the index
	os.Chtimes(filepath.Join(root, "README.md"), beforeInfo.ModTime().Add(-3600e9), beforeInfo.ModTime().Add(-3600e9))
	facts := gatherFacts(context.Background(), root)
	if facts.Commit == "" || facts.TreeStatus != "clean" {
		t.Fatalf("%+v", facts)
	}
	afterBytes, _ := os.ReadFile(index)
	afterInfo, _ := os.Stat(index)
	if string(beforeBytes) != string(afterBytes) || !beforeInfo.ModTime().Equal(afterInfo.ModTime()) {
		t.Fatal("gatherFacts modified the index of the checkout")
	}
}

func TestPinFakeIndexCopyKeepsTheOriginalMtime(t *testing.T) {
	pinSetup(t, false, false, true)
	root, _ := pinFakeRepo(t, nil)
	index := filepath.Join(root, ".git", "index")
	old := mustTime(t, 1700000000)
	if err := os.Chtimes(index, old, old); err != nil {
		t.Fatal(err)
	}
	copyPath, cleanup, err := pinCopyIndex(context.Background(), root)
	if err != nil {
		t.Fatal(err)
	}
	defer cleanup()
	info, err := os.Stat(copyPath)
	if err != nil || !info.ModTime().Equal(old) {
		t.Fatalf("the copy must keep the mtime of the original index (racy-git): %v %v", info.ModTime(), err)
	}
}

func TestPinFakeFailClosedWhenAPinnedContextMeetsAnotherCommandShape(t *testing.T) {
	env := pinSetup(t, true, true, true)
	root, head := pinFakeRepo(t, nil)
	ctx, session := beginPin(context.Background(), root, Options{ExpectCommit: head})
	defer session.finish(ctx)
	if session.refusal != "" {
		t.Fatal(session.refusal)
	}
	for _, args := range [][]string{{"run", "./cmd/sei/", "version"}, {"run", "./other", "version"}, {"build", "./cmd/sei"}, {"run", "./cmd/sei"}, {}} {
		if _, err := run(ctx, root, args...); err == nil || !strings.Contains(err.Error(), "pinned run refused") {
			t.Fatalf("%v: a pinned context must not fall back to go run: %v", args, err)
		}
		if _, err := runOutput(ctx, root, args...); err == nil {
			t.Fatalf("%v: runOutput must fail closed too", args)
		}
	}
	if runs := env.goRuns(t); runs != "" {
		t.Fatalf("go run was used: %s", runs)
	}
}

func TestPinFakeContextOverrideDoesNotLeakBetweenRuns(t *testing.T) {
	env := pinSetup(t, true, false, true)
	root, head := pinFakeRepo(t, nil)
	if receipt := pinRun(t, root, Options{ExpectCommit: head}); !receipt.Passed {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
	if env.goRuns(t) != "" {
		t.Fatal("the pinned run used go run")
	}
	if receipt := pinRun(t, root, Options{}); !receipt.Passed || receipt.Binary.Status != "not-built" {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
	if env.goRuns(t) == "" {
		t.Fatal("an unpinned run after a pinned run must use the old go run path")
	}
}

func TestPinFakeVariantsAreCoveredByThePin(t *testing.T) {
	for _, variant := range []string{"scn002-approvals", "scn002-rejections", "b"} {
		t.Run(variant, func(t *testing.T) {
			env := pinSetup(t, true, true, true)
			root, head := pinFakeRepo(t, nil)
			marker := pinMarker(t)
			receipt := RunWithOptions(context.Background(), root, variant, Options{ExpectCommit: strings.Repeat("3", 40)})
			if receipt.Passed || pinStarted(marker) || receipt.Pin.Result != "mismatch" {
				t.Fatalf("%s", pinJSON(t, receipt))
			}
			receipt = RunWithOptions(context.Background(), root, variant, Options{ExpectCommit: head})
			if receipt.Pin.Result != "match" || receipt.Binary.Status != "built" || env.goRuns(t) != "" {
				t.Fatalf("%s", pinJSON(t, receipt))
			}
		})
	}
}

func TestPinFakeBasisAndValidityModes(t *testing.T) {
	bundle := filepath.Join(t.TempDir(), "basis.json")
	validityBundle, validityTarget := filepath.Join("testdata", "validity", "t-a.json"), filepath.Join("testdata", "validity", "target-a.json")
	t.Run("basis mismatch stops before verify, no -out file", func(t *testing.T) {
		env := pinSetup(t, true, true, true)
		root, head := pinFakeRepo(t, nil)
		marker := pinMarker(t)
		if err := os.WriteFile(bundle, basisBundle(t, "v1", "sha256:"+strings.Repeat("a", 64), false), 0o600); err != nil {
			t.Fatal(err)
		}
		if _, err := inspectBasisPinned(context.Background(), root, bundle, Options{ExpectCommit: strings.Repeat("4", 40)}); err == nil || pinStarted(marker) {
			t.Fatalf("a pin mismatch must stop before verify: %v", err)
		}
		result, err := inspectBasisPinned(context.Background(), root, bundle, Options{ExpectCommit: head})
		if err != nil || result.Pin.Result != "match" || result.Binary.Status != "built" || result.SeiCommit != head || !result.RecordStructureChecked || result.BundleID != "basis-probe" {
			t.Fatalf("%v %s", err, pinJSON(t, result))
		}
		if env.goRuns(t) != "" {
			t.Fatal("go run was used")
		}
		unpinned, err := inspectBasisPinned(context.Background(), root, bundle, Options{})
		if err == nil && (unpinned.Pin.Checked || unpinned.Pin.Result != "not-checked") {
			t.Fatalf("%s", pinJSON(t, unpinned))
		}
	})
	t.Run("validity mismatch stops before verify", func(t *testing.T) {
		env := pinSetup(t, true, true, true)
		root, head := pinFakeRepo(t, nil)
		marker := pinMarker(t)
		if _, err := inspectValidityPinned(context.Background(), root, validityBundle, validityTarget, []string{nameD1}, Options{ExpectCommit: strings.Repeat("4", 40)}); err == nil || pinStarted(marker) {
			t.Fatalf("a pin mismatch must stop before verify: %v", err)
		}
		result, err := inspectValidityPinned(context.Background(), root, validityBundle, validityTarget, []string{nameD1}, Options{ExpectCommit: head})
		if err != nil || result.Pin.Result != "match" || result.SeiCommit != head || !result.RecordStructureChecked {
			t.Fatalf("%v %s", err, pinJSON(t, result))
		}
		if env.goRuns(t) != "" {
			t.Fatal("go run was used")
		}
	})
}
