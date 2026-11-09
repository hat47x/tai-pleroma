package main

import (
	"fmt"
	"regexp"
)

// Options carries opt-in expectations. The zero value means "record only".
// Any non-empty field turns the run into a pinned run.
type Options struct {
	ExpectRevision       string // revision the SUI receipt's serverIdentity must declare (exact)
	ExpectDocumentDigest string // sha256:<64 hex> the SUI receipt's documentDigest must have
}

func (o Options) specified() bool { return o.ExpectRevision != "" || o.ExpectDocumentDigest != "" }

var (
	revisionPattern = regexp.MustCompile(`^[A-Za-z0-9._-]{1,64}$`)
	digestPattern   = regexp.MustCompile(`^sha256:[0-9a-f]{64}$`)
)

// validate rejects malformed expectations; "unknown" is the value SUI reports when
// SUI_APP_REVISION was never set, so it cannot stand for any revision.
func (o Options) validate() error {
	if o.ExpectRevision != "" && (!revisionPattern.MatchString(o.ExpectRevision) || o.ExpectRevision == "unknown") {
		return fmt.Errorf("invalid pin expectation: expected revision must be 1-64 characters of A-Za-z0-9._- and not unknown")
	}
	if o.ExpectDocumentDigest != "" && !digestPattern.MatchString(o.ExpectDocumentDigest) {
		return fmt.Errorf("invalid pin expectation: expected document digest must be sha256:<64 hex digits>")
	}
	return nil
}

// ServerIdentity is what the probe receipt declares about the answering server.
// Consistent is true only when a pinned probe read the same revision before and
// after its requests; a record-only probe leaves it null.
type ServerIdentity struct {
	Status     string `json:"status"`
	Revision   string `json:"revision"`
	Consistent *bool  `json:"consistent"`
}

// ProbePin is the probe's own pin outcome. A checked pin that did not match is rejected.
type ProbePin struct {
	Checked bool   `json:"checked"`
	Result  string `json:"result"`
}

type PinItem struct {
	Status   string `json:"status"` // not-checked | match | mismatch | unavailable
	Expected string `json:"expected,omitempty"`
	Actual   string `json:"actual,omitempty"`
}

type PinCheck struct {
	Checked        bool    `json:"checked"`
	Result         string  `json:"result"` // not-checked | match | mismatch | unavailable | invalid-expectation
	ServerRevision PinItem `json:"serverRevision"`
	DocumentDigest PinItem `json:"documentDigest"`
}

func pinItem(expected, actual string) PinItem {
	switch {
	case expected == "":
		return PinItem{Status: "not-checked", Actual: actual}
	case actual == "":
		return PinItem{Status: "unavailable", Expected: expected}
	case expected == actual:
		return PinItem{Status: "match", Expected: expected, Actual: actual}
	default:
		return PinItem{Status: "mismatch", Expected: expected, Actual: actual}
	}
}

// declaredRevision is the receipt's revision when it can be used for a pin: the probe
// reported it, it has the revision shape, it is not the unset marker and the probe
// read the same value again after its last request.
func declaredRevision(identity ServerIdentity) string {
	if identity.Status != "reported" || !revisionPattern.MatchString(identity.Revision) || identity.Revision == "unknown" {
		return ""
	}
	if identity.Consistent == nil || !*identity.Consistent {
		return ""
	}
	return identity.Revision
}

// evaluatePin returns the recorded pin and the reason it fails ("" when it holds or
// when nothing was expected). Reasons are fixed texts.
func evaluatePin(options Options, sui SUIReceipt) (PinCheck, string) {
	digest := sui.DocumentDigest
	if !digestPattern.MatchString(digest) {
		digest = ""
	}
	pin := PinCheck{
		Result:         "not-checked",
		ServerRevision: pinItem("", revisionIfShaped(sui.ServerIdentity.Revision)),
		DocumentDigest: pinItem("", digest),
	}
	if !options.specified() {
		return pin, ""
	}
	pin.Checked = true
	if err := options.validate(); err != nil {
		pin.Result = "invalid-expectation"
		return pin, err.Error()
	}
	pin.ServerRevision = pinItem(options.ExpectRevision, declaredRevision(sui.ServerIdentity))
	pin.DocumentDigest = pinItem(options.ExpectDocumentDigest, digest)
	if options.ExpectRevision != "" && pin.ServerRevision.Status != "match" {
		pin.ServerRevision.Actual = revisionIfShaped(sui.ServerIdentity.Revision)
	}
	pin.Result = "match"
	reason := ""
	for _, item := range []struct {
		name string
		item PinItem
	}{{"server revision", pin.ServerRevision}, {"document digest", pin.DocumentDigest}} {
		switch {
		case item.item.Status == "mismatch" && pin.Result != "mismatch":
			pin.Result = "mismatch"
			reason = fmt.Sprintf("pin mismatch: %s differs from the expectation", item.name)
		case item.item.Status == "unavailable" && pin.Result == "match":
			pin.Result = "unavailable"
			reason = fmt.Sprintf("pin unavailable: %s could not be determined from the SUI receipt", item.name)
		}
	}
	return pin, reason
}

// revisionIfShaped keeps receipt text out of the output unless it has the revision shape.
func revisionIfShaped(value string) string {
	if revisionPattern.MatchString(value) {
		return value
	}
	return ""
}
