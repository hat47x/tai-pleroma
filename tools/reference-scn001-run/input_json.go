package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"strings"
	"unicode"
	"unicode/utf8"
)

// Check the original bytes before projecting component outputs into partial
// structs. Unknown fields remain unexamined, but cannot hide ambiguous names.
func decodeEvidenceJSON(raw []byte, target any) error {
	if !utf8.Valid(raw) {
		return fmt.Errorf("evidence JSON is not valid UTF-8")
	}
	scanner := json.NewDecoder(bytes.NewReader(raw))
	scanner.UseNumber()
	if err := scanEvidenceJSON(scanner); err != nil {
		return err
	}
	if _, err := scanner.Token(); err != io.EOF {
		return fmt.Errorf("trailing JSON")
	}
	return json.Unmarshal(raw, target)
}

func scanEvidenceJSON(decoder *json.Decoder) error {
	token, err := decoder.Token()
	if err != nil {
		return err
	}
	delim, ok := token.(json.Delim)
	if !ok {
		return nil
	}
	switch delim {
	case '{':
		seen := map[string]bool{}
		for decoder.More() {
			token, err := decoder.Token()
			if err != nil {
				return err
			}
			key, ok := token.(string)
			if !ok {
				return fmt.Errorf("expected JSON object key")
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
				return fmt.Errorf("duplicate JSON object key %q", key)
			}
			seen[name] = true
			if err := scanEvidenceJSON(decoder); err != nil {
				return err
			}
		}
		end, err := decoder.Token()
		if err != nil {
			return err
		}
		if end != json.Delim('}') {
			return fmt.Errorf("expected JSON object end")
		}
	case '[':
		for decoder.More() {
			if err := scanEvidenceJSON(decoder); err != nil {
				return err
			}
		}
		end, err := decoder.Token()
		if err != nil {
			return err
		}
		if end != json.Delim(']') {
			return fmt.Errorf("expected JSON array end")
		}
	default:
		return fmt.Errorf("unexpected JSON delimiter")
	}
	return nil
}
