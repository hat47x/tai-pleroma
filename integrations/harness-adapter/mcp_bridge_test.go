package harnessadapter

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// TestMCPToolNameRoundTrips pins the naming shape both vendors use. The shape is
// a vendor-side contract (session history and permission rules key on it), so
// the adapter treats it as fixed rather than as a naming policy of its own.
func TestMCPToolNameRoundTrips(t *testing.T) {
	cases := []struct{ server, raw, want string }{
		{"tei", "tei_model_catalog", "mcp__tei__tei_model_catalog"},
		{"tei", "tei_validate", "mcp__tei__tei_validate"},
		{"sui", "card_get", "mcp__sui__card_get"},
	}
	for _, tc := range cases {
		got := MCPToolName(tc.server, tc.raw)
		if got != tc.want {
			t.Fatalf("MCPToolName(%q,%q) = %q, want %q", tc.server, tc.raw, got, tc.want)
		}
		server, raw, ok := DecodeMCPToolName(got)
		if !ok || server != tc.server || raw != tc.raw {
			t.Fatalf("round trip lost data: %q -> (%q,%q,%v)", got, server, raw, ok)
		}
	}
}

// TestDecodeMCPToolNameSplitsAtFirstSeparator is the case a naive decoder gets
// wrong: an MCP raw tool name may itself contain `__`.
func TestDecodeMCPToolNameSplitsAtFirstSeparator(t *testing.T) {
	server, raw, ok := DecodeMCPToolName("mcp__tei__order__submit")
	if !ok {
		t.Fatal("valid name was rejected")
	}
	if server != "tei" {
		t.Fatalf("server = %q, want tei", server)
	}
	if raw != "order__submit" {
		t.Fatalf("raw = %q, want order__submit (split at the FIRST separator)", raw)
	}
}

// TestDecodeMCPToolNameRejectsMalformed keeps a non-MCP name from being read as
// an MCP tool with an empty namespace.
func TestDecodeMCPToolNameRejectsMalformed(t *testing.T) {
	for _, name := range []string{
		"pwsh", "Bash", "skill",
		"mcp____x",    // empty server segment
		"mcp__tei",    // no raw segment
		"mcp__tei__",  // no raw name
		"mcp_tei_x",   // wrong prefix separator
		"MCP__tei__x", // prefix is case-sensitive
	} {
		if _, _, ok := DecodeMCPToolName(name); ok {
			t.Fatalf("%q was accepted as an MCP tool name", name)
		}
	}
}

// TestMCPSpecValidation rejects specs the renderer cannot express instead of
// filling in a default.
func TestMCPSpecValidation(t *testing.T) {
	cases := []struct {
		name string
		spec MCPServerSpec
		ok   bool
	}{
		{"stdio ok", MCPServerSpec{ServerName: "tei", Transport: "stdio", Command: "tei-mcp"}, true},
		{"http ok", MCPServerSpec{ServerName: "tei", Transport: "streamable-http", URL: "http://x"}, true},
		{"no name", MCPServerSpec{Transport: "stdio", Command: "x"}, false},
		{"bad name", MCPServerSpec{ServerName: "tei server", Transport: "stdio", Command: "x"}, false},
		{"name too long", MCPServerSpec{ServerName: strings.Repeat("a", 33), Transport: "stdio", Command: "x"}, false},
		{"stdio without command", MCPServerSpec{ServerName: "tei", Transport: "stdio"}, false},
		{"http without url", MCPServerSpec{ServerName: "tei", Transport: "streamable-http"}, false},
		{"http with command", MCPServerSpec{ServerName: "tei", Transport: "streamable-http", URL: "u", Command: "x"}, false},
		{"unknown transport", MCPServerSpec{ServerName: "tei", Transport: "sse", Command: "x"}, false},
		{"env as assignment", MCPServerSpec{ServerName: "tei", Transport: "stdio", Command: "x", EnvVarNames: []string{"A=B"}}, false},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			err := tc.spec.Validate()
			if tc.ok && err != nil {
				t.Fatalf("valid spec rejected: %v", err)
			}
			if !tc.ok && err == nil {
				t.Fatal("invalid spec accepted")
			}
		})
	}
}

// TestDuplicateServerNameRejected stops two servers from colliding in one
// namespace, which would silently drop the later server's tools.
func TestDuplicateServerNameRejected(t *testing.T) {
	err := ValidateMCPServers([]MCPServerSpec{
		{ServerName: "tei", Transport: "stdio", Command: "a"},
		{ServerName: "tei", Transport: "stdio", Command: "b"},
	})
	if err == nil {
		t.Fatal("a duplicate serverName was accepted")
	}
	if !strings.Contains(err.Error(), "duplicate") {
		t.Fatalf("error does not name the conflict: %v", err)
	}
}

// TestWriteDSHPatchUsesInsertForm pins the vendor constraint found in the field:
// a new entry cannot be patched by id, so it takes an `insert` patch.
func TestWriteDSHPatchUsesInsertForm(t *testing.T) {
	dir := t.TempDir()
	path, digest, err := WriteDSHPatch(dir, []MCPServerSpec{{
		ServerName:         "tei",
		Transport:          "stdio",
		Command:            `C:\trial\bin\tei-mcp.exe`,
		Args:               []string{"-workspace", `C:\trial\workspace`},
		ToolCallTimeoutMS:  120000,
		FailOnStartupError: true,
	}})
	if err != nil {
		t.Fatalf("WriteDSHPatch: %v", err)
	}
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read: %v", err)
	}
	if digest != DigestBytes(data) {
		t.Fatalf("digest does not match the written bytes")
	}
	text := string(data)
	if !strings.Contains(text, "- insert:") {
		t.Fatalf("patch does not use the insert form:\n%s", text)
	}
	if strings.Contains(text, "- id: mcp-tei\n  name:") {
		t.Fatal("patch targets the row by id, which the loader rejects for a new entry")
	}
	if !strings.Contains(text, "serverName: tei") {
		t.Fatalf("serverName missing:\n%s", text)
	}
	if !strings.Contains(text, "failOnStartupError: true") {
		t.Fatalf("failOnStartupError missing:\n%s", text)
	}
}

// TestWriteDSHPatchQuotesWindowsPaths keeps a backslash from being read as a
// YAML escape.
func TestWriteDSHPatchQuotesWindowsPaths(t *testing.T) {
	dir := t.TempDir()
	path, _, err := WriteDSHPatch(dir, []MCPServerSpec{{
		ServerName: "tei", Transport: "stdio",
		Command: `C:\trial\bin\tei-mcp.exe`,
		CWD:     `C:\trial\workspace`,
	}})
	if err != nil {
		t.Fatalf("WriteDSHPatch: %v", err)
	}
	data, _ := os.ReadFile(path)
	text := string(data)
	// Single-quoted YAML keeps backslashes literal.
	if !strings.Contains(text, `command: 'C:\trial\bin\tei-mcp.exe'`) {
		t.Fatalf("command is not single-quoted:\n%s", text)
	}
	if !strings.Contains(text, `cwd: 'C:\trial\workspace'`) {
		t.Fatalf("cwd is not single-quoted:\n%s", text)
	}
}

// TestWriteDSHPatchRendersEnvAsReference is the anti-secret rule: the value must
// never be written, only the variable name resolved at launch time.
func TestWriteDSHPatchRendersEnvAsReference(t *testing.T) {
	dir := t.TempDir()
	path, _, err := WriteDSHPatch(dir, []MCPServerSpec{{
		ServerName: "tei", Transport: "stdio", Command: "x",
		EnvVarNames: []string{"TEI_TOKEN"},
	}})
	if err != nil {
		t.Fatalf("WriteDSHPatch: %v", err)
	}
	data, _ := os.ReadFile(path)
	text := string(data)
	if !strings.Contains(text, "TEI_TOKEN: !!js process.env.TEI_TOKEN") {
		t.Fatalf("env is not rendered as an environment reference:\n%s", text)
	}
	// The adapter's own environment value must not leak into the file.
	if v := os.Getenv("TEI_TOKEN"); v != "" && strings.Contains(text, v) {
		t.Fatal("the environment value was written into the patch")
	}
}

// TestWriteClaudeMCPConfigShape pins the JSON the harness reads.
func TestWriteClaudeMCPConfigShape(t *testing.T) {
	dir := t.TempDir()
	path, digest, err := WriteClaudeMCPConfig(dir, []MCPServerSpec{{
		ServerName: "tei", Transport: "stdio",
		Command: `C:\trial\bin\tei-mcp.exe`,
		Args:    []string{"-workspace", `C:\trial\workspace`},
	}})
	if err != nil {
		t.Fatalf("WriteClaudeMCPConfig: %v", err)
	}
	data, _ := os.ReadFile(path)
	if digest != DigestBytes(data) {
		t.Fatal("digest does not match the written bytes")
	}
	var doc struct {
		MCPServers map[string]struct {
			Type    string   `json:"type"`
			Command string   `json:"command"`
			Args    []string `json:"args"`
		} `json:"mcpServers"`
	}
	if err := json.Unmarshal(data, &doc); err != nil {
		t.Fatalf("config is not JSON: %v\n%s", err, data)
	}
	srv, ok := doc.MCPServers["tei"]
	if !ok {
		t.Fatalf("server missing from config:\n%s", data)
	}
	if srv.Type != "stdio" || srv.Command != `C:\trial\bin\tei-mcp.exe` {
		t.Fatalf("server rendered wrong: %+v", srv)
	}
	if len(srv.Args) != 2 {
		t.Fatalf("args lost: %+v", srv.Args)
	}
}

// TestWriteClaudeMCPConfigRefusesEnvNames is the honest-failure rule: Claude
// Code's config needs literal values, so the adapter refuses rather than
// reading a secret out of its own environment and writing it to disk.
func TestWriteClaudeMCPConfigRefusesEnvNames(t *testing.T) {
	dir := t.TempDir()
	_, _, err := WriteClaudeMCPConfig(dir, []MCPServerSpec{{
		ServerName: "tei", Transport: "stdio", Command: "x",
		EnvVarNames: []string{"TEI_TOKEN"},
	}})
	if err == nil {
		t.Fatal("a spec naming env vars was rendered for Claude Code")
	}
	if !strings.Contains(err.Error(), "literal env") {
		t.Fatalf("error does not explain the vendor constraint: %v", err)
	}
	// Nothing may have been written.
	if _, statErr := os.Stat(filepath.Join(dir, "mcp-claude-config.json")); statErr == nil {
		t.Fatal("a file was written despite the refusal")
	}
}

// TestEmptySpecsWriteNothing keeps an empty list from producing a file the
// harness would have to interpret.
func TestEmptySpecsWriteNothing(t *testing.T) {
	dir := t.TempDir()
	p, d, err := WriteDSHPatch(dir, nil)
	if err != nil || p != "" || d != "" {
		t.Fatalf("empty DSH specs produced %q/%q/%v", p, d, err)
	}
	p, d, err = WriteClaudeMCPConfig(dir, nil)
	if err != nil || p != "" || d != "" {
		t.Fatalf("empty Claude specs produced %q/%q/%v", p, d, err)
	}
}
