package main

import (
	"bytes"
	"context"
	"fmt"
	"os/exec"
	"strings"
)

// runOutput runs a go command and returns only its standard output. The
// standard error is kept for the error message, so a tool message such as
// "go: downloading ..." cannot be mixed into a JSON document that the caller
// parses.
func runOutput(ctx context.Context, dir string, args ...string) ([]byte, error) {
	cmd := exec.CommandContext(ctx, "go", args...)
	cmd.Dir = dir
	var stderr bytes.Buffer
	cmd.Stderr = &stderr
	output, err := cmd.Output()
	if err != nil {
		return output, fmt.Errorf("go %s: %w: %s", strings.Join(args, " "), err, strings.TrimSpace(stderr.String()))
	}
	return output, nil
}
