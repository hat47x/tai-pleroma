package harnessadapter

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// SHOReadOnlyTool projects SHO's read-only Markdown inspect CLI into a ToolOffer.
//
// SHO differs from TEI and SEI in a way the shared contract must not absorb:
//
//   - The command is a Node script (`bin/sho-inspect.cjs inspect <local.md>`),
//     not a single compiled binary with flags.
//   - It reports identity as `source.sha256` plus `linkOccurrenceCount`, not a
//     world fingerprint.
//   - Its failure shape is `{"error":"not-found","message":...}` — a bare string
//     code with no `ok` field at all.
//
// The projection therefore pins ONE document at construction time. SHO's inspect
// takes a path argument, and letting the model supply that path would widen the
// readable range past the declared root — the exact thing TEI's MCP adapter
// forbids. A pinned document is the narrow, honest projection.
//
// Its own README says the CLI is a minimal headless reader and "not a finished
// Composer, Editor, Writer, or broadly accepted public API". That is recorded in
// the offer's description, not hidden.
type SHOReadOnlyTool struct {
	// NodeBinary is the node executable. Empty means "node".
	NodeBinary string
	// ScriptPath is the absolute path to bin/sho-inspect.cjs.
	ScriptPath string
	// DocumentPath is the ONE Markdown file this projection may inspect. It must
	// live inside AllowedRoot.
	DocumentPath string
	// AllowedRoot bounds the projection. The document must be inside it.
	AllowedRoot string
	// Timeout bounds one invocation.
	Timeout time.Duration
	Clock   func() time.Time
	Runner  Runner
}

// NewSHOReadOnlyTool builds the projection with production defaults.
func NewSHOReadOnlyTool(nodeBinary, scriptPath, documentPath, allowedRoot string) *SHOReadOnlyTool {
	if nodeBinary == "" {
		nodeBinary = "node"
	}
	return &SHOReadOnlyTool{
		NodeBinary:   nodeBinary,
		ScriptPath:   scriptPath,
		DocumentPath: documentPath,
		AllowedRoot:  allowedRoot,
		Timeout:      2 * time.Minute,
		Clock:        time.Now,
		Runner:       ProcessRunner{},
	}
}

// Name renders the product-qualified tool name.
func (t *SHOReadOnlyTool) Name() string { return "sho.inspect" }

// argvFor builds the exact argv. The document is the projection's pinned path,
// never a model-supplied one.
func (t *SHOReadOnlyTool) argvFor() ([]string, bool) {
	if t.ScriptPath == "" || t.DocumentPath == "" {
		return nil, false
	}
	return []string{t.NodeBinary, t.ScriptPath, "inspect", t.DocumentPath}, true
}

// Offers returns the tool offer, or reports why this projection cannot offer it.
//
// A document outside AllowedRoot is refused rather than offered: the projection
// must not be able to name a path the root does not cover.
func (t *SHOReadOnlyTool) Offers() (offers []ToolOffer, unsupported []string) {
	argv, ok := t.argvFor()
	if !ok {
		return nil, []string{"sho.inspect:missing-required-input"}
	}
	if t.AllowedRoot != "" && insideRoot(t.DocumentPath, t.AllowedRoot) == false {
		return nil, []string{"sho.inspect:document-outside-allowed-root"}
	}
	return []ToolOffer{{
		Name: t.Name(),
		Description: "SHO read-only Markdown inspect (sho-inspect.cjs inspect). " +
			"Reads raw bytes and reports the source sha256, link occurrences and heading paths. " +
			"The CLI describes itself as a minimal headless reader, not a finalized public contract. " +
			"The document is pinned by the projection; a caller cannot choose another path.",
		ReadOnly:     true,
		AllowedRoots: []string{"sho-document"},
		Command:      argv,
		InputSchema:  rawSchemaObject(),
	}}, nil
}

// MCPServerSpec is not offered: SHO's read-only surface is a Node script with a
// single positional argument, and it has no stdio JSON-RPC server. Wrapping it in
// an MCP server would mean writing one, which this adapter must not do.
func (t *SHOReadOnlyTool) MCPServerSpec(string) (MCPServerSpec, error) {
	return MCPServerSpec{}, fmt.Errorf("sho: the read-only surface is a Node CLI script with no MCP server; wrapping it would require a new server implementation")
}

// Invoke runs the pinned inspect and returns a product record.
func (t *SHOReadOnlyTool) Invoke(ctx context.Context, _ string) (*ToolCallRecord, error) {
	argv, ok := t.argvFor()
	if !ok {
		return nil, fmt.Errorf("sho read-only tool: the projection has no script or document")
	}
	if ctx == nil {
		ctx = context.Background()
	}
	runner := t.Runner
	if runner == nil {
		runner = ProcessRunner{}
	}
	execRes, err := runner.Exec(ctx, ExecSpec{Argv: argv, Dir: t.AllowedRoot, Timeout: t.Timeout})
	if err != nil {
		return nil, fmt.Errorf("sho read-only tool: %w", err)
	}
	if execRes.LaunchError != "" {
		return nil, fmt.Errorf("sho read-only tool: %s", execRes.LaunchError)
	}
	code := execRes.ExitCode
	rec := &ToolCallRecord{
		CallID:      "sho-inspect",
		Tool:        t.Name(),
		InputJSON:   "{}",
		ExitCode:    &code,
		ResultBytes: int64(len(execRes.Stdout)),
		ResultText:  string(execRes.Stdout),
		Note:        "product CLI invocation; no harness involved",
	}
	// SHO has no `ok` field. A zero exit with a `status` of "indexed" is the
	// product's own completion signal; anything else is reported, not folded away.
	if code == 0 {
		verdict, diags := decodeSHOEnvelope(execRes.Stdout)
		rec.ProductVerdict = verdict
		_ = diags
	}
	if len(execRes.Stderr) > 0 {
		rec.Note += "; stderr: " + firstLine(execRes.Stderr)
	}
	return rec, nil
}

// decodeSHOEnvelope reads SHO's own result shape. It deliberately does not reuse
// TEI's envelope reader: SHO reports `status` and a bare-string `error`, with no
// `ok`, and pretending otherwise would make two products look alike when they
// are not.
func decodeSHOEnvelope(stdout []byte) (*ProductVerdict, []Diagnostic) {
	trimmed := strings.TrimSpace(string(stdout))
	if trimmed == "" || !strings.HasPrefix(trimmed, "{") {
		return nil, nil
	}
	var env struct {
		Status              string `json:"status"`
		Error               string `json:"error"`
		Message             string `json:"message"`
		LinkOccurrenceCount *int   `json:"linkOccurrenceCount"`
		Source              *struct {
			SHA256     string `json:"sha256"`
			ByteLength int64  `json:"byteLength"`
		} `json:"source"`
	}
	if err := jsonUnmarshal(trimmed, &env); err != nil {
		return nil, nil
	}
	v := &ProductVerdict{}
	if env.Error != "" {
		v.OperationCompleted = false
		v.FailureCode = env.Error
		return v, nil
	}
	v.OperationCompleted = env.Status == "indexed"
	// SHO evaluates no validation, so ValidationPassed stays nil rather than
	// becoming false.
	return v, nil
}

// jsonUnmarshal is json.Unmarshal, named so this file has one obvious place to
// change if a product needs a decoder knob.
func jsonUnmarshal(s string, v any) error { return json.Unmarshal([]byte(s), v) }

// ResolveSHO checks the script and document exist and returns their digests.
func (t *SHOReadOnlyTool) Resolve() (scriptDigest, documentDigest string, err error) {
	if _, err := os.Stat(t.ScriptPath); err != nil {
		return "", "", fmt.Errorf("sho script %q: %w", t.ScriptPath, err)
	}
	if _, err := os.Stat(t.DocumentPath); err != nil {
		return "", "", fmt.Errorf("sho document %q: %w", t.DocumentPath, err)
	}
	s, err := fileDigestOf(t.ScriptPath)
	if err != nil {
		return "", "", err
	}
	d, err := fileDigestOf(t.DocumentPath)
	if err != nil {
		return "", "", err
	}
	return s, d, nil
}

// fileDigestOf digests one file for the evidence record.
func fileDigestOf(path string) (string, error) {
	b, err := os.ReadFile(filepath.Clean(path))
	if err != nil {
		return "", err
	}
	return DigestBytes(b), nil
}
