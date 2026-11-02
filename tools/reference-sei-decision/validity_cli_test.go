package main

import (
	"bytes"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"reflect"
	"testing"
)

// fakeSEIVerify stands in for `sei verify --input`. It checks nothing: it reads bundle_id and the number of
// records and prints the summary shape that inspectValidity expects. It exists only so that the built binary's
// success path (flag wiring, -out, exit code) runs where no SEI checkout exists, such as CI. It says nothing
// about SEI's own structural check, and recordStructureChecked in these reports does not mean SEI ran.
const fakeSEIVerify = `package main

import (
	"encoding/json"
	"fmt"
	"os"
)

func main() {
	if len(os.Args) != 4 || os.Args[1] != "verify" || os.Args[2] != "--input" {
		fmt.Fprintln(os.Stderr, "fake sei: unexpected arguments")
		os.Exit(2)
	}
	raw, err := os.ReadFile(os.Args[3])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	var bundle map[string]json.RawMessage
	var id string
	var records []json.RawMessage
	if json.Unmarshal(raw, &bundle) != nil || json.Unmarshal(bundle["bundle_id"], &id) != nil || json.Unmarshal(bundle["records"], &records) != nil {
		fmt.Fprintln(os.Stderr, "fake sei: not a bundle")
		os.Exit(1)
	}
	json.NewEncoder(os.Stdout).Encode(map[string]any{"bundle_id": id, "record_count": len(records), "validated_count": len(records), "not_verified_count": 0})
}
`

func fakeSEIRoot(t *testing.T) string {
	t.Helper()
	root := t.TempDir()
	dir := filepath.Join(root, "runtime", "go")
	if err := os.MkdirAll(filepath.Join(dir, "cmd", "sei"), 0o755); err != nil {
		t.Fatal(err)
	}
	for name, content := range map[string]string{"go.mod": "module fakesei\n\ngo 1.21\n", filepath.Join("cmd", "sei", "main.go"): fakeSEIVerify} {
		if err := os.WriteFile(filepath.Join(dir, name), []byte(content), 0o600); err != nil {
			t.Fatal(err)
		}
	}
	return root
}

// runTool runs the built binary and returns its exit code and stdout.
func runTool(t *testing.T, binary string, args ...string) (int, []byte) {
	t.Helper()
	cmd := exec.Command(binary, args...)
	var stdout bytes.Buffer
	cmd.Stdout = &stdout
	err := cmd.Run()
	if exit, ok := err.(*exec.ExitError); ok {
		return exit.ExitCode(), stdout.Bytes()
	} else if err != nil {
		t.Fatal(err)
	}
	return 0, stdout.Bytes()
}

// The exit-1/exit-2 paths are checked in TestValidityCLIFlagsAndExitCodes. This is the success path: the flags must
// reach runValidity (bundle, target, every -decision, -out) and the report must be printed and written.
func TestValidityCLIWiresFlagsOnTheSuccessPath(t *testing.T) {
	if _, err := exec.LookPath("go"); err != nil {
		t.Skip("go is not available")
	}
	dir := t.TempDir()
	binary := filepath.Join(dir, "tool"+exeSuffix)
	if out, err := exec.Command("go", "build", "-o", binary, ".").CombinedOutput(); err != nil {
		t.Fatalf("build: %v: %s", err, out)
	}
	root := fakeSEIRoot(t)
	validity := func(name string) string { return filepath.Join("testdata", "validity", name+".json") }

	// bundle, target and -decision all reach the report, and -out receives the same bytes that are printed
	outPath := filepath.Join(dir, "report.json")
	code, stdout := runTool(t, binary, "-sei-root", root, "-decision-validity", validity("t-ap-scope-reaccepted"), "-current-target", validity("target-ap-scope"),
		"-decision", nameD1, "-decision", nameD3, "-out", outPath)
	if code != 0 {
		t.Fatalf("a produced report must exit 0, got %d", code)
	}
	written, err := os.ReadFile(outPath)
	if err != nil || !bytes.Equal(written, stdout) {
		t.Fatalf("-out must hold the printed report (err %v)", err)
	}
	var r ValidityInspection
	if err := json.Unmarshal(stdout, &r); err != nil {
		t.Fatal(err)
	}
	if r.BundleID != "n33-ap-scope" || r.RecordCount != 3 {
		t.Fatalf("%+v", r)
	}
	var names []string
	for _, named := range r.NamedDecisions {
		names = append(names, named.Ref)
	}
	if !reflect.DeepEqual(names, []string{nameD1, nameD3}) || !reflect.DeepEqual(r.BoundDecisionRecordIDs, []string{"rec-d3"}) ||
		!isTrue(r.StructurallyBoundToCurrentTarget) || r.ReacceptanceRequired != nil || r.CurrentTargetSource != "caller-supplied" {
		t.Fatalf("every -decision and the -current-target file must reach the report: %+v", r)
	}

	// another bundle and target file naming the old Decision, and then a name that is not in the bundle
	code, stdout = runTool(t, binary, "-sei-root", root, "-decision-validity", validity("t-a"), "-current-target", validity("target-a"), "-decision", nameD1)
	var a ValidityInspection
	if code != 0 || json.Unmarshal(stdout, &a) != nil || !isTrue(a.StructurallyBoundToCurrentTarget) || !reflect.DeepEqual(a.BoundDecisionRecordIDs, []string{"rec-d1"}) {
		t.Fatalf("exit %d: %s", code, stdout)
	}
	code, stdout = runTool(t, binary, "-sei-root", root, "-decision-validity", validity("t-a"), "-current-target", validity("target-a"), "-decision", "decision:dec-missing")
	var missing ValidityInspection
	if code != 0 || json.Unmarshal(stdout, &missing) != nil || !hasCode(missing, "named-decision-not-found", true) || missing.StructurallyBoundToCurrentTarget != nil {
		t.Fatalf("a name that is not in the bundle must reach the report as unresolved, not as no name: exit %d: %s", code, stdout)
	}

	// bundle and target are not interchangeable
	if code, stdout = runTool(t, binary, "-sei-root", root, "-decision-validity", validity("target-a"), "-current-target", validity("t-a"), "-decision", nameD1); code != 1 || len(stdout) != 0 {
		t.Fatalf("a target file given as the bundle must be rejected without a report (exit %d)", code)
	}

	// an existing -out file is kept and no report is printed (exit 2)
	if code, stdout = runTool(t, binary, "-sei-root", root, "-decision-validity", validity("t-a"), "-current-target", validity("target-a"), "-decision", nameD1, "-out", outPath); code != 2 || len(stdout) != 0 {
		t.Fatalf("exit %d, stdout %q", code, stdout)
	}
	if after, err := os.ReadFile(outPath); err != nil || !bytes.Equal(after, written) {
		t.Fatal("the existing -out file changed")
	}
}
