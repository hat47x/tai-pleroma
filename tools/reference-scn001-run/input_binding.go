package main

import (
	"fmt"
	"os"
	"strings"
)

type mmiSelectedRows struct {
	Selected []struct {
		ID   string `json:"id"`
		Text string `json:"text"`
	} `json:"selected"`
}

// selectedDigests hashes the MMI rows exactly as returned, so a later overlay
// or render step cannot silently substitute other text for the same ID.
func selectedDigests(path string) (map[string]string, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var rows mmiSelectedRows
	if err := decodeEvidenceJSON(raw, &rows); err != nil {
		return nil, err
	}
	digests := map[string]string{}
	for _, row := range rows.Selected {
		if strings.TrimSpace(row.ID) == "" {
			return nil, fmt.Errorf("MMI selected row has no ID")
		}
		if _, duplicate := digests[row.ID]; duplicate {
			return nil, fmt.Errorf("MMI selected row is duplicated: %s", row.ID)
		}
		digests[row.ID] = artifactDigest([]byte(row.Text))
	}
	return digests, nil
}

func validDigestMap(digests map[string]string) bool {
	for id, value := range digests {
		if strings.TrimSpace(id) == "" || !strings.HasPrefix(value, "sha256:") || len(value) != len("sha256:")+64 {
			return false
		}
	}
	return true
}

func subsetWithSameDigests(subset, superset map[string]string) bool {
	for id, value := range subset {
		if superset[id] != value {
			return false
		}
	}
	return true
}

// checkInputBinding relates MMI selection, SCN-001 evaluation input, and the
// D-04 evidence rows inside one receipt. Records made before these fields
// existed stay verifiable but report the binding as unverified.
func checkInputBinding(receipt RunReceipt) (bool, string) {
	mmi := receipt.Components.MMI.SelectedDigests
	scn := receipt.Components.SCN001.ObservationDigests
	artifact := receipt.Components.ReviewArtifact.ObservationDigests
	if len(mmi) == 0 && len(scn) == 0 && len(artifact) == 0 {
		return false, ""
	}
	if !validDigestMap(mmi) || !validDigestMap(scn) || !validDigestMap(artifact) {
		return false, "input binding contains an empty ID or malformed digest"
	}
	if len(mmi) != 0 && len(scn) != 0 && !subsetWithSameDigests(mmi, scn) {
		return false, "SCN-001 evaluated text differs from the MMI selection"
	}
	if len(artifact) != 0 && len(scn) != 0 && !subsetWithSameDigests(artifact, scn) {
		return false, "D-04 evidence rows differ from the SCN-001 evaluated input"
	}
	if len(mmi) != 0 && len(artifact) != 0 {
		for id, value := range mmi {
			if rendered, ok := artifact[id]; ok && rendered != value {
				return false, "D-04 evidence rows differ from the MMI selection"
			}
		}
	}
	if len(mmi) == 0 || len(scn) == 0 || len(artifact) == 0 {
		if receipt.Passed {
			return false, "input binding is incomplete for a successful run"
		}
		return false, ""
	}
	if len(mmi) != receipt.Components.MMI.SelectedRows {
		return false, "MMI selected digests do not match the selected row count"
	}
	for id := range mmi {
		if _, ok := artifact[id]; !ok {
			return false, "D-04 evidence rows omit an MMI-selected observation"
		}
	}
	return true, ""
}
