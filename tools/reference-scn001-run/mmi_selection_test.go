package main

import (
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"testing"
)

func TestAmbiguousMMISelectionDoesNotReplaceResolvedFixture(t *testing.T) {
	for name, ids := range map[string][]string{
		"missing O-07":   {"O-02", "O-03"},
		"duplicate O-02": {"O-02", "O-03", "O-02"},
	} {
		t.Run(name, func(t *testing.T) {
			work := t.TempDir()
			rows := []map[string]string{}
			for _, id := range ids {
				text := "施設の利用は予約不要"
				if id == "O-03" {
					text = "会議室の利用には事前予約が必要"
				}
				rows = append(rows, map[string]string{"id": id, "text": text, "source": "test-copy", "version": "v0", "availability": "available"})
			}
			raw, err := json.Marshal(map[string]any{
				"schema": "tai.reference.mmi-readonly/v0", "realProductConnected": true,
				"readOnly": true, "conflictPreserved": true, "selected": rows,
			})
			if err != nil {
				t.Fatal(err)
			}
			input := filepath.Join(work, "mmi.json")
			if err := os.WriteFile(input, raw, 0600); err != nil {
				t.Fatal(err)
			}
			resolved := filepath.Join(work, "resolved.json")
			previous := []byte("previous output must not be overwritten\n")
			if err := os.WriteFile(resolved, previous, 0600); err != nil {
				t.Fatal(err)
			}
			receipt := filepath.Join(work, "scn.json")
			cmd := exec.Command("go", "run", ".", "-fixture", "testdata/scn001.json", "-mmi-receipt", input, "-out-fixture", resolved, "-out", receipt)
			cmd.Dir = filepath.Join("..", "reference-scn001")
			output, err := cmd.CombinedOutput()
			if err == nil {
				t.Fatalf("invalid MMI selection accepted: %s", output)
			}
			after, readErr := os.ReadFile(resolved)
			if readErr != nil || string(after) != string(previous) {
				t.Fatalf("rejected input overwrote resolved fixture: %q %v", after, readErr)
			}
			if _, err := os.Stat(receipt); !os.IsNotExist(err) {
				t.Fatalf("rejected input created a receipt: %v", err)
			}
		})
	}
}
