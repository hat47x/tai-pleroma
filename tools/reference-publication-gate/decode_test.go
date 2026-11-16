package main

import (
	"encoding/json"
	"strings"
	"testing"
)

func TestDecodeStatusRejectsShadowedFields(t *testing.T) {
	raw, err := json.Marshal(acceptedStatus())
	if err != nil {
		t.Fatal(err)
	}
	valid := string(raw)
	for name, bad := range map[string]string{
		"duplicate items":       `{"items":[],` + valid[1:],
		"case folded items":     `{"Items":[],` + valid[1:],
		"shadowed pending":      strings.Replace(valid, `"status":"accepted"`, `"status":"pending","status":"accepted"`, 1),
		"case folded status":    strings.Replace(valid, `"status":"accepted"`, `"status":"pending","Status":"accepted"`, 1),
		"escaped status":        strings.Replace(valid, `"status":"accepted"`, `"status":"pending","sta\u0074us":"accepted"`, 1),
		"unicode folded status": strings.Replace(valid, `"status":"accepted"`, `"status":"pending","ſtatus":"accepted"`, 1),
		"duplicate id":          strings.Replace(valid, `"id":"R-01"`, `"id":"R-01","id":"R-01"`, 1),
		"unknown field":         strings.Replace(valid, `"id":"R-01"`, `"id":"R-01","approval":true`, 1),
		"trailing object":       valid + `{}`,
	} {
		t.Run(name, func(t *testing.T) {
			if bad == valid {
				t.Fatal("mutation did not change JSON")
			}
			if _, err := DecodeStatus([]byte(bad)); err == nil {
				t.Fatal("ambiguous JSON accepted")
			}
		})
	}
	status, err := DecodeStatus(raw)
	if err != nil || !Evaluate(status).Allowed {
		t.Fatalf("unambiguous accepted input rejected: %+v %v", status, err)
	}
}
