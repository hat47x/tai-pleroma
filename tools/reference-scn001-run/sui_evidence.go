package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
)

const suiEvidenceSchema = "tai.reference.scn001-sui-evidence/v0"

var suiEvidenceFiles = []string{"run.json", "mmi.json", "resolved-scn001.json", "sui-source.json", "review.md"}

type suiEvidenceManifest struct {
	Schema    string            `json:"schema"`
	RunDigest string            `json:"runDigest"`
	Files     map[string]string `json:"files"`
}

type SUIEvidenceVerification struct {
	Schema                string `json:"schema"`
	Passed                bool   `json:"passed"`
	Reason                string `json:"reason,omitempty"`
	RunDigest             string `json:"runDigest,omitempty"`
	ArtifactBytesVerified bool   `json:"artifactBytesVerified"`
	SUIContentVerified    bool   `json:"suiContentVerified"`
	HumanReviewed         bool   `json:"humanReviewed"`
	AuthorityVerified     bool   `json:"authorityVerified"`
	PublicationApproved   bool   `json:"publicationApproved"`
}

func checkSUIEvidenceOutput(dir string, outputs ...string) error {
	if err := requireNewReviewPath(dir); err != nil {
		return err
	}
	base, err := filepath.Abs(dir)
	if err != nil {
		return err
	}
	for _, output := range outputs {
		if output == "" {
			continue
		}
		absolute, err := filepath.Abs(output)
		if err != nil {
			return err
		}
		if !strings.EqualFold(filepath.VolumeName(base), filepath.VolumeName(absolute)) {
			continue
		}
		relative, err := filepath.Rel(base, absolute)
		if err != nil {
			return err
		}
		if relative != ".." && !strings.HasPrefix(relative, ".."+string(filepath.Separator)) {
			return fmt.Errorf("separate outputs must be outside the SUI evidence directory")
		}
	}
	return nil
}

// Capture a regular file once, without following a substituted symlink.
func readEvidenceFile(path string) ([]byte, error) {
	info, err := os.Lstat(path)
	if err != nil {
		return nil, err
	}
	if !info.Mode().IsRegular() {
		return nil, fmt.Errorf("evidence input is not a regular file: %s", path)
	}
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()
	opened, err := file.Stat()
	if err != nil {
		return nil, err
	}
	if !os.SameFile(info, opened) {
		return nil, fmt.Errorf("evidence file changed while opening: %s", path)
	}
	return io.ReadAll(file)
}

func validateSUIEvidence(manifest suiEvidenceManifest, files map[string][]byte) (RunReceipt, error) {
	var receipt RunReceipt
	if manifest.Schema != suiEvidenceSchema || len(manifest.Files) != len(suiEvidenceFiles) || len(files) != len(suiEvidenceFiles) {
		return receipt, fmt.Errorf("unsupported SUI evidence schema or file set")
	}
	for _, name := range suiEvidenceFiles {
		raw, ok := files[name]
		if !ok || manifest.Files[name] != artifactDigest(raw) {
			return receipt, fmt.Errorf("SUI evidence bytes differ: %s", name)
		}
		if name != "review.md" {
			var checked json.RawMessage
			if err := decodeEvidenceJSON(raw, &checked); err != nil {
				return receipt, fmt.Errorf("invalid %s: %w", name, err)
			}
		}
	}
	if err := decodeEvidenceJSON(files["run.json"], &receipt); err != nil {
		return receipt, err
	}
	if verification := Verify(receipt); !verification.Passed {
		return receipt, fmt.Errorf("invalid evidence run: %s", verification.Reason)
	}
	if !receipt.Passed || receipt.Components.SUILink == nil || manifest.RunDigest != receipt.RunDigest {
		return receipt, fmt.Errorf("SUI evidence requires its successful run with SUI link")
	}
	if artifactDigest(files["review.md"]) != receipt.Components.ReviewArtifact.ArtifactDigest {
		return receipt, fmt.Errorf("SUI evidence artifact differs from run")
	}
	var mmi MMIComponent
	if err := decodeEvidenceJSON(files["mmi.json"], &mmi); err != nil {
		return receipt, err
	}
	if !sameEvidenceValue(mmi, receipt.Components.MMI) {
		return receipt, fmt.Errorf("saved MMI component differs from run")
	}
	return receipt, nil
}

func sameEvidenceValue(a, b any) bool {
	left, err1 := json.Marshal(a)
	right, err2 := json.Marshal(b)
	return err1 == nil && err2 == nil && bytes.Equal(left, right)
}

func loadSUIEvidence(dir string) (map[string][]byte, RunReceipt, error) {
	var receipt RunReceipt
	info, err := os.Lstat(dir)
	if err != nil || !info.IsDir() || info.Mode()&os.ModeSymlink != 0 {
		return nil, receipt, fmt.Errorf("SUI evidence must be a directory without a symlink")
	}
	entries, err := os.ReadDir(dir)
	if err != nil || len(entries) != len(suiEvidenceFiles)+1 {
		return nil, receipt, fmt.Errorf("SUI evidence directory has an incomplete or unexpected file set")
	}
	raw, err := readEvidenceFile(filepath.Join(dir, "manifest.json"))
	if err != nil {
		return nil, receipt, err
	}
	var manifest suiEvidenceManifest
	if err := decodeEvidenceJSON(raw, &manifest); err != nil {
		return nil, receipt, err
	}
	files := make(map[string][]byte)
	for _, name := range suiEvidenceFiles {
		files[name], err = readEvidenceFile(filepath.Join(dir, name))
		if err != nil {
			return nil, receipt, err
		}
	}
	receipt, err = validateSUIEvidence(manifest, files)
	return files, receipt, err
}

func saveSUIEvidence(dir string, receipt RunReceipt, files map[string][]byte) error {
	manifest := suiEvidenceManifest{Schema: suiEvidenceSchema, RunDigest: receipt.RunDigest, Files: make(map[string]string)}
	for _, name := range suiEvidenceFiles {
		manifest.Files[name] = artifactDigest(files[name])
	}
	saved, err := validateSUIEvidence(manifest, files)
	if err != nil {
		return err
	}
	if !sameEvidenceValue(saved, receipt) {
		return fmt.Errorf("evidence run differs from the requested run")
	}
	if err := os.Mkdir(dir, 0700); err != nil {
		return err
	}
	for _, name := range suiEvidenceFiles {
		if err := writeNewReviewFile(filepath.Join(dir, name), files[name]); err != nil {
			return err
		}
	}
	raw, err := json.MarshalIndent(manifest, "", "  ")
	if err != nil {
		return err
	}
	// Last file marks a complete set; incomplete directories are never reused.
	if err := writeNewReviewFile(filepath.Join(dir, "manifest.json"), append(raw, '\n')); err != nil {
		return err
	}
	_, _, err = loadSUIEvidence(dir)
	return err
}

// Replay uses captured inputs and the currently selected local reference tools.
// It does not repeat MMI/SEI access, establish provenance, or grant approval.
func VerifySUIEvidence(ctx context.Context, root, dir string) SUIEvidenceVerification {
	result := SUIEvidenceVerification{Schema: "tai.reference.scn001-sui-evidence-verification/v0"}
	fail := func(err error) SUIEvidenceVerification {
		result.Reason = err.Error()
		return result
	}
	files, receipt, err := loadSUIEvidence(dir)
	if err != nil {
		return fail(err)
	}
	result.RunDigest = receipt.RunDigest
	work, err := os.MkdirTemp("", "tai-sui-replay-")
	if err != nil {
		return fail(err)
	}
	defer os.RemoveAll(work)
	for _, name := range suiEvidenceFiles {
		if err := writeNewReviewFile(filepath.Join(work, name), files[name]); err != nil {
			return fail(err)
		}
	}
	fixture := filepath.Join(work, "resolved-scn001.json")
	resolved := filepath.Join(work, "re-resolved.json")
	scnOutput, err := goRunOutput(ctx, filepath.Join(root, "tools", "reference-scn001"),
		"run", ".", "-fixture", fixture, "-mmi-receipt", filepath.Join(work, "mmi.json"), "-out-fixture", resolved)
	if err != nil {
		return fail(fmt.Errorf("reapplying saved MMI observations: %w", err))
	}
	var scn SCNComponent
	if err := decodeEvidenceJSON(scnOutput, &scn); err != nil {
		return fail(err)
	}
	raw, err := os.ReadFile(resolved)
	if err != nil || !bytes.Equal(raw, files["resolved-scn001.json"]) || !sameEvidenceValue(scn, receipt.Components.SCN001) {
		return fail(fmt.Errorf("saved MMI observations or SCN result do not match the resolved fixture and run"))
	}
	linkOutput, err := goRunOutput(ctx, filepath.Join(root, "tools", "reference-sui-link"),
		"run", ".", "-fixture", fixture, "-sui-receipt", filepath.Join(work, "sui-source.json"))
	if err != nil {
		return fail(fmt.Errorf("rechecking saved SUI content: %w", err))
	}
	var link struct {
		SUILinkComponent
		Schema string `json:"schema"`
	}
	if err := decodeEvidenceJSON(linkOutput, &link); err != nil {
		return fail(err)
	}
	if link.Schema != "tai.reference.sui-scn-link/v0" || !sameEvidenceValue(link.SUILinkComponent, *receipt.Components.SUILink) {
		return fail(fmt.Errorf("rechecked SUI link differs from run"))
	}
	artifact := filepath.Join(work, "re-rendered.md")
	renderOutput, err := goRunOutput(ctx, filepath.Join(root, "tools", "reference-scn001-render"), "run", ".", "-fixture", fixture, "-out", artifact)
	if err != nil {
		return fail(err)
	}
	var rendered ArtifactComponent
	if err := decodeEvidenceJSON(renderOutput, &rendered); err != nil {
		return fail(err)
	}
	raw, err = os.ReadFile(artifact)
	if err != nil || !bytes.Equal(raw, files["review.md"]) || !sameEvidenceValue(rendered, receipt.Components.ReviewArtifact) {
		return fail(fmt.Errorf("re-rendered artifact differs from saved run and bytes"))
	}
	result.Passed, result.ArtifactBytesVerified, result.SUIContentVerified = true, true, true
	return result
}
