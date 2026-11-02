package main

import (
	"encoding/json"
	"fmt"
	"slices"
	"sort"
	"strings"
)

// ValidateJSON is what `tei validate -workspace W -json` reported. TEI's JSON
// carries schemaVersion, ok, diagnostics and error only: no type names and no
// version of TEI itself, so it can show that TEI agrees with its own text output
// but not that the declared types were loaded (see ModelBinding).
type ValidateJSON struct {
	Status        string `json:"status"` // not-run | consistent | inconsistent | unavailable
	ExitCode      int    `json:"exitCode"`
	SchemaVersion string `json:"schemaVersion,omitempty"`
	OK            bool   `json:"ok"`
	Diagnostics   struct {
		Total    int `json:"total"`
		Errors   int `json:"errors"`
		Warnings int `json:"warnings"`
	} `json:"diagnostics"`
	ErrorCode string `json:"errorCode,omitempty"`
}

type validateReport struct {
	SchemaVersion string `json:"schemaVersion"`
	OK            *bool  `json:"ok"`
	Diagnostics   *[]struct {
		Diagnostic struct {
			Severity string `json:"severity"`
		} `json:"diagnostic"`
	} `json:"diagnostics"`
	Error *struct {
		Code string `json:"code"`
	} `json:"error"`
}

// parseValidateJSON judges the -json output against the exit code and the text
// output that already said "ok". It never stores TEI's messages (they can carry
// local paths); only counts and the error code are kept.
func parseValidateJSON(stdout string, exitCode int, textOK bool) ValidateJSON {
	result := ValidateJSON{Status: "unavailable", ExitCode: exitCode}
	var report validateReport
	if err := json.Unmarshal([]byte(stdout), &report); err != nil || report.OK == nil || report.Diagnostics == nil {
		return result
	}
	result.SchemaVersion = report.SchemaVersion
	result.OK = *report.OK
	for _, item := range *report.Diagnostics {
		result.Diagnostics.Total++
		switch item.Diagnostic.Severity {
		case "error":
			result.Diagnostics.Errors++
		case "warning":
			result.Diagnostics.Warnings++
		}
	}
	if report.Error != nil {
		result.ErrorCode = report.Error.Code
	}
	if report.SchemaVersion != "tei.cli.validate/v0" {
		return result // another contract version: record it, do not interpret it
	}
	if textOK && (!result.OK || exitCode != 0 || result.ErrorCode != "" || result.Diagnostics.Errors > 0) {
		result.Status = "inconsistent"
		return result
	}
	result.Status = "consistent"
	return result
}

// declaredData is what TAI declares in testdata/workspace/semantic/guidance.tei.
// A test keeps this table equal to that file.
type declaredData struct {
	Symbol     string
	Attributes map[string]string // attribute symbol -> type reference
}

const declaredNamespace = "scn001"

var declaredModel = []declaredData{
	{Symbol: "Observation", Attributes: map[string]string{
		"id": "std.code", "text": "std.text", "source": "std.text", "sourceVersion": "std.code", "availability": "std.code",
	}},
	{Symbol: "RuleCandidate", Attributes: map[string]string{
		"id": "std.code", "statement": "std.text", "status": "std.code", "provisional": "std.boolean",
	}},
}

// ModelBinding ties the types TAI declared to what TEI reported having loaded
// (`tei model catalog`, a read-only command in TEI's own `commands` list).
type ModelBinding struct {
	Status                 string   `json:"status"` // not-run | bound | mismatch | unavailable
	ExitCode               int      `json:"exitCode"`
	SchemaVersion          string   `json:"schemaVersion,omitempty"`
	Effect                 string   `json:"effect,omitempty"`
	WorldFingerprint       string   `json:"worldFingerprint,omitempty"`
	SourceIndexFingerprint string   `json:"sourceIndexFingerprint,omitempty"`
	ModelRevision          string   `json:"modelRevision,omitempty"`
	Declared               []string `json:"declared"`
	Differences            []string `json:"differences"`
}

type catalogSubject struct {
	Kind string `json:"kind"`
	ID   string `json:"id"`
}

type catalogResponse struct {
	SchemaVersion string `json:"schemaVersion"`
	OK            bool   `json:"ok"`
	Result        *struct {
		SchemaVersion          string `json:"schemaVersion"`
		Effect                 string `json:"effect"`
		WorldFingerprint       string `json:"worldFingerprint"`
		SourceIndexFingerprint string `json:"sourceIndexFingerprint"`
		ModelRevision          string `json:"modelRevision"`
		Entries                []struct {
			Subject   catalogSubject  `json:"subject"`
			Parent    *catalogSubject `json:"parent"`
			Symbol    string          `json:"symbol"`
			Detail    string          `json:"detail"`
			Ambiguous bool            `json:"ambiguous"`
		} `json:"entries"`
	} `json:"result"`
}

func declaredNames() []string {
	names := []string{}
	for _, data := range declaredModel {
		names = append(names, data.Symbol)
	}
	return names
}

// bindModel compares the catalog with declaredModel. "unavailable" means TEI gave
// no comparable value (unknown command at an older commit, another schema
// version, unparsable output); "mismatch" means it answered and the answer differs.
func bindModel(stdout string, exitCode int) ModelBinding {
	binding := ModelBinding{Status: "unavailable", ExitCode: exitCode, Declared: declaredNames(), Differences: []string{}}
	var response catalogResponse
	if err := json.Unmarshal([]byte(stdout), &response); err != nil || response.Result == nil {
		return binding
	}
	binding.SchemaVersion = response.Result.SchemaVersion
	binding.Effect = response.Result.Effect
	if exitCode != 0 || !response.OK || response.SchemaVersion != "tei.cli.model/v0" || response.Result.SchemaVersion != "tei.operations.model-catalog/v0" {
		return binding
	}
	binding.WorldFingerprint = response.Result.WorldFingerprint
	binding.SourceIndexFingerprint = response.Result.SourceIndexFingerprint
	binding.ModelRevision = response.Result.ModelRevision
	if response.Result.Effect != "read-only" {
		binding.Differences = append(binding.Differences, "effect is not read-only")
	}
	for _, want := range declaredModel {
		var dataIDs []string
		for _, entry := range response.Result.Entries {
			if entry.Subject.Kind == "semantic-data" && entry.Symbol == want.Symbol && entry.Parent != nil && entry.Parent.ID == declaredNamespace {
				if entry.Ambiguous {
					binding.Differences = append(binding.Differences, want.Symbol+" is ambiguous")
				}
				dataIDs = append(dataIDs, entry.Subject.ID)
			}
		}
		if len(dataIDs) != 1 {
			binding.Differences = append(binding.Differences, fmt.Sprintf("%s: %d data entries in namespace %s, want 1", want.Symbol, len(dataIDs), declaredNamespace))
			continue
		}
		found := map[string]string{}
		for _, entry := range response.Result.Entries {
			if entry.Subject.Kind == "semantic-attribute" && entry.Parent != nil && entry.Parent.ID == dataIDs[0] {
				found[entry.Symbol] = entry.Detail
			}
		}
		for name, typeRef := range want.Attributes {
			switch got, ok := found[name]; {
			case !ok:
				binding.Differences = append(binding.Differences, fmt.Sprintf("%s.%s is missing", want.Symbol, name))
			case got != typeRef:
				binding.Differences = append(binding.Differences, fmt.Sprintf("%s.%s has type %s, declared %s", want.Symbol, name, got, typeRef))
			}
		}
		var extra []string
		for name := range found {
			if _, ok := want.Attributes[name]; !ok {
				extra = append(extra, name)
			}
		}
		sort.Strings(extra)
		for _, name := range extra {
			binding.Differences = append(binding.Differences, fmt.Sprintf("%s.%s is not declared by TAI", want.Symbol, name))
		}
	}
	slices.Sort(binding.Differences)
	if len(binding.Differences) == 0 {
		binding.Status = "bound"
	} else {
		binding.Status = "mismatch"
	}
	return binding
}

func joinReasons(reasons []string) string { return strings.Join(reasons, "; ") }
