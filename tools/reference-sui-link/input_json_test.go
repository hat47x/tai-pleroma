package main

import (
	"bytes"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"testing"
)

type ambiguousLinkInput struct {
	name    string
	fixture []byte
	source  []byte
}

func ambiguousInputs(t *testing.T) ([]byte, []byte, []ambiguousLinkInput) {
	t.Helper()
	fixture, source := load(t)
	f, err := json.Marshal(fixture)
	if err != nil {
		t.Fatal(err)
	}
	s, err := json.Marshal(source)
	if err != nil {
		t.Fatal(err)
	}
	prefix := func(raw []byte, start string) []byte { return append([]byte(start), raw[1:]...) }
	return f, s, []ambiguousLinkInput{
		{"source conflicting passed", f, prefix(s, `{"passed":false,`)},
		{"source case alias", f, prefix(s, `{"PASSED":false,`)},
		{"source escaped alias", f, prefix(s, `{"\u0070assed":false,`)},
		{"source card digest", f, bytes.Replace(s, []byte(`"textDigest":`), []byte(`"textDigest":"sha256:wrong","textDigest":`), 1)},
		{"source invalid UTF8", f, prefix(s, "{\"unused\":\"\xff\",")},
		{"fixture observations", prefix(f, `{"observations":[],`), s},
		{"fixture text", bytes.Replace(f, []byte(`"text":`), []byte(`"text":"wrong","text":`), 1), s},
		{"fixture invalid UTF8", prefix(f, "{\"unused\":\"\xff\","), s},
	}
}

func TestAmbiguousLinkInputsCannotHideBehindPartialProjection(t *testing.T) {
	_, _, cases := ambiguousInputs(t)
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			// These cases reproduce successful links under the former reader.
			var oldFixture Fixture
			var oldSource SUIReceipt
			if err := json.Unmarshal(tc.fixture, &oldFixture); err != nil {
				t.Fatal(err)
			}
			if err := json.Unmarshal(tc.source, &oldSource); err != nil {
				t.Fatal(err)
			}
			if !Link(oldFixture, oldSource).Passed {
				t.Fatal("case does not reproduce the former false success")
			}
			fixture, source := load(t)
			beforeF, _ := json.Marshal(fixture)
			beforeS, _ := json.Marshal(source)
			ferr := decodeEvidenceJSON(tc.fixture, &fixture)
			serr := decodeEvidenceJSON(tc.source, &source)
			if ferr == nil && serr == nil {
				t.Fatal("ambiguous link input was accepted")
			}
			afterF, _ := json.Marshal(fixture)
			afterS, _ := json.Marshal(source)
			if !bytes.Equal(beforeF, afterF) || !bytes.Equal(beforeS, afterS) {
				t.Fatal("rejected input partially changed the target")
			}
		})
	}
}

func TestLinkJSONPreservesUnambiguousExtensions(t *testing.T) {
	f, s, _ := ambiguousInputs(t)
	// Unknown fields keep their former behavior; a real U+FFFD is valid UTF-8.
	s = append([]byte(`{"extension":{"replacement":"\ufffd","number":1e999},`), s[1:]...)
	var fixture Fixture
	var source SUIReceipt
	if err := decodeEvidenceJSON(f, &fixture); err != nil {
		t.Fatal(err)
	}
	if err := decodeEvidenceJSON(s, &source); err != nil {
		t.Fatal(err)
	}
	if !Link(fixture, source).Passed {
		t.Fatal("unambiguous extension changed the link")
	}
	for _, raw := range []string{
		`{"extension":{"K":1,"\u212a":2}}`,
		`{} {}`,
		`{"extension":[{"a":1,"A":2}]}`,
	} {
		if err := decodeEvidenceJSON([]byte(raw), &source); err == nil {
			t.Fatalf("ambiguous or trailing JSON accepted: %s", raw)
		}
	}
}

func TestLinkCLIRejectsAmbiguityBeforeWriting(t *testing.T) {
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
	_, _, cases := ambiguousInputs(t)
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			work := t.TempDir()
			fp, sp, out := filepath.Join(work, "fixture.json"), filepath.Join(work, "source.json"), filepath.Join(work, "link.json")
			for path, raw := range map[string][]byte{fp: tc.fixture, sp: tc.source} {
				if err := os.WriteFile(path, raw, 0600); err != nil {
					t.Fatal(err)
				}
			}
			for _, existing := range []bool{false, true} {
				sentinel := []byte("existing output must remain\n")
				if existing {
					if err := os.WriteFile(out, sentinel, 0600); err != nil {
						t.Fatal(err)
					}
				}
				cmd := exec.Command(binary, "-fixture", fp, "-sui-receipt", sp, "-out", out)
				var stdout, stderr bytes.Buffer
				cmd.Stdout, cmd.Stderr = &stdout, &stderr
				err := cmd.Run()
				if exit, ok := err.(*exec.ExitError); !ok || exit.ExitCode() != 2 || stdout.Len() != 0 {
					t.Fatalf("ambiguous input reached output: %v stdout=%s stderr=%s", err, &stdout, &stderr)
				}
				after, err := os.ReadFile(out)
				if existing && (err != nil || !bytes.Equal(after, sentinel)) {
					t.Fatal("existing output changed")
				}
				if !existing && !os.IsNotExist(err) {
					t.Fatal("rejected input created output")
				}
			}
			for path, raw := range map[string][]byte{fp: tc.fixture, sp: tc.source} {
				after, err := os.ReadFile(path)
				if err != nil || !bytes.Equal(after, raw) {
					t.Fatal("input changed")
				}
			}
		})
	}
}
