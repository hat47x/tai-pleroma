package harnessadapter

import (
	"bytes"
	"context"
	"errors"
	"os"
	"os/exec"
	"strings"
	"time"
)

// ExecSpec is one external process the adapter wants to run. It is the single
// place where argv, cwd, stdin and environment are decided, so a test can
// substitute a fake and the real path stays auditable.
type ExecSpec struct {
	// Argv is the exact argument vector. No shell is involved.
	Argv []string `json:"argv"`
	// Dir is the working directory. Empty means inherit.
	Dir string `json:"dir,omitempty"`
	// Stdin is the exact bytes fed to the process.
	Stdin []byte `json:"-"`
	// Env is the extra environment, as KEY=VALUE. Secrets are never recorded.
	Env []string `json:"env,omitempty"`
	// Timeout bounds the process.
	Timeout time.Duration `json:"-"`
}

// ExecResult is what came back.
type ExecResult struct {
	ExitCode int    `json:"exitCode"`
	Stdout   []byte `json:"-"`
	Stderr   []byte `json:"-"`
	// LaunchError is set when the process could not be started at all, which is
	// distinct from a non-zero exit.
	LaunchError string `json:"launchError,omitempty"`
	DurationMS  int64  `json:"durationMs,omitempty"`
}

// Runner executes an ExecSpec. Production code uses ProcessRunner; tests use
// FakeRunner. Keeping this seam explicit is what lets contract tests run
// without a harness being installed, and what stops a test double from being
// mistaken for a real connection.
type Runner interface {
	Exec(ctx context.Context, spec ExecSpec) (ExecResult, error)
}

// ProcessRunner is the real runner.
type ProcessRunner struct{}

// Exec runs spec as a real child process.
func (ProcessRunner) Exec(ctx context.Context, spec ExecSpec) (ExecResult, error) {
	if len(spec.Argv) == 0 {
		return ExecResult{}, errors.New("empty argv")
	}
	if spec.Timeout > 0 {
		var cancel context.CancelFunc
		ctx, cancel = context.WithTimeout(ctx, spec.Timeout)
		defer cancel()
	}
	cmd := exec.CommandContext(ctx, spec.Argv[0], spec.Argv[1:]...)
	if spec.Dir != "" {
		cmd.Dir = spec.Dir
	}
	if len(spec.Env) > 0 {
		cmd.Env = append(os.Environ(), spec.Env...)
	}
	if spec.Stdin != nil {
		cmd.Stdin = strings.NewReader(string(spec.Stdin))
	}
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	start := time.Now()
	err := cmd.Run()
	res := ExecResult{
		ExitCode:   -1,
		Stdout:     stdout.Bytes(),
		Stderr:     stderr.Bytes(),
		DurationMS: time.Since(start).Milliseconds(),
	}
	var exitErr *exec.ExitError
	if errors.As(err, &exitErr) {
		res.ExitCode = exitErr.ExitCode()
		return res, nil
	}
	if err != nil {
		res.LaunchError = err.Error()
		return res, nil
	}
	res.ExitCode = 0
	return res, nil
}

// LookPath resolves an executable. Declared on the Runner so tests can fake
// "the harness is not installed" without touching PATH.
type PathResolver interface {
	LookPath(file string) (string, error)
}

// OSPathResolver resolves through the OS PATH.
type OSPathResolver struct{}

// LookPath delegates to exec.LookPath.
func (OSPathResolver) LookPath(file string) (string, error) { return exec.LookPath(file) }

// ---------------------------------------------------------------------------
// FakeRunner: a test double. It records specs and replays canned results.
// ---------------------------------------------------------------------------

// FakeRunner is a deterministic Runner for contract tests. It never touches the
// network or a real harness binary.
type FakeRunner struct {
	// Script maps a joined argv prefix to the result to return. The first
	// matching prefix wins; matching is on the whole argv joined by spaces so
	// tests stay readable.
	Script []FakeStep

	// Calls records every spec the adapter produced, in order.
	Calls []ExecSpec

	// Default is returned when no script entry matches.
	Default ExecResult
}

// FakeStep is one canned response.
type FakeStep struct {
	// Match is a substring that must appear in the joined argv.
	Match string
	// Result is returned as-is.
	Result ExecResult
	// Err makes Exec return an error.
	Err error
}

// Exec records the spec and replays the scripted result.
func (f *FakeRunner) Exec(_ context.Context, spec ExecSpec) (ExecResult, error) {
	f.Calls = append(f.Calls, spec)
	joined := strings.Join(spec.Argv, " ")
	for _, step := range f.Script {
		if step.Match == "" || strings.Contains(joined, step.Match) {
			if step.Err != nil {
				return ExecResult{}, step.Err
			}
			return step.Result, nil
		}
	}
	return f.Default, nil
}

// FakePathResolver answers LookPath from a fixed map.
type FakePathResolver struct {
	Paths map[string]string
}

// LookPath returns the mapped path or an error shaped like exec.LookPath's.
func (p FakePathResolver) LookPath(file string) (string, error) {
	if path, ok := p.Paths[file]; ok {
		return path, nil
	}
	return "", &exec.Error{Name: file, Err: exec.ErrNotFound}
}

// ArgvJoined renders an argv for evidence and matching.
func ArgvJoined(argv []string) string { return strings.Join(argv, " ") }

// Quote renders an argv for a human-readable evidence record. It is not used to
// build commands and is not a shell grammar: it wraps arguments containing
// whitespace in double quotes and leaves everything else verbatim.
func Quote(argv []string) string {
	parts := make([]string, 0, len(argv))
	for _, a := range argv {
		if strings.ContainsAny(a, " \t") {
			parts = append(parts, `"`+a+`"`)
			continue
		}
		parts = append(parts, a)
	}
	return strings.Join(parts, " ")
}
