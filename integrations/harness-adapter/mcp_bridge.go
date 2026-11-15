package harnessadapter

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
)

// MCPServerSpec is one MCP server a harness should connect to. It is data the
// caller supplies; the adapter never invents one, never starts one, and never
// speaks MCP itself.
//
// The adapter deliberately owns no MCP client. Every vendor already ships one
// (DSH's `@deepseek-ai/dsh-mcp-client`, Claude Code's `--mcp-config`), and
// building a second client in this package would be exactly the parallel
// machinery the contract forbids. What this file adds is the *projection*: one
// neutral spec rendered into each vendor's own configuration shape, with the
// digest of what was rendered recorded as evidence.
//
// Secrets never enter the spec. Env is a list of variable *names*: DSH renders
// `!!js process.env.NAME` so the value stays in the launching environment, and
// Claude Code's JSON needs literal values, so a server that needs one is
// reported as unsupported for that harness instead of writing the value to disk.
type MCPServerSpec struct {
	// ServerName is the local namespace for this server's tools. It is NOT the
	// remote serverInfo.name: DSH's own contract says the remote name is
	// untrusted, not unique across deployments, and may change on upgrade.
	ServerName string `json:"serverName"`
	// Transport is "stdio" or "streamable-http".
	Transport string `json:"transport"`
	// Command is the executable for a stdio server.
	Command string `json:"command,omitempty"`
	// Args are the stdio server's arguments.
	Args []string `json:"args,omitempty"`
	// CWD is the stdio server's working directory.
	CWD string `json:"cwd,omitempty"`
	// EnvVarNames are the environment variable NAMES the server needs. Values
	// are resolved by the harness at launch time and never written by us.
	EnvVarNames []string `json:"envVarNames,omitempty"`
	// URL is the endpoint for a streamable-http server.
	URL string `json:"url,omitempty"`
	// ToolCallTimeoutMS bounds one tools/call. Zero means the harness default.
	ToolCallTimeoutMS int `json:"toolCallTimeoutMs,omitempty"`
	// FailOnStartupError makes the harness refuse to start when the connection
	// or the initial tool sync fails, instead of starting with no tools.
	FailOnStartupError bool `json:"failOnStartupError,omitempty"`
}

// Validate reports a spec the renderer cannot express. It refuses to guess: a
// stdio server without a command, or an http server without a URL, is a caller
// mistake and is reported rather than papered over with a default.
func (s MCPServerSpec) Validate() error {
	if s.ServerName == "" {
		return fmt.Errorf("mcp server: serverName is required")
	}
	if !serverNamePattern.MatchString(s.ServerName) {
		return fmt.Errorf("mcp server %q: serverName must match %s", s.ServerName, serverNamePattern.String())
	}
	switch s.Transport {
	case "stdio":
		if s.Command == "" {
			return fmt.Errorf("mcp server %q: stdio transport requires command", s.ServerName)
		}
	case "streamable-http":
		if s.URL == "" {
			return fmt.Errorf("mcp server %q: streamable-http transport requires url", s.ServerName)
		}
		if s.Command != "" || len(s.Args) > 0 {
			return fmt.Errorf("mcp server %q: streamable-http transport cannot carry command/args", s.ServerName)
		}
	default:
		return fmt.Errorf("mcp server %q: transport must be stdio or streamable-http, got %q", s.ServerName, s.Transport)
	}
	for _, name := range s.EnvVarNames {
		if name == "" || strings.Contains(name, "=") {
			return fmt.Errorf("mcp server %q: env entries are variable names, not assignments: %q", s.ServerName, name)
		}
	}
	return nil
}

// serverNamePattern mirrors DSH's documented namespace constraint so a spec
// that DSH would reject is rejected here first.
var serverNamePattern = regexp.MustCompile(`^[A-Za-z0-9_-]{1,32}$`)

// ValidateMCPServers checks every spec and rejects a duplicate ServerName,
// because two servers sharing a namespace cannot coexist and the later one
// would silently lose its tools.
func ValidateMCPServers(specs []MCPServerSpec) error {
	seen := map[string]bool{}
	for _, s := range specs {
		if err := s.Validate(); err != nil {
			return err
		}
		if seen[s.ServerName] {
			return fmt.Errorf("mcp server %q: duplicate serverName", s.ServerName)
		}
		seen[s.ServerName] = true
	}
	return nil
}

// ---------------------------------------------------------------------------
// Tool naming. Both vendors publish MCP tools under the same shape.
// ---------------------------------------------------------------------------

// MCPToolPrefix is the vendor-neutral prefix both DSH and Claude Code use.
const MCPToolPrefix = "mcp__"

// MCPToolName renders the model-facing name for one MCP tool.
//
// The shape is a *pinned contract* on the vendor side: session history and
// permission rules key on it. The adapter never parses a public name to recover
// the raw name over the wire — it only decodes for evidence and comparison.
func MCPToolName(serverName, rawName string) string {
	return MCPToolPrefix + serverName + "__" + rawName
}

// DecodeMCPToolName splits `mcp__<server>__<raw>` into its parts. The raw name
// may itself contain `__`, so the split is at the FIRST separator after the
// server segment, never at the last.
func DecodeMCPToolName(name string) (serverName, rawName string, ok bool) {
	if !strings.HasPrefix(name, MCPToolPrefix) {
		return "", "", false
	}
	rest := strings.TrimPrefix(name, MCPToolPrefix)
	idx := strings.Index(rest, "__")
	if idx <= 0 || idx+2 >= len(rest) {
		return "", "", false
	}
	return rest[:idx], rest[idx+2:], true
}

// IsMCPToolName reports whether a model-facing tool name is an MCP tool.
func IsMCPToolName(name string) bool {
	_, _, ok := DecodeMCPToolName(name)
	return ok
}

// ---------------------------------------------------------------------------
// Rendering: DSH patch overlay.
// ---------------------------------------------------------------------------

// WriteDSHPatch renders the caller's MCP servers as a DSH patch-list overlay and
// writes it to dir. It returns the path and the digest of the exact bytes
// written, so the evidence can name what was handed to the harness.
//
// New DSH entries cannot be targeted by id: `--patch` reports
// `entry "<id>" not found` for a row the composed index does not know. Adding
// one therefore takes an `insert` patch, which is the launcher's documented
// mechanism (`$defs.patch` in `--dump-config-schema`).
func WriteDSHPatch(dir string, specs []MCPServerSpec) (path, digest string, err error) {
	if len(specs) == 0 {
		return "", "", nil
	}
	if err := ValidateMCPServers(specs); err != nil {
		return "", "", err
	}
	var b strings.Builder
	b.WriteString("# Generated by the harness-adapter. Do not edit by hand.\n")
	b.WriteString("#\n")
	b.WriteString("# One `insert` patch adds each MCP server row. Values are the caller's\n")
	b.WriteString("# MCPServerSpec rendered verbatim; env is rendered as a reference to the\n")
	b.WriteString("# launching environment, never as a literal value.\n")
	b.WriteString("- insert:\n")
	for _, s := range specs {
		fmt.Fprintf(&b, "    - id: %s\n", dshEntryID(s.ServerName))
		fmt.Fprintf(&b, "      name: '%s'\n", dshMCPClientPlugin)
		b.WriteString("      config:\n")
		fmt.Fprintf(&b, "        serverName: %s\n", s.ServerName)
		fmt.Fprintf(&b, "        transport: %s\n", s.Transport)
		if s.Transport == "stdio" {
			fmt.Fprintf(&b, "        command: %s\n", yamlSingleQuoted(s.Command))
			if len(s.Args) > 0 {
				b.WriteString("        args:\n")
				for _, a := range s.Args {
					fmt.Fprintf(&b, "          - %s\n", yamlSingleQuoted(a))
				}
			}
			if s.CWD != "" {
				fmt.Fprintf(&b, "        cwd: %s\n", yamlSingleQuoted(s.CWD))
			}
			if len(s.EnvVarNames) > 0 {
				b.WriteString("        env:\n")
				for _, n := range sortedCopy(s.EnvVarNames) {
					fmt.Fprintf(&b, "          %s: !!js process.env.%s\n", n, n)
				}
			}
		} else {
			fmt.Fprintf(&b, "        url: %s\n", yamlSingleQuoted(s.URL))
		}
		if s.ToolCallTimeoutMS > 0 {
			fmt.Fprintf(&b, "        toolCallTimeoutMs: %d\n", s.ToolCallTimeoutMS)
		}
		if s.FailOnStartupError {
			b.WriteString("        failOnStartupError: true\n")
		}
	}
	return writeEvidenceFile(dir, "mcp-dsh-patch.yml", []byte(b.String()))
}

// dshMCPClientPlugin is the shipped MCP client plugin every DSH profile carries
// but leaves unused by default.
const dshMCPClientPlugin = "@deepseek-ai/dsh-mcp-client"

// dshEntryID derives a stable DSH row id from the server namespace.
func dshEntryID(serverName string) string { return "mcp-" + serverName }

// ---------------------------------------------------------------------------
// Rendering: Claude Code MCP config.
// ---------------------------------------------------------------------------

// WriteClaudeMCPConfig renders the caller's MCP servers as a Claude Code
// `--mcp-config` JSON file and writes it to dir.
//
// Claude Code's config carries literal `env` values. A spec that names
// environment variables is therefore refused here rather than written with the
// value read from the adapter's own environment: the adapter must not handle
// secrets, and a config file is the wrong place to resolve them.
func WriteClaudeMCPConfig(dir string, specs []MCPServerSpec) (path, digest string, err error) {
	if len(specs) == 0 {
		return "", "", nil
	}
	if err := ValidateMCPServers(specs); err != nil {
		return "", "", err
	}
	type claudeServer struct {
		Type    string   `json:"type"`
		Command string   `json:"command,omitempty"`
		Args    []string `json:"args,omitempty"`
		Env     struct{} `json:"env,omitempty"`
		URL     string   `json:"url,omitempty"`
	}
	servers := map[string]claudeServer{}
	for _, s := range specs {
		if len(s.EnvVarNames) > 0 {
			return "", "", fmt.Errorf(
				"mcp server %q: Claude Code --mcp-config needs literal env values, so this adapter will not render it; supply a caller-built config file instead",
				s.ServerName)
		}
		c := claudeServer{Command: s.Command, Args: s.Args, URL: s.URL}
		if s.Transport == "stdio" {
			c.Type = "stdio"
		} else {
			c.Type = "http"
		}
		servers[s.ServerName] = c
	}
	doc := struct {
		MCPServers map[string]claudeServer `json:"mcpServers"`
	}{MCPServers: servers}
	data, err := json.MarshalIndent(doc, "", "  ")
	if err != nil {
		return "", "", err
	}
	data = append(data, '\n')
	return writeEvidenceFile(dir, "mcp-claude-config.json", data)
}

// ---------------------------------------------------------------------------
// Helpers.
// ---------------------------------------------------------------------------

// yamlSingleQuoted renders one YAML scalar. Single quotes are used because a
// Windows path's backslashes are escape characters inside double quotes; only
// an internal single quote needs doubling.
func yamlSingleQuoted(s string) string {
	return "'" + strings.ReplaceAll(s, "'", "''") + "'"
}

// writeEvidenceFile writes data to dir/name and returns the path and digest of
// the bytes written.
func writeEvidenceFile(dir, name string, data []byte) (path, digest string, err error) {
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return "", "", fmt.Errorf("mkdir %s: %w", dir, err)
	}
	path = filepath.Join(dir, name)
	if err := os.WriteFile(path, data, 0o644); err != nil {
		return "", "", fmt.Errorf("write %s: %w", path, err)
	}
	return path, DigestBytes(data), nil
}

// sortedCopy returns a sorted copy so rendering is deterministic.
func sortedCopy(in []string) []string {
	out := append([]string(nil), in...)
	sort.Strings(out)
	return out
}

// mcpServerNames renders the server namespaces for evidence, sorted.
func mcpServerNames(specs []MCPServerSpec) string {
	names := make([]string, 0, len(specs))
	for _, s := range specs {
		names = append(names, s.ServerName)
	}
	sort.Strings(names)
	return strings.Join(names, ",")
}

// MCPServersFromOffers derives server specs from the task's ToolOffers, when a
// caller represents its tools as an MCP server. It exists so a pilot can build
// one spec set from the same pinned product surface the task already names.
func MCPServersFromOffers(serverName, command string, args []string, timeoutMS int, failOnStartupError bool) MCPServerSpec {
	return MCPServerSpec{
		ServerName:         serverName,
		Transport:          "stdio",
		Command:            command,
		Args:               args,
		ToolCallTimeoutMS:  timeoutMS,
		FailOnStartupError: failOnStartupError,
	}
}
