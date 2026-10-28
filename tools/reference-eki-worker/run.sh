#!/usr/bin/env bash
set -euo pipefail

# Run the EKI Agent/Worker test profile inside the Docker engine available in WSL.
# EKI source is mounted from ext4; do not run this from /mnt/d.

EKI_ROOT="${EKI_ROOT:-/home/hat47x/eki-worker}"
IMAGE="${EKI_IMAGE:-golang:1.27}"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required" >&2
  exit 2
fi
if [ ! -f "$EKI_ROOT/go.mod" ]; then
  echo "EKI source is not at $EKI_ROOT" >&2
  exit 2
fi

docker run --rm \
  -v "$EKI_ROOT":/src \
  -w /src \
  "$IMAGE" \
  sh -c 'go test ./internal/agent/... ./internal/control/... -count=1'
