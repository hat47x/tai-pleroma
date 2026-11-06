"""Run TAI's projected TaskRequest through EKI's own HTTP-submit execution harness."""

import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "evaluations/artifacts/eki-task-request-policy-aligned.json"
RECEIPT = ROOT / "evaluations/records/EKI-TEI-policy-execution-2026-11-03.json"

TEST_TEMPLATE = """package process

// Temporary test written by TAI: submits the projected TaskRequest through the
// Client API and expects the enrolled Agent to execute it.

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"os"
	"runtime"
	"testing"
	"time"

	"github.com/hat47x/eki-fabric/conformance/signedchain"
	agentservice "github.com/hat47x/eki-fabric/internal/agent/service"
	"github.com/hat47x/eki-fabric/internal/control/signingkeys"
	"github.com/hat47x/eki-fabric/internal/core/decisionpayload"
	"github.com/hat47x/eki-fabric/internal/core/ids"
	"github.com/hat47x/eki-fabric/internal/core/taskstate"
)

func TestTAIProjectedTaskExecution(t *testing.T) {
	path := os.Getenv("TAI_EKI_TASK_REQUEST")
	if path == "" {
		t.Fatal("TAI_EKI_TASK_REQUEST is required")
	}
	raw, err := os.ReadFile(path)
	must(t, err)

	e := newMTLSEnv(t, 0)
	e.seedPolicyNow(t)

	oldLimits, oldSandbox := signedchain.Limits, signedchain.Sandbox
	signedchain.Limits = decisionpayload.ResourceLimits{
		CPUMillis: 1000, MemoryBytes: 1 << 28, WallTimeMillis: 300_000, OutputBytesMaximum: 1 << 20,
	}
	signedchain.Sandbox = decisionpayload.SandboxPolicy{Profile: "native-fixed-spike"}
	defer func() { signedchain.Limits, signedchain.Sandbox = oldLimits, oldSandbox }()

	e.writeConfig(t)
	keyFile, controlKeys := controlSigningKeys(t, e)
	e.enableDispatch(t, keyFile)
	control := e.startControl(t)

	now := time.Now().UTC()
	auth := signedchain.New(t, now.Add(-2*time.Hour), 31)
	command, args := "/bin/echo", []string{"hello"}
	if runtime.GOOS == "windows" {
		command, args = "cmd.exe", []string{"/c", "echo", "hello"}
	}
	agentSide := e.assignmentAgentWithSigningKeys(t, "tai", auth, now, controlKeys,
		&agentservice.ExecutionConfig{Command: command, Args: args})
	_ = agentSide.start(t)

	request, err := http.NewRequest(http.MethodPost, "http://"+e.clientAddr+"/v1/tasks", bytes.NewReader(raw))
	must(t, err)
	request.Header.Set("Authorization", "Bearer "+clientToken)
	request.Header.Set("Content-Type", "application/json")
	request.Header.Set("Idempotency-Key", "tai-projection-e2e-0001")
	response, err := http.DefaultClient.Do(request)
	must(t, err)
	body, err := io.ReadAll(io.LimitReader(response.Body, 1<<20))
	response.Body.Close()
	must(t, err)
	if response.StatusCode != http.StatusAccepted {
		t.Fatalf("submit = %d: %s", response.StatusCode, body)
	}
	var accepted struct {
		TaskID string `json:"task_id"`
	}
	must(t, json.Unmarshal(body, &accepted))
	taskID, err := ids.ParseTaskID(accepted.TaskID)
	must(t, err)

	store := openState(t, e.controlDB)
	released := false
	for attempt := 0; attempt < 10 && !released; attempt++ {
		task, err := store.LoadTask(t.Context(), taskID)
		must(t, err)
		switch task.Phase {
		case taskstate.TaskPhaseAdmitted:
			next := task
			next.Phase, next.UpdatedAt = taskstate.TaskPhaseReady, time.Now().UTC()
			next.Revision = task.Revision + 1
			if err := store.CompareAndSwapTask(t.Context(), taskID, task.Revision, next); err == nil {
				released = true
			} else {
				time.Sleep(10 * time.Millisecond)
			}
		case taskstate.TaskPhaseReady, taskstate.TaskPhaseActive:
			released = true
		default:
			t.Fatalf("task phase = %s", task.Phase)
		}
	}
	if !released {
		t.Fatal("the Task was not released to the dispatch loop")
	}
	store.Close()

	waitFor(t, "agent execution and claim", func() (bool, string) {
		executed, claimed := false, false
		for _, ev := range readEvents(t, agentSide.events) {
			if ev.ExecutionStatus == "completed" {
				executed = true
			}
			if ev.ClaimDecision != "" {
				claimed = true
			}
		}
		return executed && claimed, control.out.String()
	})

	finalStore := openState(t, e.controlDB)
	defer finalStore.Close()
	attempts, err := finalStore.ListAttemptsByTask(t.Context(), taskID)
	must(t, err)
	var foundID ids.AttemptID
	for _, attempt := range attempts {
		if attempt.WorkerIdentity == agentSide.worker {
			foundID = attempt.ID
		}
	}
	if foundID == "" {
		t.Fatalf("the projected Task was not assigned to the Agent: %+v", attempts)
	}
	claim, ok, err := finalStore.LoadResultClaim(t.Context(), foundID)
	must(t, err)
	if !ok {
		t.Fatal("the Agent's ResultClaim was not stored")
	}
	t.Logf("TAI_RESULT task=%s attempt=%s claim=%s", taskID, foundID, claim.OutputDigest().Hex())
	_ = signingkeys.File{}
}
"""


def run_test(eki, envelope_path):
    target = eki / "conformance/process/zz_tai_projection_e2e_test.go"
    env = {**os.environ, "TAI_EKI_TASK_REQUEST": str(envelope_path)}
    try:
        target.write_text(TEST_TEMPLATE, encoding="utf-8")
        return subprocess.run(
            ["go", "test", "./conformance/process", "-run", "TestTAIProjectedTaskExecution", "-v"],
            cwd=eki,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    finally:
        target.unlink(missing_ok=True)


def main():
    eki = Path(os.environ.get("EKI_REPO", r"D:\GIT\hat47x\eki-wt-proj"))
    flat = json.loads(ARTIFACT.read_text(encoding="utf-8"))["taskRequest"]

    def envelope(wall_seconds, output_bytes, network_bytes):
        return {
            "schema": flat["schema"],
            "executor": {"id": flat["executorId"], "version_constraint": flat["versionConstraint"]},
            "inputs": [],
            "parameters": {},
            "resources": {
                "cpu_millis": flat["cpuMillis"],
                "memory_bytes": flat["memoryBytes"],
                "wall_time_seconds": wall_seconds,
                "output_bytes_max": output_bytes,
                "network_bytes_max": network_bytes,
            },
            "reliability": {
                "retryable": flat["retryable"],
                "preemptible": flat["preemptible"],
                "checkpointable": flat["checkpointable"],
                "deterministic": flat["deterministic"],
                "max_attempts": flat["maxAttempts"],
                "effect_mode": flat["effectMode"],
            },
            "priority": flat["priority"],
        }

    workdir = Path(tempfile.mkdtemp(prefix="tai-eki-envelope-"))
    first_path = workdir / "task-request-projected.json"
    first_path.write_text(json.dumps(envelope(flat["wallTimeSeconds"], flat["outputBytesMax"], flat["networkBytesMax"]), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    first = run_test(eki, first_path)
    first_rejected = "422" in first.stdout and "RESOURCE_BUDGET_EXCEEDED" in first.stdout

    second = None
    second_path = None
    if first.returncode != 0:
        second_path = workdir / "task-request-clamped.json"
        second_path.write_text(json.dumps(envelope(60, 1 << 20, 1 << 20), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        second = run_test(eki, second_path)

    output = first.stdout + first.stderr
    if second is not None and second.returncode == 0:
        output = second.stdout + second.stderr
    match = re.search(r"TAI_RESULT task=(\S+) attempt=(\S+) claim=([0-9a-f]+)", output)
    passed = (second.returncode == 0 if second is not None else first.returncode == 0) and match is not None
    receipt = {
        "schema": "tai.reference.eki-projection-execution/v0",
        "synthetic": False,
        "evidenceKind": "real-execution",
        "publicationAllowed": False,
        "date": time.strftime("%Y-%m-%d"),
        "host": "Windows with the EKI checkout, its conformance harness, and a temporary test file",
        "command": "python integrations/tools/eki_projection_execution.py",
        "result": "PASS" if passed else "FAIL",
        "artifact": {"path": str(ARTIFACT.relative_to(ROOT)).replace("\\", "/")},
        "observed": {
            "projectedWallSeconds": flat["wallTimeSeconds"],
            "projectedOutputBytesMax": flat["outputBytesMax"],
            "projectedNetworkBytesMax": flat["networkBytesMax"],
            "projectedSubmissionRejected": first_rejected,
            "firstExitCode": first.returncode,
            "secondExitCode": second.returncode if second is not None else None,
            "taskId": match.group(1) if match else None,
            "attemptId": match.group(2) if match else None,
            "claimDigest": match.group(3) if match else None,
            "logTail": output.strip().splitlines()[-10:],
        },
        "scope": "Submits TAI's projected TaskRequest through EKI's Client API. The projected wall-time budget exceeds the harness policy, so when it is rejected the tool retries with wall_time_seconds, output_bytes_max and network_bytes_max clamped to the harness policy (60 s, 1 MiB, 1 MiB) to show the execution path. This is EKI's TEST PROFILE, not Worker Protocol compatibility.",
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "rejected": first_rejected, "task": receipt["observed"]["taskId"]}))


if __name__ == "__main__":
    raise SystemExit(main())