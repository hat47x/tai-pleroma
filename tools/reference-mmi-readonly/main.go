package main

import (
	"bufio"
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

const protocolVersion = "2024-11-05"

type Receipt struct {
	Schema                string            `json:"schema"`
	Server                string            `json:"server"`
	ProtocolVersion       string            `json:"protocolVersion"`
	MmiCommit             string            `json:"mmiCommit,omitempty"`
	PackageLockDigest     string            `json:"packageLockDigest,omitempty"`
	NodeVersion           string            `json:"nodeVersion,omitempty"`
	Tool                  string            `json:"tool"`
	CandidateCount        int               `json:"candidateCount"`
	SelectedRows          int               `json:"selectedRows"`
	ObservedIDs           []string          `json:"observedIds"`
	ConflictPreserved     bool              `json:"conflictPreserved"`
	SourceDigestBefore    string            `json:"sourceDigestBefore"`
	SourceDigestAfter     string            `json:"sourceDigestAfter"`
	GuideDigestBefore     string            `json:"guideDigestBefore"`
	GuideDigestAfter      string            `json:"guideDigestAfter"`
	BoundaryRejected      bool              `json:"boundaryRejected"`
	MissingSourceRejected bool              `json:"missingSourceRejected"`
	ReadOnly              bool              `json:"readOnly"`
	RealProductConnected  bool              `json:"realProductConnected"`
	Passed                bool              `json:"passed"`
	Reason                string            `json:"reason,omitempty"`
	Notes                 []string          `json:"notes"`
	Extra                 map[string]string `json:"extra,omitempty"`
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
	cmd    *exec.Cmd
	stdin  io.WriteCloser
	reader *bufio.Reader
	stderr bytes.Buffer
	nextID int
}

func startMCP(ctx context.Context, mmiRoot, workspace string) (*mcpClient, error) {
	node, err := exec.LookPath("node")
	if err != nil {
		return nil, fmt.Errorf("node is unavailable: %w", err)
	}
	workspace, err = filepath.Abs(workspace)
	if err != nil {
		return nil, err
	}
	implement := filepath.Join(mmiRoot, "03_Implement")
	if _, err := os.Stat(filepath.Join(implement, "src", "cli", "mcp.ts")); err != nil {
		return nil, fmt.Errorf("MMI MCP source is unavailable: %w", err)
	}
	cmd := exec.CommandContext(ctx, node, "--import", "tsx", "src/cli/mcp.ts", "--root", workspace)
	cmd.Dir = implement
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

func (c *mcpClient) close() {
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
}

type toolResult struct {
	Content []struct {
		Type string `json:"type"`
		Text string `json:"text"`
	} `json:"content"`
	IsError bool `json:"isError"`
}

func inspect(client *mcpClient, source string) (string, bool, error) {
	result, err := client.call("tools/call", map[string]any{
		"name": "inspect",
		"arguments": map[string]any{
			"source": source,
			"values": 10,
		},
	})
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

type selectionResult struct {
	Schema string `json:"schema"`
	Result struct {
		OK      bool `json:"ok"`
		Preview struct {
			Headers []string   `json:"headers"`
			Rows    [][]string `json:"rows"`
		} `json:"preview"`
		Errors []struct {
			Code    string `json:"code"`
			Message string `json:"message"`
		} `json:"errors"`
	} `json:"result"`
}

func selectObservations(client *mcpClient) (selectionResult, error) {
	result, err := client.call("tools/call", map[string]any{
		"name": "select",
		"arguments": map[string]any{
			"source":  "observations.csv",
			"table":   "Sheet1!A1:E4",
			"columns": "id,text,source,version,availability",
		},
	})
	if err != nil {
		return selectionResult{}, err
	}
	var tool toolResult
	if err := json.Unmarshal(result, &tool); err != nil {
		return selectionResult{}, err
	}
	if len(tool.Content) == 0 {
		return selectionResult{}, fmt.Errorf("select returned no content")
	}
	if tool.IsError {
		return selectionResult{}, fmt.Errorf("select returned isError: %s", tool.Content[0].Text)
	}
	var selection selectionResult
	if err := json.Unmarshal([]byte(tool.Content[0].Text), &selection); err != nil {
		return selectionResult{}, err
	}
	if !selection.Result.OK {
		return selectionResult{}, fmt.Errorf("select was rejected: %+v", selection.Result.Errors)
	}
	return selection, nil
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

func Run(ctx context.Context, mmiRoot, workspace string) Receipt {
	receipt := Receipt{
		Schema: "tai.reference.mmi-readonly/v0", Tool: "inspect", ReadOnly: true,
		RealProductConnected: false,
		Notes: []string{
			"MMI MCPのinspectとselectだけを呼ぶ読み取り専用接続。",
			"原本・ledger・成果物を書き換えない。実運用の権限・認可は検証しない。",
		},
	}
	csvPath := filepath.Join(workspace, "observations.csv")
	guidePath := filepath.Join(workspace, "guide.md")
	beforeCSV, err := digestFile(csvPath)
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	beforeGuide, err := digestFile(guidePath)
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	receipt.SourceDigestBefore = beforeCSV
	receipt.GuideDigestBefore = beforeGuide
	receipt.NodeVersion = commandOutput(ctx, "", "node", "--version")
	receipt.MmiCommit = commandOutput(ctx, mmiRoot, "git", "rev-parse", "HEAD")
	if lockDigest, err := digestFile(filepath.Join(mmiRoot, "03_Implement", "package-lock.json")); err == nil {
		receipt.PackageLockDigest = lockDigest
	}

	runCtx, cancel := context.WithTimeout(ctx, 30*time.Second)
	defer cancel()
	client, err := startMCP(runCtx, mmiRoot, workspace)
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	defer client.close()

	initResult, err := client.call("initialize", map[string]any{
		"protocolVersion": protocolVersion,
		"capabilities":    map[string]any{},
		"clientInfo":      map[string]any{"name": "tai-reference-mmi", "version": "0"},
	})
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	var init struct {
		ProtocolVersion string `json:"protocolVersion"`
		ServerInfo      struct {
			Name    string `json:"name"`
			Version string `json:"version"`
		} `json:"serverInfo"`
	}
	if err := json.Unmarshal(initResult, &init); err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	receipt.ProtocolVersion = init.ProtocolVersion
	receipt.Server = init.ServerInfo.Name + "/" + init.ServerInfo.Version
	if err := client.notify("notifications/initialized"); err != nil {
		receipt.Reason = err.Error()
		return receipt
	}

	text, isError, err := inspect(client, "observations.csv")
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	if isError {
		receipt.Reason = "inspect returned isError: " + text
		return receipt
	}
	receipt.CandidateCount = strings.Count(text, `"candidates"`)
	if receipt.CandidateCount == 0 {
		receipt.Reason = "inspect result did not contain candidates"
		return receipt
	}
	selection, err := selectObservations(client)
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	receipt.SelectedRows = len(selection.Result.Preview.Rows)
	texts := map[string]string{}
	for _, row := range selection.Result.Preview.Rows {
		if len(row) < 2 {
			continue
		}
		receipt.ObservedIDs = append(receipt.ObservedIDs, row[0])
		texts[row[0]] = row[1]
	}
	receipt.ConflictPreserved = texts["O-02"] != "" && texts["O-03"] != "" && texts["O-02"] != texts["O-03"]
	if receipt.SelectedRows != 3 || !receipt.ConflictPreserved {
		receipt.Reason = "select did not preserve the O-02/O-03 observations"
		return receipt
	}
	_, boundaryError, err := inspect(client, "../outside.csv")
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	receipt.BoundaryRejected = boundaryError
	if !receipt.BoundaryRejected {
		receipt.Reason = "path outside the MMI root was not rejected"
		return receipt
	}
	_, missingError, err := inspect(client, "missing.csv")
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	receipt.MissingSourceRejected = missingError
	if !receipt.MissingSourceRejected {
		receipt.Reason = "missing source was not rejected"
		return receipt
	}

	afterCSV, err := digestFile(csvPath)
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	afterGuide, err := digestFile(guidePath)
	if err != nil {
		receipt.Reason = err.Error()
		return receipt
	}
	receipt.SourceDigestAfter = afterCSV
	receipt.GuideDigestAfter = afterGuide
	if beforeCSV != afterCSV || beforeGuide != afterGuide {
		receipt.Reason = "MMI changed a source file"
		return receipt
	}
	receipt.RealProductConnected = true
	receipt.Passed = true
	return receipt
}

func main() {
	mmiRoot := flag.String("mmi-root", "", "MMI checkout root (default: MMI_ROOT or ../../../markdown-matrix-injector)")
	workspace := flag.String("workspace", "testdata/workspace", "read-only MMI workspace")
	outPath := flag.String("out", "", "write receipt JSON to this file")
	flag.Parse()
	root := *mmiRoot
	if root == "" {
		root = os.Getenv("MMI_ROOT")
	}
	if root == "" {
		root = filepath.Clean(filepath.Join("..", "..", "..", "markdown-matrix-injector"))
	}
	receipt := Run(context.Background(), root, *workspace)
	encoded, err := json.MarshalIndent(receipt, "", "  ")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	encoded = append(encoded, '\n')
	if *outPath != "" {
		if err := os.WriteFile(*outPath, encoded, 0o644); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
	}
	os.Stdout.Write(encoded)
	if !receipt.Passed {
		os.Exit(1)
	}
}
