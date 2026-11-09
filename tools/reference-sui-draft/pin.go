package main

import (
	"fmt"
	"regexp"
)

// Options carries an opt-in expectation. The zero value means "record only".
type Options struct {
	ExpectDocumentDigest string // sha256:<64 hex> the SUI link receipt's documentDigest must have
}

var digestPattern = regexp.MustCompile(`^sha256:[0-9a-f]{64}$`)

func (o Options) validate() error {
	if o.ExpectDocumentDigest != "" && !digestPattern.MatchString(o.ExpectDocumentDigest) {
		return fmt.Errorf("invalid pin expectation: expected document digest must be sha256:<64 hex digits>")
	}
	return nil
}

type PinItem struct {
	Status   string `json:"status"` // not-checked | match | mismatch | unavailable
	Expected string `json:"expected,omitempty"`
	Actual   string `json:"actual,omitempty"`
}

type PinCheck struct {
	Checked        bool    `json:"checked"`
	Result         string  `json:"result"` // not-checked | match | mismatch | unavailable | invalid-expectation
	DocumentDigest PinItem `json:"documentDigest"`
}

// evaluatePin compares the documentDigest the SUI link receipt declares with the
// expectation. The reason is a fixed text, "" when the pin holds or was not asked for.
// The server revision is not handled here: the link step already checks it.
func evaluatePin(options Options, link SUILink) (PinCheck, string) {
	actual := link.DocumentDigest
	if !digestPattern.MatchString(actual) {
		actual = ""
	}
	pin := PinCheck{Result: "not-checked", DocumentDigest: PinItem{Status: "not-checked", Actual: actual}}
	if options.ExpectDocumentDigest == "" {
		return pin, ""
	}
	pin.Checked = true
	if err := options.validate(); err != nil {
		pin.Result = "invalid-expectation"
		return pin, err.Error()
	}
	item := PinItem{Status: "match", Expected: options.ExpectDocumentDigest, Actual: actual}
	reason := ""
	switch {
	case actual == "":
		item.Status = "unavailable"
		reason = "pin unavailable: document digest could not be determined from the SUI link receipt"
	case actual != options.ExpectDocumentDigest:
		item.Status = "mismatch"
		reason = "pin mismatch: document digest differs from the expectation"
	}
	pin.DocumentDigest, pin.Result = item, item.Status
	return pin, reason
}
