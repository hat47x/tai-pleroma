#!/usr/bin/env bash
set -euo pipefail

EKI_ROOT="${EKI_ROOT:-/home/hat47x/eki-worker}"
IMAGE="${EKI_IMAGE:-golang:1.27}"

docker run --rm \
  -v "$EKI_ROOT":/src \
  -w /src \
  "$IMAGE" \
  sh -c 'mkdir -p /out && go build -o /out/eki-control ./cmd/eki-control && go build -o /out/eki-agent ./cmd/eki-agent && /out/eki-control --version && /out/eki-agent --version'
