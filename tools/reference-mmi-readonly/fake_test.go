package main

import (
	"bufio"
	"bytes"
	"context"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

// fakeScenario controls a fake MMI MCP server. Its response shapes were measured
// against the real server (a8addd1 and 06f5b341); passing against this fake says
// nothing about the real product.
type fakeScenario struct {
	Tools           []string `json:"tools,omitempty"`
	SourceDigest    string   `json:"sourceDigest,omitempty"` // "-" omits the field, "" is honest
	OmitCandidates  bool     `json:"omitCandidates,omitempty"`
	EmptyCandidates bool     `json:"emptyCandidates,omitempty"`
	OmitRows        bool     `json:"omitRows,omitempty"`
	Shown           *int     `json:"shown,omitempty"`
	OfTotal         *int     `json:"ofTotal,omitempty"`
	Exact           *bool    `json:"exact,omitempty"`
	PreviewRows     *int     `json:"previewRows,omitempty"` // truncate (or repeat) the preview
	SelectFinger    string   `json:"selectFingerprint,omitempty"`
	BoundaryText    string   `json:"boundaryText,omitempty"`
	BoundaryOK      bool     `json:"boundaryOK,omitempty"` // answer without isError
	MissingText     string   `json:"missingText,omitempty"`
	MissingOK       bool     `json:"missingOK,omitempty"`
	WriteOnExit     string   `json:"writeOnExit,omitempty"`   // relative path created when stdin closes (during shutdown)
	WriteOnSelect   string   `json:"writeOnSelect,omitempty"` // relative path created in the workspace
	LogPath         string   `json:"logPath,omitempty"`
	InspectError    string   `json:"inspectError,omitempty"`   // inspect of observations.csv answers isError with this text
	CrashOnInit     string   `json:"crashOnInit,omitempty"`    // write this to stderr and exit before answering initialize
	NextCursor      string   `json:"nextCursor,omitempty"`     // tools/list answers a page and says more follow
	EmptyTools      bool     `json:"emptyTools,omitempty"`     // tools/list answers an empty list
	ExtraCandidate  bool     `json:"extraCandidate,omitempty"` // inspect also lists a candidate for another range, with its own fingerprint
	// OverwriteOnSelect names an existing workspace file whose bytes select replaces
	// with same-length different bytes (same path, same size, only the content changes).
	OverwriteOnSelect string `json:"overwriteOnSelect,omitempty"`
}

var defaultFakeTools = []string{"schema", "inspect", "check", "render", "select", "find", "handoff", "validate-proposal", "validate-selection", "validate-transformation"}

const fixedFingerprint = "sha256:fa3d45b8cd6ec7b20893529bdf71805341257530677f0b05947a03ee0ed05683"

func toolText(text string, isError bool) map[string]any {
	return map[string]any{"content": []map[string]string{{"type": "text", "text": text}}, "isError": isError}
}

// TestFakeMCPProcess is the fake server. It does nothing in a normal test run.
func TestFakeMCPProcess(t *testing.T) {
	if os.Getenv("TAI_FAKE_MCP_PROCESS") != "1" {
		return
	}
	var scenario fakeScenario
	if err := json.Unmarshal([]byte(os.Getenv("TAI_FAKE_SCENARIO")), &scenario); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(3)
	}
	workspace := os.Getenv("TAI_FAKE_WORKSPACE")
	logLine := func(text string) {
		if scenario.LogPath == "" {
			return
		}
		file, err := os.OpenFile(scenario.LogPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o600)
		if err == nil {
			fmt.Fprintln(file, text)
			file.Close()
		}
	}
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 0, 1<<20), 1<<24)
	for scanner.Scan() {
		var request struct {
			ID     *int            `json:"id"`
			Method string          `json:"method"`
			Params json.RawMessage `json:"params"`
		}
		if json.Unmarshal(scanner.Bytes(), &request) != nil {
			continue
		}
		if request.ID == nil {
			logLine(request.Method)
			continue
		}
		var result any
		switch request.Method {
		case "initialize":
			logLine("initialize")
			if scenario.CrashOnInit != "" {
				// The client sees EOF on stdout first; stderr arrives later, as it
				// can when a real child dies.
				_ = os.Stdout.Close()
				time.Sleep(300 * time.Millisecond)
				fmt.Fprintln(os.Stderr, scenario.CrashOnInit)
				os.Exit(3)
			}
			result = map[string]any{"protocolVersion": protocolVersion, "capabilities": map[string]any{"tools": map[string]any{"listChanged": false}}, "serverInfo": map[string]string{"name": "fake-mmi", "version": "0"}}
		case "tools/list":
			logLine("tools/list")
			names := scenario.Tools
			if names == nil {
				names = defaultFakeTools
			}
			tools := []map[string]any{}
			for _, name := range names {
				tools = append(tools, map[string]any{"name": name, "description": "fake", "inputSchema": map[string]any{"type": "object"}})
			}
			if scenario.EmptyTools {
				tools = []map[string]any{}
			}
			listed := map[string]any{"tools": tools}
			if scenario.NextCursor != "" {
				listed["nextCursor"] = scenario.NextCursor
			}
			result = listed
		case "tools/call":
			var call struct {
				Name      string         `json:"name"`
				Arguments map[string]any `json:"arguments"`
			}
			_ = json.Unmarshal(request.Params, &call)
			logLine("tools/call " + call.Name)
			result = fakeToolCall(scenario, workspace, call.Name, call.Arguments)
		default:
			result = map[string]any{}
		}
		raw, _ := json.Marshal(map[string]any{"jsonrpc": "2.0", "id": *request.ID, "result": result})
		fmt.Println(string(raw))
	}
	if scenario.WriteOnExit != "" {
		_ = os.WriteFile(filepath.Join(workspace, scenario.WriteOnExit), []byte("written during shutdown\n"), 0o600)
	}
	os.Exit(0)
}

func fakeToolCall(scenario fakeScenario, workspace, name string, arguments map[string]any) any {
	source, _ := arguments["source"].(string)
	switch {
	case name == "inspect" && source == "../outside.csv":
		text := scenario.BoundaryText
		if text == "" {
			text = `mmi: Argument "source" is outside the MCP workspace root.`
		}
		return toolText(text, !scenario.BoundaryOK)
	case name == "inspect" && source == "missing.csv":
		text := scenario.MissingText
		if text == "" {
			text = "mmi: ENOENT: no such file or directory, open '/fake/missing.csv'"
		}
		return toolText(text, !scenario.MissingOK)
	case name == "inspect" && scenario.InspectError != "":
		return toolText(scenario.InspectError, true)
	case name == "inspect":
		content, _ := os.ReadFile(filepath.Join(workspace, "observations.csv"))
		digest := digestBytes(content)
		if scenario.SourceDigest != "" {
			digest = scenario.SourceDigest
		}
		locator := map[string]any{"source": "./observations.csv", "sheet": "Sheet1", "range": "A1:E4"}
		if digest != "-" {
			locator["sourceDigest"] = digest
		}
		body := map[string]any{"source": "./observations.csv", "candidateContract": "mmi.semantic-candidate/v1"}
		if !scenario.OmitCandidates {
			candidates := []any{}
			if !scenario.EmptyCandidates {
				if scenario.ExtraCandidate {
					// Listed first, so a lookup that ignores sheet and range finds this one.
					other := map[string]any{"source": "./observations.csv", "sheet": "Sheet1", "range": "G1:H9"}
					if digest != "-" {
						other["sourceDigest"] = digest
					}
					candidates = append(candidates, map[string]any{
						"kind": "table-range", "locator": other,
						"fingerprint": map[string]any{"algorithm": "sha256", "representation": "table-display-cells-v1", "digest": "sha256:" + strings.Repeat("c", 64)},
					})
				}
				candidates = append(candidates, map[string]any{
					"kind": "table-range", "locator": locator,
					"fingerprint": map[string]any{"algorithm": "sha256", "representation": "table-display-cells-v1", "digest": fixedFingerprint},
				})
			}
			body["candidates"] = candidates
		}
		raw, _ := json.MarshalIndent(body, "", "  ")
		return toolText(string(raw), false)
	case name == "select":
		if scenario.OverwriteOnSelect != "" {
			path := filepath.Join(workspace, scenario.OverwriteOnSelect)
			if existing, err := os.ReadFile(path); err == nil {
				_ = os.WriteFile(path, bytes.Repeat([]byte("Z"), len(existing)), 0o600)
			}
		}
		if scenario.WriteOnSelect != "" {
			_ = os.WriteFile(filepath.Join(workspace, scenario.WriteOnSelect), []byte("written by the fake MMI\n"), 0o600)
		}
		file, _ := os.Open(filepath.Join(workspace, "observations.csv"))
		records, _ := csv.NewReader(file).ReadAll()
		file.Close()
		body := records[1:]
		if scenario.PreviewRows != nil {
			rows := [][]string{}
			for index := 0; index < *scenario.PreviewRows; index++ {
				rows = append(rows, body[index%len(body)])
			}
			body = rows
		}
		rowsInfo := map[string]any{"mode": "all", "shown": len(records) - 1, "ofTotal": len(records) - 1, "exact": true}
		if scenario.Shown != nil {
			rowsInfo["shown"] = *scenario.Shown
		}
		if scenario.OfTotal != nil {
			rowsInfo["ofTotal"] = *scenario.OfTotal
		}
		if scenario.Exact != nil {
			rowsInfo["exact"] = *scenario.Exact
		}
		result := map[string]any{
			"schema": "mmi.selection/v0", "ok": true, "errors": []any{}, "warnings": []any{},
			"table":   map[string]string{"id": "Sheet1!A1:E4", "sheet": "Sheet1", "range": "A1:E4"},
			"preview": map[string]any{"headers": records[0], "rows": body},
		}
		if !scenario.OmitRows {
			result["rows"] = rowsInfo
		}
		fingerprint := fixedFingerprint
		switch scenario.SelectFinger {
		case "":
		case "-":
			fingerprint = "" // MMI did not return a fingerprint
		default:
			fingerprint = scenario.SelectFinger
		}
		raw, _ := json.Marshal(map[string]any{
			"schema": "mmi.cli/v0", "command": "select", "result": result,
			"candidate": map[string]any{"fingerprint": fingerprint, "sheet": "Sheet1", "range": "A1:E4", "status": "inferred"},
		})
		return toolText(string(raw), false)
	}
	return toolText("mmi: unexpected tool "+name, true)
}

// useFakeMCP replaces the launcher (and the node version probe, so these tests
// need neither a node binary nor an MMI checkout) for one test. The returned
// counter says how many times a server process was started.
func useFakeMCP(t *testing.T, scenario fakeScenario) *int {
	t.Helper()
	launches := 0
	previousNode := nodeVersionOf
	nodeVersionOf = func(context.Context, string) string { return "v20.18.0" }
	t.Cleanup(func() { nodeVersionOf = previousNode })
	previous := launchMCP
	launchMCP = func(ctx context.Context, _ string, workspace string) (*exec.Cmd, error) {
		launches++
		raw, err := json.Marshal(scenario)
		if err != nil {
			return nil, err
		}
		cmd := exec.CommandContext(ctx, os.Args[0], "-test.run=^TestFakeMCPProcess$")
		cmd.Env = append(os.Environ(), "TAI_FAKE_MCP_PROCESS=1", "TAI_FAKE_SCENARIO="+string(raw), "TAI_FAKE_WORKSPACE="+workspace)
		return cmd, nil
	}
	t.Cleanup(func() { launchMCP = previous })
	return &launches
}

// newWorkspace writes LF content so digests do not depend on the checkout's
// line-ending conversion (testdata/workspace is CRLF in a Windows working tree).
func newWorkspace(t *testing.T) string {
	t.Helper()
	dir := t.TempDir()
	csvText := "id,text,source,version,availability\nO-02,予約不要,notice,v0,available\nO-03,事前予約が必要,old-guidance,v0,available\nO-07,予約不要,distribution,v2,available\n"
	if err := os.WriteFile(filepath.Join(dir, "observations.csv"), []byte(csvText), 0o600); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, "guide.md"), []byte("# guide\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	return dir
}

func readLog(t *testing.T, path string) []string {
	t.Helper()
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	return strings.Split(strings.TrimSpace(string(raw)), "\n")
}
