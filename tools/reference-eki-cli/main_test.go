package main

import (
	"bufio"
	"context"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"testing"
)

// goDirectiveSatisfied reports whether the local go command is at least the go
// directive of the checkout's go.mod. With GOTOOLCHAIN=local an older go cannot build
// it (the real EKI needs go 1.27, CI runs 1.26.x), and the real EKI tests skip then.
func goDirectiveSatisfied(root string) bool {
	file, err := os.Open(filepath.Join(root, "go.mod"))
	if err != nil {
		return false
	}
	defer file.Close()
	required := ""
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		if fields := strings.Fields(scanner.Text()); len(fields) == 2 && fields[0] == "go" {
			required = fields[1]
			break
		}
	}
	out, err := exec.Command("go", "version").Output()
	if err != nil || required == "" {
		return false
	}
	fields := strings.Fields(string(out))
	if len(fields) < 3 {
		return false
	}
	return versionAtLeast(strings.TrimPrefix(fields[2], "go"), required)
}

var versionPart = regexp.MustCompile(`^\d+`)

func versionAtLeast(have, want string) bool {
	h, w := strings.Split(have, "."), strings.Split(want, ".")
	for len(h) < 3 {
		h = append(h, "0")
	}
	for len(w) < 3 {
		w = append(w, "0")
	}
	for i := 0; i < 3; i++ {
		hn, _ := strconv.Atoi(versionPart.FindString(h[i]))
		wn, _ := strconv.Atoi(versionPart.FindString(w[i]))
		if hn != wn {
			return hn > wn
		}
	}
	return true
}

func ekiRootForTest(t *testing.T) string {
	t.Helper()
	if _, err := exec.LookPath("go"); err != nil {
		t.Skip("go is not available")
	}
	root := os.Getenv("EKI_ROOT")
	if root == "" {
		root = filepath.Clean(filepath.Join("..", "..", "..", "eki-fabric"))
	}
	if _, err := os.Stat(filepath.Join(root, "cmd", "eki-control")); err != nil {
		t.Skip("EKI runtime is not available")
	}
	if !goDirectiveSatisfied(root) {
		t.Skip("the local go is older than the go directive of the EKI go.mod")
	}
	return root
}

func TestEKIVersionProbe(t *testing.T) {
	receipt := Run(context.Background(), ekiRootForTest(t))
	if !receipt.Passed {
		t.Fatalf("EKI version probe failed: %+v", receipt)
	}
	if !receipt.ReadOnly || receipt.TaskDelegated || receipt.AuthorityVerified {
		t.Fatalf("EKI probe overclaims: %+v", receipt)
	}
	if receipt.ControlVersion == "" || receipt.AgentVersion == "" || receipt.GoVersion == "" {
		t.Fatalf("EKI probe evidence is incomplete: %+v", receipt)
	}
}

// TestRealEkiPinnedRun runs a pinned run against a real EKI checkout. The expectations
// come only from the environment, never from this file: with no expectation the test
// skips, and a pinned run is not attempted.
func TestRealEkiPinnedRun(t *testing.T) {
	commit := strings.ToLower(os.Getenv("TAI_EKI_EXPECT_COMMIT"))
	if commit == "" {
		t.Skip("TAI_EKI_EXPECT_COMMIT is not set")
	}
	root := ekiRootForTest(t)
	options := Options{ExpectCommit: commit, ExpectGoVersion: os.Getenv("TAI_EKI_EXPECT_GO_VERSION")}
	receipt := RunWithOptions(context.Background(), root, options)
	if !receipt.Passed || receipt.Pin.Result != "match" || receipt.Checkout.Status != "unchanged" {
		t.Fatalf("pinned run against the real EKI failed: %+v", receipt)
	}
	wrong := RunWithOptions(context.Background(), root, Options{ExpectCommit: strings.Repeat("0", 40)})
	if wrong.Passed || wrong.Toolchain.Build != "not-run" {
		t.Fatalf("a wrong commit must fail before EKI is built: %+v", wrong)
	}
}
