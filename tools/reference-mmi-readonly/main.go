package main

import (
	"bufio"
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"slices"
	"strings"
	"sync"
	"time"
)

const protocolVersion = "2024-11-05"

type SelectedObservation struct {
	ID            string `json:"id"`
	Text          string `json:"text"`
	Source        string `json:"source"`
	SourceVersion string `json:"version"`
	Availability  string `json:"availability"`
}

// RowsBinding records what select reported about its own row counts.
type RowsBinding struct {
	Status      string `json:"status"` // complete | incomplete | unavailable
	Shown       int    `json:"shown"`
	OfTotal     int    `json:"ofTotal"`
	Exact       bool   `json:"exact"`
	PreviewRows int    `json:"previewRows"`
}

// Binding ties TAI-computed values to values MMI returned.
type Binding struct {
	CandidateContract     string      `json:"candidateContract,omitempty"`
	CSVDigest             string      `json:"csvDigest"`
	MMISourceDigest       string      `json:"mmiSourceDigest,omitempty"`
	SourceDigest          string      `json:"sourceDigest"` // match | mismatch | unavailable
	TableFingerprint      string      `json:"tableFingerprint,omitempty"`
	FingerprintCrossCheck string      `json:"fingerprintCrossCheck"` // match | mismatch | unavailable
	Rows                  RowsBinding `json:"rows"`
}

type ToolSurface struct {
	Status       string   `json:"status"` // listed | unavailable
	Tools        []string `json:"tools"`
	WriteCapable []string `json:"writeCapable"`
	Unmeasured   []string `json:"unmeasured"`
	CalledByTAI  []string `json:"calledByTai"`
	Basis        string   `json:"basis"`
}

type RejectionKinds struct {
	Boundary string `json:"boundary"` // outside-workspace | not-found | other | none
	Missing  string `json:"missing"`
}

type Receipt struct {
	Schema                string                `json:"schema"`
	Server                string                `json:"server"`
	ProtocolVersion       string                `json:"protocolVersion"`
	MmiCommit             string                `json:"mmiCommit,omitempty"`
	PackageLockDigest     string                `json:"packageLockDigest,omitempty"`
	NodeVersion           string                `json:"nodeVersion,omitempty"`
	Tool                  string                `json:"tool"`
	CandidateCount        int                   `json:"candidateCount"`
	SelectedRows          int                   `json:"selectedRows"`
	ObservedIDs           []string              `json:"observedIds"`
	Selected              []SelectedObservation `json:"selected"`
	ConflictPreserved     bool                  `json:"conflictPreserved"`
	SourceDigestBefore    string                `json:"sourceDigestBefore"`
	SourceDigestAfter     string                `json:"sourceDigestAfter"`
	GuideDigestBefore     string                `json:"guideDigestBefore"`
	GuideDigestAfter      string                `json:"guideDigestAfter"`
	BoundaryRejected      bool                  `json:"boundaryRejected"`
	MissingSourceRejected bool                  `json:"missingSourceRejected"`
	ReadOnly              bool                  `json:"readOnly"`
	RealProductConnected  bool                  `json:"realProductConnected"`
	Passed                bool                  `json:"passed"`
	Reason                string                `json:"reason,omitempty"`
	Notes                 []string              `json:"notes"`
	Extra                 map[string]string     `json:"extra,omitempty"`
	// Additive fields. Consumers decode this receipt without DisallowUnknownFields.
	Pin           PinCheck       `json:"pin"`
	Binding       Binding        `json:"binding"`
	ToolSurface   ToolSurface    `json:"toolSurface"`
	RejectionKind RejectionKinds `json:"rejectionKinds"`
	WorkspaceTree WorkspaceTree  `json:"workspaceTree"`
}

type rpcRequest struct {
	JSONRPC string `json:"jsonrpc"`
	ID      any    `json:"id,omitempty"`
	Method  string `json:"method"`
	Params  any    `json:"params,omitempty"`
}

type rpcError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

type rpcResponse struct {
	JSONRPC string          `json:"jsonrpc"`
	ID      json.RawMessage `json:"id"`
	Result  json.RawMessage `json:"result"`
	Error   *rpcError       `json:"error"`
}

type mcpClient struct {
	cmd       *exec.Cmd
	stdin     io.WriteCloser
	reader    *bufio.Reader
	stderr    bytes.Buffer
	nextID    int
	closeOnce sync.Once
	called    []string
}

// launchMCP builds the MMI MCP server command. Tests replace it with a fake
// server so the negative cases run without a real MMI checkout.
var launchMCP = func(ctx context.Context, mmiRoot, workspace string) (*exec.Cmd, error) {
	node, err := exec.LookPath("node")
	if err != nil {
		return nil, fmt.Errorf("node is unavailable: %w", err)
	}
	implement := filepath.Join(mmiRoot, "03_Implement")
	if _, err := os.Stat(filepath.Join(implement, "src", "cli", "mcp.ts")); err != nil {
		return nil, fmt.Errorf("MMI MCP source is unavailable: %w", err)
	}
	cmd := exec.CommandContext(ctx, node, "--import", "tsx", "src/cli/mcp.ts", "--root", workspace)
	cmd.Dir = implement
	return cmd, nil
}

func startMCP(ctx context.Context, mmiRoot, workspace string) (*mcpClient, error) {
	workspace, err := filepath.Abs(workspace)
	if err != nil {
		return nil, err
	}
	cmd, err := launchMCP(ctx, mmiRoot, workspace)
	if err != nil {
		return nil, err
	}
	stdin, err := cmd.StdinPipe()
	if err != nil {
		return nil, err
	}
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return nil, err
	}
	client := &mcpClient{cmd: cmd, stdin: stdin, reader: bufio.NewReaderSize(stdout, 16*1024*1024), nextID: 1}
	cmd.Stderr = &client.stderr
	if err := cmd.Start(); err != nil {
		return nil, err
	}
	return client, nil
}

func (c *mcpClient) call(method string, params any) (json.RawMessage, error) {
	id := c.nextID
	c.nextID++
	request := rpcRequest{JSONRPC: "2.0", ID: id, Method: method, Params: params}
	raw, err := json.Marshal(request)
	if err != nil {
		return nil, err
	}
	if _, err := c.stdin.Write(append(raw, '\n')); err != nil {
		return nil, err
	}
	for {
		line, err := c.reader.ReadBytes('\n')
		if err != nil {
			c.close() // wait for the process: stderr is complete, and safe to read, only after it exited
			return nil, fmt.Errorf("reading MCP response: %w (stderr: %s)", err, strings.TrimSpace(c.stderr.String()))
		}
		if len(bytes.TrimSpace(line)) == 0 {
			continue
		}
		var response rpcResponse
		if err := json.Unmarshal(line, &response); err != nil {
			return nil, fmt.Errorf("invalid MCP response: %w", err)
		}
		var responseID int
		if err := json.Unmarshal(response.ID, &responseID); err != nil || responseID != id {
			continue
		}
		if response.Error != nil {
			return nil, fmt.Errorf("MCP error %d: %s", response.Error.Code, response.Error.Message)
		}
		return response.Result, nil
	}
}

func (c *mcpClient) notify(method string) error {
	raw, err := json.Marshal(rpcRequest{JSONRPC: "2.0", Method: method})
	if err != nil {
		return err
	}
	_, err = c.stdin.Write(append(raw, '\n'))
	return err
}

// close is idempotent: Run closes explicitly before the after-digests (so a
// write during shutdown is observed) and again from defer on early returns.
func (c *mcpClient) close() {
	c.closeOnce.Do(func() {
		_ = c.stdin.Close()
		done := make(chan struct{})
		go func() {
			_ = c.cmd.Wait()
			close(done)
		}()
		select {
		case <-done:
		case <-time.After(2 * time.Second):
			_ = c.cmd.Process.Kill()
			<-done
		}
	})
}

type toolResult struct {
	Content []struct {
		Type string `json:"type"`
		Text string `json:"text"`
	} `json:"content"`
	IsError bool `json:"isError"`
}

// allowedCalls is the whole set of MMI tools this connection may invoke.
var allowedCalls = []string{"inspect", "select"}

func (c *mcpClient) callTool(name string, arguments map[string]any) (string, bool, error) {
	if !slices.Contains(allowedCalls, name) {
		return "", false, fmt.Errorf("refusing to call MMI tool %q: only %v are allowed", name, allowedCalls)
	}
	if !slices.Contains(c.called, name) {
		c.called = append(c.called, name)
	}
	result, err := c.call("tools/call", map[string]any{"name": name, "arguments": arguments})
	if err != nil {
		return "", false, err
	}
	var tool toolResult
	if err := json.Unmarshal(result, &tool); err != nil {
		return "", false, err
	}
	if len(tool.Content) == 0 {
		return "", tool.IsError, fmt.Errorf("tool returned no content")
	}
	return tool.Content[0].Text, tool.IsError, nil
}

// measuredTools are the tool names observed in tools/list at the documented pin
// and at later MMI commits (a measurement by the implementer, not a review by
// the MMI owner). MMI exposes no MCP annotations (name, description, inputSchema
// only), so write capability is judged from the name tokens.
var measuredTools = []string{
	"schema", "html-audit", "inspect", "check", "render", "select", "find", "handoff",
	"validate-proposal", "validate-selection", "validate-transformation",
}

var writeVerbs = []string{
	"write", "commit", "save", "import", "apply", "delete", "remove", "create", "update",
	"set", "put", "upload", "publish", "send", "push", "export", "patch", "rename", "move",
}

func writeCapable(name string) bool {
	for _, token := range regexp.MustCompile(`[-_./ ]+`).Split(strings.ToLower(name), -1) {
		if slices.Contains(writeVerbs, token) {
			return true
		}
	}
	return false
}

func (c *mcpClient) listTools() (ToolSurface, error) {
	surface := ToolSurface{Status: "unavailable", Tools: []string{}, WriteCapable: []string{}, Unmeasured: []string{}, Basis: "tool-name tokens; MMI exposes no MCP annotations"}
	result, err := c.call("tools/list", map[string]any{})
	if err != nil {
		return surface, err
	}
	var list struct {
		Tools []struct {
			Name string `json:"name"`
		} `json:"tools"`
		NextCursor string `json:"nextCursor"`
	}
	if err := json.Unmarshal(result, &list); err != nil {
		return surface, err
	}
	if list.NextCursor != "" || len(list.Tools) == 0 {
		return surface, nil // an incomplete or empty list proves nothing
	}
	for _, tool := range list.Tools {
		surface.Tools = append(surface.Tools, tool.Name)
		if writeCapable(tool.Name) {
			surface.WriteCapable = append(surface.WriteCapable, tool.Name)
		}
		if !slices.Contains(measuredTools, tool.Name) {
			surface.Unmeasured = append(surface.Unmeasured, tool.Name)
		}
	}
	slices.Sort(surface.Tools)
	slices.Sort(surface.WriteCapable)
	slices.Sort(surface.Unmeasured)
	surface.Status = "listed"
	return surface, nil
}

type inspectResult struct {
	CandidateContract string `json:"candidateContract"`
	Candidates        *[]struct {
		Locator struct {
			SourceDigest string `json:"sourceDigest"`
			Sheet        string `json:"sheet"`
			Range        string `json:"range"`
		} `json:"locator"`
		Fingerprint struct {
			Digest string `json:"digest"`
		} `json:"fingerprint"`
	} `json:"candidates"`
}

type selectionResult struct {
	Schema string `json:"schema"`
	Result struct {
		OK    bool `json:"ok"`
		Table struct {
			Sheet string `json:"sheet"`
			Range string `json:"range"`
		} `json:"table"`
		Rows *struct {
			Shown   int  `json:"shown"`
			OfTotal int  `json:"ofTotal"`
			Exact   bool `json:"exact"`
		} `json:"rows"`
		Preview struct {
			Headers []string   `json:"headers"`
			Rows    [][]string `json:"rows"`
		} `json:"preview"`
		Errors []struct {
			Code    string `json:"code"`
			Message string `json:"message"`
		} `json:"errors"`
	} `json:"result"`
	Candidate *struct {
		Fingerprint string `json:"fingerprint"`
		Sheet       string `json:"sheet"`
		Range       string `json:"range"`
	} `json:"candidate"`
}

func selectObservations(client *mcpClient) (selectionResult, error) {
	text, isError, err := client.callTool("select", map[string]any{
		"source":  "observations.csv",
		"table":   "Sheet1!A1:E4",
		"columns": "id,text,source,version,availability",
	})
	if err != nil {
		return selectionResult{}, err
	}
	if isError {
		// The MMI error text can carry an absolute local path, so only its kind is kept.
		return selectionResult{}, fmt.Errorf("select returned isError (reason kind: %s)", classifyRejection(text))
	}
	var selection selectionResult
	if err := json.Unmarshal([]byte(text), &selection); err != nil {
		return selectionResult{}, err
	}
	if !selection.Result.OK {
		codes := []string{}
		for _, item := range selection.Result.Errors {
			codes = append(codes, item.Code)
		}
		return selectionResult{}, fmt.Errorf("select was rejected: %s", strings.Join(codes, ","))
	}
	return selection, nil
}

// nodeVersionOf reports `node --version`. Tests replace it so the negative cases
// do not depend on a node binary.
var nodeVersionOf = defaultNodeVersionOf

// defaultNodeVersionOf asks the node binary that launchMCP would start, from the
// directory it starts it in (03_Implement). A version manager's shim (Volta, asdf,
// mise, .node-version) chooses the version by the working directory, so a probe
// from any other directory could report a different Node than the one that runs MMI.
func defaultNodeVersionOf(ctx context.Context, mmiRoot string) string {
	node, err := exec.LookPath("node")
	if err != nil {
		return ""
	}
	return commandOutput(ctx, filepath.Join(mmiRoot, "03_Implement"), node, "--version")
}

func commandOutput(ctx context.Context, dir, name string, args ...string) string {
	cmd := exec.CommandContext(ctx, name, args...)
	cmd.Dir = dir
	output, err := cmd.Output()
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(output))
}

func digestFile(path string) (string, error) {
	content, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	sum := sha256.Sum256(content)
	return "sha256:" + hex.EncodeToString(sum[:]), nil
}

var sourceDigestPattern = regexp.MustCompile(`^sha256:[0-9a-f]{64}$`)

// classifyRejection maps an MMI isError text to a reason kind. MMI returns no
// machine-readable code for these errors (measured at a8addd1, 06f5b341,
// c1724e77, 1989b827), so the kind comes from the message. The message itself
// is never stored: the ENOENT text carries an absolute local path.
func classifyRejection(text string) string {
	switch {
	case strings.Contains(text, "outside the MCP workspace root"):
		return "outside-workspace"
	case strings.Contains(text, "ENOENT"):
		return "not-found"
	default:
		return "other"
	}
}

func fail(receipt Receipt, reason string) Receipt {
	receipt.Reason = reason
	return receipt
}

// Run keeps the record-only behaviour when options carry no expectation.
func Run(ctx context.Context, mmiRoot, workspace string) Receipt {
	return RunWithOptions(ctx, mmiRoot, workspace, Options{})
}

func RunWithOptions(ctx context.Context, mmiRoot, workspace string, options Options) Receipt {
	receipt := Receipt{
		Schema: "tai.reference.mmi-readonly/v0", Tool: "inspect", ReadOnly: true,
		RealProductConnected: false,
		Notes: []string{
			"MMI MCPのinspectとselectだけを呼ぶ読み取り専用接続。",
			"原本・ledger・成果物を書き換えない。実運用の権限・認可は検証しない。",
		},
		Pin:           PinCheck{Result: "not-checked"},
		Binding:       Binding{SourceDigest: "unavailable", FingerprintCrossCheck: "unavailable", Rows: RowsBinding{Status: "unavailable"}},
		ToolSurface:   ToolSurface{Status: "unavailable", Tools: []string{}, WriteCapable: []string{}, Unmeasured: []string{}, CalledByTAI: []string{}},
		RejectionKind: RejectionKinds{Boundary: "none", Missing: "none"},
	}
	csvPath := filepath.Join(workspace, "observations.csv")
	guidePath := filepath.Join(workspace, "guide.md")
	beforeCSV, err := digestFile(csvPath)
	if err != nil {
		return fail(receipt, err.Error())
	}
	beforeGuide, err := digestFile(guidePath)
	if err != nil {
		return fail(receipt, err.Error())
	}
	beforeTree, entries, err := digestTree(workspace)
	if err != nil {
		return fail(receipt, err.Error())
	}
	receipt.SourceDigestBefore = beforeCSV
	receipt.GuideDigestBefore = beforeGuide
	receipt.Binding.CSVDigest = beforeCSV
	receipt.WorkspaceTree = WorkspaceTree{DigestBefore: beforeTree, Entries: entries}
	receipt.NodeVersion = nodeVersionOf(ctx, mmiRoot)
	facts := gatherFacts(ctx, mmiRoot, receipt.NodeVersion)
	receipt.MmiCommit = facts.Commit
	if lockDigest, err := digestFile(filepath.Join(mmiRoot, "03_Implement", "package-lock.json")); err == nil {
		receipt.PackageLockDigest = lockDigest
	}
	pin, pinReasons := evaluatePin(options, facts)
	receipt.Pin = pin
	if len(pinReasons) > 0 {
		// Fail before executing any MMI code that is not the expected version.
		return fail(receipt, strings.Join(pinReasons, "; "))
	}
	strict := pin.Checked
	if !strict {
		receipt.Notes = append(receipt.Notes, "版固定の期待値が指定されていないため、MMIのcommit・lock digest・Node versionは記録のみで照合していない。")
	}

	runCtx, cancel := context.WithTimeout(ctx, 30*time.Second)
	defer cancel()
	client, err := startMCP(runCtx, mmiRoot, workspace)
	if err != nil {
		return fail(receipt, err.Error())
	}
	defer client.close()

	initResult, err := client.call("initialize", map[string]any{
		"protocolVersion": protocolVersion,
		"capabilities":    map[string]any{},
		"clientInfo":      map[string]any{"name": "tai-reference-mmi", "version": "0"},
	})
	if err != nil {
		return fail(receipt, err.Error())
	}
	var init struct {
		ProtocolVersion string `json:"protocolVersion"`
		ServerInfo      struct {
			Name    string `json:"name"`
			Version string `json:"version"`
		} `json:"serverInfo"`
	}
	if err := json.Unmarshal(initResult, &init); err != nil {
		return fail(receipt, err.Error())
	}
	receipt.ProtocolVersion = init.ProtocolVersion
	receipt.Server = init.ServerInfo.Name + "/" + init.ServerInfo.Version
	if err := client.notify("notifications/initialized"); err != nil {
		return fail(receipt, err.Error())
	}

	surface, err := client.listTools()
	if err != nil {
		return fail(receipt, err.Error())
	}
	receipt.ToolSurface = surface
	if len(surface.WriteCapable) > 0 {
		names := strings.Join(surface.WriteCapable, ",")
		if strict {
			receipt.ReadOnly = false
			return fail(receipt, fmt.Sprintf("pinned run: MMI tools/list contains write-capable tool(s): %s", names))
		}
		// The name heuristic alone must not turn a record-only run red when MMI
		// grows a tool; the workspace digest below is the evidence of a write.
		receipt.Notes = append(receipt.Notes, fmt.Sprintf("MMIのtools/listに書込み可能と判定される名前がある（%s）。TAIはinspectとselectしか呼ばず、版固定なしのため記録のみ。", names))
	}
	if strict && (surface.Status != "listed" || len(surface.Unmeasured) > 0) {
		return fail(receipt, fmt.Sprintf("pinned run requires a complete tools/list of measured tools (status=%s, unmeasured=%s)", surface.Status, strings.Join(surface.Unmeasured, ",")))
	}

	text, isError, err := client.callTool("inspect", map[string]any{"source": "observations.csv", "values": 10})
	if err != nil {
		return fail(receipt, err.Error())
	}
	if isError {
		return fail(receipt, "inspect returned isError (reason kind: "+classifyRejection(text)+")")
	}
	var inspected inspectResult
	if err := json.Unmarshal([]byte(text), &inspected); err != nil || inspected.Candidates == nil {
		return fail(receipt, "inspect result is not JSON with a candidates array")
	}
	candidates := *inspected.Candidates
	receipt.CandidateCount = len(candidates)
	receipt.Binding.CandidateContract = inspected.CandidateContract
	if receipt.CandidateCount == 0 {
		return fail(receipt, "inspect returned zero candidates")
	}
	for _, candidate := range candidates {
		digest := candidate.Locator.SourceDigest
		if !sourceDigestPattern.MatchString(digest) {
			continue // absent or a different format: unavailable, not a mismatch
		}
		receipt.Binding.MMISourceDigest = digest
		if digest != beforeCSV {
			receipt.Binding.SourceDigest = "mismatch"
			return fail(receipt, fmt.Sprintf("inspect sourceDigest %s differs from the TAI-computed CSV digest %s", digest, beforeCSV))
		}
		receipt.Binding.SourceDigest = "match"
	}

	selection, err := selectObservations(client)
	if err != nil {
		return fail(receipt, err.Error())
	}
	previewRows := len(selection.Result.Preview.Rows)
	receipt.SelectedRows = previewRows
	if rows := selection.Result.Rows; rows != nil {
		receipt.Binding.Rows = RowsBinding{Status: "complete", Shown: rows.Shown, OfTotal: rows.OfTotal, Exact: rows.Exact, PreviewRows: previewRows}
		if rows.Shown != rows.OfTotal || !rows.Exact || rows.Shown != previewRows {
			receipt.Binding.Rows.Status = "incomplete"
			return fail(receipt, fmt.Sprintf("select rows are incomplete: shown=%d ofTotal=%d exact=%t previewRows=%d", rows.Shown, rows.OfTotal, rows.Exact, previewRows))
		}
	}
	if selection.Candidate != nil && selection.Candidate.Fingerprint != "" {
		receipt.Binding.TableFingerprint = selection.Candidate.Fingerprint
		for _, candidate := range candidates {
			if candidate.Locator.Sheet == selection.Result.Table.Sheet && candidate.Locator.Range == selection.Result.Table.Range && candidate.Fingerprint.Digest != "" {
				receipt.Binding.FingerprintCrossCheck = "match"
				if candidate.Fingerprint.Digest != selection.Candidate.Fingerprint {
					receipt.Binding.FingerprintCrossCheck = "mismatch"
					return fail(receipt, "select candidate fingerprint differs from the inspect candidate for the same table")
				}
			}
		}
	}
	if strict && (receipt.Binding.SourceDigest != "match" || receipt.Binding.FingerprintCrossCheck != "match" || receipt.Binding.Rows.Status != "complete") {
		return fail(receipt, fmt.Sprintf("pinned run requires MMI to return values that bind to TAI's (sourceDigest=%s, fingerprintCrossCheck=%s, rows=%s)",
			receipt.Binding.SourceDigest, receipt.Binding.FingerprintCrossCheck, receipt.Binding.Rows.Status))
	}
	texts := map[string]string{}
	for _, row := range selection.Result.Preview.Rows {
		if len(row) < 5 {
			continue
		}
		receipt.ObservedIDs = append(receipt.ObservedIDs, row[0])
		texts[row[0]] = row[1]
		receipt.Selected = append(receipt.Selected, SelectedObservation{
			ID: row[0], Text: row[1], Source: row[2], SourceVersion: row[3], Availability: row[4],
		})
	}
	receipt.ConflictPreserved = texts["O-02"] != "" && texts["O-03"] != "" && texts["O-02"] != texts["O-03"]
	if receipt.SelectedRows != 3 || !receipt.ConflictPreserved {
		return fail(receipt, "select did not preserve the O-02/O-03 observations")
	}

	boundaryText, boundaryError, err := client.callTool("inspect", map[string]any{"source": "../outside.csv"})
	if err != nil {
		return fail(receipt, err.Error())
	}
	if !boundaryError {
		return fail(receipt, "path outside the MMI root was not rejected")
	}
	receipt.RejectionKind.Boundary = classifyRejection(boundaryText)
	switch receipt.RejectionKind.Boundary {
	case "outside-workspace":
		receipt.BoundaryRejected = true
	case "not-found":
		return fail(receipt, "path outside the MMI root reached the filesystem (ENOENT) instead of being rejected by the workspace boundary")
	default:
		if strict {
			return fail(receipt, "path outside the MMI root was rejected for an unrecognised reason")
		}
		receipt.BoundaryRejected = true
		receipt.Notes = append(receipt.Notes, "境界外の拒否理由の文言が測定済みの版と異なる（版固定なしのため記録のみ）。")
	}
	missingText, missingError, err := client.callTool("inspect", map[string]any{"source": "missing.csv"})
	if err != nil {
		return fail(receipt, err.Error())
	}
	if !missingError {
		return fail(receipt, "missing source was not rejected")
	}
	receipt.RejectionKind.Missing = classifyRejection(missingText)
	switch receipt.RejectionKind.Missing {
	case "not-found":
		receipt.MissingSourceRejected = true
	case "outside-workspace":
		return fail(receipt, "missing.csv was reported as outside the workspace")
	default:
		if strict {
			return fail(receipt, "missing source was rejected for an unrecognised reason")
		}
		receipt.MissingSourceRejected = true
		receipt.Notes = append(receipt.Notes, "存在しないsourceの拒否理由の文言が測定済みの版と異なる（版固定なしのため記録のみ）。")
	}
	receipt.ToolSurface.CalledByTAI = slices.Clone(client.called)

	client.close() // the server is gone before the after-digests are taken
	afterCSV, err := digestFile(csvPath)
	if err != nil {
		return fail(receipt, err.Error())
	}
	afterGuide, err := digestFile(guidePath)
	if err != nil {
		return fail(receipt, err.Error())
	}
	afterTree, _, err := digestTree(workspace)
	if err != nil {
		return fail(receipt, err.Error())
	}
	receipt.SourceDigestAfter = afterCSV
	receipt.GuideDigestAfter = afterGuide
	receipt.WorkspaceTree.DigestAfter = afterTree
	if beforeCSV != afterCSV || beforeGuide != afterGuide || beforeTree != afterTree {
		receipt.ReadOnly = false
		return fail(receipt, "MMI changed the workspace")
	}
	receipt.RealProductConnected = true
	receipt.Passed = true
	return receipt
}

// cliConfig is what main passes on: where MMI and the workspace are, and the
// opt-in pin expectations.
type cliConfig struct {
	MMIRoot   string
	Workspace string
	OutPath   string
	Options   Options
}

// parseConfig reads the command line, with environment variables as the default
// of each expectation flag (a flag given on the command line wins, an empty value
// means "no expectation"). main is a thin wrapper, so the only way to give an
// expectation is tested here and not in an untested flag block.
func parseConfig(args []string, getenv func(string) string) (cliConfig, error) {
	flags := flag.NewFlagSet("reference-mmi-readonly", flag.ContinueOnError)
	mmiRoot := flags.String("mmi-root", "", "MMI checkout root (default: MMI_ROOT or ../../../markdown-matrix-injector)")
	workspace := flags.String("workspace", "testdata/workspace", "read-only MMI workspace")
	outPath := flags.String("out", "", "write receipt JSON to this file")
	expectCommit := flags.String("expect-commit", getenv("TAI_MMI_EXPECT_COMMIT"), "fail unless the MMI checkout HEAD equals this commit (env TAI_MMI_EXPECT_COMMIT)")
	expectLock := flags.String("expect-lock-digest", getenv("TAI_MMI_EXPECT_PACKAGE_LOCK_DIGEST"), "fail unless package-lock.json (CRLF->LF) has this sha256:<hex> digest (env TAI_MMI_EXPECT_PACKAGE_LOCK_DIGEST)")
	expectNode := flags.String("expect-node-major", getenv("TAI_MMI_EXPECT_NODE_MAJOR"), "fail unless node --version has this major (env TAI_MMI_EXPECT_NODE_MAJOR)")
	if err := flags.Parse(args); err != nil {
		return cliConfig{}, err
	}
	root := *mmiRoot
	if root == "" {
		root = getenv("MMI_ROOT")
	}
	if root == "" {
		root = filepath.Clean(filepath.Join("..", "..", "..", "markdown-matrix-injector"))
	}
	return cliConfig{
		MMIRoot: root, Workspace: *workspace, OutPath: *outPath,
		Options: Options{
			ExpectCommit: strings.ToLower(*expectCommit), ExpectLockDigest: strings.ToLower(*expectLock), ExpectNodeMajor: *expectNode,
		},
	}, nil
}

func main() {
	config, err := parseConfig(os.Args[1:], os.Getenv)
	if err != nil {
		if errors.Is(err, flag.ErrHelp) {
			os.Exit(0)
		}
		os.Exit(2)
	}
	receipt := RunWithOptions(context.Background(), config.MMIRoot, config.Workspace, config.Options)
	encoded, err := json.MarshalIndent(receipt, "", "  ")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	encoded = append(encoded, '\n')
	if config.OutPath != "" {
		if err := os.WriteFile(config.OutPath, encoded, 0o644); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
	}
	os.Stdout.Write(encoded)
	if !receipt.Passed {
		os.Exit(1)
	}
}
