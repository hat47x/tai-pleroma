package main

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
)

func TestGoEnvironmentIsEnforcedForPinnedRun(t *testing.T) {
	repo := newFakeEKI(t)
	// An ldflags value in the caller's environment changes the program that is built
	// without changing a file of the checkout. The fake prints the linked-in marker.
	t.Setenv("GOFLAGS", "-ldflags=-X=main.marker=injected")
	unpinned := Run(t.Context(), repo.Root)
	if unpinned.ControlVersion != "eki-control injected" || unpinned.Toolchain.GoFlags != "-ldflags=-X=main.marker=injected" {
		t.Fatalf("an unpinned run inherits and records the environment: %+v", unpinned)
	}
	pinned := run(t, repo.Root, Options{ExpectCommit: repo.Head})
	if !pinned.Passed || pinned.ControlVersion != "eki-control dev" {
		t.Fatalf("a pinned run must ignore the inherited GOFLAGS: %+v", pinned)
	}
	if pinned.Toolchain.GoFlags != "-ldflags=-X=main.marker=injected" || len(pinned.Toolchain.Enforced) != 3 {
		t.Fatalf("the inherited value stays recorded next to the enforced ones: %+v", pinned.Toolchain)
	}
}

func TestPinnedRunRefusesFlagsThatChangeWhatIsCompiled(t *testing.T) {
	// evaluatePin is exercised directly: an enforced GOFLAGS makes the inherited value
	// moot for the build, but a tool that reports -modfile or -overlay is not trusted.
	for _, flag := range []string{"-modfile=/x/go.mod", "-overlay=/x/o.json"} {
		pin, reasons := evaluatePin(Options{ExpectCommit: strings.Repeat("a", 40)},
			ekiFacts{Commit: strings.Repeat("a", 40), TreeStatus: "clean"}, Toolchain{GoFlags: flag})
		if pin.Result != "unavailable" || len(reasons) == 0 {
			t.Fatalf("%s: %+v %v", flag, pin, reasons)
		}
	}
}

func TestVersionOutputDisagreementFailsPinnedRunOnly(t *testing.T) {
	cases := map[string]struct {
		env       map[string]string
		agreement string
		reported  string
		reason    string
	}{
		"different version tokens":         {map[string]string{"TAI_FAKE_OUT_AGENT": "eki-agent 1.2.3\n"}, "disagree", "not-reported", "version output of eki-control and eki-agent disagree"},
		"output outside the expected form": {map[string]string{"TAI_FAKE_OUT_CONTROL": "hello\n"}, "disagree", "not-reported", "version output of eki-control and eki-agent disagree"},
		"names swapped":                    {map[string]string{"TAI_FAKE_OUT_CONTROL": "eki-agent dev\n"}, "disagree", "not-reported", "version output of eki-control and eki-agent disagree"},
		"reported commit differs":          {map[string]string{"TAI_FAKE_OUT_CONTROL": "eki-control dev commit=" + strings.Repeat("b", 40) + "\n", "TAI_FAKE_OUT_AGENT": "eki-agent dev commit=" + strings.Repeat("b", 40) + "\n"}, "disagree", "mismatch", "reports commit"},
	}
	for name, test := range cases {
		t.Run(name, func(t *testing.T) {
			repo := newFakeEKI(t)
			for key, value := range test.env {
				t.Setenv(key, value)
			}
			pinned := run(t, repo.Root, Options{ExpectCommit: repo.Head})
			assertFailsClosed(t, pinned, test.reason)
			if test.reported == "mismatch" && pinned.Binaries.ReportedCommit.Status != "mismatch" {
				t.Fatalf("reported commit: %+v", pinned.Binaries)
			}
			if test.reported == "not-reported" && pinned.Binaries.VersionAgreement != test.agreement {
				t.Fatalf("agreement: %+v", pinned.Binaries)
			}
			if pinned.Pin.Result != "match" {
				t.Fatalf("the pin itself held, the version output did not: %+v", pinned.Pin)
			}
			if test.reported == "not-reported" {
				unpinned := Run(t.Context(), repo.Root)
				if !unpinned.Passed {
					t.Fatalf("an unpinned run only records the disagreement: %+v", unpinned)
				}
			}
			assertNoLocalText(t, pinned, repo.Root)
		})
	}
}

func TestReportedCommitIsMatchedAgainstHead(t *testing.T) {
	repo := newFakeEKI(t)
	t.Setenv("TAI_FAKE_OUT_CONTROL", "eki-control dev commit="+repo.Head+"\n")
	t.Setenv("TAI_FAKE_OUT_AGENT", "eki-agent dev commit="+repo.Head+"\n")
	receipt := run(t, repo.Root, Options{ExpectCommit: repo.Head})
	if !receipt.Passed || receipt.Binaries.ReportedCommit.Status != "match" || receipt.Binaries.VersionAgreement != "agree" {
		t.Fatalf("a reported commit equal to HEAD: %+v", receipt.Binaries)
	}
}

func TestEmptyVersionOutputFailsEvenUnpinned(t *testing.T) {
	repo := newFakeEKI(t)
	t.Setenv("TAI_FAKE_OUT_CONTROL", "")
	receipt := Run(t.Context(), repo.Root)
	assertFailsClosed(t, receipt, "EKI version output is empty")
	if receipt.Binaries.VersionAgreement != "disagree" && receipt.Binaries.VersionAgreement != "not-run" {
		t.Fatalf("agreement: %+v", receipt.Binaries)
	}
}

func TestWriteIntoCheckoutIsDetected(t *testing.T) {
	cases := map[string]func(t *testing.T, root string){
		"new file":       func(t *testing.T, root string) { t.Setenv("TAI_FAKE_WRITE", filepath.Join(root, "dropped.txt")) },
		"tracked edit":   func(t *testing.T, root string) { t.Setenv("TAI_FAKE_APPEND", filepath.Join(root, "README.md")) },
		"inside the git": func(t *testing.T, root string) { t.Setenv("TAI_FAKE_WRITE", filepath.Join(root, ".git", "index")) },
		"new go file": func(t *testing.T, root string) {
			t.Setenv("TAI_FAKE_WRITE", filepath.Join(root, "cmd", "eki-agent", "late.go"))
		},
	}
	for name, arm := range cases {
		for _, pinned := range []bool{false, true} {
			t.Run(name, func(t *testing.T) {
				repo := newFakeEKI(t)
				arm(t, repo.Root)
				cwdLog := filepath.Join(t.TempDir(), "cwd")
				t.Setenv("TAI_FAKE_CWDLOG", cwdLog)
				options := Options{}
				if pinned {
					options.ExpectCommit = repo.Head
				}
				receipt := run(t, repo.Root, options)
				if receipt.Passed || receipt.Checkout.Status != "changed" || receipt.ReadOnly {
					t.Fatalf("a write into the checkout must fail the run (pinned=%t): %+v", pinned, receipt)
				}
				if !strings.Contains(receipt.Reason, "changed the EKI checkout") || strings.Contains(receipt.Reason, "dropped") || strings.Contains(receipt.Reason, "edit") {
					t.Fatalf("the reason names the fields, never the content: %q", receipt.Reason)
				}
				cwd, err := os.ReadFile(cwdLog)
				if err != nil {
					t.Fatal(err)
				}
				resolvedRoot, _ := filepath.EvalSymlinks(repo.Root)
				resolvedCwd, _ := filepath.EvalSymlinks(string(cwd))
				if resolvedCwd == resolvedRoot || strings.HasPrefix(resolvedCwd, resolvedRoot+string(filepath.Separator)) {
					t.Fatalf("the EKI command must not run with the checkout as its working directory: %s", cwd)
				}
				assertNoLocalText(t, receipt, repo.Root)
			})
		}
	}
}

func TestFailureReceiptKeepsPassedFalseAndNoErrorText(t *testing.T) {
	t.Run("build failure", func(t *testing.T) {
		needTools(t)
		repo := newFakeEKIWith(t, "go 99")
		for _, options := range []Options{{}, {ExpectCommit: repo.Head}} {
			receipt := run(t, repo.Root, options)
			assertFailsClosed(t, receipt, "EKI build failed")
			if receipt.Toolchain.Build != "failed" || receipt.Passed {
				t.Fatalf("build state: %+v", receipt.Toolchain)
			}
			assertNoLocalText(t, receipt, repo.Root)
			if strings.Contains(receiptJSON(t, receipt), "requires") || strings.Contains(receiptJSON(t, receipt), "go.mod") {
				t.Fatalf("go's error text must not reach the receipt: %s", receipt.Reason)
			}
			if options.ExpectCommit != "" && receipt.Pin.Result != "match" {
				t.Fatalf("the pin facts stay on a failure receipt: %+v", receipt.Pin)
			}
		}
	})
	t.Run("version command exits non-zero", func(t *testing.T) {
		repo := newFakeEKI(t)
		t.Setenv("TAI_FAKE_EXIT_AGENT", "1")
		receipt := Run(t.Context(), repo.Root)
		assertFailsClosed(t, receipt, "eki-agent --version failed")
		assertNoLocalText(t, receipt, repo.Root)
	})
	t.Run("control command missing", func(t *testing.T) {
		root := t.TempDir()
		receipt := Run(t.Context(), root)
		assertFailsClosed(t, receipt, "EKI control command is unavailable")
		assertNoLocalText(t, receipt, root)
	})
	t.Run("go missing", func(t *testing.T) {
		repo := newFakeEKI(t)
		t.Setenv("PATH", "")
		receipt := Run(t.Context(), repo.Root)
		assertFailsClosed(t, receipt, "go is unavailable")
		assertNoLocalText(t, receipt, repo.Root)
	})
}

func TestBuildOutRejectsCheckout(t *testing.T) {
	repo := newFakeEKI(t)
	marker := armMarker(t)
	inside := filepath.Join(repo.Root, "out")
	if err := os.MkdirAll(inside, 0o755); err != nil {
		t.Fatal(err)
	}
	link := filepath.Join(t.TempDir(), "link")
	if err := os.Symlink(inside, link); err != nil {
		t.Skip("symlinks are not available")
	}
	for name, dir := range map[string]string{"inside": inside, "the checkout itself": repo.Root, "not yet created inside": filepath.Join(repo.Root, "new", "dir"), "symlink into the checkout": link} {
		receipt := run(t, repo.Root, Options{BuildOut: dir})
		assertFailsClosed(t, receipt, "build-out must be outside the EKI checkout")
		if wasStarted(marker) || receipt.Toolchain.Build != "not-run" {
			t.Fatalf("%s: nothing may be built: %+v", name, receipt)
		}
		assertNoLocalText(t, receipt, repo.Root)
	}
}

func TestBuildOutKeepsBinaries(t *testing.T) {
	repo := newFakeEKI(t)
	out := filepath.Join(t.TempDir(), "kept")
	receipt := run(t, repo.Root, Options{ExpectCommit: repo.Head, BuildOut: out})
	if !receipt.Passed || receipt.Binaries.KeptAt != "build-out" {
		t.Fatalf("receipt: %+v", receipt)
	}
	suffix := ""
	if runtime.GOOS == "windows" {
		suffix = ".exe"
	}
	for name, want := range map[string]string{"eki-control": receipt.Binaries.ControlSha256, "eki-agent": receipt.Binaries.AgentSha256} {
		raw, err := os.ReadFile(filepath.Join(out, name+suffix))
		if err != nil {
			t.Fatalf("%s was not kept: %v", name, err)
		}
		if digestBytes(raw) != want {
			t.Fatalf("%s digest differs from the receipt", name)
		}
	}
	if strings.Contains(receiptJSON(t, receipt), out) {
		t.Fatal("the receipt must not carry the build-out path")
	}
	// Without -build-out the temporary directory is removed. A private temp dir keeps
	// other processes' directories out of the comparison.
	private := t.TempDir()
	t.Setenv("TMPDIR", private)
	t.Setenv("TMP", private)
	t.Setenv("TEMP", private)
	tmpBefore, _ := filepath.Glob(filepath.Join(os.TempDir(), "tai-eki-bin-*"))
	run(t, repo.Root, Options{})
	tmpAfter, _ := filepath.Glob(filepath.Join(os.TempDir(), "tai-eki-bin-*"))
	if len(tmpAfter) > len(tmpBefore) {
		t.Fatalf("temporary build directories were left behind: %v", tmpAfter)
	}
}

func TestParseConfigWiresEveryExpectation(t *testing.T) {
	commit := strings.Repeat("a", 40)
	other := strings.Repeat("b", 40)
	env := map[string]string{"TAI_EKI_EXPECT_COMMIT": commit, "TAI_EKI_EXPECT_GO_VERSION": "go1.26.9"}
	getenv := func(name string) string { return env[name] }
	config, err := parseConfig(nil, getenv)
	if err != nil || config.Options.ExpectCommit != commit || config.Options.ExpectGoVersion != "go1.26.9" {
		t.Fatalf("environment: %+v %v", config, err)
	}
	config, err = parseConfig([]string{"-expect-commit", other, "-expect-go-version", "go1.27.3", "-build-out", "kept"}, getenv)
	if err != nil || config.Options.ExpectCommit != other || config.Options.ExpectGoVersion != "go1.27.3" || config.Options.BuildOut != "kept" {
		t.Fatalf("flags win over the environment: %+v %v", config, err)
	}
	config, _ = parseConfig([]string{"-expect-commit", "", "-expect-go-version", ""}, getenv)
	if config.Options.specified() {
		t.Fatalf("an empty value means no expectation: %+v", config.Options)
	}
	config, _ = parseConfig([]string{"-expect-commit", strings.ToUpper(commit)}, func(string) string { return "" })
	if config.Options.ExpectCommit != commit {
		t.Fatalf("an upper case commit is normalised: %+v", config.Options)
	}
	config, _ = parseConfig([]string{"-eki-root", "x"}, func(string) string { return "" })
	if config.Options.specified() || config.EkiRoot != "x" {
		t.Fatalf("no expectation by default: %+v", config)
	}
}

func TestMainExitCodeAndReceipt(t *testing.T) {
	repo := newFakeEKI(t)
	nothing := func(string) string { return "" }
	var out, errOut bytes.Buffer
	if code := realMain([]string{"-eki-root", repo.Root, "-expect-commit", strings.Repeat("0", 40)}, nothing, &out, &errOut); code != 1 {
		t.Fatalf("a mismatch must exit 1, got %d", code)
	}
	var receipt Receipt
	if err := json.Unmarshal(out.Bytes(), &receipt); err != nil || receipt.Passed || receipt.Pin.Result != "mismatch" {
		t.Fatalf("stdout: %s %v", out.String(), err)
	}
	out.Reset()
	env := func(name string) string {
		if name == "TAI_EKI_EXPECT_COMMIT" {
			return repo.Head
		}
		return ""
	}
	if code := realMain([]string{"-eki-root", repo.Root}, env, &out, &errOut); code != 0 {
		t.Fatalf("a match via the environment must exit 0, got %d: %s", code, out.String())
	}
	if code := realMain([]string{"-bogus"}, nothing, &out, &errOut); code != 2 {
		t.Fatalf("a bad flag exits 2, got %d", code)
	}
}

func TestReceiptKeepsExistingKeysAndSchema(t *testing.T) {
	repo := newFakeEKI(t)
	raw, err := json.Marshal(Run(t.Context(), repo.Root))
	if err != nil {
		t.Fatal(err)
	}
	var decoded map[string]any
	if err := json.Unmarshal(raw, &decoded); err != nil {
		t.Fatal(err)
	}
	for _, key := range []string{"schema", "ekiCommit", "goVersion", "controlVersion", "agentVersion", "readOnly", "taskDelegated", "authorityVerified", "passed", "notes"} {
		if _, ok := decoded[key]; !ok {
			t.Fatalf("existing key %q is missing", key)
		}
	}
	if decoded["schema"] != "tai.reference.eki-cli/v0" || decoded["readOnly"] != true || decoded["taskDelegated"] != false || decoded["authorityVerified"] != false {
		t.Fatalf("schema or claims changed: %v", decoded)
	}
	for _, key := range []string{"pin", "checkout", "toolchain", "binaries"} {
		if _, ok := decoded[key]; !ok {
			t.Fatalf("additive key %q is missing", key)
		}
	}
	notes, _ := decoded["notes"].([]any)
	if len(notes) < 2 || notes[0] != "EKIの`eki-control`/`eki-agent`のversion表示だけを確認する。" || notes[1] != "Taskの委任・Worker・Authority・結果検証は未実施。" {
		t.Fatalf("the first two notes keep their text: %v", notes)
	}
	// A stored record written before these fields existed still decodes.
	stored, err := os.ReadFile(filepath.Join("..", "..", "evaluations", "records", "EKI-cli-2026-10-26.json"))
	if err != nil {
		t.Skip("stored record is not available")
	}
	var old Receipt
	if err := json.Unmarshal(stored, &old); err != nil || old.Schema != "tai.reference.eki-cli/v0" || old.Pin.Checked {
		t.Fatalf("stored record: %+v %v", old, err)
	}
}
