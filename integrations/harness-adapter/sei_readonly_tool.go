package harnessadapter

import (
	"context"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"time"
)

// SEIReadOnlyTool projects the SEI CLI's read-only surface into ToolOffers.
//
// SEI differs from TEI in three ways that this projection keeps out of the
// shared contract rather than importing:
//   - It has no `-workspace` flag; it has `-data-root`.
//   - Its MCP server takes `--data-root` and has a `-read-only` mode that offers
//     only `resume`. Offering `add_recommendation` or `add_decision` would put a
//     write through the adapter, which the contract forbids.
//   - It reports `snapshot_digest` where TEI reports `worldFingerprint`. The
//     identity comparison handles that by comparing only shared keys.
type SEIReadOnlyTool struct {
	// Binary is the sei executable. Empty means resolve "sei" on PATH.
	Binary string
	// DataRoot is the SEI record store directory.
	DataRoot string
	// Timeout bounds one invocation.
	Timeout time.Duration
	Clock   func() time.Time
	Runner  Runner
}

// NewSEIReadOnlyTool builds the projection with production defaults.
func NewSEIReadOnlyTool(binary, dataRoot string) *SEIReadOnlyTool {
	return &SEIReadOnlyTool{
		Binary:   binary,
		DataRoot: dataRoot,
		Timeout:  2 * time.Minute,
		Clock:    time.Now,
		Runner:   ProcessRunner{},
	}
}

// SEIReadOnlyCommands are the SEI commands this projection may offer. They are
// the commands whose documented effect is read-only: `resume`, `doctor`,
// `verify`, `version`. `init` creates a store, `add`/`export`/`gate` write, and
// `mcp` is a transport, so none of those is offered.
var SEIReadOnlyCommands = []string{"resume", "doctor", "verify", "version"}

// Name renders the product-qualified tool name.
func (t *SEIReadOnlyTool) Name(command string) string { return "sei." + command }

// argvFor builds the exact argv for one command, or reports that this projection
// cannot express it.
func (t *SEIReadOnlyTool) argvFor(command string) ([]string, bool) {
	exe := t.Binary
	if exe == "" {
		exe = "sei"
	}
	switch command {
	case "version":
		return []string{exe, "version"}, true
	case "resume":
		if t.DataRoot == "" {
			return nil, false
		}
		// -json is required: the adapter compares structured identity, not prose.
		return []string{exe, "resume", "-data-root", t.DataRoot, "-json"}, true
	case "doctor":
		if t.DataRoot == "" {
			return nil, false
		}
		// doctor has no -json; it is offered because it reports the store's
		// identity in its text, but its result is NOT used for equivalence.
		return []string{exe, "doctor", "-data-root", t.DataRoot}, true
	case "verify":
		// verify needs a bundle path this projection does not own.
		return nil, false
	}
	return nil, false
}

// Offers returns the tool offers for every allowlisted command this projection
// can build, plus the commands it cannot.
func (t *SEIReadOnlyTool) Offers() (offers []ToolOffer, unsupported []string) {
	for _, cmd := range SEIReadOnlyCommands {
		argv, ok := t.argvFor(cmd)
		if !ok {
			unsupported = append(unsupported, t.Name(cmd)+":missing-required-input")
			continue
		}
		offers = append(offers, ToolOffer{
			Name:         t.Name(cmd),
			Description:  "SEI read-only CLI: " + cmd,
			ReadOnly:     true,
			AllowedRoots: []string{"sei-store"},
			Command:      argv,
			InputSchema:  rawSchemaObject(),
		})
	}
	return offers, unsupported
}

// MCPServerSpec renders the SEI MCP server as a spec. It always uses
// `-read-only`, which offers only `resume`: an MCP server that also offers
// `add_recommendation` would let a harness append to the record store through
// the adapter.
func (t *SEIReadOnlyTool) MCPServerSpec(serverName string) MCPServerSpec {
	return MCPServerSpec{
		ServerName:         serverName,
		Transport:          "stdio",
		Command:            t.Binary,
		Args:               []string{"mcp", "-read-only", "--data-root", t.DataRoot},
		ToolCallTimeoutMS:  60000,
		FailOnStartupError: true,
	}
}

// Invoke runs one offered command and returns a product record.
func (t *SEIReadOnlyTool) Invoke(ctx context.Context, command string) (*ToolCallRecord, error) {
	argv, ok := t.argvFor(command)
	if !ok {
		return nil, fmt.Errorf("sei read-only tool: command %q is not offered by this projection", command)
	}
	if ctx == nil {
		ctx = context.Background()
	}
	runner := t.Runner
	if runner == nil {
		runner = ProcessRunner{}
	}
	execRes, err := runner.Exec(ctx, ExecSpec{Argv: argv, Dir: t.DataRoot, Timeout: t.Timeout})
	if err != nil {
		return nil, fmt.Errorf("sei read-only tool: %w", err)
	}
	if execRes.LaunchError != "" {
		return nil, fmt.Errorf("sei read-only tool: %s", execRes.LaunchError)
	}
	code := execRes.ExitCode
	rec := &ToolCallRecord{
		CallID:      "sei-" + command,
		Tool:        t.Name(command),
		InputJSON:   "{}",
		ExitCode:    &code,
		ResultBytes: int64(len(execRes.Stdout)),
		ResultText:  string(execRes.Stdout),
		Note:        "product CLI invocation; no harness involved",
	}
	if code == 0 {
		if env, err := ParseProductEnvelope(execRes.Stdout); err == nil {
			rec.ProductVerdict = &ProductVerdict{OperationCompleted: true}
			_ = env
		}
	}
	if len(execRes.Stderr) > 0 {
		rec.Note += "; stderr: " + firstLine(execRes.Stderr)
	}
	return rec, nil
}

// ResolveBinary resolves the sei executable and returns its digested identity.
func (t *SEIReadOnlyTool) ResolveBinary() (string, error) {
	if t.Binary != "" {
		if _, err := os.Stat(t.Binary); err != nil {
			return "", fmt.Errorf("sei binary %q: %w", t.Binary, err)
		}
		return filepath.Clean(t.Binary), nil
	}
	return exec.LookPath("sei")
}

// rawSchemaObject is an empty JSON Schema object, which is what a no-argument
// product tool advertises. It is a function so each offer gets its own copy.
func rawSchemaObject() []byte {
	return []byte(`{"type":"object","additionalProperties":false,"properties":{}}`)
}

// SEIStoreDigest digests the SEI store's snapshot-bearing file set as a
// directory listing observation, mirroring DigestWorkspace.
func SEIStoreDigest(root string) (string, int, int64, error) {
	return DigestWorkspace(root)
}
