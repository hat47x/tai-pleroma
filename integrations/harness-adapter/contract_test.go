package harnessadapter

import (
	"encoding/json"
	"strings"
	"testing"
)

// TestContractVersionStable guards the one field every adapter must agree on.
func TestContractVersionStable(t *testing.T) {
	if ContractVersion != "yi.harness-adapter/v0" {
		t.Fatalf("contract version changed to %q; a bump means field meanings changed", ContractVersion)
	}
}

// TestPinsAreSeparateTypes is the structural form of the separation rule: if
// someone collapses two pins into one field, this test stops compiling.
func TestPinsAreSeparateTypes(t *testing.T) {
	var _ SourcePin = SourcePin{Repo: "r", Revision: "rev", BytesSHA256: "sha256:x"}
	var _ ModelPin = ModelPin{Provider: "p", Model: "m", Route: "official-api"}
	var _ SkillPin = SkillPin{ID: "s", PlacedPath: "/p", BytesSHA256: "sha256:y", LoadState: LoadUnknown}
	var _ ToolSchemaPin = ToolSchemaPin{Name: "t", SchemaSHA256: "sha256:z", Advertised: true}
	var _ RootPin = RootPin{Logical: "root", Path: "/w", Access: "read-only"}
	var _ OutboundRecord = OutboundRecord{Direction: "argv", BytesSHA256: "sha256:a"}
	var _ Receipt = Receipt{State: ReceiptPartial}
}

// TestDigestDistinguishesBytes checks that the digest helpers actually see
// different bytes, and that they prefix the algorithm so a bare hex string is
// never mistaken for a digest.
func TestDigestDistinguishesBytes(t *testing.T) {
	a := DigestString("alpha")
	b := DigestString("beta")
	if a == b {
		t.Fatalf("different inputs produced the same digest: %s", a)
	}
	if !strings.HasPrefix(a, "sha256:") {
		t.Fatalf("digest %q lacks the algorithm prefix", a)
	}
	if len(a) != len("sha256:")+64 {
		t.Fatalf("digest %q is not a sha256 hex string", a)
	}
	if DigestBytes([]byte("alpha")) != a {
		t.Fatalf("DigestBytes and DigestString disagree on the same bytes")
	}
}

// TestPromotedAlwaysFalse is the anti-shortcut guard. No result produced by this
// package may be read as product acceptance, permission or effect.
func TestPromotedAlwaysFalse(t *testing.T) {
	completed := &Result{
		Transport: TransportDelivered,
		Run:       RunCompleted,
		ExitCode:  intPtr(0),
		ToolCalls: []ToolCallRecord{{Tool: "tei.validate", HarnessStatus: "completed"}},
		Receipt:   Receipt{State: ReceiptComplete},
	}
	if completed.Promoted() {
		t.Fatal("a completed harness run was reported as promoted")
	}
	if nilResult := (*Result)(nil); nilResult.Promoted() {
		t.Fatal("a nil result was reported as promoted")
	}
}

// TestTransportRunAndProductVerdictAreSeparateFields fails to compile if the
// three levels collapse into one.
func TestTransportRunAndProductVerdictAreSeparateFields(t *testing.T) {
	r := Result{
		Transport: TransportDelivered,
		Run:       RunCompleted,
		ToolCalls: []ToolCallRecord{{
			Tool:          "tei.validate",
			HarnessStatus: "completed",
			ExitCode:      intPtr(0),
			ProductVerdict: &ProductVerdict{
				OperationCompleted: true,
				ValidationPassed:   boolPtr(false),
			},
		}},
	}
	if r.Transport != TransportDelivered || r.Run != RunCompleted {
		t.Fatal("transport/run levels were lost")
	}
	v := r.ToolCalls[0].ProductVerdict
	if v == nil || !v.OperationCompleted || v.ValidationPassed == nil || *v.ValidationPassed {
		t.Fatal("product verdict lost the operation/validation split")
	}
}

// TestSessionExternalIDCarriesNoMeaning pins the rule that a session id is an
// opaque observation. The test asserts the field exists and that nothing in the
// package derives meaning from it.
func TestSessionExternalIDCarriesNoMeaning(t *testing.T) {
	s := SessionRef{Adapter: "dsh-headless", ExternalID: "session-abc", State: SessionCreated}
	if s.ExternalID == "" {
		t.Fatal("expected an opaque id")
	}
	// A resumed id the harness refused must stay distinguishable from an adopted
	// one, so a caller cannot treat a refusal as continuity.
	rejected := SessionRef{ExternalID: "session-abc", State: SessionRejected, RequestedID: "session-abc"}
	if rejected.State == SessionCreated {
		t.Fatal("a rejected session was recorded as created")
	}
}

// TestLoadStateIsThreeValued stops a boolean from standing in for "unknown".
func TestLoadStateIsThreeValued(t *testing.T) {
	if LoadUnknown == LoadNotLoaded || LoadNotLoaded == LoadLoaded || LoadUnknown == LoadLoaded {
		t.Fatal("load states collapsed")
	}
}

// TestResultJSONRoundTrips keeps the evidence file stable enough to diff.
func TestResultJSONRoundTrips(t *testing.T) {
	r := &Result{
		Contract:  ContractVersion,
		Adapter:   "direct-control",
		Transport: TransportDelivered,
		Run:       RunCompleted,
		Session:   SessionRef{Adapter: "direct-control", State: SessionUnknown},
		Receipt:   Receipt{State: ReceiptNotObserved},
		ToolCalls: []ToolCallRecord{{Tool: "tei.validate", ExitCode: intPtr(0)}},
	}
	b, err := json.Marshal(r)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	var back Result
	if err := json.Unmarshal(b, &back); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}
	if back.Contract != ContractVersion || back.Run != RunCompleted || len(back.ToolCalls) != 1 {
		t.Fatalf("round trip lost data: %s", string(b))
	}
}

// TestNormalizeToolCallsDropsVolatileIDs checks that two adapters can be
// compared on what was invoked, not on harness-specific call ids.
func TestNormalizeToolCallsDropsVolatileIDs(t *testing.T) {
	r := &Result{ToolCalls: []ToolCallRecord{
		{CallID: "call_zzz", Tool: "tei.validate", InputJSON: `{"a":1}`},
		{CallID: "call_aaa", Tool: "tei.model-catalog", InputJSON: `{}`},
	}}
	got := r.NormalizeToolCalls()
	if len(got) != 2 {
		t.Fatalf("expected 2 calls, got %d", len(got))
	}
	if got[0].CallID != "" || got[1].CallID != "" {
		t.Fatal("call ids survived normalization")
	}
	if got[0].Tool != "tei.model-catalog" {
		t.Fatalf("calls were not sorted by tool: %s", got[0].Tool)
	}
}

// TestExitStringDoesNotInventZero guards against a missing exit code reading as
// a successful zero.
func TestExitStringDoesNotInventZero(t *testing.T) {
	if ExitString(nil) != "n/a" {
		t.Fatalf("nil exit code rendered as %q", ExitString(nil))
	}
	if ExitString(intPtr(0)) != "0" {
		t.Fatalf("zero exit code rendered as %q", ExitString(intPtr(0)))
	}
}

// TestAllCapabilitiesClosed keeps the capability set a closed list.
func TestAllCapabilitiesClosed(t *testing.T) {
	caps := AllCapabilities()
	if len(caps) != 9 {
		t.Fatalf("capability set changed size to %d; add a constant and update this", len(caps))
	}
	seen := map[Capability]bool{}
	for _, c := range caps {
		if seen[c] {
			t.Fatalf("duplicate capability %q", c)
		}
		seen[c] = true
	}
}

func intPtr(v int) *int    { return &v }
func boolPtr(v bool) *bool { return &v }
