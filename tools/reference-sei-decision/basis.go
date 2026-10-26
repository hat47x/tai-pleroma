package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"unicode"
)

type DecisionBasis struct {
	RecordID    string            `json:"recordId"`
	JSONPointer string            `json:"jsonPointer"`
	DecisionRef json.RawMessage   `json:"decisionRef"`
	BasisRefs   []json.RawMessage `json:"basisRefs"`
}

// BasisInspection is a local diagnostic, not an approval or a new SEI Contract.
type BasisInspection struct {
	SourceDigest           string          `json:"sourceDigest"`
	SeiCommit              string          `json:"seiCommit,omitempty"`
	BundleID               string          `json:"bundleId"`
	RecordCount            int             `json:"recordCount"`
	NotVerifiedRecordCount int             `json:"notVerifiedRecordCount"`
	Decisions              []DecisionBasis `json:"decisions"`
	RecordStructureChecked bool            `json:"recordStructureChecked"`
	ExactTargetsVerified   bool            `json:"exactTargetsVerified"`
	HumanReviewed          bool            `json:"humanReviewed"`
	AuthorityVerified      bool            `json:"authorityVerified"`
	PublicationApproved    bool            `json:"publicationApproved"`
}

func inspectBasis(ctx context.Context, seiRoot, path string) (BasisInspection, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return BasisInspection{}, err
	}
	result, err := basisFromSnapshot(raw)
	if err != nil {
		return BasisInspection{}, err
	}
	work, err := os.MkdirTemp("", "tai-sei-basis-")
	if err != nil {
		return BasisInspection{}, err
	}
	defer os.RemoveAll(work)
	snapshot := filepath.Join(work, "bundle.json")
	if err := os.WriteFile(snapshot, raw, 0600); err != nil {
		return BasisInspection{}, err
	}
	// Verify and extract the same snapshot, never re-read a changing input path.
	checked, err := run(ctx, filepath.Join(seiRoot, "runtime", "go"), "run", "./cmd/sei", "verify", "--input", snapshot)
	if err != nil {
		return BasisInspection{}, err
	}
	var summary struct {
		BundleID         string `json:"bundle_id"`
		RecordCount      int    `json:"record_count"`
		ValidatedCount   int    `json:"validated_count"`
		NotVerifiedCount int    `json:"not_verified_count"`
	}
	if err := json.Unmarshal(checked, &summary); err != nil {
		return BasisInspection{}, err
	}
	if summary.BundleID != result.BundleID || summary.RecordCount != result.RecordCount ||
		summary.ValidatedCount < 0 || summary.NotVerifiedCount < 0 || summary.ValidatedCount+summary.NotVerifiedCount != summary.RecordCount ||
		summary.ValidatedCount < len(result.Decisions) {
		return BasisInspection{}, fmt.Errorf("SEI verification summary differs from the snapshot")
	}
	result.NotVerifiedRecordCount = summary.NotVerifiedCount
	result.RecordStructureChecked = true
	result.SeiCommit = output(ctx, seiRoot, "git", "rev-parse", "HEAD")
	return result, nil
}

func basisFromSnapshot(raw []byte) (BasisInspection, error) {
	scanner := json.NewDecoder(bytes.NewReader(raw))
	scanner.UseNumber()
	if err := scanBasisJSON(scanner); err != nil {
		return BasisInspection{}, err
	}
	if _, err := scanner.Token(); err != io.EOF {
		return BasisInspection{}, fmt.Errorf("trailing JSON")
	}
	var bundle struct {
		Contract string `json:"contract"`
		BundleID string `json:"bundle_id"`
		Records  []struct {
			RecordID string `json:"record_id"`
			Contract struct {
				ID      string `json:"contract_id"`
				Version string `json:"version"`
			} `json:"contract"`
			Payload json.RawMessage `json:"payload"`
		} `json:"records"`
	}
	if err := json.Unmarshal(raw, &bundle); err != nil {
		return BasisInspection{}, err
	}
	if bundle.Contract != "sei.semantic-interchange/v1alpha1" || bundle.BundleID == "" {
		return BasisInspection{}, fmt.Errorf("unsupported interchange")
	}
	result := BasisInspection{SourceDigest: fmt.Sprintf("sha256:%x", sha256.Sum256(raw)), BundleID: bundle.BundleID, RecordCount: len(bundle.Records), Decisions: []DecisionBasis{}}
	seen := map[string]bool{}
	for i, record := range bundle.Records {
		if record.RecordID == "" || seen[record.RecordID] {
			return BasisInspection{}, fmt.Errorf("missing or duplicate record ID")
		}
		seen[record.RecordID] = true
		if record.Contract.ID != "sei.decision-memory" || record.Contract.Version != "v1alpha1" {
			continue
		}
		var doc struct {
			RecordType string `json:"record_type"`
			Decision   *struct {
				Ref   json.RawMessage   `json:"ref"`
				Basis []json.RawMessage `json:"basis_refs"`
			} `json:"decision"`
		}
		if err := json.Unmarshal(record.Payload, &doc); err != nil {
			return BasisInspection{}, err
		}
		if doc.RecordType != "decision" {
			continue
		}
		if doc.Decision == nil {
			return BasisInspection{}, fmt.Errorf("decision payload is missing")
		}
		refs := doc.Decision.Basis
		if refs == nil {
			refs = []json.RawMessage{}
		}
		result.Decisions = append(result.Decisions, DecisionBasis{RecordID: record.RecordID, JSONPointer: fmt.Sprintf("/records/%d/payload/decision", i), DecisionRef: doc.Decision.Ref, BasisRefs: refs})
	}
	return result, nil
}

// Reject ambiguous names before encoding/json's case-insensitive last-wins
// behavior. This diagnostic accepts a stricter JSON subset than opaque SEI data.
func scanBasisJSON(decoder *json.Decoder) error {
	token, err := decoder.Token()
	if err != nil {
		return err
	}
	delimiter, ok := token.(json.Delim)
	if !ok {
		return nil
	}
	switch delimiter {
	case '{':
		seen := map[string]bool{}
		for decoder.More() {
			token, err := decoder.Token()
			if err != nil {
				return err
			}
			key, ok := token.(string)
			if !ok {
				return fmt.Errorf("invalid object key")
			}
			var folded strings.Builder
			for _, r := range key {
				minimum := r
				for next := unicode.SimpleFold(r); next != r; next = unicode.SimpleFold(next) {
					if next < minimum {
						minimum = next
					}
				}
				folded.WriteRune(minimum)
			}
			name := folded.String()
			if seen[name] {
				return fmt.Errorf("ambiguous JSON field %q", key)
			}
			seen[name] = true
			if err := scanBasisJSON(decoder); err != nil {
				return err
			}
		}
	case '[':
		for decoder.More() {
			if err := scanBasisJSON(decoder); err != nil {
				return err
			}
		}
	default:
		return fmt.Errorf("unexpected JSON delimiter")
	}
	_, err = decoder.Token()
	return err
}

func writeBasisInspection(path string, raw []byte) error {
	file, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0600)
	if err != nil {
		return err
	}
	if _, err := file.Write(raw); err != nil {
		_ = file.Close()
		return err
	}
	return file.Close()
}
