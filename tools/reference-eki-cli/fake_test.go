package main

import (
	"context"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

// The fake EKI is a throwaway git repository with a tiny Go module whose
// cmd/eki-control and cmd/eki-agent print `<name> dev`. It is built with the real
// go command, so the build, environment and checkout checks run for real. Passing
// against it says nothing about the real EKI.

const fakeCommandSource = `package main

import (
	"fmt"
	"os"
)

var marker = "dev"

func main() {
	name := "NAME"
	if path := os.Getenv("TAI_FAKE_MARKER"); path != "" {
		_ = os.WriteFile(path, []byte("started"), 0o600)
	}
	if path := os.Getenv("TAI_FAKE_CWDLOG"); path != "" {
		wd, _ := os.Getwd()
		_ = os.WriteFile(path, []byte(wd), 0o600)
	}
	if path := os.Getenv("TAI_FAKE_WRITE"); path != "" {
		_ = os.WriteFile(path, []byte("written by the fake EKI\n"), 0o600)
	}
	if path := os.Getenv("TAI_FAKE_APPEND"); path != "" {
		if file, err := os.OpenFile(path, os.O_APPEND|os.O_WRONLY, 0); err == nil {
			_, _ = file.WriteString("edit\n")
			file.Close()
		}
	}
	if os.Getenv("TAI_FAKE_EXIT_UPPER") != "" {
		os.Exit(3)
	}
	if out, ok := os.LookupEnv("TAI_FAKE_OUT_UPPER"); ok {
		fmt.Print(out)
		return
	}
	if len(os.Args) > 1 && os.Args[1] == "--version" {
		fmt.Println(name, marker)
	}
}
`

type fakeRepo struct {
	Root, Head string
}

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

// needTools skips a test that needs go and git, and pins the caller-controlled go
// settings so a developer's environment does not change what the test measures.
func needTools(t *testing.T) {
	t.Helper()
	for _, tool := range []string{"go", "git"} {
		if _, err := exec.LookPath(tool); err != nil {
			t.Skip(tool + " is not available")
		}
	}
	t.Setenv("GOTOOLCHAIN", "local")
	t.Setenv("GOFLAGS", "")
	t.Setenv("GOWORK", "")
}

func writeFiles(t *testing.T, root string, files map[string]string) {
	t.Helper()
	for path, content := range files {
		full := filepath.Join(root, filepath.FromSlash(path))
		if err := os.MkdirAll(filepath.Dir(full), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(full, []byte(content), 0o644); err != nil {
			t.Fatal(err)
		}
	}
}

func newFakeEKI(t *testing.T) fakeRepo {
	t.Helper()
	needTools(t)
	return newFakeEKIWith(t, "go 1.21")
}

func newFakeEKIWith(t *testing.T, goDirective string) fakeRepo {
	t.Helper()
	root := t.TempDir()
	git(t, root, "init", "-q")
	git(t, root, "config", "core.autocrlf", "false")
	writeFiles(t, root, map[string]string{
		"cmd/eki-control/main.go": strings.Replace(fakeCommandSource, "NAME", "eki-control", 1),
		"cmd/eki-agent/main.go":   strings.Replace(strings.Replace(fakeCommandSource, "NAME", "eki-agent", 1), "UPPER", "AGENT", -1),
		"internal/core/core.go":   "package core\n",
		"go.mod":                  "module eki\n\n" + goDirective + "\n",
		"README.md":               "stub\n",
	})
	// The control command reads the CONTROL variables, the agent the AGENT ones.
	control := filepath.Join(root, "cmd", "eki-control", "main.go")
	raw, err := os.ReadFile(control)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(control, []byte(strings.Replace(string(raw), "UPPER", "CONTROL", -1)), 0o644); err != nil {
		t.Fatal(err)
	}
	git(t, root, "add", "-A")
	git(t, root, "commit", "-q", "-m", "fixture")
	return fakeRepo{Root: root, Head: git(t, root, "rev-parse", "HEAD")}
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

func receiptJSON(t *testing.T, receipt Receipt) string {
	t.Helper()
	raw, err := json.Marshal(receipt)
	if err != nil {
		t.Fatal(err)
	}
	return string(raw)
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

// assertNoLocalText fails when the receipt carries a local absolute path.
func assertNoLocalText(t *testing.T, receipt Receipt, root string) {
	t.Helper()
	text := receiptJSON(t, receipt)
	for _, local := range []string{root, os.TempDir(), "tai-eki-"} {
		if local != "" && strings.Contains(text, local) {
			t.Fatalf("receipt contains local text %q: %s", local, text)
		}
	}
}

// started reports whether a fake EKI command ran (it writes the marker file).
func armMarker(t *testing.T) string {
	t.Helper()
	marker := filepath.Join(t.TempDir(), "started")
	t.Setenv("TAI_FAKE_MARKER", marker)
	return marker
}

func wasStarted(marker string) bool {
	_, err := os.Stat(marker)
	return err == nil
}

func run(t *testing.T, root string, options Options) Receipt {
	t.Helper()
	return RunWithOptions(context.Background(), root, options)
}
