package harnessadapter

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"sort"
	"strings"
	"time"
)

// ContractVersion identifies the shared contract this package speaks. Adapters
// must not silently reinterpret it: a bump means the meaning of a field changed,
// not that a field was added.
const ContractVersion = "yi.harness-adapter/v0"

// ---------------------------------------------------------------------------
// Pins: what a claim is bound to. Every pin is a separate concept. Collapsing
// any two of them into one field is the failure mode this file exists to
// prevent (TAI #168 §47.1, TAI #232, TEI #2516).
// ---------------------------------------------------------------------------

// SourcePin binds a claim to the bytes a product actually read. A revision is
// not a digest: the same revision can carry different working-tree bytes, and a
// digest is not a statement about what was parsed.
type SourcePin struct {
	// Repo is the logical product/source identity, not a URL.
	Repo string `json:"repo"`
	// Revision is the exact declared revision (git SHA, release id, ...).
	Revision string `json:"revision,omitempty"`
	// ResolvedPath is the absolute path actually used for the run.
	ResolvedPath string `json:"resolvedPath,omitempty"`
	// BytesSHA256 is the digest of the bytes actually consumed. Empty means
	// "not measured"; it never means "unchanged".
	BytesSHA256 string `json:"bytesSha256,omitempty"`
	// ByteCount is the size of those bytes; 0 with an empty digest is unknown.
	ByteCount int64 `json:"byteCount,omitempty"`
	// Note carries non-secret provenance (e.g. "working tree modified").
	Note string `json:"note,omitempty"`
}

// ModelPin binds a claim to the model route. The harness and the model are
// independent: the same model behind two harnesses is two different runs, and
// the same harness behind two models is two different runs (TAI #168 MX-01).
type ModelPin struct {
	Provider string `json:"provider,omitempty"`
	Model    string `json:"model,omitempty"`
	Version  string `json:"version,omitempty"`
	// Route records how the model was reached (official API, subscription CLI,
	// gateway). It is an observation, never a billing entitlement.
	Route string `json:"route,omitempty"`
}

// SkillPin binds a claim to a Product Skill. "Placed" and "loaded" are
// different states: a skill sitting in a scanned root has not been read by the
// model, and a catalog entry is not a body.
type SkillPin struct {
	ID string `json:"id"`
	// PlacedPath is where the skill bytes were actually made visible to the
	// harness. Empty means the adapter did not place it.
	PlacedPath string `json:"placedPath,omitempty"`
	// BytesSHA256 digests the bytes actually placed.
	BytesSHA256 string `json:"bytesSha256,omitempty"`
	// LoadState is observed from harness tool calls, never asserted by the
	// adapter on the model's behalf.
	LoadState LoadState `json:"loadState"`
	// LoadedVia names the harness tool that loaded it, when observed.
	LoadedVia string `json:"loadedVia,omitempty"`
}

// LoadState is a three-valued observation, not a boolean.
type LoadState string

const (
	// LoadUnknown means the adapter could not observe whether the skill loaded.
	LoadUnknown LoadState = "unknown"
	// LoadNotLoaded means the skill was offered but no load was observed.
	LoadNotLoaded LoadState = "not-loaded"
	// LoadLoaded means a harness tool call naming this skill was observed.
	LoadLoaded LoadState = "loaded"
)

// ToolSchemaPin binds a claim to one tool's advertised schema. A tool being
// listed is not a tool being callable, and a tool being callable is not a tool
// being permitted.
type ToolSchemaPin struct {
	// Name is the model-facing name the harness publishes. For an MCP tool that
	// is `mcp__<serverName>__<rawName>`; for a native tool it is the harness's
	// own name.
	Name string `json:"name"`
	// ProductName is the raw product-side name, when the model-facing name is a
	// namespace-qualified form. Empty means the two are the same name.
	//
	// Keeping both is what lets a reader answer "did the product's tool run, or
	// did the harness's own shell tool run?" without parsing one from the other
	// at comparison time.
	ProductName string `json:"productName,omitempty"`
	// Via names how the tool reached the harness: "native", "mcp", or
	// "shell-bridge" when the model used the harness's own shell tool to reach a
	// product CLI instead of a typed tool.
	Via string `json:"via,omitempty"`
	// ServerName is the MCP namespace, when Via is "mcp".
	ServerName string `json:"serverName,omitempty"`
	// SchemaSHA256 digests the schema the harness actually advertised.
	SchemaSHA256 string `json:"schemaSha256,omitempty"`
	// Advertised is true only when the harness's own tool list was observed.
	Advertised bool `json:"advertised"`
	// Invoked is true only when a real call was observed in the run events.
	Invoked bool `json:"invoked"`
	// CallCount counts observed invocations.
	CallCount int `json:"callCount,omitempty"`
}

// RootPin binds a claim to one allowed root. Declaring a root and the harness
// actually being confined to it are different facts; Verified is only set by an
// independent probe that attempted a read outside the root.
type RootPin struct {
	// Logical is the product-side name (e.g. "tei-reference-workspace").
	Logical string `json:"logical"`
	// Path is the resolved absolute path handed to the harness.
	Path string `json:"path"`
	// Access is the access mode the harness was configured with.
	Access string `json:"access,omitempty"`
	// Verified records that an out-of-root read was attempted and refused.
	Verified bool `json:"verified"`
	// Note records the probe result when Verified is false.
	Note string `json:"note,omitempty"`
}

// Pins is the full pin set a Task carries. A pin that was not measured stays
// empty rather than defaulting to a reassuring value.
type Pins struct {
	Source      SourcePin         `json:"source"`
	Model       ModelPin          `json:"model"`
	Skills      []SkillPin        `json:"skills,omitempty"`
	ToolSchemas []ToolSchemaPin   `json:"toolSchemas,omitempty"`
	Roots       []RootPin         `json:"roots,omitempty"`
	Harness     HarnessPin        `json:"harness"`
	Extra       map[string]string `json:"extra,omitempty"`
}

// HarnessPin binds a claim to the harness executable and profile actually run.
// A harness family name ("DSH") is not a version, and a version is not a
// profile: the profile decides tool reachability and sandbox mode.
type HarnessPin struct {
	Family   string `json:"family"`
	Version  string `json:"version,omitempty"`
	Profile  string `json:"profile,omitempty"`
	ExePath  string `json:"exePath,omitempty"`
	ExeBytes string `json:"exeSha256,omitempty"`
	Platform string `json:"platform,omitempty"`
}

// ---------------------------------------------------------------------------
// Context projection: references, not raw data.
// ---------------------------------------------------------------------------

// ContextRef is a limited pointer to product context. It carries a reference
// and a disclosure class; it never carries the raw payload, and the adapter
// must not widen it.
type ContextRef struct {
	// Kind names the projection kind (e.g. "model-catalog", "subject-inspect").
	Kind string `json:"kind"`
	// Ref is the product-side locator. It is opaque to the adapter.
	Ref string `json:"ref"`
	// Disclosure records the disclosure class the product assigned. The adapter
	// forwards it and does not re-grade it.
	Disclosure string `json:"disclosure,omitempty"`
	// Required marks context the task cannot proceed without.
	Required bool `json:"required,omitempty"`
}

// ---------------------------------------------------------------------------
// Tool offers: what the product is willing to expose to the harness.
// ---------------------------------------------------------------------------

// ToolOffer is a product tool made available to the harness. The schema is
// pinned by digest so a drift between what was offered and what ran is
// detectable.
type ToolOffer struct {
	Name        string          `json:"name"`
	Description string          `json:"description,omitempty"`
	InputSchema json.RawMessage `json:"inputSchema,omitempty"`
	// ReadOnly states the product's declared effect class. It is a declaration,
	// not an enforcement.
	ReadOnly bool `json:"readOnly"`
	// AllowedRoots names the RootPin.Logical values this tool may touch.
	AllowedRoots []string `json:"allowedRoots,omitempty"`
	// Command is the product CLI invocation template, when the tool is backed by
	// a CLI. It is recorded verbatim; the adapter does not parse or rewrite it.
	Command []string `json:"command,omitempty"`
}

// ---------------------------------------------------------------------------
// Task and limits.
// ---------------------------------------------------------------------------

// Task is one unit of work handed to one harness. It is the interchange unit:
// the same Task must be runnable through any conforming adapter.
type Task struct {
	ID     string `json:"id"`
	Prompt string `json:"prompt"`

	Pins        Pins         `json:"pins"`
	ContextRefs []ContextRef `json:"contextRefs,omitempty"`
	Tools       []ToolOffer  `json:"tools,omitempty"`
	Skills      []SkillPin   `json:"skills,omitempty"`

	// Limits are advisory budgets. Exceeding them is an observation, and a
	// budget is never a permission grant.
	Limits Limits `json:"limits"`
}

// WorkDirHint returns the first pinned root path as a suggested working
// directory for an adapter that runs a process. It is a hint, not a
// confinement: the adapter still records what it actually used.
func (t Task) WorkDirHint() string {
	for _, r := range t.Pins.Roots {
		if r.Path != "" {
			return r.Path
		}
	}
	return ""
}

// Limits carries advisory budgets for one run.
type Limits struct {
	TimeoutMS   int64 `json:"timeoutMs,omitempty"`
	MaxSteps    int   `json:"maxSteps,omitempty"`
	MaxTools    int   `json:"maxTools,omitempty"`
	MaxOutBytes int64 `json:"maxOutBytes,omitempty"`
}

// ---------------------------------------------------------------------------
// Session reference. The harness-side id is opaque and carries no product
// meaning: it is not an acceptance, not a permission and not an identity the
// product may rely on (TAI Draft #270 §46, TAI #271).
// ---------------------------------------------------------------------------

// SessionState reports what the adapter observed about the session.
type SessionState string

const (
	// SessionUnknown means the adapter did not obtain a session reference.
	SessionUnknown SessionState = "unknown"
	// SessionCreated means the harness reported a fresh session.
	SessionCreated SessionState = "created"
	// SessionResumed means the harness reported it adopted an existing session.
	SessionResumed SessionState = "resumed"
	// SessionRejected means the harness refused the requested session id.
	SessionRejected SessionState = "rejected"
)

// SessionRef is the harness-side session reference.
type SessionRef struct {
	// Adapter names the adapter that produced this reference.
	Adapter string `json:"adapter"`
	// ExternalID is the harness's own id. Opaque by contract.
	ExternalID string       `json:"externalId,omitempty"`
	State      SessionState `json:"state"`
	// CWD is the working directory the harness reported.
	CWD string `json:"cwd,omitempty"`
	// RequestedID is the id the caller asked to resume, if any. Kept separate
	// so a refusal is distinguishable from an adoption.
	RequestedID string `json:"requestedId,omitempty"`
	// Note records a non-secret reason for a rejection.
	Note       string `json:"note,omitempty"`
	ObservedAt string `json:"observedAt,omitempty"`
}

// ---------------------------------------------------------------------------
// Result: five levels that must never collapse into one "ok".
// ADR-0048 §2.4; TAI #168 §16.1 D/T/Q/E.
// ---------------------------------------------------------------------------

// TransportState reports whether the request reached the harness at all.
type TransportState string

const (
	TransportNotAttempted TransportState = "not-attempted"
	TransportDelivered    TransportState = "delivered"
	TransportFailed       TransportState = "failed"
	TransportUnknown      TransportState = "unknown"
)

// RunState reports what the harness says about its own run. "completed" is the
// harness's verdict about its turn, not about the product's meaning.
type RunState string

const (
	RunUnknown   RunState = "unknown"
	RunCompleted RunState = "completed"
	RunAborted   RunState = "aborted"
	RunError     RunState = "error"
)

// ToolCallRecord is one observed tool call. HarnessStatus is what the harness
// reported; ExitCode and ProductVerdict are what the product reported. They are
// recorded side by side and never merged.
type ToolCallRecord struct {
	CallID     string `json:"callId"`
	Tool       string `json:"tool"`
	InputJSON  string `json:"inputJson,omitempty"`
	ResultText string `json:"resultText,omitempty"`
	// ResultBytes is the size of the harness-visible result payload.
	ResultBytes int64 `json:"resultBytes,omitempty"`
	// HarnessStatus is the harness's own status word (e.g. "completed").
	HarnessStatus string `json:"harnessStatus,omitempty"`
	// ExitCode is the product-side process exit, when the tool wrapped a CLI.
	ExitCode *int `json:"exitCode,omitempty"`
	// ProductVerdict is the product-side semantic verdict, when the tool
	// returned one. Nil means the product did not report one.
	ProductVerdict *ProductVerdict `json:"productVerdict,omitempty"`
	// Truncated records that the harness bounded the payload it showed.
	Truncated bool   `json:"truncated,omitempty"`
	Note      string `json:"note,omitempty"`
}

// ProductVerdict keeps operation completion separate from validation success
// (ADR-0048 §2.4 items 2 and 3).
type ProductVerdict struct {
	// OperationCompleted is the product's "the operation ran to the end".
	OperationCompleted bool `json:"operationCompleted"`
	// ValidationPassed is the product's "the model/诊断 passed". Nil when the
	// product did not evaluate it.
	ValidationPassed *bool `json:"validationPassed,omitempty"`
	// FailureCode is the product's stable string failure code.
	FailureCode string `json:"failureCode,omitempty"`
	// Diagnostics are the product's own diagnostics, forwarded verbatim.
	Diagnostics []Diagnostic `json:"diagnostics,omitempty"`
}

// Diagnostic is one non-secret diagnostic line.
type Diagnostic struct {
	Severity string `json:"severity"`
	Code     string `json:"code,omitempty"`
	Message  string `json:"message,omitempty"`
	Source   string `json:"source,omitempty"`
}

// Result is one adapter's answer for one Task.
type Result struct {
	Contract string `json:"contract"`
	Adapter  string `json:"adapter"`

	Transport TransportState `json:"transport"`
	Run       RunState       `json:"run"`

	Session   SessionRef `json:"session"`
	FinalText string     `json:"finalText,omitempty"`

	ToolCalls   []ToolCallRecord `json:"toolCalls,omitempty"`
	Diagnostics []Diagnostic     `json:"diagnostics,omitempty"`

	// Outbound records what actually left, by direction and digest.
	Outbound []OutboundRecord `json:"outbound,omitempty"`
	// Receipt records what the consumer actually received.
	Receipt Receipt `json:"receipt"`

	// Unsupported names capabilities this adapter could not provide for this
	// task. An absent capability is reported, not quietly dropped.
	Unsupported []string `json:"unsupported,omitempty"`

	// ObservedModel is the model the harness itself reported using. It is kept
	// apart from Pins.Model, which is what the caller pinned: a harness that
	// silently substitutes a model has produced a different run, not the same
	// one with a different label.
	ObservedModel ModelPin `json:"observedModel,omitempty"`

	// Observations are adapter-recorded, harness-specific measurements with no
	// common meaning across vendors (a dollar cost, a token count, a turn
	// count). They are never compared across adapters as though they meant the
	// same thing, and the divergence computation ignores them deliberately.
	Observations map[string]string `json:"observations,omitempty"`

	// ExitCode is the harness process exit code, when a process was run.
	ExitCode *int `json:"exitCode,omitempty"`
	// Reason is the harness's own run reason string, verbatim.
	Reason string `json:"reason,omitempty"`

	StartedAt  string `json:"startedAt,omitempty"`
	FinishedAt string `json:"finishedAt,omitempty"`
}

// OutboundRecord is one outbound byte stream, digested.
type OutboundRecord struct {
	// Direction names the stream: "task-text", "argv", "stdin",
	// "context-projection", "skill-bytes", "stderr".
	Direction   string `json:"direction"`
	BytesSHA256 string `json:"bytesSha256,omitempty"`
	ByteCount   int64  `json:"byteCount,omitempty"`
	// Detail is a non-secret description. It must not contain credentials,
	// raw product data or full paths to protected material.
	Detail    string `json:"detail,omitempty"`
	Truncated bool   `json:"truncated,omitempty"`
}

// ReceiptState reports what the consumer actually received.
type ReceiptState string

const (
	ReceiptNotObserved ReceiptState = "not-observed"
	ReceiptPartial     ReceiptState = "partial"
	ReceiptComplete    ReceiptState = "complete"
)

// Receipt is the consumer-side receipt. A harness reporting "delivered" does
// not set this; only an observed consumer read does (TAI #271, EKI #465).
type Receipt struct {
	State       ReceiptState `json:"state"`
	Consumer    string       `json:"consumer,omitempty"`
	BytesSHA256 string       `json:"bytesSha256,omitempty"`
	ByteCount   int64        `json:"byteCount,omitempty"`
	Note        string       `json:"note,omitempty"`
}

// ---------------------------------------------------------------------------
// Availability: probed, never assumed.
// ---------------------------------------------------------------------------

// Availability is the outcome of a real probe. An adapter must not report
// Reachable=true without having run something.
type Availability struct {
	Reachable bool              `json:"reachable"`
	Reason    string            `json:"reason,omitempty"`
	Detail    map[string]string `json:"detail,omitempty"`
}

// ---------------------------------------------------------------------------
// Capabilities: what an adapter can and cannot do.
// ---------------------------------------------------------------------------

// Capability names one adapter feature. The set is closed so an adapter cannot
// invent a capability that means whatever it likes.
type Capability string

const (
	CapSessionCreate    Capability = "session:create"
	CapSessionResume    Capability = "session:resume"
	CapContextProject   Capability = "context:project"
	CapToolInvoke       Capability = "tool:invoke"
	CapSkillDiscover    Capability = "skill:discover"
	CapSkillLoad        Capability = "skill:load"
	CapResultReceipt    Capability = "result:receipt"
	CapDiagnostics      Capability = "diagnostics"
	CapEvidenceTracking Capability = "evidence:tracking"
)

// AllCapabilities lists the closed capability set in a stable order.
func AllCapabilities() []Capability {
	return []Capability{
		CapSessionCreate, CapSessionResume, CapContextProject, CapToolInvoke,
		CapSkillDiscover, CapSkillLoad, CapResultReceipt, CapDiagnostics,
		CapEvidenceTracking,
	}
}

// ---------------------------------------------------------------------------
// Adapter interface.
// ---------------------------------------------------------------------------

// Adapter is the vendor-neutral seam. An adapter owns no product semantics: it
// launches an external harness, offers the task's pinned context/tools/skills,
// and reports what happened without promoting any of it.
type Adapter interface {
	// Name is the stable adapter id (e.g. "dsh-headless").
	Name() string
	// Probe performs a real reachability probe. It must not fabricate success
	// and must not run the task.
	Probe(ctx context.Context) (Availability, error)
	// Capabilities reports the closed capability set this adapter supports.
	Capabilities() []Capability
	// Run executes one Task through one harness. ctx bounds the run.
	Run(ctx context.Context, t Task, session *SessionRef) (*Result, error)
}

// ---------------------------------------------------------------------------
// Digest helpers.
// ---------------------------------------------------------------------------

// DigestBytes returns the sha256 of b, hex encoded with the algorithm prefix.
func DigestBytes(b []byte) string {
	sum := sha256.Sum256(b)
	return "sha256:" + hex.EncodeToString(sum[:])
}

// DigestString is DigestBytes for a string.
func DigestString(s string) string {
	return DigestBytes([]byte(s))
}

// NowRFC3339 returns the current UTC time in RFC3339. Injectable in tests via
// the clock field of a Runner.
func NowRFC3339() string {
	return time.Now().UTC().Format(time.RFC3339)
}

// ---------------------------------------------------------------------------
// Result helpers: comparison and promotion guards.
// ---------------------------------------------------------------------------

// ToolNames returns the distinct tool names observed in the result, sorted.
func (r *Result) ToolNames() []string {
	seen := map[string]bool{}
	for _, c := range r.ToolCalls {
		seen[c.Tool] = true
	}
	out := make([]string, 0, len(seen))
	for n := range seen {
		out = append(out, n)
	}
	sort.Strings(out)
	return out
}

// MCPToolCalls returns the observed calls that went through an MCP tool, with
// the server namespace and raw tool name decoded. Calls made through the
// harness's own shell tool are NOT included: reaching a product CLI by running
// it in a shell is a different observation from calling a typed product tool.
func (r *Result) MCPToolCalls() []MCPCall {
	var out []MCPCall
	for _, c := range r.ToolCalls {
		server, raw, ok := DecodeMCPToolName(c.Tool)
		if !ok {
			continue
		}
		out = append(out, MCPCall{
			ServerName: server,
			RawName:    raw,
			Call:       c,
		})
	}
	return out
}

// MCPCall is one observed MCP tool call with its name decoded.
type MCPCall struct {
	ServerName string
	RawName    string
	Call       ToolCallRecord
}

// ShellBridgeCalls returns the observed calls that used the harness's own shell
// tool. They may still have reached a product CLI, but they are recorded as a
// bridge rather than as a typed tool invocation, because the product never saw
// a typed request.
func (r *Result) ShellBridgeCalls() []ToolCallRecord {
	var out []ToolCallRecord
	for _, c := range r.ToolCalls {
		if isShellTool(c.Tool) {
			out = append(out, c)
		}
	}
	return out
}

// isShellTool reports whether a harness tool name is a general command runner.
// The list is harness-specific vocabulary, so it is a helper rather than a
// contract constant.
func isShellTool(tool string) bool {
	switch strings.ToLower(tool) {
	case "pwsh", "bash", "shell", "powershell", "terminal", "exec", "run_command":
		return true
	}
	return false
}

// ToolSchemaPins derives the advertised/invoked pin for each observed tool.
// An MCP tool contributes both its model-facing name and its raw product name.
func (r *Result) ToolSchemaPins() []ToolSchemaPin {
	counts := map[string]int{}
	for _, c := range r.ToolCalls {
		counts[c.Tool]++
	}
	names := make([]string, 0, len(counts))
	for n := range counts {
		names = append(names, n)
	}
	sort.Strings(names)
	out := make([]ToolSchemaPin, 0, len(names))
	for _, n := range names {
		pin := ToolSchemaPin{Name: n, Invoked: true, CallCount: counts[n]}
		if server, raw, ok := DecodeMCPToolName(n); ok {
			pin.Via = "mcp"
			pin.ProductName = raw
			pin.ServerName = server
		} else if isShellTool(n) {
			pin.Via = "shell-bridge"
		} else {
			pin.Via = "native"
		}
		out = append(out, pin)
	}
	return out
}

// Promoted reports whether this result would justify claiming the product
// semantically accepted, permitted or completed the work. It always returns
// false by construction: no harness observation in this package carries that
// meaning. It exists so callers have a named place to ask the question instead
// of inventing their own shortcut.
func (r *Result) Promoted() bool { return false }

// Summary renders a one-line, non-secret summary of the result.
func (r *Result) Summary() string {
	if r == nil {
		return "<nil result>"
	}
	return fmt.Sprintf("adapter=%s transport=%s run=%s tools=%d exit=%s",
		r.Adapter, r.Transport, r.Run, len(r.ToolCalls), ExitString(r.ExitCode))
}

// ExitString renders an optional exit code without inventing a zero.
func ExitString(code *int) string {
	if code == nil {
		return "n/a"
	}
	return fmt.Sprintf("%d", *code)
}

// NormalizeToolCalls returns a copy of the calls with the volatile fields
// (call ids, timestamps) removed, so two adapters can be compared on what was
// invoked rather than on harness-specific noise.
func (r *Result) NormalizeToolCalls() []ToolCallRecord {
	out := make([]ToolCallRecord, 0, len(r.ToolCalls))
	for _, c := range r.ToolCalls {
		c.CallID = ""
		out = append(out, c)
	}
	sort.Slice(out, func(i, j int) bool {
		if out[i].Tool != out[j].Tool {
			return out[i].Tool < out[j].Tool
		}
		return out[i].InputJSON < out[j].InputJSON
	})
	return out
}

// UnsupportedList renders the unsupported list for evidence records.
func UnsupportedList(items []string) string {
	if len(items) == 0 {
		return ""
	}
	return strings.Join(items, ", ")
}
