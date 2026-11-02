package main

import (
	"bytes"
	"context"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
)

func unitSUIEvidence(t *testing.T) (RunReceipt, map[string][]byte) {
	t.Helper()
	run := recordedRunForMutation(t)
	raw, err := json.MarshalIndent(run, "", "  ")
	if err != nil {
		t.Fatal(err)
	}
	mmi, err := json.Marshal(run.Components.MMI)
	if err != nil {
		t.Fatal(err)
	}
	// Structural unit fixture only; {} inputs cannot pass the content replay.
	return run, map[string][]byte{"run.json": append(raw, '\n'), "mmi.json": mmi,
		"resolved-scn001.json": []byte("{}"), "sui-source.json": []byte("{}"), "review.md": reviewBytes(t)}
}

func evidenceBytes(t *testing.T, dir string) map[string][]byte {
	t.Helper()
	files := make(map[string][]byte)
	for _, name := range append(append([]string{}, suiEvidenceFiles...), "manifest.json") {
		raw, err := os.ReadFile(filepath.Join(dir, name))
		if err != nil {
			t.Fatal(err)
		}
		files[name] = raw
	}
	return files
}

func TestSUIEvidenceRejectsReplacementAndUnsafeOutputs(t *testing.T) {
	run, files := unitSUIEvidence(t)
	dir := filepath.Join(t.TempDir(), "evidence")
	if err := saveSUIEvidence(dir, run, files); err != nil {
		t.Fatal(err)
	}
	before := evidenceBytes(t, dir)
	if err := saveSUIEvidence(dir, run, files); err == nil {
		t.Fatal("existing evidence was reused")
	}
	if !sameEvidenceValue(before, evidenceBytes(t, dir)) {
		t.Fatal("existing evidence was changed")
	}
	other := run
	other.GeneratedAt = "2000-01-01T00:00:00Z"
	if err := saveSUIEvidence(filepath.Join(t.TempDir(), "mismatched"), other, files); err == nil {
		t.Fatal("a different run was paired with the evidence")
	}
	for _, output := range []string{dir, filepath.Join(dir, "run.json"), filepath.Join(dir, "nested", "output")} {
		fresh := filepath.Join(t.TempDir(), "evidence")
		inside := strings.Replace(output, dir, fresh, 1)
		if err := checkSUIEvidenceOutput(fresh, inside); err == nil {
			t.Fatal("separate output inside the evidence directory accepted")
		}
	}
	for _, name := range suiEvidenceFiles {
		t.Run(name, func(t *testing.T) {
			copy := filepath.Join(t.TempDir(), "evidence")
			if err := saveSUIEvidence(copy, run, files); err != nil {
				t.Fatal(err)
			}
			if err := os.WriteFile(filepath.Join(copy, name), append(append([]byte{}, files[name]...), ' '), 0600); err != nil {
				t.Fatal(err)
			}
			result := VerifySUIEvidence(context.Background(), "unused-root", copy)
			if result.Passed || result.SUIContentVerified || result.ArtifactBytesVerified || !strings.Contains(result.Reason, "bytes differ") {
				t.Fatalf("replacement reached replay: %+v", result)
			}
		})
	}
}

func TestSUIEvidenceManifestAndFileBoundaries(t *testing.T) {
	run, files := unitSUIEvidence(t)
	for _, mode := range []string{"missing manifest", "duplicate manifest key", "unknown schema", "unknown name", "extra file", "nonregular file", "ambiguous input"} {
		t.Run(mode, func(t *testing.T) {
			dir := filepath.Join(t.TempDir(), "evidence")
			if err := saveSUIEvidence(dir, run, files); err != nil {
				t.Fatal(err)
			}
			path := filepath.Join(dir, "manifest.json")
			raw, err := os.ReadFile(path)
			if err != nil {
				t.Fatal(err)
			}
			var manifest suiEvidenceManifest
			if err := json.Unmarshal(raw, &manifest); err != nil {
				t.Fatal(err)
			}
			switch mode {
			case "missing manifest":
				err = os.Remove(path)
			case "duplicate manifest key":
				err = os.WriteFile(path, append([]byte(`{"schema":"other",`), raw[1:]...), 0600)
			case "unknown schema":
				manifest.Schema = "other"
			case "unknown name":
				delete(manifest.Files, "mmi.json")
				manifest.Files["../mmi.json"] = "sha256:other"
			case "extra file":
				err = os.WriteFile(filepath.Join(dir, "extra"), []byte("extra"), 0600)
			case "nonregular file":
				err = os.Remove(filepath.Join(dir, "mmi.json"))
				if err == nil {
					err = os.Mkdir(filepath.Join(dir, "mmi.json"), 0700)
				}
			case "ambiguous input":
				bad := append([]byte(`{"passed":false,`), files["mmi.json"][1:]...)
				manifest.Files["mmi.json"] = artifactDigest(bad)
				err = os.WriteFile(filepath.Join(dir, "mmi.json"), bad, 0600)
			}
			if err != nil {
				t.Fatal(err)
			}
			if mode == "unknown schema" || mode == "unknown name" || mode == "ambiguous input" {
				updated, err := json.Marshal(manifest)
				if err != nil {
					t.Fatal(err)
				}
				if err := os.WriteFile(path, updated, 0600); err != nil {
					t.Fatal(err)
				}
			}
			result := VerifySUIEvidence(context.Background(), "unused-root", dir)
			if result.Passed || result.SUIContentVerified || result.ArtifactBytesVerified {
				t.Fatalf("invalid bundle accepted: %+v", result)
			}
		})
	}
}

func TestSUIEvidenceDoesNotFollowSymlinks(t *testing.T) {
	run, files := unitSUIEvidence(t)
	dir := filepath.Join(t.TempDir(), "evidence")
	if err := saveSUIEvidence(dir, run, files); err != nil {
		t.Fatal(err)
	}
	link := filepath.Join(t.TempDir(), "linked-evidence")
	if err := os.Symlink(dir, link); err != nil {
		t.Skipf("symlink creation is unavailable: %v", err)
	}
	if _, _, err := loadSUIEvidence(link); err == nil {
		t.Fatal("evidence root symlink was followed")
	}
	outside := filepath.Join(t.TempDir(), "mmi.json")
	if err := os.WriteFile(outside, files["mmi.json"], 0600); err != nil {
		t.Fatal(err)
	}
	if err := os.Remove(filepath.Join(dir, "mmi.json")); err != nil {
		t.Fatal(err)
	}
	if err := os.Symlink(outside, filepath.Join(dir, "mmi.json")); err != nil {
		t.Fatal(err)
	}
	if _, _, err := loadSUIEvidence(dir); err == nil {
		t.Fatal("evidence file symlink was followed")
	}
}

func TestSUIEvidenceRetainsAndReplaysThisRun(t *testing.T) {
	root, err := filepath.Abs(taiRootForTest(t))
	if err != nil {
		t.Fatal(err)
	}
	raw, err := os.ReadFile(filepath.Join(root, "evaluations", "records", "SUI-api-2026-10-26.json"))
	if err != nil {
		t.Fatal(err)
	}
	snapshot := append(append([]byte(" \r\n"), raw...), []byte("\n ")...)
	source := filepath.Join(t.TempDir(), "source.json")
	if err := os.WriteFile(source, snapshot, 0600); err != nil {
		t.Fatal(err)
	}
	dir := filepath.Join(t.TempDir(), "evidence")
	receipt, err := runWithSUIEvidenceOutput(context.Background(), root, "", "", source, dir)
	if err != nil || !receipt.Passed {
		t.Fatalf("capture: %v", err)
	}
	before := evidenceBytes(t, dir)
	if !bytes.Equal(snapshot, before["sui-source.json"]) {
		t.Fatal("original SUI bytes, including whitespace, were not retained")
	}
	// The original source path is deliberately replaced. Replay uses its saved
	// snapshot, without repeating product access or reading that original path.
	if err := os.WriteFile(source, []byte(`{"passed":false}`), 0600); err != nil {
		t.Fatal(err)
	}
	result := VerifySUIEvidence(context.Background(), root, dir)
	if !result.Passed || !result.SUIContentVerified || !result.ArtifactBytesVerified || result.HumanReviewed || result.AuthorityVerified || result.PublicationApproved {
		t.Fatalf("replay failed or granted approval: %+v", result)
	}
	if !sameEvidenceValue(before, evidenceBytes(t, dir)) {
		t.Fatal("read-only replay changed evidence")
	}
	for _, mode := range []string{"MMI selected text", "resolved text", "SUI card digest", "run SUI identity", "artifact and run"} {
		t.Run(mode, func(t *testing.T) {
			copy := filepath.Join(t.TempDir(), "evidence")
			if err := os.CopyFS(copy, os.DirFS(dir)); err != nil {
				t.Fatal(err)
			}
			files := evidenceBytes(t, copy)
			var run RunReceipt
			if err := json.Unmarshal(files["run.json"], &run); err != nil {
				t.Fatal(err)
			}
			var value map[string]any
			name := ""
			switch mode {
			case "MMI selected text":
				name = "mmi.json"
				_ = json.Unmarshal(files[name], &value)
				row := value["selected"].([]any)[0].(map[string]any)
				row["text"] = row["text"].(string) + " changed"
			case "resolved text":
				name = "resolved-scn001.json"
				_ = json.Unmarshal(files[name], &value)
				for _, item := range value["observations"].([]any) {
					row := item.(map[string]any)
					if row["id"] == "O-02" {
						row["text"] = row["text"].(string) + " changed"
					}
				}
			case "SUI card digest":
				name = "sui-source.json"
				_ = json.Unmarshal(files[name], &value)
				value["documentCards"].([]any)[0].(map[string]any)["textDigest"] = "sha256:changed"
			case "run SUI identity":
				run.Components.SUILink.DocumentID = "different-document"
			case "artifact and run":
				files["review.md"] = append(append([]byte{}, files["review.md"]...), []byte("changed\n")...)
				run.Components.ReviewArtifact.ArtifactDigest = artifactDigest(files["review.md"])
			}
			if name != "" {
				files[name], err = json.MarshalIndent(value, "", "  ")
				if err != nil {
					t.Fatal(err)
				}
				files[name] = append(files[name], '\n')
			}
			run.RunDigest, err = digestJSON(run.Components)
			if err != nil {
				t.Fatal(err)
			}
			files["run.json"], err = json.MarshalIndent(run, "", "  ")
			if err != nil {
				t.Fatal(err)
			}
			files["run.json"] = append(files["run.json"], '\n')
			manifest := suiEvidenceManifest{Schema: suiEvidenceSchema, RunDigest: run.RunDigest, Files: make(map[string]string)}
			for _, file := range suiEvidenceFiles {
				manifest.Files[file] = artifactDigest(files[file])
				if err := os.WriteFile(filepath.Join(copy, file), files[file], 0600); err != nil {
					t.Fatal(err)
				}
			}
			encoded, err := json.Marshal(manifest)
			if err != nil {
				t.Fatal(err)
			}
			if err := os.WriteFile(filepath.Join(copy, "manifest.json"), encoded, 0600); err != nil {
				t.Fatal(err)
			}
			if _, _, err := loadSUIEvidence(copy); err != nil {
				t.Fatalf("case must pass hashes and structural validation before content replay: %v", err)
			}
			bad := VerifySUIEvidence(context.Background(), root, copy)
			if bad.Passed || bad.SUIContentVerified || bad.ArtifactBytesVerified {
				t.Fatalf("rehashing hid content mismatch: %+v", bad)
			}
		})
	}
}

func TestSUIEvidenceCLIRejectsModeAndOutputConflicts(t *testing.T) {
	if _, err := exec.LookPath("go"); err != nil {
		t.Skip("go is not available")
	}
	binary := filepath.Join(t.TempDir(), "run")
	if runtime.GOOS == "windows" {
		binary += ".exe"
	}
	if raw, err := exec.Command("go", "build", "-o", binary, ".").CombinedOutput(); err != nil {
		t.Fatalf("build: %v %s", err, raw)
	}
	work := t.TempDir()
	dir := filepath.Join(work, "evidence")
	for _, args := range [][]string{
		{"-sui-evidence-out", dir},
		{"-sui-evidence-out", dir, "-sui-receipt", "source", "-out", filepath.Join(dir, "run.json")},
		{"-sui-evidence-out", work, "-sui-receipt", "source"},
		{"-verify-sui-evidence", dir, "-verify", "run.json"},
		{"-verify-sui-evidence", dir, "-owner-packet", "run.json"},
		{"-verify-sui-evidence", dir, "-out", filepath.Join(work, "result.json")},
	} {
		cmd := exec.Command(binary, args...)
		var stdout bytes.Buffer
		cmd.Stdout = &stdout
		err := cmd.Run()
		if exit, ok := err.(*exec.ExitError); !ok || exit.ExitCode() != 2 || stdout.Len() != 0 {
			t.Fatalf("invalid mode %v accepted: %v %s", args, err, &stdout)
		}
	}
	if entries, err := os.ReadDir(work); err != nil || len(entries) != 0 {
		t.Fatal("rejected modes created output")
	}
}
