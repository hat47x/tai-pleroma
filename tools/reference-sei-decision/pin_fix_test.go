package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestPinNestedRepositoryUnderRuntimeGoIsABuildInput(t *testing.T) {
	for name, want := range map[string]bool{
		"runtime/go/internal/x/":    true, // git lists a nested repository as one directory
		"runtime/go/":               true,
		"runtime/":                  true, // may contain runtime/go
		"runtime/go/cmd/sei/x.go":   true,
		"runtime/go/notes.txt":      false,
		"docs/nested/":              false,
		"runtime/other/":            false,
		"runtime/go/internal/x.txt": false,
	} {
		if got := len(pinBuildInputs([]byte(name+"\x00"))) == 1; got != want {
			t.Errorf("%s: build input %v, want %v", name, got, want)
		}
	}
}

func TestPinFakeNestedRepositoryUnderRuntimeGoFailsThePin(t *testing.T) {
	pinSetup(t, true, true, true)
	root, head := pinFakeRepo(t, nil)
	marker := pinMarker(t)
	nested := filepath.Join(root, "runtime", "go", "internal", "x")
	if err := os.MkdirAll(nested, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(nested, "x.go"), []byte("package x\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	pinGit(t, nested, "init", "-q")
	receipt := pinRun(t, root, Options{ExpectCommit: head})
	if receipt.Passed || receipt.Pin.Result != "mismatch" || receipt.Pin.SourceTree.Status != "untracked-build-inputs" || receipt.Pin.SourceTree.UntrackedBuildInputs < 1 || pinStarted(marker) {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
	// A nested repository outside the module is not a build input.
	other := filepath.Join(root, "docs", "nested")
	os.MkdirAll(other, 0o755)
	os.WriteFile(filepath.Join(other, "a.go"), []byte("package a\n"), 0o644)
	pinGit(t, other, "init", "-q")
	os.RemoveAll(nested)
	if receipt := pinRun(t, root, Options{ExpectCommit: head}); !receipt.Passed || receipt.Pin.Result != "match" {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
}

func TestPinFakeRelativeBuildOutIsJudgedAndBuiltAsAbsolute(t *testing.T) {
	pinSetup(t, true, true, true)
	root, head := pinFakeRepo(t, nil)
	elsewhere := t.TempDir()
	t.Chdir(elsewhere)
	// relative to the caller's directory this is outside the checkout; go build runs in
	// runtime/go, so it must not be resolved there.
	receipt := pinRun(t, root, Options{ExpectCommit: head, BuildOut: "out"})
	if !receipt.Passed || receipt.Binary.KeptAt != "build-out" || strings.Contains(pinJSON(t, receipt), elsewhere) {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
	if _, err := os.Stat(filepath.Join(elsewhere, "out", "sei"+pinSuffix())); err != nil {
		t.Fatalf("the built sei is kept relative to the caller's directory: %v", err)
	}
	if status := pinGit(t, root, "status", "--porcelain", "--ignored"); status != "" {
		t.Fatalf("the checkout was written: %s", status)
	}
	// relative to the checkout itself it is inside: refused before any SEI code or build.
	t.Chdir(root)
	receipt = pinRun(t, root, Options{ExpectCommit: head, BuildOut: "bin"})
	if receipt.Passed || !strings.Contains(receipt.Reason, "build-out must be outside") || receipt.Binary.Status != "not-built" {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
	if status := pinGit(t, root, "status", "--porcelain", "--ignored"); status != "" {
		t.Fatalf("the checkout was written: %s", status)
	}
}

func TestPinShortCommit(t *testing.T) {
	head := "0123456789abcdef0123456789abcdef01234567"
	for value, want := range map[string]string{
		"0123456":       "match",
		"0123456789ABC": "match",
		"0123457":       "mismatch",
		"abcdef1":       "mismatch",
		"012345":        "", // six digits: not an abbreviation we judge
		"unknown":       "",
		"":              "",
		head:            "", // full length is judged by pinReportedCommit
	} {
		if got := pinShortCommit(head, value); got != want {
			t.Errorf("%q: %q, want %q", value, got, want)
		}
	}
}

func TestPinFakeAbbreviatedReportedCommitIsComparedWithHead(t *testing.T) {
	pinSetup(t, true, true, true)
	root, head := pinFakeRepo(t, nil)
	marker := pinMarker(t)
	t.Setenv("FAKE_SEI_VERSION_OUT", `{"commit":"`+head[:7]+`","target":"t","version":"dev"}`)
	receipt := pinRun(t, root, Options{ExpectCommit: head})
	if !receipt.Passed || receipt.Binary.ReportedCommit.Status != "match" {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
	wrong := "0000000"
	if strings.HasPrefix(head, wrong) {
		wrong = "fffffff"
	}
	os.Remove(marker)
	t.Setenv("FAKE_SEI_VERSION_OUT", `{"commit":"`+wrong+`","target":"t","version":"dev"}`)
	receipt = pinRun(t, root, Options{ExpectCommit: head})
	raw, _ := os.ReadFile(marker)
	if receipt.Passed || receipt.Binary.ReportedCommit.Status != "mismatch" || strings.Contains(string(raw), "init") {
		t.Fatalf("an abbreviated commit that is not a prefix of HEAD must stop the run: %s", pinJSON(t, receipt))
	}
}

// The count stays the same while the names change: only the digest sees it.
func TestPinFakeSwappedUntrackedFileIsDetectedByTheDigest(t *testing.T) {
	t.Run("untracked file, pinned", func(t *testing.T) {
		pinSetup(t, true, true, true)
		root, head := pinFakeRepo(t, nil)
		first, second := filepath.Join(root, "first.txt"), filepath.Join(root, "second.txt")
		os.WriteFile(first, []byte("x"), 0o644)
		t.Setenv("FAKE_SEI_SWAP", first+"|"+second)
		receipt := pinRun(t, root, Options{ExpectCommit: head})
		after := receipt.Checkout
		if receipt.Passed || receipt.Checkout.Status != "changed" || after.Before.UntrackedFiles != after.After.UntrackedFiles || after.Before.UntrackedDigest == after.After.UntrackedDigest {
			t.Fatalf("%s", pinJSON(t, receipt))
		}
	})
	t.Run("ignored build input, recorded", func(t *testing.T) {
		pinSetup(t, true, false, true)
		root, _ := pinFakeRepo(t, nil)
		os.WriteFile(filepath.Join(root, ".git", "info", "exclude"), []byte("hidden_*.go\n"), 0o644)
		first := filepath.Join(root, "runtime", "go", "cmd", "sei", "hidden_a.go")
		second := filepath.Join(root, "runtime", "go", "cmd", "sei", "hidden_b.go")
		os.WriteFile(first, []byte("package main\n"), 0o644)
		t.Setenv("FAKE_SEI_SWAP", first+"|"+second)
		receipt := pinRun(t, root, Options{})
		c := receipt.Checkout
		if !receipt.Passed || c.Status != "changed" || c.Before.UntrackedFiles != c.After.UntrackedFiles || c.Before.UntrackedDigest != c.After.UntrackedDigest ||
			c.Before.UntrackedBuildInputs != c.After.UntrackedBuildInputs || c.Before.BuildInputsDigest == c.After.BuildInputsDigest {
			t.Fatalf("%s", pinJSON(t, receipt))
		}
	})
}
