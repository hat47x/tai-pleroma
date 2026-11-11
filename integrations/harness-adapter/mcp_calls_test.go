package harnessadapter

import (
	"strings"
	"testing"
)

// TestMCPToolCallsSeparatesTypedFromShell is the distinction H-A-1 exists to
// create: reaching a product CLI by running it in the harness's shell is a
// different observation from calling a typed product tool. The synthetic run
// below contains both, and the two must not be lumped together.
func TestMCPToolCallsSeparatesTypedFromShell(t *testing.T) {
	r := &Result{ToolCalls: []ToolCallRecord{
		{Tool: "mcp__tei__tei_model_catalog", HarnessStatus: "completed", ResultText: `{"ok":true}`},
		{Tool: "mcp__tei__tei_validate", HarnessStatus: "completed", ResultText: `{"ok":true}`},
		{Tool: "pwsh", HarnessStatus: "completed", InputJSON: `{"command":"tei.exe model catalog"}`},
		{Tool: "skill", HarnessStatus: "completed", InputJSON: `{"name":"yi-tei-modeling"}`},
	}}
	mcp := r.MCPToolCalls()
	if len(mcp) != 2 {
		t.Fatalf("expected 2 typed MCP calls, got %d: %+v", len(mcp), mcp)
	}
	if mcp[0].ServerName != "tei" || mcp[0].RawName != "tei_model_catalog" {
		t.Fatalf("first MCP call decoded wrong: %+v", mcp[0])
	}
	if mcp[1].RawName != "tei_validate" {
		t.Fatalf("second MCP call decoded wrong: %+v", mcp[1])
	}
	shell := r.ShellBridgeCalls()
	if len(shell) != 1 || shell[0].Tool != "pwsh" {
		t.Fatalf("expected exactly the pwsh call as a shell bridge, got %+v", shell)
	}
	// A skill load is neither an MCP tool nor a shell bridge.
	for _, c := range shell {
		if c.Tool == "skill" {
			t.Fatal("a skill load was counted as a shell bridge")
		}
	}
}

// TestToolSchemaPinsRecordVia keeps the pin readable without re-parsing the
// model-facing name at comparison time.
func TestToolSchemaPinsRecordVia(t *testing.T) {
	r := &Result{ToolCalls: []ToolCallRecord{
		{Tool: "mcp__tei__tei_model_catalog"},
		{Tool: "mcp__tei__tei_model_catalog"},
		{Tool: "Bash"},
		{Tool: "skill"},
	}}
	pins := r.ToolSchemaPins()
	byName := map[string]ToolSchemaPin{}
	for _, p := range pins {
		byName[p.Name] = p
	}
	mcp := byName["mcp__tei__tei_model_catalog"]
	if mcp.Via != "mcp" {
		t.Fatalf("MCP tool via = %q", mcp.Via)
	}
	if mcp.ProductName != "tei_model_catalog" || mcp.ServerName != "tei" {
		t.Fatalf("MCP tool pin lost the decoded names: %+v", mcp)
	}
	if mcp.CallCount != 2 {
		t.Fatalf("call count = %d, want 2", mcp.CallCount)
	}
	if byName["Bash"].Via != "shell-bridge" {
		t.Fatalf("Bash via = %q", byName["Bash"].Via)
	}
	if byName["skill"].Via != "native" {
		t.Fatalf("skill via = %q", byName["skill"].Via)
	}
}

// TestMCPToolCallsIgnoresUndeclaredToolSuffix is the case a naive prefix match
// gets wrong: a native tool whose name merely starts with "mcp__" but is not a
// well-formed MCP name must not be reported as a typed MCP call.
func TestMCPToolCallsIgnoresUndeclaredToolSuffix(t *testing.T) {
	r := &Result{ToolCalls: []ToolCallRecord{
		{Tool: "mcp__tei"},
		{Tool: "mcp__tei__"},
	}}
	if got := r.MCPToolCalls(); len(got) != 0 {
		t.Fatalf("malformed names were accepted as MCP calls: %+v", got)
	}
}

// TestMCPPilotResultShape keeps the end-to-end shape: a run with typed MCP tools
// produces pins that name the server and the raw tool, so a reader can answer
// "which product tool ran".
func TestMCPPilotResultShape(t *testing.T) {
	rep := &PilotReport{Outcomes: []PilotOutcome{
		{Adapter: "dsh-headless", State: PilotObserved, Result: &Result{
			Transport: TransportDelivered, Run: RunCompleted,
			ToolCalls: []ToolCallRecord{
				{Tool: "mcp__tei__tei_model_catalog", HarnessStatus: "completed"},
			},
		}},
		{Adapter: "direct-control", State: PilotObserved, Result: &Result{
			Transport: TransportDelivered, Run: RunCompleted,
			ToolCalls: []ToolCallRecord{{Tool: "tei.model-catalog"}},
		}},
	}}
	// The two arms reached the same product capability by different routes, so
	// the tool-name axis legitimately diverges. The report must say so.
	div := Divergences(rep)
	found := false
	for _, d := range div {
		if d == "tool-names" {
			found = true
		}
	}
	if !found {
		t.Fatalf("typed-MCP vs direct-CLI divergence was not reported: %v", div)
	}
}

// TestProductNameIsNotEmptyForMCP stops a pin from carrying an empty raw name.
func TestProductNameIsNotEmptyForMCP(t *testing.T) {
	for _, c := range (&Result{ToolCalls: []ToolCallRecord{{Tool: "mcp__tei__x"}}}).ToolSchemaPins() {
		if c.Via == "mcp" && strings.TrimSpace(c.ProductName) == "" {
			t.Fatalf("MCP pin has an empty product name: %+v", c)
		}
	}
}
