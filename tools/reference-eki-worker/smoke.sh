#!/usr/bin/env bash
set -euo pipefail

# Smoke-test the EKI Control Plane binary on WSL. This is not a Task-executing
# Worker; it proves the built binary starts and rejects GET /v1/tasks (405).

EKI_ROOT="${EKI_ROOT:-/home/hat47x/eki-worker}"
IMAGE="${EKI_IMAGE:-golang:1.27}"
CONFIG="${CONFIG:-$(cd "$(dirname "$0")" && pwd)/config/control.json}"
BIN_DIR="$EKI_ROOT/bin"
CONTROL_PID=""

cleanup() {
  if [ -n "$CONTROL_PID" ] && kill -0 "$CONTROL_PID" 2>/dev/null; then
    kill "$CONTROL_PID" 2>/dev/null || true
    wait "$CONTROL_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

mkdir -p "$BIN_DIR"
docker run --rm \
  -v "$EKI_ROOT":/src \
  -w /src \
  "$IMAGE" \
  sh -c 'mkdir -p /src/bin && go build -o /src/bin/eki-control ./cmd/eki-control'

rm -f /tmp/eki-worker-smoke.db
"$BIN_DIR/eki-control" --config "$CONFIG" >/tmp/eki-worker-smoke.log 2>&1 &
CONTROL_PID=$!

for _ in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -H 'Authorization: Bearer scn001-token-0123456789' http://127.0.0.1:18086/v1/tasks || true)
  if [ "$code" = "405" ]; then
    echo "control smoke: ok (GET /v1/tasks -> 405)"
    exit 0
  fi
  sleep 1
done

echo "control smoke: failed" >&2
cat /tmp/eki-worker-smoke.log >&2 || true
exit 1
