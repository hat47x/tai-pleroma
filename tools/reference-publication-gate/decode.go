package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"strings"
)

// DecodeStatus rejects ambiguous JSON before the typed decoder can silently
// choose the last field. Field matching in encoding/json is case insensitive.
func DecodeStatus(raw []byte) (Status, error) {
	scanner := json.NewDecoder(bytes.NewReader(raw))
	if err := scanJSONValue(scanner); err != nil {
		return Status{}, err
	}
	if _, err := scanner.Token(); err != io.EOF {
		return Status{}, fmt.Errorf("unexpected trailing JSON")
	}
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.DisallowUnknownFields()
	var status Status
	if err := decoder.Decode(&status); err != nil {
		return Status{}, err
	}
	return status, nil
}

func scanJSONValue(decoder *json.Decoder) error {
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
				return fmt.Errorf("invalid JSON object key")
			}
			canonical := ""
			for _, name := range []string{"schema", "scenario", "items", "id", "status", "evidence", "evidenceKind"} {
				if strings.EqualFold(key, name) {
					canonical = name
					break
				}
			}
			if canonical == "" {
				return fmt.Errorf("unknown JSON field %q", key)
			}
			if seen[canonical] {
				return fmt.Errorf("duplicate JSON field %q", key)
			}
			seen[canonical] = true
			if err := scanJSONValue(decoder); err != nil {
				return err
			}
		}
	case '[':
		for decoder.More() {
			if err := scanJSONValue(decoder); err != nil {
				return err
			}
		}
	default:
		return fmt.Errorf("unexpected JSON delimiter")
	}
	_, err = decoder.Token()
	return err
}
