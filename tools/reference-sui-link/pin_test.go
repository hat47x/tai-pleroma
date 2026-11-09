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

const (
	revA = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
	revB = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
)

func yes() *bool { v := true; return &v }
func no() *bool  { v := false; return &v }

func identified(sui SUIReceipt, revision string, consistent *bool) SUIReceipt {
	sui.ServerIdentity = ServerIdentity{Status: "reported", Revision: revision, Consistent: consistent}
	return sui
}

func TestDefaultLinkRecordsAnUncheckedPin(t *testing.T) {
	fixture, sui := load(t)
	receipt := Link(fixture, sui)
	if !receipt.Passed || receipt.Pin.Checked || receipt.Pin.Result != "not-checked" ||
		receipt.Pin.ServerRevision.Status != "not-checked" || receipt.Pin.DocumentDigest.Status != "not-checked" {
		t.Fatalf("default run must only record: %+v", receipt)
	}
	if receipt.Pin.DocumentDigest.Actual != sui.DocumentDigest {
		t.Fatalf("document digest is not recorded: %+v", receipt.Pin)
	}
	fixture, sui = load(t)
	withRevision := identified(sui, revA, yes())
	if r := Link(fixture, withRevision); !r.Passed || r.Pin.ServerRevision.Actual != revA || r.Pin.Checked {
		t.Fatalf("declared revision is recorded but not enforced: %+v", r.Pin)
	}
}

func TestOutputKeysOnlyGainPin(t *testing.T) {
	fixture, sui := load(t)
	encoded, err := json.Marshal(Link(fixture, sui))
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
	want := []string{"contradiction", "documentDigest", "documentId", "edgeCount", "islandGroups", "linkedCards", "notes", "passed", "pin", "schema"}
	if !slices.Equal(got, want) {
		t.Fatalf("keys changed: %v", got)
	}
	var probeOut struct{ Pin map[string]any }
	if err := decodeEvidenceJSON(encoded, &probeOut); err != nil {
		t.Fatalf("output is not accepted by the strict reader: %v", err)
	}
}

func TestPinnedRevision(t *testing.T) {
	fixture, stored := load(t)
	cases := []struct {
		name   string
		sui    SUIReceipt
		expect string
		result string
	}{
		{"match", identified(stored, revA, yes()), revA, "match"},
		{"mismatch", identified(stored, revB, yes()), revA, "mismatch"},
		{"prefix is not a match", identified(stored, revA, yes()), revA[:12], "mismatch"},
		{"inconsistent run", identified(stored, revA, no()), revA, "unavailable"},
		{"no consistency recorded", identified(stored, revA, nil), revA, "unavailable"},
		{"stored record has no identity", stored, revA, "unavailable"},
		{"unknown revision", identified(stored, "unknown", yes()), "release-1", "unavailable"},
		{"unusable revision text", identified(stored, "a b\n", yes()), "release-1", "unavailable"},
		{"identity not reported", func() SUIReceipt { s := identified(stored, revA, yes()); s.ServerIdentity.Status = "invalid"; return s }(), revA, "unavailable"},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			receipt := LinkPinned(fixture, tc.sui, Options{ExpectRevision: tc.expect})
			if receipt.Pin.Result != tc.result || !receipt.Pin.Checked {
				t.Fatalf("result %q: %+v", receipt.Pin.Result, receipt.Pin)
			}
			if (tc.result == "match") != receipt.Passed {
				t.Fatalf("passed=%v for %s: %+v", receipt.Passed, tc.result, receipt)
			}
			if tc.result != "match" && (receipt.Reason == "" || len(receipt.LinkedCards) != 0) {
				t.Fatalf("a failed pin must stop before linking: %+v", receipt)
			}
		})
	}
}

func TestPinnedDocumentDigest(t *testing.T) {
	fixture, sui := load(t)
	if r := LinkPinned(fixture, sui, Options{ExpectDocumentDigest: sui.DocumentDigest}); !r.Passed || r.Pin.DocumentDigest.Status != "match" {
		t.Fatalf("digest match failed: %+v", r)
	}
	changed := sui.DocumentDigest[:len(sui.DocumentDigest)-1] + "0"
	if changed == sui.DocumentDigest {
		changed = sui.DocumentDigest[:len(sui.DocumentDigest)-1] + "1"
	}
	if r := LinkPinned(fixture, sui, Options{ExpectDocumentDigest: changed}); r.Passed || r.Pin.DocumentDigest.Status != "mismatch" {
		t.Fatalf("digest mismatch accepted: %+v", r)
	}
	empty := sui
	empty.DocumentDigest = ""
	if r := LinkPinned(fixture, empty, Options{ExpectDocumentDigest: changed}); r.Passed || r.Pin.DocumentDigest.Status != "unavailable" {
		t.Fatalf("missing digest accepted: %+v", r)
	}
	both := identified(sui, revA, yes())
	if r := LinkPinned(fixture, both, Options{ExpectRevision: revA, ExpectDocumentDigest: changed}); r.Passed || r.Pin.Result != "mismatch" || r.Pin.ServerRevision.Status != "match" {
		t.Fatalf("one failing item must fail the run: %+v", r)
	}
}

func TestReceiptWithAFailedPinIsRejectedEvenIfPassedIsSet(t *testing.T) {
	fixture, sui := load(t)
	sui.Pin = ProbePin{Checked: true, Result: "mismatch"}
	if r := Link(fixture, sui); r.Passed {
		t.Fatalf("a receipt whose own pin failed was accepted: %+v", r)
	}
	sui.Pin = ProbePin{Checked: true, Result: "match"}
	if r := Link(fixture, sui); !r.Passed {
		t.Fatalf("a matching pin must not break linking: %+v", r)
	}
}

func TestInvalidExpectationsAreRejected(t *testing.T) {
	for _, options := range []Options{
		{ExpectRevision: "unknown"}, {ExpectRevision: "a b"}, {ExpectRevision: strings.Repeat("x", 65)},
		{ExpectDocumentDigest: "sha256:xyz"}, {ExpectDocumentDigest: "SHA256:" + strings.Repeat("a", 64)},
	} {
		if err := options.validate(); err == nil {
			t.Fatalf("accepted %+v", options)
		}
		fixture, sui := load(t)
		if r := LinkPinned(fixture, sui, options); r.Passed || r.Pin.Result != "invalid-expectation" {
			t.Fatalf("invalid expectation reached linking: %+v", r)
		}
	}
	if err := (Options{ExpectRevision: "v1.2.3", ExpectDocumentDigest: "sha256:" + strings.Repeat("a", 64)}).validate(); err != nil {
		t.Fatal(err)
	}
}

func buildLink(t *testing.T) string {
	t.Helper()
	if _, err := exec.LookPath("go"); err != nil {
		t.Skip("go is not available")
	}
	binary := filepath.Join(t.TempDir(), "link")
	if runtime.GOOS == "windows" {
		binary += ".exe"
	}
	if output, err := exec.Command("go", "build", "-o", binary, ".").CombinedOutput(); err != nil {
		t.Fatalf("build: %s %v", output, err)
	}
	return binary
}

func runLink(t *testing.T, binary string, env []string, args ...string) (stdout, stderr string, code int) {
	t.Helper()
	cmd := exec.Command(binary, args...)
	cmd.Env = append(os.Environ(), "TAI_SUI_EXPECT_REVISION=", "TAI_SUI_EXPECT_DOCUMENT_DIGEST=")
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
	binary := buildLink(t)
	work := t.TempDir()
	fixturePath := filepath.Join("..", "reference-scn001", "testdata", "scn001.json")
	stored := filepath.Join("..", "..", "evaluations", "records", "SUI-api-2026-10-26.json")
	raw, err := os.ReadFile(stored)
	if err != nil {
		t.Fatal(err)
	}
	var document map[string]any
	if err := json.Unmarshal(raw, &document); err != nil {
		t.Fatal(err)
	}
	digest, _ := document["documentDigest"].(string)
	document["serverIdentity"] = map[string]any{"status": "reported", "revision": revA, "runtimeProfile": "evaluation", "consistent": true}
	withIdentity, _ := json.Marshal(document)
	identityPath := filepath.Join(work, "sui.json")
	if err := os.WriteFile(identityPath, withIdentity, 0o600); err != nil {
		t.Fatal(err)
	}

	t.Run("default output is one JSON document and stderr stays empty", func(t *testing.T) {
		stdout, stderr, code := runLink(t, binary, nil, "-fixture", fixturePath, "-sui-receipt", stored)
		if code != 0 || stderr != "" {
			t.Fatalf("code=%d stderr=%q", code, stderr)
		}
		var receipt struct {
			Passed bool
			Pin    struct {
				Checked bool
				Result  string
			}
			LinkedCards []string
		}
		if err := decodeEvidenceJSON([]byte(stdout), &receipt); err != nil {
			t.Fatalf("not strict JSON: %v", err)
		}
		if !receipt.Passed || receipt.Pin.Checked || receipt.Pin.Result != "not-checked" || len(receipt.LinkedCards) != 5 {
			t.Fatalf("unexpected: %s", stdout)
		}
	})
	t.Run("pinned match by flag and by environment", func(t *testing.T) {
		for _, tc := range []struct {
			env  []string
			args []string
		}{
			{nil, []string{"-expect-revision", revA, "-expect-document-digest", digest}},
			{[]string{"TAI_SUI_EXPECT_REVISION=" + revA, "TAI_SUI_EXPECT_DOCUMENT_DIGEST=" + digest}, nil},
			{[]string{"TAI_SUI_EXPECT_REVISION=" + revB}, []string{"-expect-revision", revA}},
		} {
			stdout, stderr, code := runLink(t, binary, tc.env, append([]string{"-fixture", fixturePath, "-sui-receipt", identityPath}, tc.args...)...)
			if code != 0 || stderr != "" || !strings.Contains(stdout, `"result": "match"`) {
				t.Fatalf("code=%d stderr=%q %s", code, stderr, stdout)
			}
		}
	})
	t.Run("pinned run against a record without identity fails with a receipt", func(t *testing.T) {
		stdout, _, code := runLink(t, binary, nil, "-fixture", fixturePath, "-sui-receipt", stored, "-expect-revision", revA)
		if code != 1 || !strings.Contains(stdout, `"result": "unavailable"`) || !strings.Contains(stdout, `"passed": false`) {
			t.Fatalf("code=%d %s", code, stdout)
		}
	})
	t.Run("invalid expectations exit 2 without output and keep an existing file", func(t *testing.T) {
		out := filepath.Join(work, "out.json")
		sentinel := []byte("keep me\n")
		for _, tc := range []struct {
			env  []string
			args []string
		}{
			{nil, []string{"-expect-revision", "unknown"}},
			{nil, []string{"-expect-document-digest", "sha256:xyz"}},
			{[]string{"TAI_SUI_EXPECT_REVISION=a b"}, nil},
			{[]string{"TAI_SUI_EXPECT_DOCUMENT_DIGEST=nope"}, nil},
		} {
			if err := os.WriteFile(out, sentinel, 0o600); err != nil {
				t.Fatal(err)
			}
			args := append([]string{"-fixture", fixturePath, "-sui-receipt", identityPath, "-out", out}, tc.args...)
			stdout, _, code := runLink(t, binary, tc.env, args...)
			after, _ := os.ReadFile(out)
			if code != 2 || stdout != "" || !bytes.Equal(after, sentinel) {
				t.Fatalf("code=%d stdout=%q file=%q", code, stdout, after)
			}
		}
	})
}
