package main

import (
	"bytes"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"slices"
	"sort"
	"strings"
	"testing"
)

func digestWith(last string, link SUILink) string {
	return link.DocumentDigest[:len(link.DocumentDigest)-1] + last
}

func TestDefaultRecordsAnUncheckedPin(t *testing.T) {
	link, artifact := load(t)
	receipt := Link(link, artifact)
	if !receipt.Passed || receipt.Pin.Checked || receipt.Pin.Result != "not-checked" || receipt.Pin.DocumentDigest.Status != "not-checked" {
		t.Fatalf("default run must only record: %+v", receipt)
	}
	if !strings.HasPrefix(link.DocumentDigest, "sha256:") || receipt.Pin.DocumentDigest.Actual != link.DocumentDigest {
		t.Fatalf("the stored link record has a documentDigest and the draft receipt records it: %+v", receipt.Pin)
	}
}

func TestOutputKeysOnlyGainPin(t *testing.T) {
	link, artifact := load(t)
	encoded, err := json.Marshal(Link(link, artifact))
	if err != nil {
		t.Fatal(err)
	}
	var keys map[string]json.RawMessage
	if err := json.Unmarshal(encoded, &keys); err != nil {
		t.Fatal(err)
	}
	var got []string
	for key := range keys {
		got = append(got, key)
	}
	sort.Strings(got)
	want := []string{"artifactDigest", "linkedCards", "notes", "passed", "pin", "publicationBlocked", "schema"}
	if !slices.Equal(got, want) {
		t.Fatalf("keys changed: %v", got)
	}
}

func TestPinnedDocumentDigest(t *testing.T) {
	link, artifact := load(t)
	if r := LinkPinned(link, artifact, Options{ExpectDocumentDigest: link.DocumentDigest}); !r.Passed || r.Pin.Result != "match" || !r.Pin.Checked {
		t.Fatalf("match failed: %+v", r)
	}
	other := digestWith("0", link)
	if other == link.DocumentDigest {
		other = digestWith("1", link)
	}
	r := LinkPinned(link, artifact, Options{ExpectDocumentDigest: other})
	if r.Passed || r.Pin.Result != "mismatch" || r.Reason == "" || r.PublicationBlocked || len(r.LinkedCards) != 0 {
		t.Fatalf("mismatch accepted: %+v", r)
	}
	empty := link
	empty.DocumentDigest = ""
	r = LinkPinned(empty, artifact, Options{ExpectDocumentDigest: other})
	if r.Passed || r.Pin.Result != "unavailable" {
		t.Fatalf("a link without documentDigest was accepted: %+v", r)
	}
	if r := Link(empty, artifact); !r.Passed {
		t.Fatalf("a record-only run must not need the digest: %+v", r)
	}
}

func TestInvalidExpectationIsRejected(t *testing.T) {
	link, artifact := load(t)
	for _, bad := range []string{"sha256:xyz", "SHA256:" + strings.Repeat("a", 64), strings.Repeat("a", 64)} {
		if err := (Options{ExpectDocumentDigest: bad}).validate(); err == nil {
			t.Fatalf("accepted %q", bad)
		}
		if r := LinkPinned(link, artifact, Options{ExpectDocumentDigest: bad}); r.Passed || r.Pin.Result != "invalid-expectation" {
			t.Fatalf("invalid expectation reached linking: %+v", r)
		}
	}
}

func runDraft(t *testing.T, binary string, env []string, args ...string) (stdout, stderr string, code int) {
	t.Helper()
	cmd := exec.Command(binary, args...)
	cmd.Env = append(os.Environ(), "TAI_SUI_EXPECT_DOCUMENT_DIGEST=")
	cmd.Env = append(cmd.Env, env...)
	var out, errOut bytes.Buffer
	cmd.Stdout, cmd.Stderr = &out, &errOut
	err := cmd.Run()
	if exit, ok := err.(*exec.ExitError); ok {
		code = exit.ExitCode()
	} else if err != nil {
		t.Fatal(err)
	}
	return out.String(), errOut.String(), code
}

func TestCLI(t *testing.T) {
	if _, err := exec.LookPath("go"); err != nil {
		t.Skip("go is not available")
	}
	binary := filepath.Join(t.TempDir(), "draft")
	if runtime.GOOS == "windows" {
		binary += ".exe"
	}
	if output, err := exec.Command("go", "build", "-o", binary, ".").CombinedOutput(); err != nil {
		t.Fatalf("build: %s %v", output, err)
	}
	link, _ := load(t)
	linkPath := filepath.Join("..", "..", "evaluations", "records", "SUI-SCN-link-2026-10-26.json")
	artifact := filepath.Join("..", "..", "evaluations", "artifacts", "SCN-001-D-04-provisional.md")
	base := []string{"-sui-link", linkPath, "-artifact", artifact}

	stdout, stderr, code := runDraft(t, binary, nil, base...)
	if code != 0 || stderr != "" || !strings.Contains(stdout, `"result": "not-checked"`) {
		t.Fatalf("default: code=%d stderr=%q %s", code, stderr, stdout)
	}
	for _, tc := range []struct {
		env  []string
		args []string
	}{
		{nil, []string{"-expect-document-digest", link.DocumentDigest}},
		{[]string{"TAI_SUI_EXPECT_DOCUMENT_DIGEST=" + link.DocumentDigest}, nil},
		{[]string{"TAI_SUI_EXPECT_DOCUMENT_DIGEST=sha256:" + strings.Repeat("0", 64)}, []string{"-expect-document-digest", link.DocumentDigest}},
	} {
		stdout, stderr, code = runDraft(t, binary, tc.env, append(append([]string{}, base...), tc.args...)...)
		if code != 0 || stderr != "" || !strings.Contains(stdout, `"result": "match"`) {
			t.Fatalf("pinned match: code=%d stderr=%q %s", code, stderr, stdout)
		}
	}
	stdout, _, code = runDraft(t, binary, nil, append(append([]string{}, base...), "-expect-document-digest", "sha256:"+strings.Repeat("0", 64))...)
	if code != 1 || !strings.Contains(stdout, `"passed": false`) || !strings.Contains(stdout, `"result": "mismatch"`) {
		t.Fatalf("pinned mismatch: code=%d %s", code, stdout)
	}
	out := filepath.Join(t.TempDir(), "out.json")
	sentinel := []byte("keep me\n")
	for _, tc := range []struct {
		env  []string
		args []string
	}{{nil, []string{"-expect-document-digest", "sha256:xyz"}}, {[]string{"TAI_SUI_EXPECT_DOCUMENT_DIGEST=nope"}, nil}} {
		if err := os.WriteFile(out, sentinel, 0o600); err != nil {
			t.Fatal(err)
		}
		stdout, _, code = runDraft(t, binary, tc.env, append(append([]string{}, base...), append(tc.args, "-out", out)...)...)
		after, _ := os.ReadFile(out)
		if code != 2 || stdout != "" || !bytes.Equal(after, sentinel) {
			t.Fatalf("invalid expectation: code=%d stdout=%q file=%q", code, stdout, after)
		}
	}
}
