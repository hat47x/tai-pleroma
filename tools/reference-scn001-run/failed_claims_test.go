package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"testing"
)

func TestFailedComponentsCannotClaimReviewAuthorityOrPublication(t *testing.T) {
	cases := map[string]func(*RunReceipt){
		"SEI human review":              func(r *RunReceipt) { r.Components.SEI.HumanReviewed = true },
		"SEI authority":                 func(r *RunReceipt) { r.Components.SEI.AuthorityVerified = true },
		"SEI publication":               func(r *RunReceipt) { r.Components.SEI.Published = true },
		"SCN human review":              func(r *RunReceipt) { r.Components.SCN001.HumanReviewed = true },
		"SCN authority":                 func(r *RunReceipt) { r.Components.SCN001.AuthorityVerified = true },
		"SCN publication approval":      func(r *RunReceipt) { r.Components.SCN001.PublicationApproved = true },
		"artifact authority":            func(r *RunReceipt) { r.Components.ReviewArtifact.AuthorityVerified = true },
		"artifact publication approval": func(r *RunReceipt) { r.Components.ReviewArtifact.PublicationApproved = true },
	}
	for name, claim := range cases {
		t.Run(name, func(t *testing.T) {
			receipt := consistentFailedRun(t)
			claim(&receipt)
			var err error
			receipt.RunDigest, err = digestJSON(receipt.Components)
			if err != nil {
				t.Fatal(err)
			}
			if result := Verify(receipt); result.Passed {
				t.Fatalf("failed component hid an unsupported claim: %+v", result)
			}
		})
	}
}

func TestFailedSEIClaimCannotPassArtifactRecheck(t *testing.T) {
	receipt := recordedRunForMutation(t)
	receipt.Components.SEI.Passed = false
	receipt.Components.SEI.HumanReviewed = true
	receipt.Passed = false
	receipt.RealProductsConnected = false
	var err error
	receipt.RunDigest, err = digestJSON(receipt.Components)
	if err != nil {
		t.Fatal(err)
	}
	artifact := filepath.Join("..", "..", "evaluations", "artifacts", "SCN-001-D-04-provisional.md")
	if result := VerifyArtifact(receipt, artifact); result.Passed || result.ArtifactBytesVerified {
		t.Fatalf("byte match hid a failed component's review claim: %+v", result)
	}
}

// Stand-ins inject child process outputs; they do not establish MMI/SEI behavior.
func childReceiptRoot(t *testing.T, receipt RunReceipt) string {
	t.Helper()
	if _, err := exec.LookPath("go"); err != nil {
		t.Skip("go is not available")
	}
	artifact, err := os.ReadFile(filepath.Join("..", "..", "evaluations", "artifacts", "SCN-001-D-04-provisional.md"))
	if err != nil {
		t.Fatal(err)
	}
	root := t.TempDir()
	for name, component := range map[string]any{
		"reference-mmi-readonly":     receipt.Components.MMI,
		"reference-sei-decision":     receipt.Components.SEI,
		"reference-scn001":           receipt.Components.SCN001,
		"reference-scn001-render":    receipt.Components.ReviewArtifact,
		"reference-publication-gate": receipt.Components.PublicationGate,
	} {
		dir := filepath.Join(root, "tools", name)
		if err := os.MkdirAll(dir, 0700); err != nil {
			t.Fatal(err)
		}
		raw, err := json.Marshal(component)
		if err != nil {
			t.Fatal(err)
		}
		fileBytes := raw
		if name == "reference-scn001-render" {
			fileBytes = artifact
		}
		source := fmt.Sprintf(`package main
import ("flag"; "os")
func main() {
 out := flag.String("out", "", "")
 for _, name := range []string{"workspace", "fixture", "mmi-receipt", "out-fixture", "status"} { flag.String(name, "", "") }
 flag.Parse()
 if *out != "" { if err := os.WriteFile(*out, []byte(%q), 0600); err != nil { panic(err) } }
 os.Stdout.Write([]byte(%q))
}
`, string(fileBytes), string(raw))
		if err := os.WriteFile(filepath.Join(dir, "go.mod"), []byte("module child-receipt-test\n\ngo 1.26\n"), 0600); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(filepath.Join(dir, "main.go"), []byte(source), 0600); err != nil {
			t.Fatal(err)
		}
	}
	return root
}

func TestRunChecksChildClaimsBeforeReturning(t *testing.T) {
	receipt := recordedRunForMutation(t)
	receipt.Components.ReviewArtifact.AuthorityVerified = true
	root := childReceiptRoot(t, receipt)
	if result, err := Run(context.Background(), root); err == nil {
		t.Fatalf("normal run returned inconsistent child evidence without an error: passed=%v", result.Passed)
	}
}

func TestRunKeepsConsistentFailureInspectable(t *testing.T) {
	receipt := recordedRunForMutation(t)
	receipt.Components.SEI.Passed = false
	root := childReceiptRoot(t, receipt)
	result, err := Run(context.Background(), root)
	if err != nil {
		t.Fatal(err)
	}
	if result.Passed || result.RealProductsConnected || !Verify(result).Passed {
		t.Fatal("consistent component failure was hidden or made uninspectable")
	}
	if _, err := BuildOwnerPacket(result); err == nil {
		t.Fatal("failed run became an owner packet")
	}
}
