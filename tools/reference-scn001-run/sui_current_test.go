package main

import (
	"bytes"
	"context"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
)

func TestSUIInputModesAreExclusive(t *testing.T) {
	_, err := runWithSUIInputs(context.Background(), t.TempDir(), "", "summary", "source")
	if err == nil || !strings.Contains(err.Error(), "not both") {
		t.Fatalf("ambiguous SUI input: %v", err)
	}
}

func TestAmbiguousSUISourceFailsBeforeComponents(t *testing.T) {
	root := t.TempDir()
	for _, tool := range []string{"reference-mmi-readonly", "reference-sei-decision", "reference-scn001", "reference-scn001-render", "reference-publication-gate"} {
		if err := os.MkdirAll(filepath.Join(root, "tools", tool), 0700); err != nil {
			t.Fatal(err)
		}
	}
	for name, raw := range map[string][]byte{
		"duplicate": []byte(`{"passed":true,"PASSED":false}`),
		"truncated": []byte(`{"passed":`),
		"utf8":      {0xff},
	} {
		t.Run(name, func(t *testing.T) {
			path := filepath.Join(t.TempDir(), "source.json")
			if err := os.WriteFile(path, raw, 0600); err != nil {
				t.Fatal(err)
			}
			_, err := runWithSUIInputs(context.Background(), root, "", "", path)
			if err == nil || !strings.Contains(err.Error(), "SUI source receipt is invalid") {
				t.Fatalf("source was not rejected before execution: %v", err)
			}
			after, err := os.ReadFile(path)
			if err != nil || !bytes.Equal(raw, after) {
				t.Fatal("source changed")
			}
		})
	}
}

func TestCurrentSUILinkRejectsChangedObservation(t *testing.T) {
	root, err := filepath.Abs(taiRootForTest(t))
	if err != nil {
		t.Fatal(err)
	}
	copyRoot := t.TempDir()
	for _, tool := range []string{"reference-mmi-readonly", "reference-sei-decision", "reference-scn001", "reference-scn001-render", "reference-publication-gate", "reference-sui-link"} {
		if err := os.CopyFS(filepath.Join(copyRoot, "tools", tool), os.DirFS(filepath.Join(root, "tools", tool))); err != nil {
			t.Fatal(err)
		}
	}
	if err := os.CopyFS(filepath.Join(copyRoot, "evaluations"), os.DirFS(filepath.Join(root, "evaluations"))); err != nil {
		t.Fatal(err)
	}
	source := filepath.Join(root, "evaluations", "records", "SUI-api-2026-10-26.json")
	before, err := os.ReadFile(source)
	if err != nil {
		t.Fatal(err)
	}
	artifact := filepath.Join(t.TempDir(), "control.md")
	receipt, err := runWithSUIInputs(context.Background(), copyRoot, artifact, "", source)
	if err != nil || !receipt.Passed || receipt.Components.SUILink == nil {
		t.Fatalf("unchanged observations must match: %v", err)
	}
	packet, err := BuildOwnerPacketWithArtifact(receipt, artifact)
	if err != nil || !packet.ArtifactBytesVerified || packet.HumanReviewed || packet.AuthorityVerified || packet.PublicationApproved {
		t.Fatalf("content matching changed review authority: %+v %v", packet, err)
	}
	csv := filepath.Join(copyRoot, "tools", "reference-mmi-readonly", "testdata", "workspace", "observations.csv")
	raw, err := os.ReadFile(csv)
	if err != nil {
		t.Fatal(err)
	}
	old := []byte("施設の利用は予約不要")
	if bytes.Count(raw, old) != 2 {
		t.Fatal("expected O-02/O-07")
	}
	changed := bytes.ReplaceAll(raw, old, []byte("施設の利用は予約不要（SUI照合の比較試験）"))
	if err := os.WriteFile(csv, changed, 0600); err != nil {
		t.Fatal(err)
	}
	rejectedArtifact := filepath.Join(t.TempDir(), "rejected.md")
	rejected, err := runWithSUIInputs(context.Background(), copyRoot, rejectedArtifact, "", source)
	if err == nil || !strings.Contains(err.Error(), "card digest does not match the SCN observation: O-02") {
		t.Fatalf("changed current observation accepted: %+v %v", rejected, err)
	}
	if _, err := os.Stat(rejectedArtifact); !os.IsNotExist(err) {
		t.Fatal("rejected input saved an artifact")
	}
	if _, err := BuildOwnerPacket(rejected); err == nil {
		t.Fatal("rejected input reached an owner packet")
	}
	after, err := os.ReadFile(source)
	if err != nil || !bytes.Equal(before, after) {
		t.Fatal("source SUI receipt changed")
	}
	after, err = os.ReadFile(csv)
	if err != nil || !bytes.Equal(changed, after) {
		t.Fatal("copy workspace changed during execution")
	}
}

func TestSUIReceiptCLIInputAndOutputBoundaries(t *testing.T) {
	if _, err := exec.LookPath("go"); err != nil {
		t.Skip("go is not available")
	}
	binary := filepath.Join(t.TempDir(), "run")
	if runtime.GOOS == "windows" {
		binary += ".exe"
	}
	if output, err := exec.Command("go", "build", "-o", binary, ".").CombinedOutput(); err != nil {
		t.Fatalf("build: %s %v", output, err)
	}
	source := filepath.Join(t.TempDir(), "source.json")
	raw := []byte(`{"passed":true}`)
	if err := os.WriteFile(source, raw, 0600); err != nil {
		t.Fatal(err)
	}
	for _, args := range [][]string{
		{"-sui-receipt", source, "-sui-link", "saved"},
		{"-sui-receipt", source, "-verify", "saved"},
		{"-sui-receipt", source, "-owner-packet", "saved"},
		{"-sui-receipt", source, "-artifact", "saved"},
		{"-sui-receipt", source, "-out", source},
	} {
		cmd := exec.Command(binary, args...)
		var stdout, stderr bytes.Buffer
		cmd.Stdout, cmd.Stderr = &stdout, &stderr
		err := cmd.Run()
		if exit, ok := err.(*exec.ExitError); !ok || exit.ExitCode() != 2 || stdout.Len() != 0 {
			t.Fatalf("invalid args %v: %v stdout=%s stderr=%s", args, err, &stdout, &stderr)
		}
	}
	after, err := os.ReadFile(source)
	if err != nil || !bytes.Equal(raw, after) {
		t.Fatal("CLI replaced its input")
	}
}
