package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"reflect"
	"strings"
	"testing"
	"time"
)

func mustTime(t *testing.T, seconds int64) time.Time {
	t.Helper()
	return time.Unix(seconds, 0)
}

func TestPinExpectationShapes(t *testing.T) {
	head := strings.Repeat("a", 40)
	facts := pinFacts{Commit: head, TreeStatus: "clean", TrackedDigest: "sha256:x"}
	tool := Toolchain{GoVersionToken: "go1.26.9"}
	cases := []struct {
		name    string
		options Options
		result  string
	}{
		{"go version alone", Options{ExpectGoVersion: "go1.26.9"}, "invalid-expectation"},
		{"short hash", Options{ExpectCommit: "abc1234"}, "invalid-expectation"},
		{"not hex", Options{ExpectCommit: strings.Repeat("z", 40)}, "invalid-expectation"},
		{"bad go token", Options{ExpectCommit: head, ExpectGoVersion: "1.26.9"}, "invalid-expectation"},
		{"sha256 length", Options{ExpectCommit: strings.Repeat("b", 64)}, "mismatch"},
		{"match", Options{ExpectCommit: head, ExpectGoVersion: "go1.26.9"}, "match"},
		{"no expectation", Options{}, "not-checked"},
	}
	for _, c := range cases {
		pin, _ := evaluatePin(c.options, facts, tool)
		if pin.Result != c.result {
			t.Errorf("%s: %s, want %s", c.name, pin.Result, c.result)
		}
	}
	if pin, _ := evaluatePin(Options{}, facts, tool); pin.Checked {
		t.Error("an empty Options must not turn the check on")
	}
}

func TestPinFlagsPrecedenceAndEnvironment(t *testing.T) {
	head := strings.Repeat("c", 40)
	env := map[string]string{"TAI_SEI_EXPECT_COMMIT": strings.ToUpper(head), "TAI_SEI_EXPECT_GO_VERSION": "go1.26.9"}
	getenv := func(name string) string { return env[name] }
	resolve := func(args ...string) Options {
		fs := flag.NewFlagSet("t", flag.ContinueOnError)
		registerPinFlags(fs)
		if err := fs.Parse(args); err != nil {
			t.Fatal(err)
		}
		return resolvePinOptions(fs, getenv)
	}
	if got := resolve(); got.ExpectCommit != head || got.ExpectGoVersion != "go1.26.9" {
		t.Errorf("environment is the default, upper case commit is lowered: %+v", got)
	}
	other := strings.Repeat("d", 40)
	if got := resolve("-expect-commit", other); got.ExpectCommit != other || got.ExpectGoVersion != "go1.26.9" {
		t.Errorf("a flag wins over the environment: %+v", got)
	}
	if got := resolve("-expect-commit", "", "-expect-go-version", ""); got.specified() {
		t.Errorf("an empty flag value cancels the environment: %+v", got)
	}
	if got := resolve("-build-out", "x"); got.BuildOut != "x" {
		t.Errorf("%+v", got)
	}
	// the flags exist on the command line of the tool itself
	for _, name := range []string{"expect-commit", "expect-go-version", "build-out"} {
		if flag.CommandLine.Lookup(name) == nil {
			t.Errorf("flag -%s is not registered on the command line", name)
		}
	}
}

func TestPinBuildInputsAreLimitedToRuntimeGo(t *testing.T) {
	yes := []string{"runtime/go/a.go", "runtime/go/cmd/sei/x.go", "runtime/go/go.mod", "runtime/go/sub/go.mod", "runtime/go/go.sum", "runtime/go/go.work",
		"runtime/go/vendor/x/y.txt", "runtime/go/a.s", "runtime/go/a.c", "runtime/go/a.h", "runtime/go/a.syso"}
	no := []string{"a.go", "go.mod", "runtime/other/a.go", "runtime/go/README.md", "runtime/go/notes.txt", "runtime/go/a.py", "tools/x.go", "runtime/gox/a.go", "vendor/x.go"}
	for _, name := range yes {
		if !isGoBuildInput(name) {
			t.Errorf("%s is a build input", name)
		}
	}
	for _, name := range no {
		if isGoBuildInput(name) {
			t.Errorf("%s is not a build input", name)
		}
	}
}

func TestPinChangedFieldsNameButNeverShowContent(t *testing.T) {
	a := CheckoutFacts{Commit: "x", TrackedChanges: 0, TrackedDigest: "d1"}
	b := a
	b.TrackedDigest = "d2"
	if got := a.changedFields(b); len(got) != 1 || !strings.HasPrefix(got[0], "tracked changes") {
		t.Fatalf("a changed digest with an unchanged count is a change: %v", got)
	}
	if got := a.changedFields(a); len(got) != 0 {
		t.Fatal(got)
	}
}

func walkKeys(t *testing.T, value any, path string, visit func(path string, keys []string)) {
	t.Helper()
	switch v := value.(type) {
	case map[string]any:
		keys := make([]string, 0, len(v))
		for key, child := range v {
			keys = append(keys, key)
			walkKeys(t, child, path+"/"+key, visit)
		}
		visit(path, keys)
	case []any:
		for i, child := range v {
			walkKeys(t, child, fmt.Sprintf("%s/%d", path, i), visit)
		}
	}
}

// TestPinNewKeysDoNotCaseFoldCollide: reference-scn001-run refuses an object that has two
// keys equal after case folding, so the added keys must not create such a pair.
func TestPinNewKeysDoNotCaseFoldCollide(t *testing.T) {
	pinSetup(t, false, false, true)
	root, head := pinFakeRepo(t, nil)
	check := func(name string, value any) {
		var generic any
		if err := json.Unmarshal([]byte(pinJSON(t, value)), &generic); err != nil {
			t.Fatal(err)
		}
		walkKeys(t, generic, "", func(path string, keys []string) {
			seen := map[string]string{}
			for _, key := range keys {
				folded := strings.ToLower(key)
				if other, ok := seen[folded]; ok {
					t.Errorf("%s %s: %q and %q fold to the same key", name, path, other, key)
				}
				seen[folded] = key
			}
		})
	}
	check("pinned receipt", pinRun(t, root, Options{ExpectCommit: head}))
	check("unpinned receipt", pinRun(t, root, Options{}))
	check("empty report", newPinReport())
}

func repoFile(t *testing.T, name string) []byte {
	t.Helper()
	raw, err := os.ReadFile(filepath.Join("..", "..", "evaluations", "records", name))
	if err != nil {
		t.Skipf("stored record %s is not available (the tool directory was copied out of the repository)", name)
	}
	return raw
}

// TestPinReceiptKeepsEveryStoredKeyAndSchema: the stored records predate the added keys.
// A new receipt must still carry every stored key with the same JSON type and the same
// schema, and a stored record must still decode into Receipt.
func TestPinReceiptKeepsEveryStoredKeyAndSchema(t *testing.T) {
	pinSetup(t, false, false, true)
	root, head := pinFakeRepo(t, nil)
	receipt := pinRun(t, root, Options{ExpectCommit: head})
	receipt.Synthetic, receipt.EvidenceKind = true, "synthetic"
	var fresh map[string]any
	if err := json.Unmarshal([]byte(pinJSON(t, receipt)), &fresh); err != nil {
		t.Fatal(err)
	}
	for _, name := range []string{"SEI-decision-2026-10-26.json", "SEI-live-2026-11-01.json"} {
		raw := repoFile(t, name)
		var stored map[string]any
		if err := json.Unmarshal(raw, &stored); err != nil {
			t.Fatal(err)
		}
		if stored["schema"] != "tai.reference.sei-decision/v0" {
			continue // not a receipt of this tool
		}
		if fresh["schema"] != stored["schema"] {
			t.Errorf("%s: schema %v -> %v", name, stored["schema"], fresh["schema"])
		}
		if _, hasPin := stored["pin"]; hasPin {
			t.Errorf("%s: the stored record is not supposed to carry the new keys", name)
		}
		for key, value := range stored {
			got, ok := fresh[key]
			if !ok {
				t.Errorf("%s: key %q of the stored record is missing from a new receipt", name, key)
				continue
			}
			if reflect.TypeOf(got) != reflect.TypeOf(value) {
				t.Errorf("%s: key %q changed its JSON type", name, key)
			}
		}
		var decoded Receipt
		if err := json.Unmarshal(raw, &decoded); err != nil || decoded.Schema != "tai.reference.sei-decision/v0" || decoded.PinReport != nil {
			t.Errorf("%s: a stored record must still decode into Receipt: %v", name, err)
		}
	}
	// the partial decode that reference-scn001-run does on a new receipt
	var component struct {
		Passed        bool   `json:"passed"`
		SeiCommit     string `json:"seiCommit"`
		GoVersion     string `json:"goVersion"`
		BundleID      string `json:"bundleId"`
		RecordCount   int    `json:"recordCount"`
		Decision      struct{ ID string }
		ReviewTrigger string `json:"reviewTrigger"`
	}
	if err := json.Unmarshal([]byte(pinJSON(t, receipt)), &component); err != nil || !component.Passed || component.SeiCommit != head || component.RecordCount != 3 || component.BundleID != "scn001" {
		t.Fatalf("%v %+v", err, component)
	}
}

// TestRealSEIPinnedRun runs the pinned path against a real SEI checkout. It needs SEI_ROOT
// and TAI_SEI_EXPECT_COMMIT (and optionally TAI_SEI_EXPECT_GO_VERSION); the expectation is
// never written in this file. Success shows that HEAD, tracked content and the Go
// toolchain match: it does not show that SEI is correct.
func TestRealSEIPinnedRun(t *testing.T) {
	root := seiRootForTest(t)
	options := resolvePinOptions(func() *flag.FlagSet {
		fs := flag.NewFlagSet("real", flag.ContinueOnError)
		registerPinFlags(fs)
		return fs
	}(), os.Getenv)
	if !options.specified() {
		t.Skip("TAI_SEI_EXPECT_COMMIT is not set")
	}
	receipt := RunWithOptions(context.Background(), root, "", options)
	if !receipt.Passed || receipt.Pin.Result != "match" || receipt.Checkout.Status != "unchanged" || receipt.RecordCount != 3 {
		t.Fatalf("%s", pinJSON(t, receipt))
	}
	if status := receipt.Binary.ReportedCommit.Status; status != "not-reported" && status != "match" {
		t.Fatalf("reportedCommit %s", status)
	}
}
